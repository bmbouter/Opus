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
Project Builder libraries

"""
import os
import os.path
from collections import namedtuple
import tempfile
import subprocess
import shutil
import re
import shutil
import keyword

import opus.lib.builder.sources
from opus.lib.conf import OpusConfig
import opus.lib.deployer
import opus.lib.log
log = opus.lib.log.get_logger()

App = namedtuple('App', ('path', 'pathtype'))

class BuildException(Exception):
    """Something went wrong when assembling a project"""

class ProjectBuilder(object):
    """ProjectBuilder class, creates and configures a Django Project
    Make an instance of this class, and then configure it with the various
    methods provided. When you're done, call create() to create the project.

    """

    def __init__(self, projectname):
        """Make a new Project Builder object. This takes one parameter, the
        project name. All other configuration is done through the configuration
        methods.

        """
        if keyword.iskeyword(projectname):
            raise BuildException("Project names cannot be keywords")
        self.projectname = projectname

        self.apps = []

        self.admin = False

    def add_app(self, src, srctype):
        """Adds an app to the configuration. srctype is a string specifying the
        source type. Source types are defined in opus.lib.builder.sources.  For
        example, if srctype is 'file', src is a local filesystem path. If
        srctype is 'git', src is a git URL.

        """
        if srctype == 'file':
            # Extra file checks
            if not os.path.isdir(src):
                raise ValueError("Given path is not a directory")
            # Properly strips trailing slashes
            src = os.path.abspath(src)
            
        self.apps.append(App(src, srctype))

    def set_admin_app(self, on=True):
        """Call this to turn the admin app on or off for this project. It is
        off by default"""
        self.admin = on

    def create(self, target):
        """Create a new Django project inside the given directory target,
        install the configured apps, and configure the project.

        This will usually be the last method one calls after adding all the apps.

        Returns a directory holding the configured app.

        """
        if not os.path.isdir(target):
            raise ValueError("Given target is not a directory")

        # Create a Django project
        self.projectdir = self._startproject(target)

        # Set up json configuration file
        self._setup_config()

        # Copy the applications into it
        appnames = self._copy_apps()

        # Add settings.py directives (installed apps, database config)
        self._configure_settings(appnames)

        # Add urls.py directives
        self._configure_urls(appnames)

        return self.projectdir

    def _startproject(self, target):
        # Returns a temporary directory containing a skeleton project

        # call django_admin.py startproject.py
        proc = subprocess.Popen(["django-admin.py", "startproject", self.projectname],
                cwd=target,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
        output = proc.communicate()[0]
        if proc.wait():
            raise BuildException("startproject failed. {0}".format(output))

        projectdir =  os.path.join(target, self.projectname)

        # Create a template and a log directory
        os.mkdir(os.path.join(projectdir, "log"))
        os.mkdir(os.path.join(projectdir, "templates"))
        os.mkdir(os.path.join(projectdir, "templates", "registration"))

        # Put login.html template in place
        with open(os.path.join(
                projectdir, "templates", "registration", "login.html"),
                'w') as loginfile:
            loginfile.write("""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <title>Login</title>
</head>
<body>
<div>
{% if form.errors %}
<p>Your username and password didn't match. Please try again.</p>
{% endif %}

<form method="post" action="{% url django.contrib.auth.views.login %}">{% csrf_token %}
<table>
<tr>
    <td>{{ form.username.label_tag }}</td>
    <td>{{ form.username }}</td>
</tr>
<tr>
    <td>{{ form.password.label_tag }}</td>
    <td>{{ form.password }}</td>
</tr>
</table>

<input type="submit" value="login" />
<input type="hidden" name="next" value="{{ next }}" />
</form>
</div>
</body>
</html>
""")

        return projectdir

    def _setup_config(self):
        # Erases the normal settings.py and creates an opussettings.json
        # to replace it
        self.config = OpusConfig.new_from_template(
                os.path.join(self.projectdir, "opussettings.json"))
        
        with open(os.path.join(self.projectdir, "settings.py"), 'w') as s:
            s.write("""# Opus-built Project Settings file
# The settings for this project are not stored in this file, but rather in the
# file opussettings.json in JSON format. You may put your own values below to
# override Opus's configuration, but this is not recommended.
from opus.lib.conf import load_settings
load_settings()
""")

        # Randomizing SECRET_KEY is taken care of for us by new_from_template,
        # but we still have to set ROOT_URLCONF
        self.config['ROOT_URLCONF'] = "{0}.urls".format(self.projectname)


    def _copy_apps(self):
        # Copies all the apps into the project
        # Returns a list of project names that were created
        before = set(os.listdir(self.projectdir))
        for app in self.apps:
            opus.lib.builder.sources.copy_functions[app.pathtype](app.path, self.projectdir)
        after = set(os.listdir(self.projectdir))
        newapps = list(after - before)
        return newapps

    def _configure_settings(self, appnames):
        self.config['LOG_LEVEL'] = "DEBUG"

        # Edit INSTALLED_APPS
        newapps = []
        for app in appnames:
            if keyword.iskeyword(app):
                raise BuildException("App name cannot be a keyword")
            fullname = "{0}.{1}".format(self.projectname, app)
            newapps.append(fullname)
        if self.admin:
            newapps.append("django.contrib.admin")
        self.config['INSTALLED_APPS'] += newapps

        # Install stock opus related apps
        self.config['INSTALLED_APPS'].append("opus.lib.profile.profilerapp")

        # Write back out the settings
        self.config.save()

    def _configure_urls(self, appnames):
        # Configures the url.py file for the project, by adding an include()
        # line for each app. Assumes each app has a urls.py file
        urlsfile = os.path.join(self.projectdir, "urls.py")

        # Slurp up urls.py
        with open(urlsfile, 'r') as fileobj:
            urls = fileobj.readlines()

        if self.admin:
            urls.append("""
