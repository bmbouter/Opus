from django.core.urlresolvers import reverse
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render_to_response

import opus.lib.log
log = opus.lib.log.getLogger()

import opus.lib.prov.deltacloud

from models import Provider

# Create your views here.

def primary_entry_point(request):
    entry_uri = request.build_absolute_uri(reverse('opus.project.dcmux_primary_entry_point'))
    return render_to_response('primary_entry.html', {'entry_uri': entry_uri})

def hardware_profiles(request):
    client = Provider.objects.all()[0].get_dc_client()
    client.connect()
    for a in client.flavors()log.warning(type(client.flavors()))
    return render_to_response('hardware_profiles.html', {'hardware_profiles': '2'})
