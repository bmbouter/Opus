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

App = namedtuple('App', ('path', 'name'))

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
        
    def __del__(self):
        # Remove any temporary app directories
        # TODO
        pass

    def add_app_by_path(self, path, name=None):
        """Add an app to the configuration by path. Specify the local
        filesystem path of a Django application.

        Optional parameters:
        name - specify this as the shortname of the app, used in the url
               configuration as the prefix. If not specified, the last
               component of the path is used

        """
        if not os.path.isdir(path):
            raise ValueError("Given path is not a directory")
        
        # Properly strips trailing slashes
        path = os.path.abspath(path)

        if not name:
            name = os.path.basename(path)

        for app in self.apps:
            if name == app.name:
                raise ValueError("An app with name %s already exists." % (name,))
        
        self.apps.append( App(path, name) )

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
        self._copy_apps(projectdir)

        # Add settings.py directives (installed apps, database config)
        self._configure_settings(os.path.join(projectdir, "settings.py"))

        # Add urls.py directives
        self._configure_urls(os.path.join(projectdir, "urls.py"))

        return projectdir

    def _startproject(self, target):
        # Returns a temporary directory containing a skeleton project

        # call django_admin.py startproject.py
        ret = subprocess.call(["django-admin.py", "startproject", self.projectname],
                cwd=target)
        if ret:
            raise Exception("startproject failed")
            # XXX: handle this better? do some cleanup?

        return os.path.join(target, self.projectname)


    def _copy_apps(self, projectdir):
        # Copies all the apps into the project
        for app in self.apps:
            shutil.copytree(app.path, os.path.join(projectdir, app.name))

    def _configure_settings(self, settingsfile):
        # Slurp up settings.py
        with open(settingsfile, 'r') as settingsobj:
            settings = settingsobj.readlines()

        # Edit INSTALLED_APPS
        settings.append("\n    # Automatically added applications from Project Builder\n")
        settings.append("INSTALLED_APPS += (\n")
        for app in self.apps:
            settings.append("    {0!r},\n".format(app.name))
        settings.append(")\n")

        # XXX Need to edit things like TEMPLATE_DIRS, MEDIA_ROOT? 

        # Write back out the settings.py
        with open(settingsfile, 'w') as settingsobj:
            settingsobj.write("".join(settings))

    def _configure_urls(self, urlsfile):
        # Configures the url.py file for the project, by adding an include()
        # line for each app. Assumes each app has a urls.py file

        # Slurp up urls.py
        with open(urlsfile, 'r') as fileobj:
            urls = fileobj.readlines()

        # Add in urls for the installed apps
        urls.append("\n# URLs added from the Project Builder:\n")
        urls.append("urlpatterns += patterns('',\n")
        for app in self.apps:
            # XXX What if an app name has a single quote in it? App names ought
            # to be python identifiers, need to check this somewhere.
            urls.append("    (r'^{appname}/', include('{appname}.urls')),\n".format(appname=app.name))
        urls.append(")\n")

        # Write it back out
        with open(urlsfile, 'w') as fileobj:
            fileobj.write("".join(urls))
