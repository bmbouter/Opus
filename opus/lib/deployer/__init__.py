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

import opus
from opus.lib.conf import OpusConfig
from opus.lib.log import get_logger
import opus.lib.deployer.ssl
log = get_logger()

# Things the deployer needs to do:
# - confuring the database / syncing the database / creating admin user
# - configuring apache/wsgi
# - configuring permissions / creating system user
# - restarting webserver
# - configuring template directory
# - configuring media directory (both setting.py and apache)

# Items TODO:
# - Media configuration

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
        self.config.save()


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

    def sync_database(self, username=None, email=None, password=None):
        """Do the initial database sync. If a username, email, and password are
        provided, a superuser is created

        """
        self._sync_database()
        if username and email and password:
            self.create_superuser(username, email, password)

    def _getenv(self):
        "Gets an environment with paths set up for a manage.py subprocess"
        env = dict(os.environ)
        env['OPUS_SETTINGS_FILE'] = os.path.join(self.projectdir, "opussettings.json")
        env['PYTHONPATH'] = os.path.split(opus.__path__[0])[0]
        # Tells the logging module to disable logging, which would create
        # permission issues
        env['OPUS_LOGGING_DISABLE'] = "1"
        try:
            # Don't leak this value from our current environment
            del env['DJANGO_SETTINGS_MODULE']
        except KeyError:
            pass
        return env

    def _sync_database(self):
        # Runs sync on the database
        proc = subprocess.Popen(["python", "manage.py", "syncdb", "--noinput"],
                cwd=self.projectdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=self._getenv(),
                )
        output = proc.communicate()[0]
        if proc.wait():
            raise DeploymentException("syncdb failed. {0}".format(output))

    def create_superuser(self, username, email, password):
        proc = subprocess.Popen(["python", "manage.py", "createsuperuser",
                "--noinput",
                "--username", username,
                "--email", email],
                cwd=self.projectdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=self._getenv(),
                )
        output = proc.communicate()[0]
        if proc.returncode:
            raise DeploymentException("create superuser failed. Return val: {0}. Output: {1}".format(proc.returncode, output))

        # Now set the password by invoking django code to directly interface
        # with the database. Do this in a sub process so as not to have all the
        # Django modules loaded and configured in this interpreter, which may
        # conflict with any Django settings already imported.
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
user = User.objects.get(username={suuser!r})
user.set_password({supassword!r})
user.save()
        """.format(
                engine=dbconfig['ENGINE'],
                name=dbconfig['NAME'],
                user=dbconfig['USER'],
                password=dbconfig['PASSWORD'],
                host=dbconfig['HOST'],
                port=dbconfig['PORT'],
                suuser=username,
                supassword=password,
                options=options
                )

        process = subprocess.Popen(["python"], stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
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
        with open(os.path.join(wsgi_dir, "django.wsgi"), 'w') as wsgi:
            wsgi.write("""
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = '{projectname}.settings'
os.environ['OPUS_SETTINGS_FILE'] = {settingspath!r}

# Needed so that apps can import their own things without having to know the
# project name.
sys.path.append({projectpath!r})

#import django.core.handlers.wsgi
#application = django.core.handlers.wsgi.WSGIHandler()

import opus.lib.profile
application = opus.lib.profile.OpusWSGIHandler()
""".format(projectname = self.projectname,
           projectpath = self.projectdir,
           settingspath = os.path.join(self.projectdir, "opussettings.json"),
           ))

        if pythonpath:
            ppdirective = "python-path={0}\n".format(pythonpath)
        else:
            ppdirective = ""

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
            config.write("""WSGIDaemonProcess {name} threads=4 processes=2 maximum-requests=1000 user={user} group={group} display-name={projectname} {ppdirective}
            """.format(
                    name="opus"+self.projectname,
                    user="opus"+self.projectname,
                    group=group,
                    projectname=self.projectname,
                    ppdirective=ppdirective,
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

class ProjectUndeployer(object):
    """Contains methods for destroying a deployed project.

    Calling code should make an instance of this object and call these methods
    in roughly this order:

    * remove_apache_conf() should be called first, so that apache immediately
      stops serving files.
    * delete_user()
    * remove_projectdir()

    """
    def __init__(self, projectdir):
        self.projectdir = projectdir

        path = os.path.abspath(self.projectdir)
        self.projectname = os.path.basename(path)

    def remove_apache_conf(self, apache_conf_dir, secureops="secureops"):
        """Removes the apache config file and reloads apache"""
        config_path = os.path.join(apache_conf_dir, "opus"+self.projectname+".conf")
        if os.path.exists(config_path):
            log.info("Removing apache config for project %s", self.projectname)
            os.unlink(config_path)

            proc = subprocess.Popen([secureops,"-r"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)
            output = proc.communicate()[0]
            ret = proc.wait()
            if ret:
                raise DeploymentException("Could not restart apache. {0}".format(output))

    def delete_user(self, secureops="secureops"):
        """Calls userdel to remove the system user"""
        log.info("Deleting user for project %s", self.projectname)
        proc = subprocess.Popen([secureops, '-d', "opus"+self.projectname],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
        output = proc.communicate()[0]
        ret = proc.wait()
        if ret not in (0, 6):
            # ignore return code 6: user doesn't exist, to make this
            # idempotent.
            raise DeploymentException("userdel failed: {0}".format(output))

    def remove_projectdir(self):
        """Deletes the entire project directory off the filesystem"""
        log.info("Removing project directory for project %s", self.projectdir)
        if os.path.exists(self.projectdir):
            shutil.rmtree(self.projectdir)
