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
