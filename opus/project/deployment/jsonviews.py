"""Views for the json interface to the data"""

import json

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from opus.project.deployment import models
from opus.project.deployment.views import get_project_object

def render(struct):
    response = HttpResponse(mimetype="application/json")
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

        ret.append(info)

    return render(ret)

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

    info['apps'] = []
    for app in project.config['INSTALLED_APPS']:
        if app.startswith(project.name + "."):
            info['apps'].append(app)

    return render(info)
