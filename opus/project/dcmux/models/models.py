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

from django.db import models

from opus.lib.prov import DRIVERS
import opus.lib.log
log = opus.lib.log.get_logger()

class Provider(models.Model):
    """A cloud services provider."""
    DRIVER_CHOICES = ((driver, driver) for driver in DRIVERS)

    # A human readable descriptive name
    name = models.CharField(max_length=60, unique=True)

    # The opus.lib.prov driver that this provider uses
    # Must be one of the items in opus.lib.prov.DRIVERS
    driver = models.CharField(max_length=60, choices=DRIVER_CHOICES)

    # A valid URI entry point for this provider
    uri = models.URLField()

    # Username to use with this provider
    username = models.CharField(max_length=60)

    # Password to use with this provider
    password = models.CharField(max_length=60)

    # Realm to use with this provider.
    # Blank if default
    realm = models.CharField(max_length=60, blank=True)

    def get_client(self):
        """Returns a driver client object configured for this provider."""

        Driver = DRIVERS[self.driver]
        d = Driver(self.username, self.password, self.uri)
        return d

    class Meta:
        unique_together = ("uri", "username", "password")
        app_label = "dcmux"

    def __str__(self):
        return self.name

class UpstreamImage(models.Model):
    """A real image provided by a Provider."""

    # The provider that this image is located on
    provider = models.ForeignKey("Provider")

    # The real image id on the provider
    image_id = models.CharField(max_length=60)

    # The DownstreamImage which will represent this UpstreamImage
    downstream_image = models.ForeignKey("DownstreamImage")

    class Meta:
        unique_together = ("provider", "image_id")
        app_label = "dcmux"

    def __str__(self):
        return 'image_id %s on provider "%s"' % (self.image_id, self.provider)

class DownstreamImage(models.Model):
    """An image that is an aggregate of UpstreamImages.

    This model is represented as an image to the end user.  A user can start an
    instance of this image and it will go to a different UpstreamImage
    depending the Policy.

    """

    # A human readable descriptive name
    name = models.CharField(max_length=60, unique=True)

    # owner_id not implemented

    # A long, pretty description of this image
    description = models.TextField(blank=True)

    # The architecture that is presented to the end user while using this image
    architecture = models.CharField(max_length=60, unique=True)

    class Meta:
        app_label = "dcmux"

    def __str__(self):
        return self.name

class Instance(models.Model):
    """An instance of a DownsteamImage."""

    # The DownsteamImage that this is an instance of
    image = models.ForeignKey("DownstreamImage")

    # The user who started up this instance
    owner_id = models.CharField(max_length=60)

    name = models.CharField(max_length=80)

    hardware_profile = "generic"

    # The provider that the image was started up on
    provider = models.ForeignKey("Provider")

    # The real id on the provider of this instance
    instance_id = models.CharField(max_length=60)

    # The policy (realm) that this image was started as
    policy = models.ForeignKey("Policy")

    class Meta:
        app_label = "dcmux"
        unique_together = ("provider", "instance_id")

    def __str__(self):
        return 'Instance id "%s" on Provider "%s"' % (self.instance_id, self.provider)

    ###### Virtual Attributes ######
    # These attributes are recieved from the instance's provider

    @property
    def driver_instance_object(self):
        """Get the instance object for this instance."""

        if not hasattr(self, "_cached_driver_instance_object"):
            client = self.provider.get_client()
            self._cached_driver_instance_object = client.instance(self.instance_id)

        return self._cached_driver_instance_object

    @property
    def state(self):
        if hasattr(self, "_state_override"):
            return self._state_override
        return self.driver_instance_object.state
    @state.setter
    def state(self, value):
        self._state_override = value

    @property
    def actions(self):
        return self.driver_instance_object.actions

    @property
    def public_addresses(self):
        return self.driver_instance_object.public_addresses

    @property
    def private_addresses(self):
        return self.driver_instance_object.private_addresses

    @property
    def actions(self):
        actions = []
        if self.state.lower() == "stopped":
            actions.extend(["start", "destroy"])
        elif self.state.lower() == "running":
            actions.extend(["stop", "reboot"])
        elif self.state.lower() == "pending":
            pass
        else:
            pass #TODO: Error
        return actions


class Policy(models.Model):
    """Base class for policies.

    This will be represented on the front end as a realm.  Policies allow
    intelligent decisions to be made about which Provider a DownsteamImage is
    deployed on. Subclassing allows for the get_next_provider function to be
    implemented to do any sort of intelligent decision making needed as far as
    which provider is used.

    """
    STATE_CHOICES = (
        (u'AVAILABLE', u'Available'),
        (u'UNAVAILABLE', u'Unavailable'),
    )

    # A human readable descriptive name
    name = models.CharField(max_length=80, unique=True)

    # State will be AVAILABLE or UNAVAILABLE
    state = models.CharField(max_length=12, choices=STATE_CHOICES)

    # A long, pretty description of this image
    description = models.TextField(blank=True)

    # type is here as a pointer to the child class.  It contains the child
    # class's name.  It is not set by the user, but instead set by a signal.
    type = models.CharField(max_length=60, editable=False, blank=True)

    def get_next_provider(self, image_id):
        """Gets the provider that should be used next for creating an instance.

        This function should be written by the child class.

        """
        # Call the child class's get_next_provider function
        PolicyClass = getattr(self, self.type.lower())
        return PolicyClass.get_next_provider(image_id)

    class Meta:
        app_label = "dcmux"

    def __str__(self):
        return self.name
