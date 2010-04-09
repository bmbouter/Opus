#!/usr/bin/env python
# encoding: utf-8
"""
Python wrapper around Windows Azure storage
Sriram Krishnan <sriramk@microsoft.com>
Steve Marx <steve.marx@microsoft.com>
"""
 
import base64
import hmac
import hashlib
import time
import sys
import os
from xml.dom import minidom #TODO: Use a faster way of processing XML
import re
from urllib2 import Request, urlopen, URLError
from urlparse import urlsplit
from datetime import datetime, timedelta
from vdi.log import log
import dataview_settings as dvsettings 

DEVSTORE_BLOB_HOST = dvsettings.DEVSTORE_BLOB_HOST
DEVSTORE_ACCOUNT = dvsettings.DEVSTORE_ACCOUNT
DEVSTORE_SECRET_KEY = dvsettings.DEVSTORE_SECRET_KEY

PREFIX_PROPERTIES = "x-ms-prop-"
PREFIX_METADATA = "x-ms-meta-"
PREFIX_STORAGE_HEADER = "x-ms-"
 
NEW_LINE = "\x0A"
 
DEBUG = False
 
TIME_FORMAT ="%a, %d %b %Y %H:%M:%S %Z"
 
def create_entry_xml(properties_dict):
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
            property.text = p[0]
        elif len(p) == 2:
            property.set('m:type',p[0])
            property.text = p[1]
        else:
            raise BadPropertyException

    return "<?xml version=\"1.0\" encoding=\"utf-8\" standalone=\"yes\"?>"+ET.tostring(root)

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
 
class SharedKeyCredentials(object):
    def __init__(self, account_name, account_key, use_path_style_uris = None):
        self._account = account_name
        self._key = base64.decodestring(account_key)
 
    def _sign_request_impl(self, request, for_tables = False, use_path_style_uris = None):
        (scheme, host, path, query, fragment) = urlsplit(request.get_full_url())
        if use_path_style_uris:
            path = path[path.index('/'):]
 
        canonicalized_resource = "/" + self._account + path
        match = re.search(r'comp=[^&]*', query)
        if match is not None:
            canonicalized_resource += "?" + match.group(0)
            
        if use_path_style_uris is None:
            use_path_style_uris = re.match('^[\d.:]+$', host) is not None
 
        request.add_header(PREFIX_STORAGE_HEADER + 'date', time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())) #RFC 1123
        canonicalized_headers = NEW_LINE.join(('%s:%s' % (k.lower(), request.get_header(k).strip()) for k in sorted(request.headers.keys(), lambda x,y: cmp(x.lower(), y.lower())) if k.lower().startswith(PREFIX_STORAGE_HEADER)))
 
        string_to_sign = request.get_method().upper() + NEW_LINE # verb
        string_to_sign += NEW_LINE # MD5 not required
        if request.get_header('Content-type') is not None: # Content-Type
            string_to_sign += request.get_header('Content-type')
        string_to_sign += NEW_LINE
        if for_tables: string_to_sign += request.get_header(PREFIX_STORAGE_HEADER.capitalize() + 'date') + NEW_LINE
        else: string_to_sign += NEW_LINE # Date
        if not for_tables:
            string_to_sign += canonicalized_headers + NEW_LINE # Canonicalized headers
        string_to_sign += canonicalized_resource # Canonicalized resource
        log.debug("-----top-------")
        log.debug(canonicalized_headers)
        log.debug("_____bot_______")
        request.add_header('Authorization', 'SharedKey ' + self._account + ':' + base64.encodestring(hmac.new(self._key, unicode(string_to_sign).encode("utf-8"), hashlib.sha256).digest()).strip())
        return request
 
    def sign_request(self, request, use_path_style_uris = None):
        return self._sign_request_impl(request, use_path_style_uris)
 
    def sign_table_request(self, request, use_path_style_uris = None):
        return self._sign_request_impl(request, for_tables = True, use_path_style_uris = use_path_style_uris)
 
class RequestWithMethod(Request):
    '''Subclass urllib2.Request to add the capability of using methods other than GET and POST.
Thanks to http://benjamin.smedbergs.us/blog/2008-10-21/putting-and-deleteing-in-python-urllib2/'''
    def __init__(self, method, *args, **kwargs):
        self._method = method
        Request.__init__(self, *args, **kwargs)
 
    def get_method(self):
        return self._method
 
class Table(object):
    def __init__(self, url, name):
        self.url = url
        self.name = name
 
