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

import httplib
import logging
import re
import mimetools
import base64
from xml.dom.minidom import parseString

from image import Image
from instance import Instance
from flavor import Flavor
from realm import Realm
from state import State
from storage_snapshot import StorageSnapshot
from storage_volume import StorageVolume
from transition import Transition

# Maps resource names to their classes
resource_classes = {
    "flavor": Flavor,
    "image": Image,
    "instance": Instance,
    "realm": Realm,
    "state": State,
    "storage-snapshot": StorageSnapshot,
    "storage-volume": StorageVolume,
    #"transition": Transition,
}

ENCODE_TEMPLATE= """--%(boundary)s
Content-Disposition: form-data; name="%(name)s"

%(value)s
""".replace('\n','\r\n')

class Deltacloud(object):
    """Represents a deltacloud api server."""

    # This is used to seperate host and path for a given api_uri
    url_regex = re.compile(r"""
        ^https?://  # Ignore preceeding http(s)
        (.*?)       # Host url
        (/.*)$      # Path
    """, re.VERBOSE)

    def __init__(self, name, password, api_uri):
        self.name = name
        self.password = password
        self.api_uri = api_uri

        # This information will be gathered when self.connect() is called
        self._auth_string = None
        self.entry_points = {}
        self.driver = None

        self.connected = False

    def connect(self):

        if self.connected:
            return
        self.connected = True

        if self.api_uri.startswith("http://"):
            self.secure = False
        elif self.api_uri.startswith("https://"):
            self.secure = True
        else:
            raise ValueError('api_uri must start with "http://" or "https://".  Given: "%s"' % self.api_uri)

        matches = Deltacloud.url_regex.match(self.api_uri)
        self.api_entry_host = matches.group(1)
        self.api_entry_path = matches.group(2)

        # _auth_string will be used in every request header to authenticate
        self._auth_string = "%s:%s" % (self.name, self.password)
        self._auth_string = base64.encodestring(self._auth_string)
        self._auth_string = self._auth_string.replace("\n", "")

        self._discover_entry_points()

    def _discover_entry_points(self):
        """Fills in self.entry_points

        Looks at the given api uri given for this deltacloud object.  Parses
        the result to find the entry points for each different resource
        (images, realms, instances, etc.)

        """
        dom = self._request(self.api_entry_path)
        if dom.documentElement.tagName != "api":
            print "Not a valid deltacloud api entry point!"
            # TODO: This should handle the error better
            raise ValueError("Deltacloud api entry point doesn't appear to be valid!")
        self.driver = dom.documentElement.getAttribute("driver")
        for entry_point in dom.getElementsByTagName('link'):
            rel = entry_point.getAttribute("rel")
            uri = entry_point.getAttribute("href")
            self.entry_points[rel] = uri
        dom.unlink()

        # There seems to be an inconsistancy in the naming of storage
        # snapshots/volumes.  In the url it's one thing, but in the xml it's
        # another.  We'll make sure the name is always gotten correct.
        self.entry_points['storage-snapshots'] = self.entry_points['storage_snapshots']
        self.entry_points['storage-volumes'] = self.entry_points['storage_volumes']

    def _request(self, location="", method="GET", query_args={}, form_data={}):
        """Send request to deltacloud and return a response dom object.

        The returned dom object should be unlinked after it's done being used:
        >>> dom = self._request("/some/path")
        >>> dom.unlink()

        """
        headers = {
            "Accept": "text/xml",
            "Authorization": self._auth_string,
        }

        # Handle both absolute and relative urls
        matches = Deltacloud.url_regex.match(location)
        if matches == None: # Relative
            host = self.api_entry_host
            path = location
        else: # Absolute
            host = matches.group(1)
            path = matches.group(2)

        # Format query_string
        query_list = map(lambda key,value: key+"="+value,
                         query_args.keys(),
                         query_args.values()
                        )
        if query_list:
            query_string = '?'+'&'.join(query_list)
        else:
            query_string = ""

        # Handle form_data
        if method=="POST" and form_data:
            # Thanks for the good form data example at:
            # http://code.google.com/p/urllib3/source/browse/urllib3/filepost.py
            BOUNDARY = mimetools.choose_boundary()
            body = ""
            for key, value in form_data.iteritems():
                body += ENCODE_TEMPLATE % {
                    'boundary': BOUNDARY,
                    'name': str(key),
                    'value': str(value),
                }
            body += "--%s--\n\r" % BOUNDARY
            content_type = "multipart/form-data; boundary=%s" % BOUNDARY
            headers['Content-Type'] = content_type
        else:
            body = None

        # The actual request
        #print (host, method, path+query_string, body, headers)
        if self.secure:
            connection = httplib.HTTPSConnection(host)
        else:
            connection = httplib.HTTPConnection(host)
        connection.request(method, path+query_string, body=body, headers=headers)
        response = connection.getresponse()
        connection.close()
        text = response.read()
        #print text
        if response.status < 200 or response.status >= 400:
            # Response was not successful (status 2xx or 3xx).  3xx is included
            # because sometimes deltacloud returns a redirect even when the
            # action is completed.
            #TODO: Handle error better
            raise ValueError("Status code returned by deltacloud was %s." % response.status)
        try:
            return parseString(text)
        except Exception:
            log.error("There was a problem parsing XML from deltacloud!")
            raise

    def _get_resources(self, singular_resource_name, opts={}):
        plural_resource_name = singular_resource_name+"s"
        resource_class = resource_classes[singular_resource_name]
        entry_point_url = self.entry_points[plural_resource_name]

        if not self.connected:
            self.connect()

        dom = self._request(entry_point_url, "GET", opts)
        if dom.documentElement.tagName != plural_resource_name:
            print 'Entry point for "%s" has something wrong with it!' % plural_resource_name
            #TODO: Handle this error better
            raise ValueError

        resource_object_list = []
        for dom in dom.getElementsByTagName(singular_resource_name):
            resource_object_list.append(resource_class(self, dom))
        dom.unlink()
        return resource_object_list

    def _get_resource_by_id(self, singular_resource_name, id):
        return self._get_resources(singular_resource_name, {"id":id})[0]

    ##### Images #####

    def images(self, opts={}):
        """Return a list of all images."""
        return self._get_resources("image", opts)

    def image(self, id):
        """Return a specific image object."""
        return self._get_resource_by_id("image", id)

    def fetch_image(self, uri):
        """Return an image baised on its url."""
        raise NotImplementedError()

    ##### Instances #####

    def instances(self, opts={}):
        """Return a list of all instances."""
        return self._get_resources("instance", opts)

    def instance(self, id):
        """Return a specific instance object."""
        return self._get_resource_by_id("instance", id)

    def create_instance(self, image_id, opts={}):
        """Create an instance and return it's instance object."""
        form_data = {"image_id":image_id}
        if "name" in opts:
            form_data["name"] = opts["name"]
        if "realm_id" in opts:
            form_data["realm_id"] = opts["realm_id"]
        if "flavor_id" in opts:
            form_data["flavor_id"] = opts["flavor_id"]

        entry_point = self.entry_points["instances"]
        dom = self._request(entry_point, "POST", {}, form_data)
        if dom.documentElement.tagName != "instance":
            print "Entry point for instances has something wrong with it!"
            #TODO: Handle this error better
            raise ValueError
        instance = Instance(self, dom)
        dom.unlink()
        return instance

    def fetch_instance(self, uri):
        """Return an instance baised on its url."""
        raise NotImplementedError()

    ##### Instance States #####

    def instance_states(self):
        """Return different states which an image can have."""
        raise NotImplementedError()

    def instance_state(self, name):
        """Returns True if the instance state name exists."""
        return name in self.instance_states()

    ##### Flavors #####

    def flavors(self, opts={}):
        """Return a list of all flavors."""
        return self._get_resources("flavor", opts)

    def flavor(self, id):
        """Return a specific flavor object."""
        return self._get_resource_by_id("flavor", id)

    def fetch_flavor(self, uri):
        """Return a flavor baised on its url."""
        raise NotImplementedError()

    ##### Realms #####

    def realms(self, opts={}):
        """Return a list of all realms."""
        return self._get_resources("realm", opts)

    def realm(self, id):
        """Return a specific realm object."""
        return self._get_resource_by_id("realm", id)

    def fetch_realm(self, uri):
        """Return a realm baised on its url."""
        raise NotImplementedError()

    ##### Storage Volumes #####

    def storage_volumes(self, opts={}):
        """Return a list of all storage volumes."""
        return self._get_resources("storage-volume", opts)

    def storage_volume(self, id):
        """Return a specific storage volume object."""
        return self._get_resource_by_id("storage-volume", id)

    def fetch_storage_volume(self, uri):
        """Return a storage volume baised on its url."""
        raise NotImplementedError()

    ##### Storage Volumes #####

    def storage_snapshots(self, opts={}):
        """Return a list of all storage snapshots."""
        return self._get_resources("storage-snapshot", opts)

    def storage_snapshot(self, id):
        """Return a specific storage snapshot."""
        return self._get_resource_by_id("storage-snapshot", id)

    def fetch_storage_snapshot(self, uri):
        """Return a storage snapshot baised on its url."""
        raise NotImplementedError()
