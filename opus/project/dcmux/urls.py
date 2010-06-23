from django.conf.urls.defaults import *

urlpatterns = patterns('opus.project.dcmux.views',
    url(r'^$', 'primary_entry_point', name='opus.project.dcmux.primary_entry_point'),
    url(r'^hardware_profiles$', 'hardware_profiles', name='opus.project.dcmux.hardware_profiles'),
    url(r'^realms$', 'realms', name='opus.project.dcmux.realms'),
    url(r'^images$', 'images', name='opus.project.dcmux.images'),
    url(r'^instances', 'instances', name='opus.project.dcmux.instances'),
)
