from django.conf.urls.defaults import *

import idpauth

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('opus.idpauth.views',
    (r'^login/$', idpauth.views.login),
    (r'^openid_login/$', idpauth.views.openid_login),
    (r'^openid_login_complete/(?P<institution>\w*)/$', idpauth.views.openid_login_complete),
    (r'^ldap_login/$', idpauth.views.ldap_login),
    (r'^local_login/$', idpauth.views.local_login),
    (r'^shibboleth_login/$', idpauth.views.shibboleth_login),
    (r'^logout/$', idpauth.views.logout),
)
