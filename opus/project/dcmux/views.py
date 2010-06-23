from django.core.urlresolvers import reverse
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render_to_response

import opus.lib.log
log = opus.lib.log.getLogger()

import opus.lib.prov.deltacloud

from collections import namedtuple

from models import Provider, Policy

def uri_lookup(request, resource):
    return request.build_absolute_uri(
        reverse("opus.project.dcmux.%s" % resource)
    )

def primary_entry_point(request):
    """The entry point which lists the urls for all resources."""

    resource_names = [
        "primary_entry_point",
        "hardware_profiles",
        #"instance_states",
        "realms",
        "images",
        "instances",
    ]
    Link = namedtuple("Link", "resource uri")
    links = []
    for resource in resource_names:
        links.append(Link(resource, uri_lookup(request, resource)))

    return render_to_response(
        'dcmux/primary_entry.xml',
        {"links": links},
        mimetype="text/xml",
    )

def hardware_profiles(request):
    """Lists all hardware profiles.

    In dcmux, there will be one hardware profile.  The real hardware profile
    that will be used is specified in the UpstreamImage.

    """
    return render_to_response(
            'dcmux/hardware_profiles.xml',
            {"hardware_profiles_uri": uri_lookup(request, "hardware_profiles")},
            mimetype="text/xml",
    )

def realms(request):
    """List all realms.

    Realms are derived from Policies.

    """
    realms = Policy.objects.all()
    return render_to_response(
        'dcmux/realms.xml',
        {
            "realms_uri": uri_lookup(request, "realms"),
            "realms": realms,
        },
        mimetype="text/xml",
    )

def images(request):
    """List all downstream images."""
    #TODO
    pass

def instances(request):
    #TODO
    pass
