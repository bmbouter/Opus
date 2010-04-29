from tools import xml_get_text, xml_get_elements_dictionary

class Instance(object):
    
    def __init__(self, deltacloud, dom):
        self._deltacloud = deltacloud
        self.xml = dom.toxml()        
        self.id = xml_get_text(dom, "id")[0]
        self.owner_id = xml_get_text(dom, "owner_id")[0]
        self.name = xml_get_text(dom, "name")[0]
        self.image = xml_get_text(dom, "image")[0]
        self.flavor = xml_get_text(dom, "flavor")[0]
        self.realm = xml_get_text(dom, "realm")[0]
        self.state = xml_get_text(dom, "state")[0]

        # Actions
        self.actions = xml_get_elements_dictionary(dom, "link", "rel", "href")
        self.available_actions = self.actions.keys()

        # Addresses
        pub_addr_element = dom.getElementsByTagName("public-addresses")[0]
        priv_addr_element = dom.getElementsByTagName("private-addresses")[0]
        self.public_addresses = xml_get_text(pub_addr_element, "address")
        self.private_addresses = xml_get_text(priv_addr_element, "address")

    def start(self):
        return self._action("start")

    def stop(self):
        return self._action("stop")

    def reboot(self):
        return self._action("reboot")

    def _action(self, action):
        try:
            url = self.actions[action]
        except KeyError:
            return False
        self._deltacloud._request(url, "POST")
        return True

    def __repr__(self):
        return self.xml
