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

"""This file has urls for the json interface to the deployment data"""

from django.conf.urls.defaults import *

# The regex that matches project names in the URL. This needs to be a python
# identifier, since it translates to a python package. It also needs to be
# less than 30 characters or so, since it translates into a system user (this
# is checked in the edit_or_create view to give a better error message)
from opus.project.deployment.urls import projectpattern

urlpatterns = patterns('opus.project.deployment.jsonviews',
        url(r'^username', 'get_user'),
        url(r'^database', 'get_database_settings'),
        url(r'^$', 'projectlist'),
        url(r'^projects/(?P<projectname>{0})/$'.format(projectpattern), 'projectinfo'),
        url(r'^projects', 'projectlist'),
)
