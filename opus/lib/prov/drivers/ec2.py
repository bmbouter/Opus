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
from boto.ec2.regioninfo import RegionInfo

from opus.lib.prov import DriverBase
from opus.lib.prov import Image, Instance, Realm
from opus.lib.prov.exceptions import ParsingError, ServerError

class EC2Driver(DriverBase):
    """An EC2 provisioning driver.

    The arguments used when instantiating the driver are:

    name
        An AWS Access Key

    password
        The AWS Secret Key corresponding to the Access key given.

    uri
        The region endpoint url that is connected to.  This can be the url for
        a different EC2 region, or it could point to any uri for a EC2 query
        API.

    """

    def __init__(self, name=None, password=None, uri=None):
        self.name = name
        self.password = password
        self.uri = uri

        # The connection that all of the ec2 communication goes through
        if uri is None:
            region = None
        else:
            region = RegionInfo(self, EC2Connection.DefaultRegionName, self.uri)
        try:
            self.ec2 = EC2Connection(self.name, self.password, is_secure=False, region=region)
        except (EC2ResponseError, AWSConnectionError) as e:
            raise ServerError(e)

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
            return [self.image(filter["id"])]
        if "owner_id" in filter:
            owner_list = [filter["owner_id"]]
        else:
            owner_list = None

        images = []
        try:
            ec2_images = self.ec2.get_all_images(None , owner_list)
        except EC2ResponseError as e:
            raise ParsingError(e)

        for ec2_image in ec2_images:
            if "name" not in filter or ec2_image.name == filter["name"]:
                if "architecture" not in filter or ec2_image.architecture == filter["architecture"]:
                    images.append(
                        _image_from_boto_image(ec2_image, self)
                    )
        return images

    def image(self, id):
        """Return a specific ``Image`` object."""
        try:
            images = self.ec2.get_all_images([id])
        except EC2ResponseError as e:
            raise ParsingError(e)
        return _image_from_boto_image(
            images[0],
            self
        )

    ##### Instances #####

    def instances(self, filter={}):
        """Return a list of all instances.

        If ``filter`` is specified, it must be a dictionary.  The results are
        then filtered so key==value in the returned object.  Possible
        options for key are:

        - "id"
        - "state"

        """

        # Parse filter argument
        if "id" in filter:
            return [self.instance(filter["id"])]
        if "state" in filter:
            state_list = [filter["state"]]
        else:
            state_list = None

        instances = []
        try:
            reservations = self.ec2.get_all_instances()
        except EC2ResponseError as e:
            raise ParsingError(e)
        for reservation in reservations:
            for ec2_instance in reservation.instances:
                if "state" not in filter or ec2_instance.state == filter["state"]:
                    instances.append(
                        _instance_from_boto_instance(ec2_instance, self, reservation.owner_id)
                    )
        return instances

    def instance(self, id):
        """Return a specific ``Instance`` object."""
        try:
            reservations = self.ec2.get_all_instances([id])
        except EC2ResponseError as e:
            raise ParsingError(e)
        return _instance_from_boto_instance(
            reservations[0].instances[0],
            self,
            reservations[0].owner_id
        )

    ##### Instance Actions #####

    def instance_create(self, image_id, realm_id=None):
        """Instantiates an image and return the created ``Instance`` object.

        Returns the ``Instance`` object of the created instance.

        """
        if realm_id != None:
            #TODO: Implement realm (region) placement
            raise NotImplementedError()
        try:
            image = self.ec2.get_all_images([image_id])[0]
            reservation = image.run(instance_type="m1.large")
        except EC2ResponseError as e:
            raise ParsingError(e)
        return _instance_from_boto_instance(reservation.instances[0], self, reservation.owner_id)

    def instance_start(self, instance_id):
        """Takes an existing ``instance_id`` and starts it.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        try:
            reservations = self.ec2.start_instances([instance_id])
        except EC2ResponseError as e:
            raise ParsingError(e)
        return len(reservations) is 1

    def instance_stop(self, instance_id):
        """Takes an existing ``instance_id`` and stops or shuts it down.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        try:
            instances = self.ec2.stop_instances([instance_id])
        except EC2ResponseError as e:
            raise ParsingError(e)
        return len(instances) is 1

    def instance_reboot(self, instance_id):
        """Takes an existing ``instance_id`` and reboots it.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        try:
            status = self.ec2.reboot_instances([instance_id])
        except EC2ResponseError as e:
            raise ParsingError(e)
        return status

    def instance_destroy(self, instance_id):
        """Takes an existing ``instance_id`` and destroys it.

        The instance_id will no longer be valid after this call.  Any lingering
        ``Instance`` objects will become invalid and shouldn't be used.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        try:
            instances = self.ec2.terminate_instances([instance_id])
        except EC2ResponseError as e:
            raise ParsingError(e)
        return len(instances) is 1

    ##### Realms #####

    def realms(self, filter={}):
        """Return a list of all ``Realm`` objects.

        If ``filter`` is specified, it must be a dictionary.  The results are
        then filtered so key==value in the returned object.  Possible
        options for key are:

        - "id"

        """
        try:
            regions = self.ec2.get_all_regions()
        except EC2ResponseError as e:
            raise ParsingError(e)
        realms = []
        for region in regions:
            if "id" not in filter or region.name == filter["id"]:
                realms.append(
                    _realm_from_boto_region(region, self)
                )
        return realms

    def realm(self, id):
        """Return a specific ``Realm`` object."""
        realms = self.realms({"id":id})
        if len(realms):
            return realms[0]
        else:
            return []


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

def _instance_from_boto_instance(boto_instance, driver, owner_id):
    """Returns a ``opus.lib.prov.instance`` object from a boto instance."""
    return Instance(
        boto_instance.id,
        driver,
        owner_id,
        boto_instance.image_id,
        boto_instance.image_id,
        boto_instance.placement,
        boto_instance.state,
        boto_instance.public_dns_name,
        boto_instance.private_dns_name,
    )

def _realm_from_boto_region(boto_region, driver):
    """Returns a ``opus.lib.prov.realm`` object from a boto Zone."""
    return Realm(
        boto_region.name,
        driver,
        boto_region.name,
        True,
        -1,
    )
