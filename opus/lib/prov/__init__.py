"""A simple interface to deltacloud.

Follows the interface to the ruby deltacloud client very closely.

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
