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

"""Views for the json interface to the data"""

import json

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.conf import settings

from opus.project.deployment import models
from opus.project.deployment.views import get_project_object, debug_view

def render(struct, request):
    response = HttpResponse(mimetype="application/json")
    callback = request.GET.get("callback", None)
    if callback:
        response.write(callback+"(")
        json.dump(struct, response)
        response.write(")")
    else:
        json.dump(struct, response)
    return response

@login_required
def projectlist(request):
    deployments = models.DeployedProject.objects.all()
    if not request.user.is_superuser:
        deployments = deployments.filter(owner=request.user)

    ret = []
    for d in deployments:
        info = {}

        info['name'] = d.name
        info['owner'] = d.owner.username
        info['uri'] = reverse('opus.project.deployment.jsonviews.projectinfo',
                kwargs=dict(projectname=d.name))
        info['href'] = reverse('opus.project.deployment.views.edit_or_create',
                kwargs=dict(projectname=d.name))
        info['urls'] = d.get_urls()
        info['active'] = d.active

        ret.append(info)

    return render(ret, request)

@login_required
@get_project_object
def projectinfo(request, project):
    
    info = {}

    info['name'] = project.name
    info['owner'] = project.owner.username
    info['uri'] = reverse('opus.project.deployment.jsonviews.projectinfo',
            kwargs=dict(projectname=project.name))
    info['href'] = reverse('opus.project.deployment.views.edit_or_create',
            kwargs=dict(projectname=project.name))
    info['urls'] = project.get_urls()
    info['active'] = project.active

    info['apps'] = []
    for app in project.config['INSTALLED_APPS']:
        if app.startswith(project.name + "."):
            info['apps'].append(app)

    database = project.config['DATABASES']['default']
    info['dbname'] = database['NAME']
    info['dbengine'] = database['ENGINE'].rsplit(".",1)[1]
    info['dbpassword'] = "12345" # Nobody would use this password
    info['dbhost'] = database['HOST']
    info['dbport'] = database['PORT']
    info['active'] = project.active

    return render(info, request)

def get_user(request):
    # No login required here
    r = {}
    r['authenticated'] = request.user.is_authenticated()
    r['username'] = request.user.username
    return render(r, request)
