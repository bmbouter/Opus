import os.path
import re

import opus.lib.deployer
from opus.lib.deployer import DeploymentException
from opus.lib.conf import OpusConfig

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
    vhost = models.CharField(max_length=50)
    vport = models.CharField(max_length=50)

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
            # TODO: touch WSGI file
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

    def clean(self):
        """Does various tests to make sure the model is consistent. This is
        called as part of full_clean, which should be called before saving and
        before deploying this model.

        This can catch some early errors so that one can bail on creating the
        project if it won't deploy (to avoid having a half deployed project
        that has failed somewhere along the way)

        Raises a ValidationError on error

        """

        # Additional check: see that the vhost and vport requested are unique
        others = DeployedProject.objects.all()
        if self.pk:
            others = others.exclude(pk=self.pk)
        if self.vhost != "*":
            others = others.filter(vhost=self.vhost)
        if self.vport != "*":
            others = others.filter(vport=self.vport)
        if others.exists():
            raise ValidationError("There seems to be a virtual host / port conflict")


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

        # XXX This is a bit of a hack, the opus libraries should be in the
        # path for the deployed app. TODO: Find a better way to handle
        # this.
        path_additions = "{0}:{1}".format(
                settings.OPUS_BASE_DIR,
                os.path.split(opus.__path__[0])[0],
                )

        if active:
            d.configure_apache(settings.OPUS_APACHE_CONFD,
                    self.vhost,
                    self.vport,
                    secureops=settings.OPUS_SECUREOPS_COMMAND,
                    pythonpath=path_additions,
                    )

        self.save()

    def activate(self):
        """Activate this project. This writes out the apache config with the
        current parameters. Also writes out the wsgi file.

        This is normally done during deployment, but this is useful to call
        after a vhost or port change so that the changes take effect. If you do
        this, don't forget to save() too.

        """
        d = opus.lib.deployer.ProjectDeployer(self.projectdir)
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

        """

        destroyer = opus.lib.deployer.ProjectUndeployer(self.projectdir)

        destroyer.remove_apache_conf(settings.OPUS_APACHE_CONFD,
                secureops=settings.OPUS_SECUREOPS_COMMAND)

        destroyer.delete_user(
                secureops=settings.OPUS_SECUREOPS_COMMAND)

        destroyer.remove_projectdir()

        self.delete()