class Storage(object):
    def __init__(self, host, account_name, secret_key, use_path_style_uris):
        self._host = host
        self._account = account_name
        self._key = secret_key
        if use_path_style_uris is None:
            use_path_style_uris = re.match(r'^[^:]*[\d:]+$', self._host)
        self._use_path_style_uris = use_path_style_uris
        self._credentials = SharedKeyCredentials(self._account, self._key)
 
    def get_base_url(self):
        if self._use_path_style_uris:
            return "http://%s/%s" % (self._host, self._account)
        else:
            return "http://%s.%s" % (self._account, self._host)
 
class TableEntity(object): pass
 
class QueueMessage(): pass
 
class QueueStorage(Storage):
    def __init__(self, host, account_name, secret_key, use_path_style_uris = None):
        super(QueueStorage, self).__init__(host, account_name, secret_key, use_path_style_uris)
 
    def create_queue(self, name):
        req = RequestWithMethod("PUT", "%s/%s" % (self.get_base_url(), name))
        req.add_header("Content-Length", "0")
        self._credentials.sign_request(req)
        try:
            response = urlopen(req)
            return response.code
        except URLError, e:
            return e.code
 
    def delete_queue(self, name):
        req = RequestWithMethod("DELETE", "%s/%s" % (self.get_base_url(), name))
        self._credentials.sign_request(req)
        try:
            response = urlopen(req)
            return response.code
        except URLError, e:
            return e.code
            
    def put_message(self, queue_name, payload):
        data = "<QueueMessage><MessageText>%s</MessageText></QueueMessage>" % base64.encodestring(payload)
        req = RequestWithMethod("POST", "%s/%s/messages" % (self.get_base_url(), queue_name), data=data)
        req.add_header("Content-Type", "application/xml")
        req.add_header("Content-Length", len(data))
        self._credentials.sign_request(req)
        try:
            response = urlopen(req)
            return response.code
        except URLError, e:
            return e.code
 
    def get_message(self, queue_name):
        req = Request("%s/%s/messages" % (self.get_base_url(), queue_name))
        self._credentials.sign_request(req)
        response = urlopen(req)
        dom = minidom.parseString(response.read())
        messages = dom.getElementsByTagName("QueueMessage")
        result = None
        if len(messages) == 1:
            message = messages[0]
            result = QueueMessage()
            result.id = message.getElementsByTagName("MessageId")[0].firstChild.data
            result.pop_receipt = message.getElementsByTagName("PopReceipt")[0].firstChild.data
            result.text = base64.decodestring(message.getElementsByTagName("MessageText")[0].firstChild.data)
        return result
 
    def delete_message(self, queue_name, message):
        id = message.id
        pop_receipt = message.pop_receipt
        req = RequestWithMethod("DELETE", "%s/%s/messages/%s?popreceipt=%s" % (self.get_base_url(), queue_name, id, pop_receipt))
        self._credentials.sign_request(req)
        try:
            response = urlopen(req)
            return response.code
        except URLError, e:
            return e.code
 
class TableStorage(Storage):
    '''Due to local development storage not supporting SharedKey authentication, this class
will only work against cloud storage.'''
    def __init__(self, host, account_name, secret_key, use_path_style_uris = None):
        super(TableStorage, self).__init__(host, account_name, secret_key, use_path_style_uris)
 
    def create_table(self, name):
        data = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<entry xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices" xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" xmlns="http://www.w3.org/2005/Atom">
