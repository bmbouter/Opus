import httplib
import logging
import re
import mimetools
import base64
from xml.dom.minidom import parseString

from image import Image
from instance import Instance

ENCODE_TEMPLATE= """--%(boundary)s
Content-Disposition: form-data; name="%(name)s"

%(value)s
""".replace('\n','\r\n')

class Deltacloud(object):
    """Represents a deltacloud api server.

    Once a Deltacloud is instantiated, you should call connect() before using
    any other methods.
    >>> d = Deltacloud("name", "pass", "http://example.com/api")
    >>> d.connect()

    """

    # This is used to seperate host and path for a given uri
    url_regex = re.compile(r"""
        ^https?://  # Ignore preceeding http(s)
        (.*?)       # Host url
        (/.*)$      # Path
    """, re.VERBOSE)

    def __init__(self, name, password, api_uri):
        self.name = name
        self.password = password

        # This information will be gathered when self.connect() is called
        self._auth_string = None
        self.entry_points = {}
        self.driver = None

        if api_uri.startswith("http://"):
            self.secure = False
        elif api_uri.startswith("https://"):
            self.secure = True
        else:
            raise ValueError('api_uri must start with "http://" or "https://".  Given: "%s"' % api_uri)

        matches = Deltacloud.url_regex.match(api_uri)
        self.api_entry_host = matches.group(1)
        self.api_entry_path = matches.group(2)

    def connect(self):

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
            raise ValueError
        self.driver = dom.documentElement.getAttribute("driver")
        for entry_point in dom.getElementsByTagName('link'):
            rel = entry_point.getAttribute("rel")
            uri = entry_point.getAttribute("href")
            self.entry_points[rel] = uri
        dom.unlink()

    def _request(self, location="", method="GET", query_args={}, form_data={}):
        """Send request to deltacloud and return a response dom object.

        The returned dom object should be unlinked after it's done being used:
        >>> dom = self.request("/some/path")
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
        print (host, method, path+query_string, body, headers)
        if self.secure:
            connection = httplib.HTTPSConnection(host)
        else:
            connection = httplib.HTTPConnection(host)
        connection.request(method, path+query_string, body=body, headers=headers)
        response = connection.getresponse()
        connection.close()
        text = response.read()
        print text
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

    def flavors(self, opts={}):
        """Return a list of all flavors."""
        raise NotImplementedError()

    def flavor(self, id):
        """Return a specific flavor object."""
        raise NotImplementedError()

    def fetch_flavor(self, uri):
        """""" #TODO
        raise NotImplementedError()

    def instance_states(self):
        """Return different states which an image can have."""
        raise NotImplementedError()

    def instance_state(self, name):
        """""" #TODO
        raise NotImplementedError()

    def realms(self, opts={}):
        """Return a list of all realms."""
        raise NotImplementedError()

    def realm(self, id):
        """Return a specific realm object."""
        raise NotImplementedError()

    def fetch_realm(self, uri):
        """""" #TODO
        raise NotImplementedError()

    def images(self, opts={}):
        """Return a list of all images."""
        path = self.entry_points["images"]
        dom = self._request(path, "GET", opts)
        if dom.documentElement.tagName != "images":
            print "Entry point for images has something wrong with it!"
            #TODO: Handle this error better
            raise ValueError
        images = []
        for image in dom.getElementsByTagName("image"):
            images.append(Image(self, image))
        dom.unlink()
        return images

    def image(self, id):
        """Return a specific image object."""
        raise NotImplementedError()

    def fetch_image(self, uri):
        """""" #TODO
        raise NotImplementedError()

    def instances(self, opts={}):
        """Return a list of all instances."""
        path = self.entry_points["instances"]
        dom = self._request(path, "GET", opts)
        if dom.documentElement.tagName != "instances":
            print "Entry point for instances has something wrong with it!"
            #TODO: Handle this error better
            raise ValueError
        instances = []
        for instance in dom.getElementsByTagName("instance"):
            instances.append(Instance(self, instance))
        dom.unlink()
        return instances

    def instance(self, id):
        """Return a specific instance object."""
        raise NotImplementedError()

    def post_instance(self, uri):
        """""" #TODO
        raise NotImplementedError()

    def fetch_instance(self, uri):
        """""" #TODO
        raise NotImplementedError()

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
        return Instance(self, dom)

    def storage_volumes(self):
        """Return a list of all storage volumes."""
        raise NotImplementedError()

    def storage_volume(self, id):
        """Return a specific storage volume object."""
        raise NotImplementedError()

    def fetch_storage_volume(self, uri):
        """""" #TODO
        raise NotImplementedError()

    def storage_snapshots(self):
        """Return a list of all storage snapshots."""
        raise NotImplementedError()

    def storage_snapshot(self, id):
        """Return a specific storage snapshot."""
        raise NotImplementedError()

    def fetch_storage_snapshot(self, uri):
        """""" #TODO
        raise NotImplementedError()
