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
