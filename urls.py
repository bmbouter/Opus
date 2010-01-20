from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^vdi/desktop/(?P<action>new)', 'mysite.vdi.views.desktop'),
    (r'^vdi/desktop/(?P<desktopId>(\w|-)*)/save/$', 'mysite.vdi.views.saveDesktop'),
    (r'^vdi/desktop/(?P<desktopId>(\w|-)*)/(?P<action>(connect|delete))$', 'mysite.vdi.views.desktop'),
    #(r'^vdi/desktop/(?P<desktopId>(\w|-)*)/(?P<conn_type>(nx|rdp))$', 'mysite.vdi.views.desktop'),
    (r'^vdi/desktop/(?P<desktopId>(\w|-)*)/$', 'mysite.vdi.views.desktop'),
    (r'^vdi/desktop/$', 'mysite.vdi.views.desktop'),
    (r'^vdi/image-library/$', 'mysite.vdi.views.imageLibrary'),
    (r'^admin/', include(admin.site.urls)),
)
