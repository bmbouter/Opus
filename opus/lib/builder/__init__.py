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
import json
import subprocess

import opus.lib.builder.sources
from opus.lib.conf import OpusConfig
import opus.lib.deployer
import opus.lib.log
log = opus.lib.log.get_logger()

App = namedtuple('App', ('path', 'pathtype'))

class BuildException(Exception):
    """Something went wrong when assembling a project"""

def merge_settings(target, source):
    """Merges setting dictionaries. This mutates the target dict and attempts
    to add as many settings from source as possible.

    Here's the merge policy:
    1) If a key exists in source but not target, the key,value pair is copied
    over.
    2) If the key exists in both and the value is a list, the target list is
    extended with the source list
    3) If the key exists in both and the value is a dict, the two dicts are
    merged with this same policy.
    4) If the key exists in both and the value is something immutable (string,
    int, etc.) then the value on the target is overwritten.

    """
    for key,value in source.iteritems():
        if key not in target:
            target[key] = value
        else:
            if isinstance(value, list):
                target[key].extend(value)
            elif isinstance(value, dict):
                merge_settings(target[key], value)
            else:
                target[key] = value

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

        # Add app media symlinks
        self._add_symlinks(appnames)

        # Add settings.py directives (installed apps, database config)
        self._configure_settings(appnames)

        # Add urls.py directives
        self._configure_urls(appnames)

        return self.projectdir

    def _add_symlinks(self, appnames):
        for app in appnames:
            # Symlink the media dir
            if os.path.exists(os.path.join(self.projectdir, app, "media")):
                os.symlink(os.path.join("..",app,"media"),
                        os.path.join(self.projectdir, "media",app))

    def _startproject(self, target):
        # Returns a temporary directory containing a skeleton project

        # Create an environment for the subprocess. DJANGO_SETTINGS_MODULE
        # must be excluded or this may fail
        env = dict(os.environ)
        try:
            del env['DJANGO_SETTINGS_MODULE']
        except KeyError:
            pass
        
        # call django_admin.py startproject
        proc = subprocess.Popen(["django-admin.py", "startproject", self.projectname],
                cwd=target,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env)
        output = proc.communicate()[0]
        if proc.wait():
            raise BuildException("startproject failed. {0}".format(output))

        projectdir =  os.path.join(target, self.projectname)

        # Create a template and a log directory
        os.mkdir(os.path.join(projectdir, "log"))
        os.mkdir(os.path.join(projectdir, "templates"))
        os.mkdir(os.path.join(projectdir, "templates", "registration"))
        os.mkdir(os.path.join(projectdir, "media"))

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
load_settings(globals())

import djcelery
djcelery.setup_loader()
""")

        # Randomizing SECRET_KEY is taken care of for us by new_from_template,
        # but we still have to set ROOT_URLCONF
        self.config['ROOT_URLCONF'] = "urls"


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
            newapps.append(app)
        newapps.append("django.contrib.admin")
        self.config['INSTALLED_APPS'] += newapps

        # Add default template context preprocessors, so that applications can
        # extend the list
        from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
        self.config['TEMPLATE_CONTEXT_PROCESSORS'] = list(TEMPLATE_CONTEXT_PROCESSORS)

        # Read in app metadata file
        for app in appnames:
            settingsfile = os.path.join(self.projectdir, app, "metadata.json")
            if not os.path.exists(settingsfile):
                continue
            with open(settingsfile, 'r') as f:
                metadata = json.load(f)

            try:
                app_settings = metadata['settings']
            except KeyError:
                continue

            # Merge settings in app_settings with global settings
            merge_settings(self.config, app_settings)

        # Write back out the settings
        self.config.save()

    def _configure_urls(self, appnames):
        # Configures the url.py file for the project, by adding an include()
        # line for each app. Assumes each app has a urls.py file
        urlsfile = os.path.join(self.projectdir, "urls.py")

        # Slurp up urls.py
        with open(urlsfile, 'r') as fileobj:
            urls = fileobj.readlines()

        urls.append("""
