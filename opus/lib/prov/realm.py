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

class Realm(object):
    """
    The exact definition of a realm is left up to a driver.  It's usually a
    division of resources.  Instances are usually created in the default realm,
    but one can be started in an alternate realm by specifying the realm.id
    when starting the instance.
    
    A ``Realm`` has the following attributes:

    id
        A unique identifier for this realm.

    driver
        The driver object which instantiated this object.

    name
        A descriptive name for this image.

    available
        Boolean ``True`` or ``False`` indicating if this realm can be used at
        the time.

    limit
        The maximum number of instantes that can be created in this realm by
        this user

    """
    
    def __init__(self, id, driver, name, available, limit):
        self.id = id
        self.driver = driver
        self.name = name
        self.available = available
        self.limit = limit

    def __repr__(self):
        return "<Realm id=%s, driver=%s, name=%s, available=%s, limit=%s>" % (self.id, self.driver, self.name, self.available, self.limit)
