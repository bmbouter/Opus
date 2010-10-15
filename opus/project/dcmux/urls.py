##############################################################################
# Copyright 2010 North Carolina State University                             #
#                                                                            #
#   Licensed under the Apache License, Version 2.0 (the "License");          #
#   you may not use this file except in compliance with the License.         #
#   You may obtain a copy of the License at                                  #
#                                                                            #
#       http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                            #
#   Unless required by applicable law or agreed to in writing, software      #
#   distributed under the License is distributed on an "AS IS" BASIS,        #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
#   See the License for the specific language governing permissions and      #
#   limitations under the License.                                           #
##############################################################################

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('opus.project.dcmux.views',
    url(r'^/?$', 'primary_entry_point', name='opus.project.dcmux.primary_entry_point'),

    url(r'^hardware_profiles/?$', 'hardware_profile_list', name='opus.project.dcmux.hardware_profiles'),
    url(r'^hardware_profiles/(.+)', 'hardware_profile_list', name='opus.project.dcmux.hardware_profile'),

    url(r'^realms/?$', 'realm_list', name='opus.project.dcmux.realms'),
    url(r'^realms/(.+)$', 'realm_list', name='opus.project.dcmux.realm'),

    url(r'^images/?$', 'image_list', name='opus.project.dcmux.images'),
    url(r'^images/(.+)$', 'image_list', name='opus.project.dcmux.image'),

    # List (GET) or create (POST) instance
    url(r'^instances/?$', 'instances_list', name='opus.project.dcmux.instances'),
    # Instance actions (start, stop, reboot...)
    url(r'^instances/(.+)/(.+)$', 'instance_action', name='opus.project.dcmux.instance_actions'),
    # List specific instance
    url(r'^instances/(.+)$', 'instance_list', name='opus.project.dcmux.instance'),
)
