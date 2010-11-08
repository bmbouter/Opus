##############################################################################
# Copyright 2010 North Carolina State University                             #
#                                                                            #
#   Licensed under the Apache License, Version 2.0 (the "License");          #
#   you may not use this file except in compliance with the License.         #
#   You may obtain a copy of the License at                                  #
#                                                                            #
#       http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                            #
#   Unless required by applicable law or agreed to in writing, software      #
#   distributed under the License is distributed on an "AS IS" BASIS,        #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
#   See the License for the specific language governing permissions and      #
#   limitations under the License.                                           #
##############################################################################

"""
Django Project Deployer

The deployer library's job is to deploy a ready built Django project onto an
Apache+mod_wsgi setup. Functionality for other webservers may be added later.

"""

import os
import os.path
import subprocess
import re
import tempfile
import grp
import random
import shutil
import time
from glob import glob

import opus
from opus.lib.conf import OpusConfig
from opus.lib.log import get_logger
import opus.lib.deployer.ssl
log = get_logger()

def which(prog):
    paths = os.environ.get("PATH", os.defpath).split(os.pathsep)
    for path in paths:
        progpath = os.path.join(path, prog)
        if os.path.exists(progpath):
            return progpath
    return False

class DeploymentException(Exception):
    pass

class ProjectDeployer(object):
    """The project deployer. Each method performs a specific deployment action.
    The typical workflow for using the deployer is to create a deployment
    object, and call these methods in roughly this order:
    
    * secure_project() should be called first to lock down the settings and set
      permissions before any sensitive information is pushed to the
      configuration files
    * configure_database() which will set the database configuration
      parameters, pushing sensitive information into config files.
    * sync-database() which will run django's syncdb function and create the
      admin superuser for the project. This pushes sensitive information to
      the database.
    * set_paths() pushes a few absolute directory paths to the configuration
    * configure_apache() creates a wsgi entry point file and apache
      configuration file, and restarts apache. This should be the last method
      called, apache will start serving project files right after this returns.

    If using Django, the deployment model DeployedProject's deploy() method
    does all of the above.

    """

    def __init__(self, projectdir):
        """Initialize the Project Deployer with the directory root of the
        project to be deployed.

        """
        self.projectdir = projectdir

        # Find the project name by taking the last component of the path
        path = os.path.abspath(self.projectdir)
        self.projectname = os.path.basename(path)

        self.uid = None

        # Go ahead and eat up the config file into memory
        self.config = OpusConfig(os.path.join(self.projectdir, "opussettings.json"))

    def set_paths(self):
        """Sets the paths for the TEMPLATE_DIRS and the LOG_DIR
        settings
        
        """
        self.config['TEMPLATE_DIRS'] = (os.path.join(self.projectdir, "templates"),)
        self.config['LOG_DIR'] = os.path.join(self.projectdir, 'log')
        self.config['MEDIA_ROOT'] = os.path.join(self.projectdir, 'media/')
        self.config['OPUS_SECURE_UPLOADS'] = os.path.join(self.projectdir, "opus_secure_uploads/")
        self.config.save()

        # Set a new manage.py with appropriate paths
        manage = """#!/usr/bin/env python
from django.core.management import execute_from_command_line

import os, os.path
import sys
projectpath = {projectdir!r}
sys.path.append(projectpath)
sys.path.append({opuspath!r})
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
os.environ['OPUS_SETTINGS_FILE'] = os.path.join(projectpath, 'opussettings.json')
try:
    open(os.path.join(projectpath, "settings.py"), 'r')
except IOError, e:
    sys.stderr.write("Error: Can't open the file 'settings.py' in %r.\\n" % projectpath)
    sys.stderr.write(str(e)+'\\n')
    sys.exit(1)

if __name__ == "__main__":
    execute_from_command_line()
"""
        with open(os.path.join(self.projectdir, "manage.py"), 'w') as manageout:
            manageout.write(manage.format(
                projectdir=self.projectdir,
                opuspath=os.path.dirname(opus.__path__[0])))
        

    def configure_database(self, engine, *args):
        """Configure the Django database
        
        engine is one of the following:
        For 'postgresql_psycopg2', 'postgresql', 'mysql', or 'oracle' the next
        five parameters should be the name, user, password, host, and port

        For 'sqlite3' no other parameters are used, an sqlite3 database is
        created automatically.
        """

        dbuser = ''
        dbpassword = ''
        dbhost = ''
        dbport = ''
        if engine == "sqlite3":
            dbname = os.path.join(self.projectdir, "sqlite", "database.sqlite")
        elif engine in ('postgresql_psycopg2', 'postgresql', 'mysql', 'oracle'):
            if len(args) < 3:
                raise TypeError("You must specify the database username and password")
            dbname = args[0]
            if not dbname:
                raise ValueError("You must specify a value for database name")
            dbuser = args[1]
            dbpassword = args[2]
            if len(args) >= 4:
                dbhost = args[3]
            if len(args) >= 5:
                dbport = args[4]
        else:
            raise ValueError("Bad database engine")

        defaultdb = {}
        self.config['DATABASES'] = {'default': defaultdb}
        defaultdb['ENGINE'] = 'django.db.backends.{0}'.format(engine)
        defaultdb['NAME'] = dbname
        defaultdb['USER'] = dbuser
        defaultdb['PASSWORD'] = dbpassword
        defaultdb['HOST'] = dbhost
        defaultdb['PORT'] = dbport
        if defaultdb['ENGINE'].endswith("postgresql_psycopg2"):
            # Require SSL on the server
            defaultdb['OPTIONS'] = {"sslmode": "require"}

        self.config.save()

    def sync_database(self, username=None, email=None, password=None,
            secureops="secureops"):
        """Do the initial database sync. If a username, email, and password are
        provided, a superuser is created

        """
        self._sync_database(secureops)
        if username and email and password:
            self.create_superuser(username, email, password)

    def _getenv(self):
        """"Gets an environment with paths set up for a manage.py or
        djang-admin subprocess"""
        env = dict(os.environ)
        env['OPUS_SETTINGS_FILE'] = os.path.join(self.projectdir, "opussettings.json")
        env['PYTHONPATH'] = os.path.split(opus.__path__[0])[0] + ":" + \
                self.projectdir
        # Tells the logging module to disable logging, which would create
        # permission issues
        env['OPUS_LOGGING_DISABLE'] = "1"
        env['DJANGO_SETTINGS_MODULE'] = "settings"
        return env

    def _sync_database(self, secureops):
        # Runs sync on the database
        log.debug("Running syncdb")
        envpython = os.path.join(self.projectdir, "env", "bin", "python")
        # Search path for where django-admin is
        djangoadmin = which("django-admin.py")
        if not djangoadmin:
            raise DeploymentException("Could not find django-admin.py. Is it installed and in the system PATH?")
        proc = subprocess.Popen([secureops, "-y", "opus"+self.projectname,
            envpython,
            djangoadmin
            ],
                cwd=self.projectdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=self._getenv(),
                close_fds=True,
                )
        output = proc.communicate()[0]
        ret = proc.wait()
        if ret:
            raise DeploymentException("syncdb failed. Code {0}. {1}".format(ret, output))

    def create_superuser(self, username, email, password):
        """Creates a new superuser with given parameters in the target
        project"""
        # Create the user and set the password by invoking django code to
        # directly interface with the database. Do this in a sub process so as
        # not to have all the Django modules loaded and configured in this
        # interpreter, which may conflict with any Django settings already
        # imported.
        # This is done this way to avoid calling manage.py or running any
        # client code that the user has access to, since this happens with
        # Opus' permissions, not the deployed project permissions.
        log.debug("Creating superuser")
        dbconfig = self.config['DATABASES']['default']
        if dbconfig['ENGINE'].endswith("postgresql_psycopg2"):
            options = """'OPTIONS': {'sslmode': 'require'}"""
        else:
            options = ""
        program = """
import os
try:
    del os.environ['DJANGO_SETTINGS_MODULE']
except KeyError:
    pass
from django.conf import settings
settings.configure(DATABASES = {{'default':
    {{
        'ENGINE': '{engine}',
        'NAME': {name!r},
        'USER': {user!r},
        'PASSWORD': {password!r},
        'HOST': {host!r},
        'PORT': {port!r},
        {options}
    }}
}})
from django.contrib.auth.models import User
User.objects.create_superuser({suuser!r},{suemail!r},{supassword!r})
        """.format(
                engine=dbconfig['ENGINE'],
                name=dbconfig['NAME'],
                user=dbconfig['USER'],
                password=dbconfig['PASSWORD'],
                host=dbconfig['HOST'],
                port=dbconfig['PORT'],
                suuser=username,
                suemail=email,
                supassword=password,
                options=options
                )

        process = subprocess.Popen(["python"], stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                close_fds=True,
                )
        output = process.communicate(program)[0]
        ret = process.wait()
        if ret:
            raise DeploymentException("Setting super user password failed. {0}".format(output))

    def _pre_secure(self):
        # Creates a directory and empty file for the sqlite3 database,
        # and touches empty files for the ssl certificates and keyfiles.
        # Done so that permissions can be set on these items *before* sensitive
        # information is put into them
        os.mkdir(
                os.path.join(self.projectdir, "sqlite")
                )
        os.mkdir(
                os.path.join(self.projectdir, "run")
                )
        os.mkdir(
                os.path.join(self.projectdir, "opus_secure_uploads")
                )
        d = open(os.path.join(self.projectdir, "sqlite", "database.sqlite"), 'w')
        d.close()

        open(os.path.join(self.projectdir, "ssl.crt"), 'w').close()
        open(os.path.join(self.projectdir, "ssl.key"), 'w').close()

    def secure_project(self, secureops="secureops"):
        """Calling this does two things: It calls useradd to create a new Linux
        user, and it changes permissions on settings.py so only that user can
        access it. This is a necessary step before calling configure_apache()

        Pass in the path to the secureops binary, otherwise PATH is searched

        """
        # Touch certian files and directories so they can be secured before
        # they're filled with sensitive information
        self._pre_secure()

        # Attempt to create a linux user, and change user permissions
        # of the settings.py and the sqlite database 
        # Name the user after opus and the project name
        newname = "opus"+self.projectname
        command = [secureops, 
                "-c",
                newname,
                ]
        # Set sensitive files appropriately
        settingsfile = os.path.join(self.projectdir, "settings.py")
        command.append(settingsfile)
        # Also secure log directory
        command.append(os.path.join(self.projectdir, "log"))
        # And the opus settings
        command.append(os.path.join(self.projectdir, "opussettings.json"))
        # And sqlite dir and file
        command.append(os.path.join(self.projectdir, "sqlite"))
        command.append(os.path.join(self.projectdir, "sqlite", "database.sqlite"))
        command.append(os.path.join(self.projectdir, "ssl.crt"))
        command.append(os.path.join(self.projectdir, "ssl.key"))
        command.append(os.path.join(self.projectdir, "run"))
        command.append(os.path.join(self.projectdir, "opus_secure_uploads"))
        # Set writable several directories under the requirements env
        command.append(os.path.join(self.projectdir, "env"))
        for d in (['bin'], ['include'], ['lib','python*','site-packages']):
            p = glob(os.path.join(self.projectdir, "env", *d))[0]
            command.append(p)

        log.info("Calling secure operation with arguments {0!r}".format(command))
        log.debug("cwd: {0}".format(os.getcwd()))
        proc = subprocess.Popen(command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                )
        output = proc.communicate()[0]
        ret = proc.wait()
        log.debug("Secure ops finished. Ret: {1}, Output: {0!r}".format(output, ret))
        if ret:
            raise DeploymentException("Could not create user and/or change file permissions. {0}. Ret: {1}".format(output, ret))

        # Also an important step: delete settings.pyc if it exists, which could
        # have sensitive information in it (although not likely, the usual
        # setup is to store settings in opussettings.json
        settingspyc = os.path.join(self.projectdir, "settings.pyc")
        if os.path.exists(settingspyc):
            try:
                os.unlink(settingspyc)
            except IOError, e:
                raise DeploymentException("Couldn't delete settings.pyc! {0}".format(e))

        # Generate a new secret key for the settings. One may have been set at
        # create time, but it should be considered public knowledge since the
        # permissions hadn't been set yet.
        self.config["SECRET_KEY"]  = ''.join([random.choice(
            'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
            for _ in range(50)])
        self.config.save()


    def configure_apache(self, apache_conf_dir, httpport, sslport,
            servername_suffix, pythonpath="", secureops="secureops",
            ssl_crt=None, ssl_key=None, ssl_chain=None):
        """Configures apache to serve this Django project.
        apache_conf_dir should be apache's conf.d directory where a .conf file
        can be dropped

        httpport and sslport are used in the port part of the <VirtualHost>
        directive in the apache config file. These can be None to omit serving
        on that port/protocol.

        servername_suffix is a string that will be appended to the end of the
        project name for the apache ServerName directive

        ssl_crt and ssl_key, if specified, will be used in lieu of a self
        signed certificate.

        """
        # Check if our dest file exists, so as not to overwrite it
        config_path = os.path.join(apache_conf_dir, "opus"+self.projectname+".conf")

        # Write out a wsgi config to the project dir
        wsgi_dir = os.path.join(self.projectdir, "wsgi")
        try:
            os.mkdir(wsgi_dir)
        except OSError, e:
            import errno
            if e.errno != errno.EEXIST:
                raise
            # Directory already exists, no big deal

        if pythonpath:
            ppdirective = "sys.path.append({0!r})\n".format(pythonpath)
        else:
            ppdirective = ""

        envpath = glob(os.path.join(self.projectdir, "env",
            "lib", "python*", "site-packages"))[0]

        with open(os.path.join(wsgi_dir, "django.wsgi"), 'w') as wsgi:
            wsgi.write("""
import os
import sys
import site

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
os.environ['OPUS_SETTINGS_FILE'] = {settingspath!r}
os.environ['CELERY_LOADER'] = 'django'

{additionalpaths}

# Any dependencies for installed applications go in here
site.addsitedir({envpath!r})

# Needed so that apps can import their own things without having to know the
# project name.
sys.path.append({projectpath!r})


#import django.core.handlers.wsgi
#application = django.core.handlers.wsgi.WSGIHandler()

import opus.lib.profile
application = opus.lib.profile.OpusWSGIHandler()
""".format(projectname = self.projectname,
           projectpath = self.projectdir,
           additionalpaths = ppdirective,
           settingspath = os.path.join(self.projectdir, "opussettings.json"),
           envpath = envpath
           ))


        # Discover the group under which to run the daemon proceses. Should be
        # an unpriviliged group, try to discover what that is.
        for group in ('nogroup',
                      'nobody',
                      ):
            try:
                groupinfo = grp.getgrnam(group)
            except KeyError:
                pass
            else:
                break
        else:
            raise DeploymentException("Couldn't guess the unprivileged group to use. Bailing")

        # Write out apache config
        # I know the following lines are confusing. Perhaps a TODO later would
        # be to push most of the templates out of the code
        with open(config_path, 'w') as config:
            config.write("""WSGIDaemonProcess {name} threads=4 processes=2 home={projectpath} maximum-requests=1000 user={user} group={group} display-name={projectname}
            """.format(
                    name="opus"+self.projectname,
                    user="opus"+self.projectname,
                    group=group,
                    projectname=self.projectname,
                    projectpath=self.projectdir,
                ))
            for port in (httpport, sslport):
                if not port: continue
                if port == sslport:
                    if not (ssl_crt and ssl_key):
                        ssl_crt = os.path.join(self.projectdir, "ssl.crt")
                        ssl_key = os.path.join(self.projectdir, "ssl.key")
                        ssl_chain = ""
                    else:
                        ssl_chain = "SSLCertificateChainFile " + ssl_chain
                    ssllines = """
                        SSLEngine On
                        SSLCertificateFile {0}
                        SSLCertificateKeyFile {1}
                        {2}
                        """.format(ssl_crt, ssl_key, ssl_chain)
                else:
                    ssllines = ""
                config.write("""
                    <VirtualHost {namevirtualhost}>
                        {ssllines}
                        ServerName {projectname}{servername_suffix}
                        Alias /adminmedia {adminmedia}
                        Alias /media {mediadir}
                        WSGIProcessGroup {name}
                        WSGIApplicationGroup %{{GLOBAL}}
                        WSGIScriptAlias / {wsgifile}
                        <Directory {wsgidir}>
                            Order allow,deny
                            Allow from all
                        </Directory>
                        <Directory {mediadir}>
                            Order allow,deny
                            Allow from all
                        </Directory>
                    </VirtualHost>
                    \n""".format(
                    port=port,
                    ssllines=ssllines,
                    projectname=self.projectname,
                    servername_suffix=servername_suffix,
                    mediadir=os.path.join(self.projectdir, "media"),
                    name="opus"+self.projectname,
                    namevirtualhost="*:{0}".format(port),
                    wsgidir=wsgi_dir,
                    wsgifile=os.path.join(wsgi_dir,"django.wsgi"),
                    adminmedia=os.path.join(__import__("django").__path__[0], 'contrib','admin','media'),
                    ))

        # Restart apache gracefully
        proc = subprocess.Popen([secureops,"-r"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
        output = proc.communicate()[0]
        ret = proc.wait()
        if ret:
            raise DeploymentException("Could not restart apache. {0}".format(output))

    def gen_cert(self, suffix):
        opus.lib.deployer.ssl.gen_cert("ssl", self.projectdir,
                self.projectname+suffix)

    def setup_celery(self, secureops="secureops", pythonpath=""):
        """Uses rabbitmqctl to create a celery user and vhost, then configures
        the project with them.

        Also sets up the supervisord daemon conf file and starts supervisord

        """
        username = "opus"+self.projectname

        # create user and vhost
        log.info("Creating the RabbitMQ user and vhost")
        proc = subprocess.Popen([secureops, '-e', username],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                )
        password = proc.communicate()[0]
        ret = proc.wait()
        if ret:
            # password is not a password if it failed, but the error output
            raise DeploymentException("Creating RabbitMQ user/vhost failed. Ret:{0}. Output:{1}".format(ret, password))
        log.debug("Secure ops finished. Ret: {0}".format(ret))

        
        self.config['BROKER_HOST'] = 'localhost'
        self.config['BROKER_PORT'] = 5672
        self.config['BROKER_USER'] = username
        self.config['BROKER_PASSWORD'] = password
        self.config['BROKER_VHOST'] = username
        self.config.save()

        path_to_python = os.path.join(self.projectdir, "env", "bin", "python")

        # Set up a supervisord configuration file
        supervisordconf = """
[supervisord]
logfile=%(here)s/log/supervisord.log
pidfile=%(here)s/run/supervisord.pid
loglevel=debug

[program:celeryd]
command={python} django-admin.py celeryd --loglevel=INFO
directory=%(here)s
numprocs=1
stdout_logfile=%(here)s/log/celeryd.log
stderr_logfile=%(here)s/log/celeryd.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs = 600
environment=PYTHONPATH="{path}:%(here)s",OPUS_SETTINGS_FILE={opussettings!r},DJANGO_SETTINGS_MODULE=settings

[program:celerybeat]
command={python} django-admin.py celerybeat --loglevel=INFO -s %(here)s/sqlite/celerybeat-schedule.db
directory=%(here)s
numprocs=1
stdout_logfile=%(here)s/log/celerybeat.log
stderr_logfile=%(here)s/log/celerybeat.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs = 600
environment=PYTHONPATH="{path}:%(here)s",OPUS_SETTINGS_FILE={opussettings!r},DJANGO_SETTINGS_MODULE=settings
""".format(path=pythonpath,
        opussettings=str(os.path.join(self.projectdir, "opussettings.json")),
        python = path_to_python)

        conffilepath = os.path.join(self.projectdir, "supervisord.conf")
        with open(os.path.join(self.projectdir, "supervisord.conf"), 'w') as sobj:
            sobj.write(supervisordconf)

    def start_supervisord(self,secureops="secureops"):
        env = dict(os.environ)
        try:
            del env['DJANGO_SETTINGS_MODULE']
        except KeyError:
            pass

        username = "opus"+self.projectname
        # Start it up
        log.info("Starting up supervisord for the project")
        proc = subprocess.Popen([secureops, '-s',
            username, self.projectdir, '-S'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                close_fds=True,
                )
        output = proc.communicate()[0]
        ret = proc.wait()
        if ret:
            raise DeploymentException("Failed to start supervisord. Ret:{0}. Output:{1}".format(ret, output))
        log.debug("Secure ops finished. Ret: {0}".format(ret))

    def create_environment(self):
        """Creates a new virtualenv for this project, which will house
        requirements for the installed applications.
        """
        log.debug("Creating environment")
        proc = subprocess.Popen(["virtualenv",
            os.path.join(self.projectdir, "env")
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            close_fds=True,
            )
        output = proc.communicate()[0]
        ret = proc.wait()
        if ret:
            raise DeploymentException("Failed to create environment. Ret:{0}. Output:{1}".format(ret, output))

    def install_requirements(self, secureops="secureops"):
        """Goes through each appdirectory in apprepos/* and looks for a
        requirements.pip or requirements.txt file. If one exists, calls pip
        install -r on that file
        """
        log.info("Installing requirements...")
        # Find the pip for the environment
        pippath = os.path.join(self.projectdir, "env", "bin", "pip")
        if not os.path.exists(pippath):
            raise DeploymentException("Could not find the environment's pip installer. Perhaps pip is not installed? Virtualenvironments must have pip installed, which is normally done automatically.")

        username = "opus"+self.projectname

        # Go through each app to look for requirements
        repodir = os.path.join(self.projectdir, "apprepos")
        repos = os.listdir(repodir)
        for repo in repos:
            for reqfilename in ('requirements.txt', 'requirements.pip'):
                reqpath = os.path.join(repodir, repo, reqfilename)
                if os.path.exists(reqpath):
                    log.debug("Installing requirements for %s, found in %s",
                            repo, reqpath)
                    # Run secureops -i 
                    command = [secureops,
                            "-i", username,
                            pippath,
                            reqpath]
                    proc = subprocess.Popen(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            close_fds=True,
                            )
                    output = proc.communicate()[0]
                    ret = proc.wait()
                    log.debug("PIP output: %s", output)
                    if ret:
                        raise DeploymentException("Failed to install requirements. Ret:{0}. Output:{1}".format(ret, output))

                            
        

class ProjectUndeployer(object):
    """Contains methods for destroying a deployed project.

    Calling code should make an instance of this object and call these methods
    in roughly this order:

    * remove_apache_conf() should be called first, so that apache immediately
      stops serving files.
    * stop_celery should be next, so that any other processes running are
      stopped
    * delete_user()
    * remove_projectdir()

    """
    def __init__(self, projectdir):
        self.projectdir = projectdir

        path = os.path.abspath(self.projectdir)
        self.projectname = os.path.basename(path)

        self.apache_restarted = False

    def _restart_apache(self, secureops):
            log.info("Restarting apache")
            proc = subprocess.Popen([secureops,"-r"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)
            output = proc.communicate()[0]
            ret = proc.wait()
            if ret:
                raise DeploymentException("Could not restart apache. {0}".format(output))
            self.apache_restarted = True

    def remove_apache_conf(self, apache_conf_dir, secureops="secureops"):
        """Removes the apache config file and reloads apache"""
        config_path = os.path.join(apache_conf_dir, "opus"+self.projectname+".conf")
        if os.path.exists(config_path):
            log.info("Removing apache config for project %s", self.projectname)
            os.unlink(config_path)

            self._restart_apache(secureops)

    def stop_celery(self, secureops="secureops"):
        """Shuts down supervisord"""
        # Check if the pid file exists. If not, nothing to do
        pidfilename = os.path.join(self.projectdir, "run", "supervisord.pid")
        if os.path.exists(pidfilename):

            log.info("attempting to sigterm supervisord")
            proc = subprocess.Popen([secureops,"-s",
                    "opus"+self.projectname,
                    self.projectdir,
                    '-T'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)
            output = proc.communicate()[0]
            ret = proc.wait()
            if ret:
                raise DeploymentException("Could not stop supervisord. {0}".format(output))

    def delete_celery(self, secureops="secureops"):
        """Removes the user/vhost from rabbitmq"""
        # Delete the user/vhost.
        log.info("removing rabbitmq user/vhost")
        proc = subprocess.Popen([secureops,"-b",
                "opus"+self.projectname,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
        output = proc.communicate()[0]
        ret = proc.wait()
        # This returns 2 if the user doesn't exist, 1 for other errors that we
        # shouldn't ignore
        if ret:
            if ret == 2:
                log.info("user/vhost didn't exist. ignoring")
            else:
                raise DeploymentException("Could not stop supervisord. {0}".format(output))
        else:
            log.debug("done")

    def kill_processes(self, secureops="secureops"):
        """Sends a sigterm to all processes owned by the user, waits 10 or so
        seconds, then sends a sigkill to all. This is called by delete_user if
        there are still processes running, so no need to call it directly
        during undeployment.

        """
        log.info("Killing all processes owned by project %s...", self.projectname)
        proc = subprocess.Popen([secureops, "-k", "opus"+self.projectname],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
        output = proc.communicate()[0]
        ret = proc.wait()
        if ret:
            raise DeploymentException("Failed to kill processes. Ret:{0}. Output:{1}"\
                    .format(ret, output))


    def delete_user(self, secureops="secureops"):
        """Calls userdel to remove the system user"""
        log.info("Deleting user for project %s", self.projectname)

        # userdel will fail on some systems if any processes are still running
        # by the user. Here we wait a maximum of 30 seconds to make sure all
        # processes have ended. A return from pgrep will return 0 if a process
        # matched, 1 if no processes match, 2 if there is an error (including
        # user doesn't exist)
        tries = 0
        while subprocess.call(["pgrep", "-u", "opus"+self.projectname]) == 0:
            if not self.apache_restarted:
                # Wasn't restarted because the config file didn't exist. But
                # somehow last time apache may not have been restarted properly
                # since some processes are still running. Restart it now.
                self._restart_apache(secureops)
            if tries >= 6:
                log.warning("User still has processes running after 30 seconds!")
                # I'll take care of this *cracks knuckles*
                self.kill_processes(secureops)
                break
            log.debug("Was about to delete user, but it still has processes running! Waiting 5 seconds")
            tries += 1
            time.sleep(5)

        proc = subprocess.Popen([secureops, '-d', "opus"+self.projectname],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
        output = proc.communicate()[0]
        ret = proc.wait()
        if ret not in (0, 6):
            # ignore return code 6: user doesn't exist, to make this
            # idempotent.
            raise DeploymentException("userdel failed: {0}".format(output))
        log.debug("User removed")



    def remove_projectdir(self):
        """Deletes the entire project directory off the filesystem"""
        log.info("Removing project directory for project %s", self.projectdir)
        if os.path.exists(self.projectdir):
            shutil.rmtree(self.projectdir)
