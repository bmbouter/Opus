from django.conf.urls.defaults import *

import vdi, nxproxy

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
    (r'^vdi/ldap_login/$', vdi.views.ldaplogin),
    (r'^vdi/ldap_login/(?P<school>\w*)/$', vdi.views.ldaplogin),
    (r'^vdi/login/$', vdi.views.login),
    (r'^vdi/logout/$', vdi.views.logout),
    (r'^vdi/$', vdi.views.applicationLibrary),
    (r'^vdi/(?P<app_pk>(\d)*)/connect$', vdi.views.connect),
    (r'^vdi/(?P<app_pk>(\d)*)/connect/nxsession$', vdi.views.nxsession),
    (r'^vdi/(?P<app_pk>(\d)*)/connect/(?P<conn_type>(nx|rdp)*)$', vdi.views.connect),
    (r'^vdi/scale', vdi.views.scale),
    (r'^admin/', include(admin.site.urls)),
    (r'^nxproxy/sessions/', nxproxy.views.sessions),
)
