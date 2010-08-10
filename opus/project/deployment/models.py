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
import time

import opus.lib.deployer
from opus.lib.deployer import DeploymentException
from opus.lib.conf import OpusConfig
from opus.lib.log import get_logger
log = get_logger()

from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator, ValidationError
import django.contrib.auth.models


id_re = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]+$')
validate_identifier = RegexValidator(id_re, u"Enter a valid identifier consisting of letters, numbers, and underscores, not starting with a number.", 'invalid')
class IdentifierField(models.CharField):
    default_validators = [validate_identifier]
    
    def __init__(self, *args, **kwargs):
        # Set max length to 25 since usernames can only be 30 characters or so
        kwargs['max_length'] = kwargs.get('max_length', 25)
        models.CharField.__init__(self, *args, **kwargs)

class DeploymentInfo(object):
    """Holds information about a project deployment"""
    def __init__(self):
        self.dbengine = None
        self.dbname = None
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
            os.utime(os.path.join(self.projectdir, "wsgi", 'django.wsgi'), None)
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

        # Do this before settings the sensitive database information
        d.secure_project(settings.OPUS_SECUREOPS_COMMAND)

        d.configure_database(info.dbengine,
                info.dbname,
                info.dbpassword,
                info.dbhost,
                info.dbport,
                )

        d.sync_database(info.superusername,
                info.superemail,
                info.superpassword,
                )

        d.set_paths()

        d.gen_cert(settings.OPUS_APACHE_SERVERNAME_SUFFIX)

        if active:
            self.activate(d)

        self.save()

    def activate(self, d=None):
        """Activate this project. This writes out the apache config with the
        current parameters. Also writes out the wsgi file.

        This is normally done during deployment, but this is useful to call
        after any change that affects the apache config so that the changes
        take effect. If you do this, don't forget to save() too.

        Pass in a deployer object, otherwise one will be created.

        """
        if not d:
            d = opus.lib.deployer.ProjectDeployer(self.projectdir)
        # XXX This is a bit of a hack, the opus libraries should be in the
        # path for the deployed app. TODO: Find a better way to handle
        # this.
        path_additions = "{0}:{1}".format(
                settings.OPUS_BASE_DIR,
                os.path.split(opus.__path__[0])[0],
                )
        d.configure_apache(settings.OPUS_APACHE_CONFD,
                settings.OPUS_HTTP_PORT,
                settings.OPUS_HTTPS_PORT,
                settings.OPUS_APACHE_SERVERNAME_SUFFIX,
                secureops=settings.OPUS_SECUREOPS_COMMAND,
                pythonpath=path_additions,
                )

    def deactivate(self):
        """Removes the apache configuration file and restarts apache.

        """
        destroyer = opus.lib.deployer.ProjectUndeployer(self.projectdir)
        destroyer.remove_apache_conf(settings.OPUS_APACHE_CONFD,
                secureops=settings.OPUS_SECUREOPS_COMMAND)

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

        # Bug 45, userdel will fail if any processes are still running by the
        # user. Here we wait a maximum of 30 seconds to make sure all processes
        # have ended. A return from pgrep will return 0 if a process matched, 1
        # if no processes match, 2 if there is an error (including user doesn't
        # exist)
        tries = 0
        while subprocess.call(["pgrep", "-u", "opus"+self.name]) == 0:
            if tries >= 6:
                log.warning("User still has processes running after 30 seconds! Continuing anyways")
                break
            log.debug("Was about to delete user, but it still has processes running! Waiting 5 seconds")
            tries += 1
            time.sleep(5)

        destroyer.delete_user(
                secureops=settings.OPUS_SECUREOPS_COMMAND)

        destroyer.remove_projectdir()

        if self.id is not None:
            self.delete()
