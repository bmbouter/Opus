from django.conf.urls.defaults import *

import vdi

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
    (r'^vdi/login/$', vdi.views.login),
    (r'^vdi/logout/$', vdi.views.logout),
    (r'^vdi/desktop/(?P<action>new)', vdi.views.desktop),
    (r'^vdi/desktop/(?P<desktopId>(\w|-)*)/save/$', vdi.views.saveDesktop),
    (r'^vdi/desktop/(?P<desktopId>(\w|-)*)/(?P<action>(connect|delete))$', vdi.views.desktop),
    #(r'^vdi/desktop/(?P<desktopId>(\w|-)*)/(?P<conn_type>(nx|rdp))$', vdi.views.desktop),
    (r'^vdi/desktop/(?P<desktopId>(\w|-)*)/$', vdi.views.desktop),
    (r'^vdi/desktop/$', vdi.views.desktop),
    (r'^vdi/image-library/$', vdi.views.imageLibrary),
    (r'^admin/', include(admin.site.urls)),
)
