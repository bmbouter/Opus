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

"""A simple interface to deltacloud.

Follows the interface to the ruby deltacloud client very closely.

Works with version 1.0 of the api, which is old.  This library will be removed
or depricated sometime after the new one is working.

"""
from deltacloud import Deltacloud

from image import Image
from instance import Instance
from flavor import Flavor
from realm import Realm
from state import State
from storage_snapshot import StorageSnapshot
from storage_volume import StorageVolume
from transition import Transition

def get_prov():
    """Returns an pre-configured Deltacloud object

    The returned Deltacloud object is tied to the deltacloud provider
    indicated in the settings file using the following variables

    DELTACLOUD_API_URI -- The primary entry point URI for the provider
    DELTACLOUD_USERNAME -- The username to logon to the provider
    DELTACLOUD_PASSWORD -- The password to logon to the provider
    """

    from django.conf import settings
    api_uri = settings.DELTACLOUD_API_URI
    username = settings.DELTACLOUD_USERNAME
    password = settings.DELTACLOUD_PASSWORD
    return Deltacloud(username, password, api_uri)
