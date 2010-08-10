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

from boto.ec2.connection import EC2Connection
from boto.exception import EC2ResponseError, AWSConnectionError, BotoClientError

from opus.lib.prov import DriverBase
from opus.lib.prov import Image, Instance, Realm

class EC2Driver(DriverBase):
    """An EC2 provisioning driver.

    The arguments used when instantiating the driver are:

    name
        An AWS Access Key

    password
        The AWS Secret Key corresponding to the Access key given.

    uri
        TODO

    """

    def __init__(self, name=None, password=None, uri=None):
        self.name = name
        self.password = password
        self.uri = uri

        # The connection that all of the ec2 communication goes through
        self.ec2 = EC2Connection(self.name, self.password, host=self.uri)

    ##### Images #####

    def images(self, filter={}):
        """Return a list of all ``image`` objects.

        If ``filter`` is specified, it must be a dictionary.  The results are
        then filtered so key==value in the returned object.  Possible
        options for key are:

        - "id"
        - "owner_id"
        - "name"
        - "architecture"

        """

        # Parse filter argument
        if "id" in filter:
            id_list = [filter["id"]]
        else:
            id_list = None
        if "owner_id" in filter:
            owner_list = [filter["owner_id"]]
        else:
            owner_list = None

        images = []
        ec2_images = self.ec2.get_all_images(id_list, owner_list)
        for ec2_image in ec2_images:
            if "name" not in filter or ec2_image.name == filter["name"]:
                if "architecture" not in filter or ec2_image.architecture == filter["architecture"]:
                    images.append(
                        _image_from_boto_image(ec2_image, self)
                    )
        return images

    def image(self, id):
        """Return a specific ``Image`` object."""
        #return opus.lib.prov.Image(...)
        raise NotImplementedError()

    ##### Instances #####

    def instances(self, filter={}):
        """Return a list of all instances.

        If ``filter`` is specified, it must be a dictionary.  The results are
        then filtered so key==value in the returned object.  Possible
        options for key are:

        - "id"
        - "state"

        """
        reservations = self.ec2.get_all_images(id_list, owner_list)
        for reservation in reservations:
            if "owner_id" not in filter or reservation.owner_id == filter["owner_id"]:
                for ec2_instance in reservation:
                    if "architecture" not in filter or ec2_instance.architecture == filter["architecture"]:
                        instances.append(
                            _instance_from_boto_instance(ec2_instance, self, reservation.owner_id)
                        )
        return instances

    def instance(self, id):
        """Return a specific ``Instance`` object."""
        #return opus.lib.prov.Instance(...)
        raise NotImplementedError()

    ##### Instance Actions #####

    def instance_create(self, image_id, realm_id=None):
        """Instantiates an image and return the created ``Instance`` object.

        Returns the ``Instance`` object of the created instance.

        """
        #return opus.lib.prov.Instance(...)
        raise NotImplementedError()

    def instance_start(self, instance_id):
        """Takes an existing ``instance_id`` and starts it.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        raise NotImplementedError()

    def instance_stop(self, instance_id):
        """Takes an existing ``instance_id`` and stops or shuts it down.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        raise NotImplementedError()

    def instance_reboot(self, instance_id):
        """Takes an existing ``instance_id`` and reboots it.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        raise NotImplementedError()

    def instance_destroy(self, instance_id):
        """Takes an existing ``instance_id`` and destroys it.

        The instance_id will no longer be valid after this call.  Any lingering
        ``Instance`` objects will become invalid and shouldn't be used.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        raise NotImplementedError()

    ##### Realms #####

    def realms(self, filter={}):
        """Return a list of all ``Realm`` objects.

        If ``filter`` is specified, it must be a dictionary.  The results are
        then filtered so key==value in the returned object.  Possible
        options for key are:

        - "id"

        """
        #return [ opus.lib.prov.Realm(...), ...]
        raise NotImplementedError()

    def realm(self, id):
        """Return a specific ``Realm`` object."""
        #return opus.lib.prov.Realm(...)
        raise NotImplementedError()


def _image_from_boto_image(boto_instance, driver):
    """Returns a ``opus.lib.prov.image`` object from a boto image."""
    return Image(
        boto_instance.id,
        driver,
        boto_instance.ownerId,
        boto_instance.name,
        boto_instance.description,
        boto_instance.architecture,
    )

def _region_to_realm(region):
    """Converts a region from boto to a realm."""
    pass #TODO

def _instance_from_boto_instance(boto_instance, driver, owner_id):
    """Returns a ``opus.lib.prov.instance`` object from a boto instance."""
    return Instance(
        boto_instance.id,
        driver,
        boto_instance.owner_id,
        boto_instance.image_id,
        boto_instance.image_id,
        _region_to_realm(boto_instance.region),
        boto_instance.state,
        boto_instance.public_dns_name,
        boto_instance.private_dns_name,
    )
