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
