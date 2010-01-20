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

    (r'^vdi/desktop/(?P<action>new)', 'djangoSite.vdi.views.desktop'),
    (r'^vdi/ldap_login/$', 'djangoSite.vdi.views.ldaplogin'),
    (r'^vdi/desktop/(?P<desktopId>(\w|-)*)/save/$', 'djangoSite.vdi.views.saveDesktop'),
    (r'^vdi/desktop/(?P<desktopId>(\w|-)*)/(?P<action>(connect|delete))$', 'djangoSite.vdi.views.desktop'),
    #(r'^vdi/desktop/(?P<desktopId>(\w|-)*)/(?P<conn_type>(nx|rdp))$', 'djangoSite.vdi.views.desktop'),
    (r'^vdi/desktop/(?P<desktopId>(\w|-)*)/$', 'djangoSite.vdi.views.desktop'),
    (r'^vdi/desktop/$', 'djangoSite.vdi.views.desktop'),
    (r'^vdi/image-library/$', 'djangoSite.vdi.views.imageLibrary'),
    (r'^admin/', include(admin.site.urls)),
)
