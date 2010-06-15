from xml_tools import xml_get_text

class State(object):
    
    def __init__(self, deltacloud, dom):
        self._deltacloud = deltacloud
        self.xml = dom.toxml()
        self.name = xml_get_text(dom, "name")[0]
        self.transitions = []

    def __repr__(self):
        return self.xml
