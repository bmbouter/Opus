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

import base64
from urlparse import urlparse
from xml.parsers.expat import ExpatError
from xml.dom.minidom import parseString
import httplib
import urllib
import mimetools

from opus.lib.prov import DriverBase
from opus.lib.prov import Image, Instance, Realm
from opus.lib.prov.exceptions import ParsingError, ServerError

from xml_tools import xml_get_text, xml_get_elements_dictionary
import driver_tools

class DeltacloudDriver(DriverBase):
    """A driver for RedHat's Deltacloud cloud api."""

    def __init__(self, name=None, password=None, uri=None):
        self.name = name
        self.password = password

        # Exctract information from given uri
        url_components = urlparse(uri)
        self.uri = uri
        self._scheme = url_components.scheme
        self._host = url_components.netloc
        self._path = url_components.path

        # This auth_header is put in the header of every request
        auth_base64 = base64.encodestring("%s:%s" % (name, password))
        auth_base64 = auth_base64.replace("\n", "")
        self._auth_header = "Basic %s" % auth_base64

        self._entry_points = self._discover_entry_points()

    def _discover_entry_points(self):
        """Fills in self.entry_points

        Looks at the given api uri given for this deltacloud object.  Parses
        the result to find the entry points for each different resource
        (images, realms, instances, etc.)

        """
        entry_points = {}
        dom = self._request(self._path)
        if dom.documentElement.tagName != "api":
            raise ParsingError("Not a valid deltacloud api entry point!")
        self.driver = dom.documentElement.getAttribute("driver")
        for entry_point in dom.getElementsByTagName('link'):
            rel = entry_point.getAttribute("rel")
            uri = entry_point.getAttribute("href")
            entry_points[rel] = uri
        dom.unlink()
        return entry_points

    def _get_resources(self, singular_resource_name, opts={}):
        """Returns a list of xml representations for the given resource."""

        plural_resource_name = singular_resource_name+"s"
        entry_point_url = self._entry_points[plural_resource_name]
        dom = self._request(entry_point_url, "GET", opts)

        if dom.documentElement.tagName != plural_resource_name:
            raise ParsingError('Entry point for "%s" has something wrong with it!' % plural_resource_name)

        return  dom.getElementsByTagName(singular_resource_name)

    def _request(self, location="", method="GET", query_args={}, form_data={}):
        """Send request and return a response dom object.

        The returned dom object should be unlinked after it's done being used:
        >>> dom = self._request("/some/path")
        >>> dom.unlink()

        """
        headers = {
            "Accept": "application/xml",
            "Authorization": self._auth_header,
        }

        # Handle both absolute and relative urls
        url_components = urlparse(location)
        host = url_components.netloc
        location = url_components.path
        if not host:
            host = self._host

        # Format query_string
        query_string = "?%s" % urllib.urlencode(query_args)
        if query_string is "?":
            query_string = ""

        # Handle form_data
        ENCODE_TEMPLATE= """--%(boundary)s
        Content-Disposition: form-data; name="%(name)s"

        %(value)s
        """.replace('\n','\r\n').replace(" "*4, "")
        if method=="POST" and form_data:
            # Thanks for the good form data example at:
            # http://code.google.com/p/urllib3/source/browse/urllib3/filepost.py
            boundary = mimetools.choose_boundary()
            body = ""
            for key, value in form_data.iteritems():
                body += ENCODE_TEMPLATE % {
                    'boundary': boundary,
                    'name': str(key),
                    'value': str(value),
                }
            body += "--%s--\n\r" % boundary
            content_type = "multipart/form-data; boundary=%s" % boundary
            headers['Content-Type'] = content_type
        else:
            body = None

        # The actual request
        #print (host, method, path+query_string, body, headers)
        if self._scheme.startswith("https"):
            connection = httplib.HTTPSConnection(host)
        else:
            connection = httplib.HTTPConnection(host)
        connection.request(method, location+query_string, body=body, headers=headers)
        #print self._host, method, location+query_string, body, headers, self._scheme
        response = connection.getresponse()
        text = response.read()
        connection.close()
        if response.status < 200 or response.status >= 400:
            # Response was not successful (status 2xx or 3xx).
            raise ServerError("Status returned from Deltacloud was %s." % response.status)

        try:
            return parseString(text)
        except ExpatError as e:
            raise ParsingError('This xml could not be parsed: """%s"""' % text, e)

    ##### Images #####

    def images(self, filter={}):
        """Return a list of all ``image`` objects.

        If ``filter`` is specified, it must be a dictionary.  The results are
        then filtered so key==value in the returned object.  Possible
        options for key are:

        - "id"
        - "owner_id"
        - "name"
        - "architecture"

        """
        images_xml = self._get_resources("image", filter)
        images = []
        for image_xml in images_xml:
            images.append(_xml_to_image(image_xml, self))
        return driver_tools.filter_images(images, filter)

    def image(self, id):
        """Return a specific ``Image`` object."""
        images_xml = self._get_resources("image", {"id":id})
        return _xml_to_image(images_xml[0], self)

    ##### Instances #####

    def instances(self, filter={}):
        """Return a list of all instances.

        If ``filter`` is specified, it must be a dictionary.  The results are
        then filtered so key==value in the returned object.  Possible
        options for key are:

        - "id"
        - "state"

        """
        instances_xml = self._get_resources("instance", filter)
        instances = []
        for instance_xml in instances_xml:
            instances.append(_xml_to_instance(instance_xml, self))
        return driver_tools.filter_instances(instances, filter)

    def instance(self, id):
        """Return a specific ``Instance`` object."""
        instances_xml = self._get_resources("instance", {"id":id})
        return _xml_to_instance(instances_xml[0], self)

    ##### Instance Actions #####

    def instance_create(self, image_id, realm_id=None):
        """Instantiates an image and return the created ``Instance`` object.

        Returns the ``Instance`` object of the created instance.

        """
        form_data = {"image_id":image_id}
        if realm_id:
            form_data["realm_id"] = opts["realm_id"]

        entry_point = self._entry_points["instances"]
        dom = self._request(entry_point, "POST", form_data=form_data)
        if dom.documentElement.tagName != "instance":
           raise ParsingError('Entry point for "instances" has something wrong with it!')
        instance = _xml_to_instance(dom.firstChild, self)
        dom.unlink()
        return instance

    def _instance_action(self, action, instance_id):
        instance = self.instance(instance_id)
        # instance._action_urls is set in the _xml_to_instance function
        try:
            self._request(instance._action_urls[action], "POST")
        except KeyError:
            raise ServerError('The action: "%s" is not available for instance id "%s".' % (action, instance_id))
        return True

    def instance_start(self, instance_id):
        """Takes an existing ``instance_id`` and starts it.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        return self._instance_action("start", instance_id)

    def instance_stop(self, instance_id):
        """Takes an existing ``instance_id`` and stops or shuts it down.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        return self._instance_action("stop", instance_id)

    def instance_reboot(self, instance_id):
        """Takes an existing ``instance_id`` and reboots it.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        return self._instance_action("reboot", instance_id)

    def instance_destroy(self, instance_id):
        """Takes an existing ``instance_id`` and destroys it.

        The instance_id will no longer be valid after this call.  Any lingering
        ``Instance`` objects will become invalid and shouldn't be used.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        raise NotImplementedError()
        return self._instance_action("destroy", instance_id)

    ##### Realms #####

    def realms(self, filter={}):
        """Return a list of all ``Realm`` objects.

        If ``filter`` is specified, it must be a dictionary.  The results are
        then filtered so key==value in the returned object.  Possible
        options for key are:

        - "id"

        """
        realms_xml = self._get_resources("realm", filter)
        realms = []
        for realm_xml in realms_xml:
            realms.append(_xml_to_realm(realm_xml, self))
        return driver_tools.filter_realms(realms, filter)

    def realm(self, id):
        """Return a specific ``Realm`` object."""
        realms_xml = self._get_resources("realm", {"id":id})
        return _xml_to_realm(realms_xml[0], self)


