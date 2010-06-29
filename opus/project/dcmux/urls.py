from django.conf.urls.defaults import *

urlpatterns = patterns('opus.project.dcmux.views',
    url(r'^/?$', 'primary_entry_point', name='opus.project.dcmux.primary_entry_point'),

    url(r'^hardware_profiles/?$', 'hardware_profiles', name='opus.project.dcmux.hardware_profiles'),
    url(r'^hardware_profiles/(.+)', 'hardware_profiles', name='opus.project.dcmux.hardware_profile'),

    url(r'^realms/?$', 'realms', name='opus.project.dcmux.realms'),
    url(r'^realms/(.+)$', 'realms', name='opus.project.dcmux.realm'),

    url(r'^images/?$', 'images', name='opus.project.dcmux.images'),
    url(r'^images/(.+)$', 'images', name='opus.project.dcmux.image'),

    url(r'^instances/?$', 'instances', name='opus.project.dcmux.instances'),
    # Instance actions (start, stop, reboot...)
    url(r'^instances/(.+)/(.+)/$', 'instance_action', name='opus.project.dcmux.instance_actions'),
    url(r'^instances/(.+)$', 'instances', name='opus.project.dcmux.instance'),
)
