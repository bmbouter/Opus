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

from libcloud.providers import DRIVERS, get_driver
import opus.lib.log
log = opus.lib.log.get_logger()

class Provider(models.Model):
    """A cloud services provider."""

    DRIVER_CHOICES = ( # Same order as on the libcloud website
        (0, "Dummy"),
        (17, "Dreamhost"),
        (1, "EC2-US EAST"),
        (10, "EC2-US WEST"),
        (2, "EC2-EU WEST"),
        (14, "Enomaly ECP"),
        # (13, "Eucalyptus"), # Can not list images
        # (#, "flexiscale"), # Not finished in libcloud yet
        (5, "GoGrid"),
        # (#, "Hosting.com"),
        (15, "IBM Cloud"),
        (7, "Linode"),
        (16, "OpenNebula"),
        (3, "Rackspace"),
        (9, "RimuHosting"),
        (4, "Slicehost"),
        (12, "SoftLayer"),
        # (#, "Terremark"), # Need dev or updated version of libcloud?
        (8, "vCloud"),
        (11, "Voxel"),
        (6, "VPS.net"),
    )

    # A human readable descriptive name
    name = models.CharField(max_length=60, unique=True)

    # The libcloud driver that this provider uses
    # The driver ids that this refers to are defined in libcloud.types.Provider
    driver = models.IntegerField(choices=DRIVER_CHOICES)

    # A valid URI entry point for this provider
    uri = models.URLField(blank=True, help_text="Most drivers have an "\
            "inherent url, and don't need this field.")

    # Username to use with this provider
    username = models.CharField(max_length=60)

    # Password to use with this provider
    password = models.CharField(max_length=60)

    def get_client(self):
        """Returns a driver client object configured for this provider."""

        Driver = get_driver(self.driver)
        d = Driver(
            # When these strings are unicode, they break.  Convert exilicitly
            str(self.username),
            str(self.password)
        )
        return d

    class Meta:
        unique_together = ("uri", "username", "password")
        app_label = "dcmux"

    def __str__(self):
        driver = "Unknown"
        for item in Provider.DRIVER_CHOICES:
            if item[0] is self.driver:
                driver = item[1]
                break
        return '"%s" with driver "%s"' % (self.name, driver)

class RealImage(models.Model):
    """A real image provided by a Provider."""

    # The provider that this image is located on
    provider = models.ForeignKey("Provider")

    # The real image id on the provider
    image_id = models.CharField(max_length=60)

    # The AggregateImage which will represent this RealImage
    aggregate_image = models.ForeignKey("AggregateImage", help_text=\
        "The Aggregate Image that this Real Image is a part of.")

    class Meta:
        unique_together = ("provider", "image_id")
        app_label = "dcmux"

    def __str__(self):
        return 'image_id %s on provider "%s"' % (self.image_id, self.provider)

class AggregateImage(models.Model):
    """An image that is an aggregate of RealImages.

    This model is represented as an image to the end user.  A user can start an
    instance of this image and it will go to a different RealImage
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
    """An instance of an image."""

    # The AggregateImage that this is an instance of
    image = models.ForeignKey("AggregateImage")

    # The user who started up this instance
    owner_id = models.CharField(max_length=60, blank=True)

    name = models.CharField(max_length=80, blank=True)

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
            driver = self.provider.get_client()
            for node in driver.list_nodes():
                if node.id == self.instance_id:
                    self._cached_driver_instance_object = node
                    return node
            raise ValueError("Instance was not found in the provider. "\
                'instance="%s" on provider %s' %\
                (self.instance_id, self.provider)
            )
        else:
            return self._cached_driver_instance_object

    @property
    def state(self):
        STATE_MAPPING = {
            0: "RUNNING",
            1: "PENDING", # REBOOTING
            2: "TERMINATED",
            3: "PENDING",
            4: "UNKNOWN",
        }
        if hasattr(self, "_state_override"):
            return self._state_override
        return STATE_MAPPING[ self.driver_instance_object.state ]
    @state.setter
    def state(self, value):
        self._state_override = value

    @property
    def public_addresses(self):
        return self.driver_instance_object.public_ip

    @property
    def private_addresses(self):
        return self.driver_instance_object.private_ip

    @property
    def actions(self):
        if self.state == "RUNNING":
            actions = ["destroy", "reboot"]
        else:
            actions = ["destroy"]
        return actions


class Policy(models.Model):
    """Base class for policies.

    This will be represented on the front end as a realm.  Policies allow
    intelligent decisions to be made about which Provider an AggregateImage is
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
