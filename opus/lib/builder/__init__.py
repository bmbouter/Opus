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
        projectdir = self._startproject(target)

        # Copy the applications into it
        appnames = self._copy_apps(projectdir)

        # Add settings.py directives (installed apps, database config)
        self._configure_settings(os.path.join(projectdir, "settings.py"), appnames)

        # Add urls.py directives
        self._configure_urls(os.path.join(projectdir, "urls.py"), appnames)

        return projectdir

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

        return os.path.join(target, self.projectname)


    def _copy_apps(self, projectdir):
        # Copies all the apps into the project
        # Returns a list of project names that were created
        # XXX are race conditions a problem here? Probably not a big deal
        before = set(os.listdir(projectdir))
        for app in self.apps:
            opus.lib.builder.sources.copy_functions[app.pathtype](app.path, projectdir)
        after = set(os.listdir(projectdir))
        newapps = list(after - before)
        return newapps

    def _configure_settings(self, settingsfile, appnames):
        # Slurp up settings.py
        with open(settingsfile, 'r') as settingsobj:
            settings = settingsobj.readlines()

        # Edit INSTALLED_APPS
        settings.append("\n# Automatically added applications from Project Builder\n")
        settings.append("INSTALLED_APPS += (\n")
        for app in appnames:
            fullname = "{0}.{1}".format(self.projectname, app)
            settings.append("    {0!r},\n".format(fullname))
        if self.admin:
            settings.append("    'django.contrib.admin',\n")
        settings.append(")\n")

        # XXX Need to edit things like TEMPLATE_DIRS, MEDIA_ROOT? 

        # Write back out the settings.py
        with open(settingsfile, 'w') as settingsobj:
            settingsobj.write("".join(settings))

    def _configure_urls(self, urlsfile, appnames):
        # Configures the url.py file for the project, by adding an include()
        # line for each app. Assumes each app has a urls.py file

        # Slurp up urls.py
        with open(urlsfile, 'r') as fileobj:
            urls = fileobj.readlines()

        # Add in urls for the installed apps
        urls.append("\n# URLs added from the Project Builder:\n")
        urls.append("urlpatterns += patterns('',\n")
        for app in appnames:
            fullname = "{0}.{1}".format(self.projectname, app)
            urls.append("    (r'^{appname}/', include('{fullname}.urls')),\n"\
                    .format(appname=app,
                            fullname=fullname))
        urls.append(")\n")
        
        if self.admin:
            urls.append("""
from django.contrib import admin
admin.autodiscover()
""")

        # Write it back out
        with open(urlsfile, 'w') as fileobj:
            fileobj.write("".join(urls))
