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

import opus.lib.builder.sources
from opus.lib.conf import OpusConfig

App = namedtuple('App', ('path', 'pathtype'))

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
            raise Exception("startproject failed. {0}".format(output))
            # XXX: handle this better? do some cleanup?

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
        self.config['LOG_DIR'] = os.path.join(self.projectdir, 'log')
        self.config['LOG_LEVEL'] = "DEBUG"

        # Edit INSTALLED_APPS
        newapps = []
        for app in appnames:
            fullname = "{0}.{1}".format(self.projectname, app)
            newapps.append(fullname)
        if self.admin:
            newapps.append("django.contrib.admin")
        self.config['INSTALLED_APPS'] += newapps

        # Add the templates directory
        self.config['TEMPLATE_DIRS'] = (os.path.join(self.projectdir, "templates"),)

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
