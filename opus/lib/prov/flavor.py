from xml_tools import xml_get_text

class Flavor(object):
    
    def __init__(self, deltacloud, dom):
        self._deltacloud = deltacloud
        self.xml = dom.toxml()
        self.id = xml_get_text(dom, "id")[0]
        self.memory = xml_get_text(dom, "memory")[0]
        self.storage = xml_get_text(dom, "storage")[0]
        self.architecture = xml_get_text(dom, "architecture")[0]

    def __repr__(self):
        return self.xml
