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

"""
If you want to create a driver, reading this file should explain
everything.

"""

class DriverBase(object):
    """A base class for a provisioning driver.

    Writing a Driver
    =====================
    This base class is designed to make every driver have the same interface
    and be entirely interchangeable.  The only thing a driver is required to do
    is to subclass this class.  In order to make sure drivers are written
    correctly, here are some rules to follow:

    - Do not change the arguments to each function.
    - Remember to document exactly what the ``name``, ``password`` and ``uri``
      arguments to __init__ should be for your driver
    - On errors, raise the appropriate exceptions found in
      opus.lib.prov.exceptions

    """

    def __init__(self, name=None, password=None, uri=None):
        self.name = name
        self.password = password
        self.uri = uri

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
        #return [ opus.lib.prov.Image(...), ...]
        raise NotImplementedError()

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
        #return [ opus.lib.prov.Instance(...), ...]
        raise NotImplementedError()

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
