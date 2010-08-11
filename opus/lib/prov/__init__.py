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
This package provides two things:

1. An interface for provisioning drivers to implement.  This is given in the
   DriverBase class and the supporting objects in image.py, instance.py and
   realm.py.  The DriverBase class is the only class that must be subclassed in
   order to create a driver.  This is where you should look if you want to
   implement a driver.

2. Various drivers which implement the interface.  Any drivers which properly
   implement this interface can be used interchangeably.  These drivers are
   contained in the drivers/ folder.

"""

from image import Image
from instance import Instance
from realm import Realm

from driver_base import DriverBase
import exceptions
import drivers

DRIVERS = {
    "ec2":drivers.EC2Driver,
}
