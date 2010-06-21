import os.path
import re

import opus.lib.deployer

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

class DeploymentException(Exception):
    pass

class DeployedProject(models.Model):
    name = IdentifierField(unique=True)
    owner = models.ForeignKey(django.contrib.auth.models.User)
    vhost = models.CharField(max_length=50)
    vport = models.CharField(max_length=50)

    @property
    def projectdir(self):
        return os.path.join(settings.OPUS_BASE_DIR, self.name)

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

    def deploy(self, info):
        """Call this to deploy a project. If successful, the model is saved and
        this method returns None. If something went wrong, a
        DeploymentException is raised with a description of the error, and the
        model is not saved. If something is wrong with the given information, a
        ValidationError is raised.

        Pass in a DeploymentInfo object with the appropriate attributes set.
        That information is used to deploy a project, but is not stored within
        the model itself.

        """
        # Raise an error now if there's a problem
        # Part of this is to check unique fields, so this should cover the
        # check that an existing deployment with this name exists.
        self.full_clean()

        # Do some validation checks to see if the given project name points to
        # a valid django project
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

        # XXX This is a bit of a hack, the opus libraries should be in the
        # path for the deployed app. TODO: Find a better way to handle
        # this.
        path_additions = "{0}:{1}".format(
                settings.OPUS_BASE_DIR,
                os.path.split(opus.__path__[0])[0],
                )

        d.configure_apache(settings.OPUS_APACHE_CONFD,
                self.vhost,
                self.vport,
                secureops=settings.OPUS_SECUREOPS_COMMAND,
                pythonpath=path_additions,
                )

        self.save()
