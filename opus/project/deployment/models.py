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

import os.path
import re
import subprocess
import json
import itertools

import opus.lib.deployer
from opus.lib.deployer import DeploymentException
from opus.lib.conf import OpusConfig
import opus.project.deployment.tasks
from opus.project.deployment import database
from opus.lib.log import get_logger
log = get_logger()

from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator, ValidationError
import django.contrib.auth.models


id_re = re.compile(r'^[a-z][a-z0-9_]+$')
validate_identifier = RegexValidator(id_re, u"Enter a valid identifier consisting of letters, numbers, and underscores, not starting with a number.", 'invalid')
class IdentifierField(models.CharField):
    default_validators = [validate_identifier]
    
    def __init__(self, *args, **kwargs):
        # Set max length to 25 since usernames can only be 30 characters or so
        kwargs['max_length'] = kwargs.get('max_length', 25)
        models.CharField.__init__(self, *args, **kwargs)

class DeploymentInfo(object):
    """Just a container that holds information about a project deployment"""
    def __init__(self):
        self.dbengine = None
        self.dbname = None
        self.dbuser = ""
        self.dbpassword = ""
        self.dbhost = ""
        self.dbport = ""
        self.superusername = None
        self.superemail = None
        self.superpassword = None

    def validate(self):
        if not (self.dbengine and self.superusername and
                self.superemail and self.superpassword):
            raise ValidationError("Deployment parameters not specified")

