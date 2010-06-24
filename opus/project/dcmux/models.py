from django.db import models

from opus.lib.prov.deltacloud import Deltacloud

class Provider(models.Model):
    """A deltacloud cloud services provider.

    This represents something that implements the deltacloud api.

    """

    # A human readable descriptive name
    name = models.CharField(max_length=60, unique=True)

    # A valid URI entry point for this provider
    uri = models.URLField()

    # Username to use with this provider
    username = models.CharField(max_length=60)

    # Password to use with this provider
    password = models.CharField(max_length=60)

    def get_dc_client(self):
        """Returns a deltacloud client object configured for this provider."""

        return Deltacloud(self.username, self.password, self.uri)

    class Meta:
        unique_together = ("uri", "username", "password")


class UpstreamImage(models.Model):
    """A real image provided by a Provider."""

    # The provider that this image is located on
    provider = models.ForeignKey("Provider")

    # The real image id on the provider
    image_id = models.CharField(max_length=60)

    # A valid hardware profile for this provider, or blank for the default
    # hardware profile
    hardware_profile = models.CharField(max_length=60)

    # The DownstreamImage which will represent this UpstreamImage
    downstream_image = models.ForeignKey("DownstreamImage")

    class Meta:
        unique_together = ("provider", "image_id")

class DownstreamImage(models.Model):
    """An image that is an aggregate of UpstreamImages.

    This model is represented as an image to the end user.  A user can start an
    instance of this image and it will go to a different UpstreamImage
    depending the Policy.

    """

    # A human readable descriptive name
    name = models.CharField(max_length=60, unique=True)

    # A long, pretty description of this image
    description = models.TextField()

    # The architecture that is presented to the end user while using this image
    architecture = models.CharField(max_length=60, unique=True)

class Instance(models.Model):
    """An instance of a DownsteamImage."""

    # The DownsteamImage that this is an instance of
    image = models.ForeignKey("DownstreamImage")

    # The user who started up this instance
    owner_id = models.CharField(max_length=60)

    # The provider that the image was started up on
    provider = models.ForeignKey("Provider")

    # The real id on the provider of this instance
    instance_id = models.CharField(max_length=60)

    # The policy (realm) that this image was started as
    policy = models.ForeignKey("Policy")

    class Meta:
        unique_together = ("provider", "instance_id")

class Policy(models.Model):
    """Base class for policies.

    This will be represented on the front end as a realm.  Policies allow of
    intelligent decisions to be made about which Provider a DownsteamImage is
    deployed on.

    """
    STATE_CHOICES = (
        (u'AVAILABLE', u'Available'),
        (u'UNAVAILABLE', u'Unavailable'),
    )

    # A human readable descriptive name
    name = models.CharField(max_length=80, unique=True)

    # State will be AVAILABLE or UNAVAILABLE
    state = models.CharField(max_length=12, choices=STATE_CHOICES)

class SingleProviderPolicy(Policy):
    """A policy that maps one to one with a provider.

    When an instance is started using this policy, it will always go to the
    provider which is given for the policy.

    """

    # The associated provider
    provider = models.ForeignKey("Provider")

    class Meta:
        verbose_name = "Single provider policy"
        verbose_name_plural = "Single provider policies"
