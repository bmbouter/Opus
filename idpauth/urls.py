from django.conf.urls.defaults import *

urlpatterns = patterns('idpauth.views',
    (r'^login/$', 'determine_login'),
    (r'^openid_login/$', 'openid_login'),
    (r'^openid_login_complete/$', 'openid_login_complete'),
    (r'^ldap_login/$', 'ldap_login'),
    (r'^local_login/$', 'local_login'),
    (r'^shibboleth_login/$', 'shibboleth_login'),
    (r'^logout/$', 'logout_view'),
)
