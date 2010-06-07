"""
Django Project Deployer

The deployer library's job is to deploy a ready built Django project onto an
Apache+mod_wsgi setup. Functionality for other webservers may be added later.

"""

import os.path
import subprocess
import re
import tempfile
import pwd

# Things the deployer needs to do:
# - confuring the database / syncing the database / creating admin user
# - configuring apache/wsgi
# - configuring permissions / creating system user
# - restarting webserver
# - configuring template directory
# - configuring media directory (both setting.py and apache)

# Items TODO:
# - XXX WSGI configuration for separate user
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
        path = os.path.abspath(self.projectdir)
        self.projectname = os.path.basename(path)

        # Database configuration
        self.dbengine = None
        self.dbname = ''
        self.dbuser = ''
        self.dbpassword = ''
        self.dbhost = ''
        self.dbport = ''

        self.uid = None

    @property
    def _settings(self):
        return os.path.join(self.projectdir, "settings.py")

    def configure_database(self, engine, *args):
        """Configure the Django database
        
        engine is one of the following:
        For 'postgresql_psycopg2', 'postgresql', 'mysql', or 'oracle' the next
        five parameters should be the name, user, password, host, and port

        For 'sqlite3' the next parameter should be the path
        """

        if engine == "sqlite3":
            if len(args) < 1:
                raise TypeError("You must specify the database name")
            self.dbname = args[0]
        elif engine in ('postgresql_psycopg2', 'postgresql', 'mysql', 'oracle'):
            if len(args) < 3:
                raise TypeError("You must specify the database username and password")
            self.dbname = args[0]
            self.dbuser = args[1]
            self.dbpassword = args[2]
            if len(args) >= 4:
                self.dbhost = args[3]
            if len(args) >= 5:
                self.dbhost = args[4]
        else:
            raise ValueError("Bad database engine")

        self.dbengine = engine

        # Actually go and edit settings.py to make the changes
        self._do_database()

    def _do_database(self):
        # Go and edit settings.py to add the database settings

        settingsfile = os.path.join(self.projectdir, "settings.py")
        with open(settingsfile, 'r') as settingsobj:
            settings = settingsobj.readlines()

        # Find the DATABASES= line and put a comment that additional DATABASE
        # lines are to be inserted below
        db_start_re = re.compile(r"DATABASES\s*=")
        for lineno, line in enumerate(settings):
            if db_start_re.match(line):
                settings.insert(lineno,
                        "# Warning: More DATABASE lines are defined below.\n"
                        "# Including lines that override 'default'\n"
                        )
                break

        # Edit DATABASES line
        db_lines = """# Automatically added Database configuration from the Opus Project Deployer:
DATABASES['default'] = {{
        'ENGINE': 'django.db.backends.{engine}',
        'NAME': {name!r},
        'USER': {user!r},
        'PASSWORD': {password!r},
        'HOST': {host!r},
        'PORT': {port!r},
    }}
"""
        db_lines = db_lines.format(
                engine=self.dbengine,
                name=self.dbname,
                user=self.dbuser,
                password=self.dbpassword,
                host=self.dbhost,
                port=self.dbport,
        )
        settings.append(db_lines)

        with open(settingsfile, 'w') as settingsobj:
            settingsobj.write("".join(settings))

    def sync_database(self, username, email, password):
        """Do the initial database sync. Requires to set an admin username,
        email, and password

        """
        self._sync_database()
        self._create_superuser(username, email, password)

    def _sync_database(self):
        # Runs sync on the database
        proc = subprocess.Popen(["python", "manage.py", "syncdb", "--noinput"],
                cwd=self.projectdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
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
                stderr=subprocess.STDOUT)
        output = proc.communicate()[0]
        if proc.returncode:
            raise DeploymentException("create superuser failed. Return val: {0}. Output: {1}".format(proc.returncode, output))

        # Now set the password by invoking django code to directly interface
        # with the database. Do this in a sub process so as not to have all the
        # Django modules loaded and configured in this interpreter, which may
        # conflict with any Django settings already imported.
        program = """
import os
try:
    del os.environ['DJANGO_SETTINGS_MODULE']
except KeyError:
    pass
from django.conf import settings
settings.configure(DATABASES = {{'default':
    {{
        'ENGINE': 'django.db.backends.{engine}',
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
                engine=self.dbengine,
                name=self.dbname,
                user=self.dbuser,
                password=self.dbpassword,
                host=self.dbhost,
                port=self.dbport,
                suuser=username,
                supassword=password,
                )

        process = subprocess.Popen(["python"], stdin=subprocess.PIPE)
        process.stdin.write(program)
        process.stdin.close()
        ret = process.wait()
        if ret:
            raise DeploymentException("Setting super user password failed")

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
        if self.dbengine == "sqlite3":
            command.append(self.dbname)
        # Also secure log directory
        command.append(os.path.join(self.projectdir, "log"))

        ret = subprocess.call(command)
        if ret:
            raise DeploymentException("Could not create user and/or change file permissions")


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

# Needed so that apps can import their own things without having to know the
# project name.
sys.path.append({projectpath!r})

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
""".format(projectname = self.projectname,
           projectpath = self.projectdir))

        if vhostport != "*":
            listendirective = "Listen {0}\n".format(vhostport)
        else:
            listendirective = ""
        if pythonpath:
            ppdirective = "python-path={0}\n".format(pythonpath)
        else:
            ppdirective = ""
        # Write out apache config
        with open(config_path, 'w') as config:
            config.write("""
{listendirective}
<VirtualHost {vhostname}:{vhostport}>
    Alias /media {adminmedia}
    WSGIDaemonProcess {name} threads=4 processes=2 maximum-requests=1000 user={user} {ppdirective}
    WSGIProcessGroup {name}
    WSGIApplicationGroup %{{GLOBAL}}
    WSGIScriptAlias / {wsgifile}
    <Directory {wsgidir}>
        Order allow,deny
        Allow from all
    </Directory>
</VirtualHost>
""".format(
                    name="opus"+self.projectname,
                    user= "opus"+self.projectname,
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
