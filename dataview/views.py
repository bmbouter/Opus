from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django import forms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
import winazurestorage as azure
import xml.dom.minidom
import xml.etree.ElementTree as ET
import exceptions
import string
from vdi.log import log
# Create your views here.

'''TODO:Check ff store was created succesfully and '''
store = azure.TableStorage(azure.CLOUD_TABLE_HOST, azure.DEVSTORE_ACCOUNT, azure.DEVSTORE_SECRET_KEY)

@csrf_exempt
def create_service(request, table_name):
    '''TODO:
    check header for username and satisfy the request with proper account
    check if service requested is Azure or Gdata
    check if request was a post
    '''
    response_code = store.create_table(table_name)

    return HttpResponse(response_code,mimetype="xml")

def list_tables(request):
    response = store.list_tables()
    return HttpResponse(response, mimetype="xml")

def get_entry(request, table_name, row_key, partition_key):
    log.debug("table_name: %s" % table_name)
    response = store.get_entity(table_name, partition_key, row_key)
    return HttpResponse(response, mimetype="xml")

def get_all(request, table_name):
    response = store.get_all(table_name)
    return HttpResponse(response, mimetype="xml")

@csrf_exempt
def insert(request,table_name):
    log.debug(request.raw_post_data)

    response = store.insert_entry(table_name,request.raw_post_data)
    return HttpResponse(response.read(), mimetype="xml")
