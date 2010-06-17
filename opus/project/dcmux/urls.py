from django.conf.urls.defaults import *

urlpatterns = patterns('opus.project.dcmux.views',
    url(r'^$', 'primary_entry_point', name='opus.project.dcmux_primary_entry_point'),
    url(r'^hardware_profiles$', 'hardware_profiles', name='opus.project.dcmux_hardware_profiles'),
)