class DeployedProject(models.Model):
    """The actual model for a deployed project. The database doesn't contain
    too many fields, but this class contains lots of methods to query information and
    edit projects. Most of the state is stored in the filesystem and not the
    database. (For example, whether the project is activated is defined by the
    presence of an apache config file for the project)
    """
    name = IdentifierField(unique=True)
    owner = models.ForeignKey(django.contrib.auth.models.User)

    def __init__(self, *args, **kwargs):
        super(DeployedProject, self).__init__(*args, **kwargs)

        self._conf = None

    @property
    def projectdir(self):
        return os.path.join(settings.OPUS_BASE_DIR, self.name)

    @property
    def apache_conf(self):
        return os.path.join(settings.OPUS_APACHE_CONFD, "opus"+self.name+".conf")

    @models.permalink
    def get_absolute_url(self):
        return ("opus.project.deployment.views.edit_or_create",
                (),
                dict(projectname=self.name))

    @property
    def serve_http(self):
        port = settings.OPUS_HTTP_PORT
        if not port:
            return
        if port != 80:
            portline = ":"+str(port)
        else:
            portline = ""
        return "http://{0}{1}{2}/".format(
                self.name, settings.OPUS_APACHE_SERVERNAME_SUFFIX,
                portline)
    @property
    def serve_https(self):
        port = settings.OPUS_HTTPS_PORT
        if not port:
            return
        if port != 443:
            portline = ":"+str(port)
        else:
            portline = ""
        return "https://{0}{1}{2}/".format(
                self.name, settings.OPUS_APACHE_SERVERNAME_SUFFIX,
                portline)

    def get_urls(self):
        """Gets the urls that this project is being served from. This list is
        populated even if active is False.
        """
        urls = []
        http = self.serve_http
        if http:
            urls.append(http)
        https = self.serve_https
        if https:
            urls.append(https)
        return urls

    def get_apps(self):
        """Returns an iterator over application names that are currently
        installed"""
        for app in self.config['INSTALLED_APPS']:
            if os.path.exists(os.path.join(self.projectdir, app)):
                yield app

    @property
    def config(self):
        """Returns an opus.lib.conf.OpusConfig object for this project. This is
        automatically saved when the model's save() method is called.

        This will raise an error if the project doesn't exist (such as before
        it's deployed for the first time

        """
        if not self._conf:
            self._conf = OpusConfig(os.path.join(self.projectdir, "opussettings.json"))
        return self._conf

    def save(self, *args, **kwargs):
        if self._conf:
            self._conf.save()
            # Touch wsgi file, indicating to mod_wsgi to re-load modules and
            # therefore any changed configuration parameters
            wsgifile = os.path.join(self.projectdir, "wsgi", 'django.wsgi')
            if os.path.exists(wsgifile):
                # It may not exist if the project isn't active
                os.utime(wsgifile, None)
        super(DeployedProject, self).save(*args, **kwargs)

    def is_active(self):
        return os.path.exists(self.apache_conf)
    active = property(is_active)

    def _verify_project(self):
        """Verifies that the given project name corresponds to a real un-deployed
        project in the base dir.
        Returns False if something went wrong.

        """
        fullpath = self.projectdir
        if not os.path.isdir(fullpath):
            return False
        if os.path.exists(os.path.join(fullpath, "wsgi")):
            # Already deployed?
            return False
        if not os.path.exists(os.path.join(fullpath, "__init__.py")):
            return False
        if not os.path.exists(os.path.join(fullpath, "settings.py")):
            return False
        return True

    def deploy(self, info, active=True):
        """Call this to deploy a project. If successful, the model is saved and
        this method returns None. If something went wrong, a
        DeploymentException is raised with a description of the error, and the
        model is not saved. If something is wrong with the given information, a
        ValidationError is raised.

        Pass in a DeploymentInfo object with the appropriate attributes set.
        That information is used to deploy a project, but is not stored within
        the model itself.

        If active is not True, the deployment will be created inactive, and the
        apache configuration file will not be created.

        """
        # This should have been called externally before, but do it again just
        # to be sure nothing's changed.
        self.full_clean()

        # Do some validation checks to see if the given project name points to
        # a valid un-deployed django project
        if not self._verify_project():
            raise DeploymentException("Sanity check failed, will not create project with that name")

        d = opus.lib.deployer.ProjectDeployer(self.projectdir)

        d.create_environment()

        # Do this before settings the sensitive database information
        d.secure_project(settings.OPUS_SECUREOPS_COMMAND)

        d.configure_database(info.dbengine,
                info.dbname,
                info.dbuser,
                info.dbpassword,
                info.dbhost,
                info.dbport,
                )

        # This must go before sync_database, in case some settings that are
        # set by set_paths are used by a models.py at import time.
        d.set_paths()

        d.install_requirements(settings.OPUS_SECUREOPS_COMMAND)

        d.sync_database(info.superusername,
                info.superemail,
                info.superpassword,
                settings.OPUS_SECUREOPS_COMMAND
                )

        d.gen_cert(settings.OPUS_APACHE_SERVERNAME_SUFFIX)

        d.setup_celery(settings.OPUS_SECUREOPS_COMMAND,
                pythonpath=self._get_path_additions())

        if active:
            self.activate(d)

        self.save()

    def _get_path_additions(self):
        return "{0}".format(
                os.path.split(opus.__path__[0])[0],
                )

    def set_debug(self, d):
        """Sets debug mode on or off. Remember to save afterwards"""
        self.config['DEBUG'] = bool(d)
        self.config['TEMPLATE_DEBUG'] = bool(d)
        if d:
            self.config['LOG_LEVEL'] = "DEBUG"
        else:
            self.config['LOG_LEVEL'] = "INFO"

    def activate(self, d=None):
        """Activate this project. This writes out the apache config with the
        current parameters. Also writes out the wsgi file. Finally, starts the
        supervisord process which starts celeryd and celerybeat

        This is normally done during deployment, but this is useful to call
        after any change that affects the apache config so that the changes
        take effect. If you do this, don't forget to save() too.

        Pass in a deployer object, otherwise one will be created.

        """
        if not self.all_settings_set():
            raise DeploymentException("Tried to activate, but some applications still have settings to set")
        if not d:
            d = opus.lib.deployer.ProjectDeployer(self.projectdir)
        # The opus libraries should be in the path for the deployed app. TODO:
        # Find a better way to handle this.
        path_additions = self._get_path_additions()
        d.configure_apache(settings.OPUS_APACHE_CONFD,
                settings.OPUS_HTTP_PORT,
                settings.OPUS_HTTPS_PORT,
                settings.OPUS_APACHE_SERVERNAME_SUFFIX,
                secureops=settings.OPUS_SECUREOPS_COMMAND,
                pythonpath=path_additions,
                ssl_crt=settings.OPUS_SSL_CRT,
                ssl_key=settings.OPUS_SSL_KEY,
                ssl_chain=settings.OPUS_SSL_CHAIN,
                )

        # Schedule celery to start supervisord. Somehow if supervisord is
        # started directly by mod_wsgi, strange things happen to supervisord's
        # signal handlers
        opus.project.deployment.tasks.start_supervisord.delay(self.projectdir)


    def deactivate(self):
        """Removes the apache configuration file and restarts apache.

        """
        destroyer = opus.lib.deployer.ProjectUndeployer(self.projectdir)
        destroyer.remove_apache_conf(settings.OPUS_APACHE_CONFD,
                secureops=settings.OPUS_SECUREOPS_COMMAND)
        destroyer.stop_celery(
                secureops=settings.OPUS_SECUREOPS_COMMAND)

        # Make sure all processes are stopped
        opus.project.deployment.tasks.kill_processes.apply_async(
                args=[self.pk],
                countdown=5)

    def destroy(self):
        """Destroys the project. Deletes it off the drive, removes the system
        user, de-configures apache, and finally removes itself from the
        database.

        This method is idempotent, it can be called on a non-existant project
        or project in an inconsistant or intermediate state.

        This method will still error in these cases (not necessarily
        exaustive)

        * Apache can't be restarted
        * There's an error removing the user other than "user doesn't exist"
        * The project dir exists but cannot be removed

        """

        destroyer = opus.lib.deployer.ProjectUndeployer(self.projectdir)

        destroyer.remove_apache_conf(settings.OPUS_APACHE_CONFD,
                secureops=settings.OPUS_SECUREOPS_COMMAND)

        destroyer.stop_celery(
                secureops=settings.OPUS_SECUREOPS_COMMAND)

        destroyer.delete_celery(
                secureops=settings.OPUS_SECUREOPS_COMMAND)

        # This also kills off any remaining processes owned by that user
        destroyer.delete_user(
                secureops=settings.OPUS_SECUREOPS_COMMAND)

        # Remove database and user if automatically created
        try:
            if self.config['DATABASES']['default']['ENGINE'].endswith(\
                    "postgresql_psycopg2") and \
                    settings.OPUS_AUTO_POSTGRES_CONFIG:
                database.delete_postgres(self.name)
        except Exception, e:
            log.warning("Ignoring this error when trying to delete postgres user: %s", e)

        destroyer.remove_projectdir()

        if self.id is not None:
            self.delete()

    def get_app_settings(self):
        """Returns a mapping of app names to a list of settings.

        The "Default" values are the values from the metadata here, not the
        values from the project config. If sending the current values from
        settings to the user, you'll need to modify this data. (this is done in
        jsonviews.py for the projectinfo() view)

        """
        app_settings = {}
        for app in self.get_apps():
            # Is this application local to the project? If not skip it, since
            # we don't have a good way right now to find where it's installed
            md_filename = os.path.join(self.projectdir, app, "metadata.json")
            if not os.path.exists(md_filename):
                continue

            with open(md_filename, 'r') as md_file:
                app_metadata = json.load(md_file)

            usersettings = app_metadata.get("usersettings", None)

            if not usersettings:
                continue

            # Do some really brief validity checking. Most validity checking is
            # done in the constructor of UserSettingsForm though
            u = []
            for s in usersettings:
                if len(s) < 3:
                    log.warning("usersettings line has wrong number of args: %s", s)
                    continue
                # All values except the last (default) must be a string
                if not all(isinstance(x, basestring) for x in s[:3]):
                    log.warning("usersettings line is bad, one of the first three elements is not a string: %s", s)
                    continue
                if s[2] not in ("int", "char", "str", "string", "float", 'choice', 'bool'):
                    log.warning("usersettings line has bad type: %s", s)
                    continue
                u.append(s)

            if u:
                app_settings[app] = u
        return app_settings

    def all_settings_set(self):
        """Returns true if all the application specific settings are set in the
        global config. If false is returned, the project shouldn't be activated
        yet.

        """
        app_settings = self.get_app_settings()
        for setting in itertools.chain.from_iterable(app_settings.itervalues()):
            if setting[0] not in self.config:
                return False
        return True
