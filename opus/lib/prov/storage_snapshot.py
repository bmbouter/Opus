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

from xml_tools import xml_get_text

class StorageSnapshot(object):
    
    def __init__(self, deltacloud, dom):
        self._deltacloud = deltacloud
        self.xml = dom.toxml()
        self.created = xml_get_text(dom, "created")[0]
        self.state = xml_get_text(dom, "state")[0]
        #TODO: Storage Volumes

    def __repr__(self):
        return self.xml
