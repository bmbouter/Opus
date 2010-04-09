from django.conf.urls.defaults import *

import vdi, nxproxy, vdi.testing_tools

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^djangoSite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/jsi18n', 'django.views.i18n.javascript_catalog'),
    (r'idpauth/', include('idpauth.urls')),
    (r'vdi/', include('vdi.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^nxproxy/sessions/', nxproxy.views.sessions),
    (r'^nxproxy/conn_builder', nxproxy.views.conn_builder),
    (r'^dataview/', include('dataview.urls')),
)
