from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django import forms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login

import os
import urllib

import openid   
from openid.consumer.consumer import Consumer, \
    SUCCESS, CANCEL, FAILURE, SETUP_NEEDED
from openid.consumer.discover import DiscoveryFailure
from openid.extensions import ax
from openid.extensions import pape

from idpauth import user_tools
from idpauth.models import IdentityProvider, IdentityProviderLDAP, Role
from idpauth import openid_tools
from idpauth import authentication_tools
from idpauth import ldap_tools

import core
log = core.log.getLogger()

def login(request, message=None):
    institution = authentication_tools.get_institution(request)
    institutional_IdP = IdentityProvider.objects.filter(institution__iexact=str(institution))

    if not institutional_IdP:
        log.debug("No institution")
        return HttpResponse("There is no Identity Provider specified for your institution")
    else:
        authentication_type = institutional_IdP[0].type
        return render_to_response(str(authentication_type)+'.html',
        {'institution': institution,
        'message' : message,},
        context_instance=RequestContext(request))

def ldap_login(request):
    #TODO: What if one of these 3 fields aren't set?
    username = request.POST['username']
    password = request.POST['password']
    institution = request.POST['institution']

    identityprovider = IdentityProviderLDAP.objects.filter(institution__iexact=str(institution))
    if identityprovider:
        server = identityprovider[0]
    result_set = []
    
    log.debug(identityprovider)

    if identityprovider:
        roles = ldap_tools.get_ldap_roles(server.url, username, password, server.authentication, server.ssl)
        user_tools.login(request, username, roles, institution)
        if roles == None:
            return HttpResponseRedirect('/idpauth/login/')
        else:
            log.debug("Redirecting to vdi")
            return HttpResponseRedirect(settings.RESOURCE_REDIRECT_URL)
    else:
        message = 'There were errors retrieving the identity provider'
        return render_to_response('ldap.html', 
        {'institution' : institution,
        'message' : message},
        context_instance=RequestContext(request))

def openid_login(request):
    openid_url = request.POST['openid_url']
    institution = authentication_tools.get_institution(request)

    consumer = Consumer(request.session, openid_tools.DjangoOpenIDStore())

    try:
        auth_request = consumer.begin(openid_url)
    except DiscoveryFailure:
        return HttpResponse('The OpenID was invalid')

    trust_root =  authentication_tools.get_url_host(request) + '/'
    redirect_to = trust_root + 'idpauth/openid_login_complete/'
    log.debug(redirect_to)

    #Attribute Exchange
    requested_attributes = getattr(settings, 'OPENID_AX', False)

    if requested_attributes:
        log.debug("AX true")
        ax_request = ax.FetchRequest()
        for i in requested_attributes:
            ax_request.add(ax.AttrInfo(i['type_uri'], i['count'], i['required'], i['alias']))
        auth_request.addExtension(ax_request)

    redirect_url = auth_request.redirectURL(trust_root, redirect_to)

    debug_redirect_url = str(urllib.url2pathname(redirect_url)).split('&')
    for r in debug_redirect_url:
        log.debug(r)

    return HttpResponseRedirect(redirect_url)

def openid_login_complete(request):
    institution = authentication_tools.get_institution(request)
    for r in request.GET.items():
        log.debug(r)

    consumer = Consumer(request.session, openid_tools.DjangoOpenIDStore())

    url = (authentication_tools.get_url_host(request) + '/idpauth/openid_login_complete/').encode('utf8') + '?janrain_nonce=' + urllib.pathname2url(request.GET['janrain_nonce'])
    query_dict = dict([
        (k.encode('utf8'), v.encode('utf8')) for k, v in request.GET.items()
    ])

    openid_response = consumer.complete(query_dict, url)

    if openid_response.status == SUCCESS:
        openid = openid_tools.from_openid_response(openid_response)
        username = openid.ax.getExtensionArgs()['value.ext0.1']
        roles = authentication_tools.get_provider(request.GET['openid.op_endpoint'])
        user_tools.login(request, username, roles, institution)
        return HttpResponseRedirect(settings.RESOURCE_REDIRECT_URL)
    elif openid_response.status == CANCEL:
        message = "OpenID login failed due to a cancelled request.  This can be due to failure to release email address which is required by the service."
        return render_to_response('openid.html',
        {'message' : message,},
        context_instance=RequestContext(request))
    else:
        message = openid_response.message
        return render_to_response('openid.html',
        {'message' : message,},
        context_instance=RequestContext(request))
    
def local_login(request):

    username = request.POST['username']
    password = request.POST['password']
    institution = request.POST['institution']
    user = authenticate(username=username, password=password)

    roles = 'local'

    if user is not None:
        if user.is_active:
            user_tools.login(request, username, roles, institution)
        return HttpResponseRedirect(settings.RESOURCE_REDIRECT_URL)
    else:
        return HttpResponseRedirect('/idpauth/login/')

def shibboleth_login(request):

    try:
        username = request.META['REMOTE_USER']
        user_tools.login(request, username, "T", "null")
        
        return HttpResponse("Remote user set to:  " + remote_user)
    except KeyError, e:
        log.debug(e)
        return HttpResponse("Remote user not set.")

@user_tools.login_required
def logout(request):
    institution = request.session['institution']
    user_tools.logout(request)
    
    return render_to_response('logout.html',
    {'institution' : institution,},
    context_instance=RequestContext(request))
