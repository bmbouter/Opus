from django.conf.urls.defaults import *


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
    (r'^admin/', include(admin.site.urls)),
    (r'^idpauth/', include('idpauth.urls')),
    (r'^vdi/', include('vdi.urls')),
    (r'^nxproxy/', include('nxproxy.urls')),
    (r'^dataview/', include('dataview.urls')),
)