from django.contrib import admin
admin.autodiscover()
""")

        # Add in urls for the installed apps
        urls.append("\n# URLs added from the Project Builder:\n")
        urls.append("urlpatterns += patterns('',\n")
        for app in appnames:
            fullname = "{0}.{1}".format(self.projectname, app)
            urls.append("    (r'^{appname}/', include('{fullname}.urls')),\n"\
                    .format(appname=app,
                            fullname=fullname))
        # Add the login view
        urls.append("    (r'^accounts/login/$', 'django.contrib.auth.views.login'),\n")
        # Add the admin interface view
        if self.admin:
            urls.append("    (r'^admin/', include(admin.site.urls)),\n")
        urls.append(")\n")
        

        # Write it back out
        with open(urlsfile, 'w') as fileobj:
            fileobj.write("".join(urls))

class ProjectEditor(object):
    """Contains routines for editing a project itself, not its deployment
    parameters. Contains routines for adding, removing, and upgrading
    applications.

    """
    def __init__(self, projectdir):
        self.projectdir = projectdir

        # Find the project name by taking the last component of the path
        path = os.path.abspath(self.projectdir)
        self.projectname = os.path.basename(path)

    def _get_config(self):
        return OpusConfig(os.path.join(self.projectdir, "opussettings.json"))

    def _touch_wsgi(self):
        # Reloads the project
        os.utime(os.path.join(self.projectdir, "wsgi", 'django.wsgi'), None)

    def add_app(self, apppath, apptype):
        """Adds an application to the project and touches the wsgi file. This
        takes effect immediately.
        Also invokes the project deployer's syncdb routine

        """
        before = set(os.listdir(self.projectdir))
        opus.lib.builder.sources.copy_functions[apptype](apppath, self.projectdir)
        after = set(os.listdir(self.projectdir))
        newapps = list(after - before)
        if len(newapps) != 1:
            raise BuildException("Project dir changed when adding the app. Bailing")

        newapp = newapps[0]

        if keyword.iskeyword(newapp):
            raise BuildException("App name cannot be a keyword")

        # Now add the app to installed apps
        config = self._get_config()
        config["INSTALLED_APPS"].append("{0}.{1}".format(
                self.projectname, newapp))
        config.save()

        # Add a line in urls.py for it
        with open(os.path.join(self.projectdir, "urls.py"), 'a') as urls:
            fullname = "{0}.{1}".format(self.projectname, newapp)
            urls.write("urlpatterns += "\
                    "patterns('', url(r'^{appname}/', "\
                    "include('{fullname}.urls')))\n"\
                    .format(appname=newapp,
                            fullname=fullname))

        # Sync db
        deployer = opus.lib.deployer.ProjectDeployer(self.projectdir)
        deployer.sync_database()

        # reload
        self._touch_wsgi()

    def del_app(self, appname):
        """Removes an application from the project. This takes effect
        immediately.

        Raises ValueError if the project is not in INSTALLED_APPS

        """
        if "/" in appname or "\\" in appname:
            raise ValueError("Bad app name")

        appname = self._strip_appname(appname)

        # Remove from INSTALLED_APPS
        config = self._get_config()
        config["INSTALLED_APPS"].remove("{0}.{1}".format(
                self.projectname, appname))
        config.save()

        # Removes the urls.py line
        with open(os.path.join(self.projectdir, "urls.py"), 'r') as urlfile:
            urllines = urlfile.readlines()
        match = re.compile(r"include\('{projectname}\.{appname}\.urls'\)"\
                .format(projectname=self.projectname,
                        appname=appname))
        for linenum, line in enumerate(urllines):
            if match.search(line):
                del urllines[linenum]
                break
        else:
            raise BuildException("No lines in urls.py matched for removal")
        with open(os.path.join(self.projectdir, "urls.py"), 'w') as urlfile:
            for line in urllines:
                urlfile.write(line)

        # Touch wsgi file
        self._touch_wsgi()

        # Deletes the app dir
        appdir = os.path.join(self.projectdir, appname)
        shutil.rmtree(appdir)

    def upgrade_app(self, appname, to):
        """Upgrades the given app to the given version."""
        if "/" in appname or "\\" in appname:
            raise ValueError("Bad app name")

        appname = self._strip_appname(appname)

        log.info("Upgrading {0}.{1} to version {2}".format(
            self.projectname, appname, to))
        apppath = os.path.join(self.projectdir, appname)
        apptype = opus.lib.builder.sources.introspect_source(apppath)
        log.debug("apppath is %s", apppath)
        log.debug("apptype is %s", apptype)

        opus.lib.builder.sources.upgrade_functions[apptype](apppath, to)

        self._touch_wsgi()

    def _strip_appname(self, appname):
        # appnames are given as projectname.appname
        if not appname.startswith(self.projectname + "."):
            raise BuildException("Bad app name")
        newappname = appname[len(self.projectname)+1:]
        if not os.path.exists(os.path.join(self.projectdir, newappname)):
            raise BuildException("App doesn't exist")
        return newappname
