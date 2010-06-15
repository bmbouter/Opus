import os.path
import re

import opus.lib.deployer

from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator
import django.contrib.auth.models


id_re = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]+$')
validate_identifier = RegexValidator(id_re, u"Enter a valid identifier consisting of letters, numbers, and underscores, not starting with a number.", 'invalid')
class IdentifierField(models.CharField):
    default_validators = [validate_identifier]
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 30)
        models.CharField.__init__(self, *args, **kwargs)


class DeployedProject(models.Model):
    name = IdentifierField(unique=True)
    owner = models.ForeignKey(django.contrib.auth.models.User)
    vhost = models.CharField(max_length=50)
    vport = models.CharField(max_length=50)

    @property
    def projectdir(self):
        return os.path.join(settings.OPUS_BASE_DIR, self.name)

    def deploy(self, dbengine, dbname, dbpassword="", dbhost="", dbport=""):
        """Call this to deploy a project. If successful, the model is saved and
        this method returns None. If something went wrong, a
        DeploymentException is raised with a description of the error, and the
        model is not saved.

        """
        # Raise an error now if there's a problem
        self.full_clean()

        d = opus.lib.deployer.ProjectDeployer(self.projectdir)

        d.configure_database(dbengine,
                dbname,
                dbpassword,
                dbhost,
                dbport,
                )

        d.sync_database(form.cleaned_data['superusername'],
                form.cleaned_data['superemail'],
                form.cleaned_data['superpassword'],
                )

        d.secure_project(settings.OPUS_SECUREOPS_COMMAND)

        # XXX This is a bit of a hack, the opus libraries should be in the
        # path for the deployed app. TODO: Find a better way to handle
        # this.
        path_additions = "{0}:{1}".format(
                settings.OPUS_BASE_DIR,
                os.path.split(opus.__path__[0])[0],
                )

        d.configure_apache(settings.OPUS_APACHE_CONFD,
                form.cleaned_data['vhost'],
                form.cleaned_data['vport'],
                secureops=settings.OPUS_SECUREOPS_COMMAND,
                pythonpath=path_additions,
                )
