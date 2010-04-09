from django.conf.urls.defaults import *


urlpatterns = patterns('nxproxy.views',
    (r'^sessions/', 'sessions'),
    (r'^conn_builder', 'conn_builder'),
)
