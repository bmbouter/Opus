import xml.dom.minidom
import xml.etree.ElementTree as ET
import exceptions
import string
from urllib2 import Request, urlopen, URLError
from xml.dom import minidom #TODO: Use a faster way of processing XML
import time
from datetime import datetime, timedelta

class RequestWithMethod(Request):
    """Subclass urllib2.Request that adds methods other than GET and POST.

    Thanks to http://benjamin.smedbergs.us/blog/2008-10-21/putting-and-deleteing-in-python-urllib2/

    """
    def __init__(self, method, *args, **kwargs):
        self._method = method
        Request.__init__(self, *args, **kwargs)

    def get_method(self):
        return self._method

class BadPropertyException(exceptions.Exception):
    def __init__(self):
        return

    def __str__(self):
        print "","Property definition exception occured."

class TableEntity(object):
    """This is filled in baised on the table's data."""
    pass

def parse_edm_datetime(input):
    d = datetime.strptime(input[:input.find('.')], "%Y-%m-%dT%H:%M:%S")
    if input.find('.') != -1:
        d += timedelta(0, 0, int(round(float(input[input.index('.'):-1])*1000000)))
    return d

def parse_edm_int32(input):
    return int(input)

def parse_edm_double(input):
    return float(input)

def parse_edm_boolean(input):
    return input.lower() == "true"

class DVClient():
    """Represents a client for dataview."""

    def __init__(self,opus_uri,username):
        self.username = username
        self.opus_uri = opus_uri

    def create_entry_xml(self,properties_dict):
        root = ET.Element('entry')
        root.set("xmlns","http://www.w3.org/2005/Atom")
        root.set("xmlns:m","http://schemas.microsoft.com/ado/2007/08/dataservices/metadata")
        root.set("xmlns:d","http://schemas.microsoft.com/ado/2007/08/dataservices")
        title = ET.SubElement(root,'title')
        updated = ET.SubElement(root,'updated')
        updated.text = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        author = ET.SubElement(root,'author')
        id = ET.SubElement(root,'id')
        content = ET.SubElement(root,'content')
        content.set('type','application/xml')
        properties = ET.SubElement(content,'m:properties')
        for k in properties_dict:
            p = properties_dict[k]
            property = ET.SubElement(properties,'d:'+k)
            if isinstance(p,str):
                property.text = p
            elif len(p) == 2:
                property.set('m:type',p[0])
                property.text = p[1]
            else:
                raise BadPropertyException

        return unicode('<?xml version="1.0" encoding="utf-8" standalone="yes"?>')+ET.tostring(root)

    def create_table(self, table_name):
        req = RequestWithMethod("POST", "%s/dataview/create/%s/" % (self.opus_uri, table_name))
        req.add_header("Content-Length", "0")
        try:
            return urlopen(req).read()
        except URLError, e:
            return e.read()

    def list_tables(self):
        pass

    def _parse_entity(self, entry):
        entity = TableEntity()
        for property in (p for p in entry.getElementsByTagName("m:properties")[0].childNodes if p.nodeType == minidom.Node.ELEMENT_NODE):
            key = property.tagName[2:]
            if property.hasAttribute('m:type'):
                t = property.getAttribute('m:type')
                if t.lower() == 'edm.datetime': value = parse_edm_datetime(property.firstChild.data)
                elif t.lower() == 'edm.int32': value = parse_edm_int32(property.firstChild.data)
                elif t.lower() == 'edm.boolean': value = parse_edm_boolean(property.firstChild.data)
                elif t.lower() == 'edm.double': value = parse_edm_double(property.firstChild.data)
                else: raise Exception(t.lower())
            else: value = property.firstChild is not None and property.firstChild.data or None
            setattr(entity, key, value)
        return entity

    def get_all_from_table(self, table_name):
        req = RequestWithMethod("GET", "%s/dataview/%s/" % (self.opus_uri, table_name))
        req.add_header("Content-Length", "0")
        req.add_header("Content-Type", "application/xml")
        try:
            dom = minidom.parseString(urlopen(req).read())
            entries = dom.getElementsByTagName("entry")
            entities = []
            for entry in entries:
                entities.append(self._parse_entity(entry))
            dom.unlink()
            return entities
        except URLError, e:
            return e

    def insert(self, table_name, props):
        data = self.create_entry_xml(props)
        req = RequestWithMethod("POST", "%s/dataview/%s/insert/" % (self.opus_uri, table_name), data=data)
        req.add_header("Content-Length", "%d" % len(data))
        req.add_header("Content-Type", "application/xml")
        #req.add_header("Content-Type","multipart/form-data")
        try:
            return urlopen(req)
        except URLError, e:
            return e.read()

    def get_entry(self, table_name, row_key, partition_key):
        pass

