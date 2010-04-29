from xml_tools import xml_get_text

class Realm(object):
    
    def __init__(self, deltacloud, dom):
        self._deltacloud = deltacloud
        self.xml = dom.toxml()
        self.id = xml_get_text(dom, "id")[0]
        self.name = xml_get_text(dom, "name")[0]
        self.state = xml_get_text(dom, "state")[0]
        self.limit = xml_get_text(dom, "limit")[0]

    def __repr__(self):
        return self.xml
