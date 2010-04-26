from tools import xml_get_content
from log import log

class Image(object):
    
    def __init__(self, deltacloud, dom):
        self._deltacloud = deltacloud
        self.xml = dom.toxml()
        self.id = xml_get_content(dom, "id")[0]
        self.owner_id = xml_get_content(dom, "owner_id")[0]
        self.name = xml_get_content(dom, "name")[0]
        self.description = xml_get_content(dom, "description")[0]
        self.architecture = xml_get_content(dom, "architecture")[0]

    def __repr__(self):
        return self.xml
