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

class Instance(object):
    """Represents a machine that is a concrete form of an image.

    The following actions can be performed with an instance:

        start()
            This starts an instance which has previously been shut down.

        stop()
            This stops an instance that is running.

        reboot()
            This reboots an instance that is running.

        destroy()
            This destroys an instance from existance, and invalidates this object.

    An instance has the following attributes:

        id
            A unique identifier for this instance.

        driver
            The driver object which instantiated this object.

        owner_id
            A unique identifier for the owner of this instance.

        name
            A descriptive name for this

        image_id
            The image id which this instance is an instantiation of.

        realm
            The realm which this instance was started in.

        state
            An instance will be in one of the following states: "pending", "stopped" or "running".

        public_addresses
            A list of strings that are valid public ip addresses or a domain
            name that resolves to a valid public ip address.

        private_addresses
            A list of strings that are valid private ip addresses or a domain
            name that resolves to a valid private ip address.

    """
    
    def __init__(self, id, driver, owner_id, name, image_id,
            realm_id, state, public_addresses, private_addresses):
        self.id = id
        self.driver = driver
        self.owner_id = owner_id
        self.name = name
        self.image_id = image_id
        self.realm_id = realm_id
        self.state = state
        self.public_addresses = public_addresses
        self.private_addresses = private_addresses

    def start(self):
        """Starts a stopped instance.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        return self.driver.instance_start(self.id)

    def stop(self):
        """Stops an instance that is running.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        return self.driver.instance_stop(self.id)

    def reboot(self):
        """Reboots a running instance.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        return self.driver.instance_reboot(self.id)

    def destroy(self):
        """Deletes an existing instance

        The instance_id will no longer be valid after this call.  Any lingering
        ``Instance`` objects will become invalid and shouldn't be used.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        return self.driver.instance_destroy(self.id)

    def __repr__(self):
        return "<Instance id=%s, driver=%s, owner_id=%s, name=%s, image_id=%s, realm_id=%s, state=%s, public_addresses=%s, private_addresses=%s>" % (self.id, self.driver, self.owner_id, self.name, self.image_id, self.realm_id, self.state, self.public_addresses, self.private_addresses)