from django.contrib import admin
admin.autodiscover()
""")

        # Add in urls for the installed apps
        urls.append("\n# URLs added from the Project Builder:\n")
        urls.append("urlpatterns += patterns('',\n")
        for app in appnames:
            urls.append("    (r'^{appname}/', include('{appname}.urls')),\n"\
                    .format(appname=app))
        # Add the login view
        urls.append("    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),\n")
        urls.append("    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', name='logout'),\n")
        # Add the admin interface view
        urls.append("    url(r'^admin/', include(admin.site.urls)),\n")
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
        wsgifile = os.path.join(self.projectdir, "wsgi", 'django.wsgi')
        if os.path.exists(wsgifile):
            os.utime(wsgifile, None)

    def add_app(self, apppath, apptype, secureops="secureops"):
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
        config["INSTALLED_APPS"].append(newapp)
        config.save()

        # Add a line in urls.py for it
        with open(os.path.join(self.projectdir, "urls.py"), 'a') as urls:
            urls.write("urlpatterns += "\
                    "patterns('', url(r'^{appname}/', "\
                    "include('{appname}.urls')))\n"\
                    .format(appname=newapp))

        # If the app has a media directory, add a symlink for it
        if os.path.exists(os.path.join(self.projectdir, newapp, "media")):
            os.symlink(os.path.join("..",newapp,"media"),
                    os.path.join(self.projectdir, "media",newapp))

        # Sync db
        deployer = opus.lib.deployer.ProjectDeployer(self.projectdir)
        deployer.sync_database(secureops=secureops)

        # reload
        self._touch_wsgi()

    def restart_celery(self, secureops="secureops"):
        """Call this after you're done adding, upgrading, or deleting apps to
        reload the celery daemon"""
        log.info("Restarting supervisord/celery")
        proc = subprocess.Popen([secureops,"-s",
                "opus"+self.projectname,
                self.projectdir,
                "-H",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
        output = proc.communicate()[0]
        ret = proc.wait()
        if ret:
            raise BuildException("Could not restart supervisord. {0}".format(output))

    def del_app(self, appname):
        """Removes an application from the project. This takes effect
        immediately.

        Raises ValueError if the project is not in INSTALLED_APPS

        """
        if "/" in appname or "\\" in appname or "." in appname:
            raise ValueError("Bad app name")

        self._check_appname(appname)

        # Remove from INSTALLED_APPS
        config = self._get_config()
        config["INSTALLED_APPS"].remove(appname)
        config.save()

        # Removes the urls.py line
        with open(os.path.join(self.projectdir, "urls.py"), 'r') as urlfile:
            urllines = urlfile.readlines()
        match = re.compile(r"include\('{appname}\.urls'\)"\
                .format(appname=appname))
        for linenum, line in enumerate(urllines):
            if match.search(line):
                del urllines[linenum]
                break
        else:
            raise BuildException("No lines in urls.py matched for removal")
        with open(os.path.join(self.projectdir, "urls.py"), 'w') as urlfile:
            for line in urllines:
                urlfile.write(line)

        # If there's a media symlink, remove it
        medialink = os.path.join(self.projectdir,"media",appname)
        if os.path.exists(medialink):
            os.unlink(medialink)

        # Touch wsgi file
        self._touch_wsgi()

        # Deletes the app dir
        appdir = os.path.join(self.projectdir, appname)
        shutil.rmtree(appdir)

    def upgrade_app(self, appname, to):
        """Upgrades the given app to the given version."""
        if "/" in appname or "\\" in appname:
            raise ValueError("Bad app name")

        self._check_appname(appname)

        log.info("Upgrading {0} to version {1}".format(
            appname, to))
        apppath = os.path.join(self.projectdir, appname)
        apptype = opus.lib.builder.sources.introspect_source(apppath)
        log.debug("apppath is %s", apppath)
        log.debug("apptype is %s", apptype)

        opus.lib.builder.sources.upgrade_functions[apptype](apppath, to)

        # If there isn't a media link and there should be, add one
        if os.path.exists(os.path.join(self.projectdir, appname, "media")) \
                and not os.path.exists(os.path.join(self.projectdir,
                    "media",appname)):
            os.symlink(os.path.join("..",appname,"media"),
                    os.path.join(self.projectdir, "media",appname))


        self._touch_wsgi()

    def _check_appname(self, appname):
        if not os.path.exists(os.path.join(self.projectdir, appname)):
            raise BuildException("App doesn't exist")
