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

class Image(object):
    """
    An abstract form of an instance.  An ``Image`` can be instantiated to
    create multiple instances.

    An ``Image`` has the following attributes:

    id
        A unique identifier for this image.

    driver
        The driver object which instantiated this object.

    owner_id
        A unique identifier for the owner of this image.

    name
        A descriptive name for this image

    description
        An optional long description.

    architecture
        The machine architecture that this ``Image`` uses.  Examples are "i386
        and "x86_64".

    """

    def __init__(self, id, driver, owner_id, name, description, architecture):
        self.driver = driver
        self.id = id
        self.owner_id = owner_id
        self.name = name
        self.description = description
        self.architecture = architecture

    def __repr__(self):
        return '<Image id=%s, driver=%s, owner_id=%s, name="%s", description="%s", architecture="%s">' % \
            (self.id, self.driver, self.owner_id, self.name, self.description, self.architecture)
