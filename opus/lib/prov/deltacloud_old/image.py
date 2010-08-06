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

class Image(object):
    
    def __init__(self, deltacloud, dom):
        self._deltacloud = deltacloud
        self.xml = dom.toxml()
        self.id = xml_get_text(dom, "id")[0]
        self.owner_id = xml_get_text(dom, "owner_id")[0]
        self.name = xml_get_text(dom, "name")[0]
        self.description = xml_get_text(dom, "description")[0]
        self.architecture = xml_get_text(dom, "architecture")[0]

    def __repr__(self):
        return self.xml