def _id_from_url(url):
    return url.strip("/").split("/")[-1]

def _xml_to_image(xml, driver):
    return Image(
        xml.getAttribute("id"),
        driver,
        xml_get_text(xml, "owner_id")[0],
        xml_get_text(xml, "name")[0],
        xml_get_text(xml, "description")[0],
        xml_get_text(xml, "architecture")[0],
    )

def _xml_to_instance(xml, driver):

    # Get image_id
    image_id = _id_from_url( xml.getElementsByTagName("image")[0].getAttribute("href") )

    # Get realm_id
    realm_id = _id_from_url( xml.getElementsByTagName("realm")[0].getAttribute("href") )

    # Get Addresses
    public_addresses_element = xml.getElementsByTagName("public_addresses")[0]
    private_addresses_element = xml.getElementsByTagName("private_addresses")[0]
    public_addresses = xml_get_text(public_addresses_element, "address")
    private_addresses = xml_get_text(private_addresses_element, "address")

    instance = Instance(
        xml.getAttribute("id"),
        driver,
        xml_get_text(xml, "owner_id")[0],
        xml_get_text(xml, "name")[0],
        image_id,
        realm_id,
        xml_get_text(xml, "state")[0],
        public_addresses,
        private_addresses,
    )
    # We set _action_urls here because we need it later when modifying the
    # instance's state.
    instance._action_urls = xml_get_elements_dictionary(xml, "link", "rel", "href")
    return instance

def _xml_to_realm(xml, driver):
    return Realm(
        xml.getAttribute("id"),
        driver,
        xml_get_text(xml, "name")[0],
        xml_get_text(xml, "state")[0] is "AVAILABLE",
        -1,
    )
