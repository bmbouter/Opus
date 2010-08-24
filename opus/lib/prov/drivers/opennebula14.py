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
import hashlib
from urlparse import urlparse
from xml.parsers.expat import ExpatError
from xml.dom.minidom import parseString
import httplib

from opus.lib.prov import DriverBase
from opus.lib.prov import Image, Instance, Realm
from opus.lib.prov.exceptions import ParsingError, ServerError

from xml_tools import xml_get_text

DEFAULT_URI = "http://localhost:4567/"

CREATE_INSTANCE_TEMPLATE = """
    <COMPUTE>
        <NAME>%(name)s</NAME>
        <INSTANCE_TYPE>small</INSTANCE_TYPE>
        <STORAGE>
            <DISK image="%(image_id)s" dev="sda1" />
        </STORAGE>
    </COMPUTE>
""".replace(" "*4, "").replace("\n", "")

CHANGE_INSTANCE_STATE_TEMPLATE = """
    <COMPUTE>
        <ID>%(id)s</ID>
        <STATE>%(new_state)s</STATE>
    </COMPUTE>
""".replace(" "*4, "").replace("\n", "")

class OpenNebula14Driver(object):
    """Provisioning driver for OpenNebula 1.4.

    Uses the OpenNebula OCCI API.

    The arguments used for instantiating the driver:

    name
        An OpenNebula user.

    password
        An OpenNebula password.

    uri
        The uri for OpenNebula's OCCI interface.  In both OpenNebula, and
        this driver, the default uri is "http://localhost:4567/"

    """

    def __init__(self, name=None, password=None, uri=DEFAULT_URI):
        self.name = name
        self.password = password

        # Exctract information from given uri
        url_components = urlparse(uri)
        self.uri = uri
        self._scheme = url_components.scheme
        self._host = url_components.netloc
        self._path = url_components.path

        # This auth_header is put in the header of every request
        auth_base64 = base64.encodestring("%s:%s" % (name, hashlib.sha1(password).hexdigest()))
        auth_base64 = auth_base64.replace("\n", "")
        self._auth_header = "Basic %s" % auth_base64

    def _request(self, location="", method="GET", body=None):
        """Send request and return a response dom object.

        The returned dom object should be unlinked after it's done being used:
        >>> dom = self._request("/some/path")
        >>> dom.unlink()

        """
        headers = {
            "Accept": "*/*",
            "Authorization": self._auth_header,
            #"Accept-Encoding":"*",
        }

        if self._scheme is "https":
            connection = httplib.HTTPSConnection(self._host)
        else:
            connection = httplib.HTTPConnection(self._host)
        connection.request(method, location, body=body, headers=headers)
        response = connection.getresponse()
        text = response.read()
        connection.close()
        if response.status < 200 or response.status >= 400:
            # Response was not successful (status 2xx or 3xx).
            raise ServerError("Status returned from OpenNebula was %s." % response.status)

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

        # Parse filter argument
        if "id" in filter:
            return [self.image(filter["id"])]

        image_list_xml = self._request("/storage")
        images_xml = image_list_xml.getElementsByTagName("DISK")
        images = []
        for image_xml in images_xml:
            href = image_xml.getAttribute("href")
            id = _id_from_url(href)
            image = self.image(id)
            if image is not None and \
               ("owner_id" not in filter or image.owner_id is filter["owner_id"]) and \
               ("name" not in filter or image.name is filter["name"]):
                images.append(image)
        return images

    def image(self, id):
        """Return a specific ``Image`` object."""
        return _xml_to_image(
            self._request("/storage/%s" % id),
            self
        )

    ##### Instances #####

    def instances(self, filter={}):
        """Return a list of all instances.

        If ``filter`` is specified, it must be a dictionary.  The results are
        then filtered so key==value in the returned object.  Possible
        options for key are:

        - "id"
        - "state"

        """

        # Parse filter argument
        if "id" in filter:
            return [self.instance(filter["id"])]

        instance_list_xml = self._request("/compute")
        instances_xml = instance_list_xml.getElementsByTagName("COMPUTE")
        instances = []
        for instance_xml in instances_xml:
            href = instance_xml.getAttribute("href")
            id = _id_from_url(href)
            instance = self.instance(id)
            if instance is not None and \
               ("state" not in filter or instance.state is filter["state"]):
                instances.append(instance)
        return instances

    def instance(self, id):
        """Return a specific ``Instance`` object."""
        return _xml_to_instance(
            self._request("/compute/%s" % id),
            self
        )

    ##### Instance Actions #####

    def _change_instance_state(self, instance_id, new_state):
        info_dict = {
            "id":instance_id,
            "new_state":new_state,
        }
        body = CHANGE_INSTANCE_STATE_TEMPLATE % info_dict
        print body
        self._request("/compute/%s" % instance_id, "PUT", body)
        return True

    def instance_create(self, image_id, realm_id=None):
        """Instantiates an image and return the created ``Instance`` object.

        Returns the ``Instance`` object of the created instance.

        """
        info_dict = {
            "name":image_id,
            "image_id":image_id,
        }
        body = CREATE_INSTANCE_TEMPLATE % info_dict
        self._request("/compute", "POST", body)

    def instance_start(self, instance_id):
        """Takes an existing ``instance_id`` and starts it.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        return self._change_instance_state(instance_id, "RESUME")

    def instance_stop(self, instance_id):
        """Takes an existing ``instance_id`` and stops or shuts it down.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        return self._change_instance_state(instance_id, "STOPPED")

    def instance_reboot(self, instance_id):
        """Takes an existing ``instance_id`` and reboots it.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        raise NotImplementedError()

    def instance_destroy(self, instance_id):
        """Takes an existing ``instance_id`` and destroys it.

        The instance_id will no longer be valid after this call.  Any lingering
        ``Instance`` objects will become invalid and shouldn't be used.

        Returns ``True`` on success.  Returns ``False``, or raises an exception
        on failure.

        """
        return self._change_instance_state(instance_id, "DONE")

    ##### Realms #####

    def realms(self, filter={}):
        """Return a list of all ``Realm`` objects.

        If ``filter`` is specified, it must be a dictionary.  The results are
        then filtered so key==value in the returned object.  Possible
        options for key are:

        - "id"

        """
        if id not in filter or filter["id"] is "default":
            return [Realm(
                "default",
                self,
                "default",
                True,
                -1,
            )]
        else:
            return []

    def realm(self, id):
        """Return a specific ``Realm`` object."""
        if id is "default":
            return self.realms()[0]
        else:
            return None

def _xml_to_image(xml, driver):
    return Image(
        xml_get_text(xml, "ID")[0],
        driver,
        driver.name,
        xml_get_text(xml, "NAME")[0],
        xml_get_text(xml, "DESCRIPTION")[0],
        "default",
    )

def _id_from_url(url):
    return url.strip("/").split("/")[-1]

def _xml_to_instance(xml, driver):
    """Converts the xml for one vm to an ``Instance`` object."""

    # Get IP addresses
    ips = []
    for nic in xml.getElementsByTagName("NIC"):
        ip = xml_get_text(nic, "IP")[0]
        if ip:
            ips.append(ip)

    # Get image_id
    image_id = None
    for disk in xml.getElementsByTagName("DISK"):
        if xml_get_text(xml, "TYPE") is "disk":
            url = disk.getElementsByTagName("STORAGE")[0].getAttribute("href")
            image_id = _id_from_url(url)
            break

    return Instance(
        xml_get_text(xml, "ID")[0],
        driver,
        driver.name,
        xml_get_text(xml, "NAME")[0],
        image_id,
        "default",
        xml_get_text(xml, "STATE")[0],
        ips,
        ips,
    )