<title />
<updated>%s</updated>
<author>
<name />
</author>
<id />
<content type="application/xml">
<m:properties>
<d:TableName>%s</d:TableName>
</m:properties>
</content>
</entry>""" % (time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()), name)
        log.debug(data)
        req = RequestWithMethod("POST", "%s/Tables" % self.get_base_url(), data=data)
        req.add_header("Content-Length", "%d" % len(data))
        req.add_header("Content-Type", "application/atom+xml")
        self._credentials.sign_table_request(req)
        try:
            response = urlopen(req)
            return response
        except URLError, e:
            return e

    def insert_entry(self,name,data):
        log.debug(data)
        log.debug(("%s/%s") % (self.get_base_url(), name))
        req = RequestWithMethod("POST", "%s/%s" % (self.get_base_url(), name),data=data)
        req.add_header("Content-Length", "%d" % len(data))
        req.add_header("Content-Type", "application/atom+xml")

        self._credentials.sign_table_request(req)
        try:
            response = urlopen(req)
            return response.read()
        except URLError, e:
            return e


    def delete_table(self, name):
        req = RequestWithMethod("DELETE", "%s/Tables('%s')" % (self.get_base_url(), name))
        self._credentials.sign_table_request(req)
        try:
            response = urlopen(req)
            return response.code
        except URLError, e:
            return e.code
 
    def list_tables(self):
        req = Request("%s/Tables" % self.get_base_url())
        self._credentials.sign_table_request(req)
        response = urlopen(req)
        return response.read()
        '''dom = minidom.parseString(response.read())
        entries = dom.getElementsByTagName("entry")
        for entry in entries:
            table_url = entry.getElementsByTagName("id")[0].firstChild.data
            table_name = entry.getElementsByTagName("content")[0].getElementsByTagName("m:properties")[0].getElementsByTagName("d:TableName")[0].firstChild.data
            yield Table(table_url, table_name)
        dom.unlink()'''

    def get_entity(self, table_name, partition_key, row_key):
        try:
            return urlopen(self._credentials.sign_table_request(Request("%s/%s(PartitionKey='%s',RowKey='%s')" % (self.get_base_url(), table_name, partition_key, row_key)))).read()
 
        except URLError, e:
            return e.read()
        '''dom = minidom.parseString(urlopen(self._credentials.sign_table_request(Request("%s/%s(PartitionKey='%s',RowKey='%s')" % (self.get_base_url(), table_name, partition_key, row_key)))).read())
        entity = self._parse_entity(dom.getElementsByTagName("entry")[0])
        dom.unlink()
        return entity'''
 
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
 
    def get_all(self, table_name):
        return urlopen(self._credentials.sign_table_request(Request("%s/%s" % (self.get_base_url(), table_name)))).read()

        '''dom = minidom.parseString(urlopen(self._credentials.sign_table_request(Request("%s/%s" % (self.get_base_url(), table_name)))).read())
        entries = dom.getElementsByTagName("entry")
        entities = []
        for entry in entries:
            entities.append(self._parse_entity(entry))
        dom.unlink()
        return entities'''
 
class BlobStorage(Storage):
    def __init__(self, host = DEVSTORE_BLOB_HOST, account_name = DEVSTORE_ACCOUNT, secret_key = DEVSTORE_SECRET_KEY, use_path_style_uris = None):
        super(BlobStorage, self).__init__(host, account_name, secret_key, use_path_style_uris)
 
    def create_container(self, container_name, is_public = False):
        req = RequestWithMethod("PUT", "%s/%s" % (self.get_base_url(), container_name))
        req.add_header("Content-Length", "0")
        if is_public: req.add_header(PREFIX_PROPERTIES + "publicaccess", "true")
        self._credentials.sign_request(req)
        try:
            response = urlopen(req)
            return response.code
        except URLError, e:
            return e.code
 
    def delete_container(self, container_name):
        req = RequestWithMethod("DELETE", "%s/%s" % (self.get_base_url(), container_name))
        self._credentials.sign_request(req)
        try:
            response = urlopen(req)
            return response.code
        except URLError, e:
            return e.code
 
    def list_containers(self):
        req = Request("%s/?comp=list" % self.get_base_url())
        self._credentials.sign_request(req)
        dom = minidom.parseString(urlopen(req).read())
        containers = dom.getElementsByTagName("Container")
        for container in containers:
            container_name = container.getElementsByTagName("Name")[0].firstChild.data
            etag = container.getElementsByTagName("Etag")[0].firstChild.data
            last_modified = time.strptime(container.getElementsByTagName("LastModified")[0].firstChild.data, TIME_FORMAT)
            yield (container_name, etag, last_modified)
        
        dom.unlink() #Docs say to do this to force GC. Ugh.
 
    def put_blob(self, container_name, blob_name, data, content_type = None):
        req = RequestWithMethod("PUT", "%s/%s/%s" % (self.get_base_url(), container_name, blob_name), data=data)
        req.add_header("Content-Length", "%d" % len(data))
        if content_type is not None: req.add_header("Content-Type", content_type)
        self._credentials.sign_request(req)
        try:
            response = urlopen(req)
            return response.code
        except URLError, e:
            return e.code
 
    def get_blob(self, container_name, blob_name):
        req = Request("%s/%s/%s" % (self.get_base_url(), container_name, blob_name))
        self._credentials.sign_request(req)
        return urlopen(req).read()
 
def main():
    pass
 
if __name__ == '__main__':
    main()
