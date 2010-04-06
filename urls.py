from django.conf.urls.defaults import *

import vdi, nxproxy, dataservice.views, auth
import vdi.testing_tools

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
    (r'^vdi/login/(?P<school>\w*)/$', vdi.views.ldaplogin),
    (r'^vdi/login/$', vdi.views.login),
    (r'^vdi/ldap_login/$', vdi.views.ldaplogin),
    (r'^vdi/logout/$', vdi.views.logout),
    (r'^vdi/$', vdi.views.applicationLibrary),
    (r'^vdi/(?P<app_pk>(\d)+)/connect$', vdi.views.connect),
    (r'^vdi/(?P<app_pk>(\d)+)/connect/(?P<conn_type>(nx|nxweb|rdp|rdpweb)+)$', vdi.views.connect),
    (r'^vdi/scale', vdi.views.scale),
    (r'^admin/', include(admin.site.urls)),
    (r'^nxproxy/sessions/', nxproxy.views.sessions),
    (r'^dataservice/', dataservice.views.meta_feed),
    (r'^vdi/(?P<app_pk>(\d)+)/stats', vdi.views.stats),
    (r'^nxproxy/conn_builder', nxproxy.views.conn_builder),
    (r'^vdi/calculate_cost/(?P<start_date>(\d{4}-\d{2}-\d{2}[T]\d{2}:\d{2}:\d{2}){1}),(?P<end_date>(\d{4}-\d{2}-\d{2}[T]\d{2}:\d{2}:\d{2}){1})', vdi.views.calculate_cost),
    (r'^vdi/testing_tools/(?P<app_pk>(\d)+)/clusterSize/(?P<date_time>(\d{4}-\d{2}-\d{2}[T]\d{2}:\d{2}:\d{2}){1})$', vdi.testing_tools.get_nodesInCluster),
    (r'^vdi/testing_tools/(?P<app_pk>(\d)+)/provEvents/(?P<start_date>(\d{4}-\d{2}-\d{2}[T]\d{2}:\d{2}:\d{2}){1}),(?P<end_date>(\d{4}-\d{2}-\d{2}[T]\d{2}:\d{2}:\d{2}){1})', vdi.testing_tools.get_provisioningEventsInDateRange),
    (r'^vdi/testing_tools/(?P<app_pk>(\d)+)/deprovEvents/(?P<start_date>(\d{4}-\d{2}-\d{2}[T]\d{2}:\d{2}:\d{2}){1}),(?P<end_date>(\d{4}-\d{2}-\d{2}[T]\d{2}:\d{2}:\d{2}){1})$', vdi.testing_tools.get_deprovisioningEventsInDateRange),
)
