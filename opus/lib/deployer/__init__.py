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

import opus
from opus.lib.conf import OpusConfig
from opus.lib.log import get_logger
log = get_logger()

# Things the deployer needs to do:
# - confuring the database / syncing the database / creating admin user
# - configuring apache/wsgi
# - configuring permissions / creating system user
# - restarting webserver
# - configuring template directory
# - configuring media directory (both setting.py and apache)

# Items TODO:
# - SSL configuration?
# - Media configuration

class ProjectDeployer(object):
    """This object keeps track of all the configuration for a project until the
    deploy() method is called, where the deployment actually happens

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

        For 'sqlite3' the next parameter should be the path
        """

        dbuser = ''
        dbpassword = ''
        dbhost = ''
        dbport = ''
        if engine == "sqlite3":
            if len(args) < 1:
                raise TypeError("You must specify the database name")
            dbname = args[0]
        elif engine in ('postgresql_psycopg2', 'postgresql', 'mysql', 'oracle'):
            if len(args) < 3:
                raise TypeError("You must specify the database username and password")
            dbname = args[0]
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

        self.config.save()

    def sync_database(self, username, email, password):
        """Do the initial database sync. Requires to set an admin username,
        email, and password

        """
        self._sync_database()
        self._create_superuser(username, email, password)

    def _getenv(self):
        "Gets an environment with paths set up for a manage.py subprocess"
        env = dict(os.environ)
        env['OPUS_SETTINGS_FILE'] = os.path.join(self.projectdir, "opussettings.json")
        env['PYTHONPATH'] = os.path.split(opus.__path__[0])[0]
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

    def _create_superuser(self, username, email, password):
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
                )

        process = subprocess.Popen(["python"], stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                )
        output = process.communicate(program)[0]
        ret = process.wait()
        if ret:
            raise DeploymentException("Setting super user password failed. {0}".format(output))

    def secure_project(self, secureops="secureops"):
        """Calling this does two things: It calls useradd to create a new Linux
        user, and it changes permissions on settings.py so only that user can
        access it. This is a necessary step before calling configure_apache()

        Pass in the path to the secureops binary, otherwise PATH is searched

        """
        # Attempt to create a linux user, and change user permissions
        # of the settings.py and the sqlite database if any
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


    def configure_apache(self, apache_conf_dir, vhostname, vhostport, pythonpath="", secureops="secureops"):
        """Configures apache to serve this Django project.  apache_conf_dir
        should be apache's conf.d directory where a .conf file can be dropped
        vhostname and vhostport are the virtual host configurations that this
        project should be served under. One or both of these could be *, but
        make sure you know what you're doing. Those parameters are passed into
        apache's VirtualHost directive.

        """
        # Check if our dest file exists, so as not to overwrite it
        config_path = os.path.join(apache_conf_dir, "opus"+self.projectname+".conf")
        if os.path.exists(config_path):
            raise DeploymentException("Config exists already, aborting")

        # Write out a wsgi config to the project dir
        wsgi_dir = os.path.join(self.projectdir, "wsgi")
        try:
            os.mkdir(wsgi_dir)
        except OSError, e:
            import errno
            if e.errno != errno.EEXIST:
                raise e
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

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
""".format(projectname = self.projectname,
           projectpath = self.projectdir,
           settingspath = os.path.join(self.projectdir, "opussettings.json"),
           ))

        if vhostport != "*":
            listendirective = "Listen {0}\n".format(vhostport)
        else:
            listendirective = ""
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
        with open(config_path, 'w') as config:
            config.write("""
{listendirective}
<VirtualHost {vhostname}:{vhostport}>
    Alias /media {adminmedia}
    WSGIDaemonProcess {name} threads=4 processes=2 maximum-requests=1000 user={user} group={group} display-name={projectname} {ppdirective}
    WSGIProcessGroup {name}
    WSGIApplicationGroup %{{GLOBAL}}
    WSGIScriptAlias / {wsgifile}
    <Directory {wsgidir}>
        Order allow,deny
        Allow from all
    </Directory>
</VirtualHost>
""".format(
                    projectname=self.projectname,
                    name="opus"+self.projectname,
                    user="opus"+self.projectname,
                    group=group,
                    vhostname=vhostname,
                    vhostport=vhostport,
                    wsgidir=wsgi_dir,
                    wsgifile=os.path.join(wsgi_dir,"django.wsgi"),
                    listendirective=listendirective,
                    ppdirective=ppdirective,
                    adminmedia=os.path.join(__import__("django").__path__[0], 'contrib','admin','media'),
                    ))

        # Restart apache gracefully
        ret = subprocess.call([secureops,"-r"])
        if ret:
            raise DeploymentException("Could not restart apache")

class DeploymentException(Exception):
    pass
