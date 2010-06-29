from django.core.urlresolvers import reverse
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist

from collections import namedtuple

import opus.lib.log
log = opus.lib.log.getLogger()
import opus.lib.prov.deltacloud
from models import Provider, Policy, DownstreamImage, UpstreamImage, Instance

HardwareProfile = namedtuple("HardwareProfile", "id")

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

def hardware_profiles(request, name=None):
    """Lists all hardware profiles, or the given one if id!=None.

    In dcmux, there is one hardware profile.  The real hardware profile
    that will be used is specified in the UpstreamImage.

    """

    if name == None or name == "generic":
        hardware_profiles = [HardwareProfile("generic")]
    else:
        hardware_profiles = []

    return render_to_response(
            'dcmux/hardware_profiles.xml',
            {
                "hardware_profiles_uri": uri_lookup(request, "hardware_profiles"),
                "hardware_profiles": hardware_profiles,
            },
            mimetype="text/xml",
    )

def realms(request, id=None):
    """List all realms, or the given realm if id!=None."""

    if id == None:
        realms = Policy.objects.all()
    else:
        try:
            realms = [Policy.objects.get(id=id)]
        except ValueError:
            # id wasn't an int, which it should be
            realms = []
        except ObjectDoesNotExist:
            realms = []

    return render_to_response(
        'dcmux/realms.xml',
        {
            "realms_uri": uri_lookup(request, "realms"),
            "realms": realms,
        },
        mimetype="text/xml",
    )

def images(request, id=None):
    """List all downstream images, or the given image if id!=None."""

    if id == None:
        images = DownstreamImage.objects.all()
    else:
        try:
            images = [DownstreamImage.objects.get(id=id)]
        except ValueError:
            # id wasn't an int, which it should be
            images = []
        except ObjectDoesNotExist:
            images = []

    return render_to_response(
        'dcmux/images.xml',
        {
            "images_uri": uri_lookup(request, "images"),
            "images": images,
        },
        mimetype="text/xml",
    )

def instances(request, id=None):
    """List all instances, or the given instance if id!=None."""

    if id == None:
        instances = Instance.objects.all()
    else:
        try:
            instances = [Instance.objects.get(id=id)]
        except ValueError:
            # id wasn't an int, which it should be
            instances = []
        except ObjectDoesNotExist:
            instances = []

    return render_to_response(
        'dcmux/instances.xml',
        {
            "instances_uri": uri_lookup(request, "instances"),
            "instances": instances,
        },
        mimetype="text/xml",
    )
