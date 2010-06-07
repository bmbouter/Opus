import os
import os.path

import opus.lib.deployer

from django import forms
from django.forms.fields import *
from django.forms.widgets import *
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext


class DeploymentForm(forms.Form):
    vhost = CharField(required=True)
    vport = IntegerField(required=True)
    superusername = CharField(required=True)
    superpassword = CharField(required=True, widget=PasswordInput)
    superpasswordconfirm = CharField(required=True, widget=PasswordInput)
    superemail = CharField(required=True)
    dbengine = ChoiceField((
            ('sqlite3', 'SQLite'),
            ('postgresql_psycopg2', 'PostgreSQL', ),
            ('mysql', 'MySQL', ),
            ('oracle', 'Oracle', ),
            ))
    dbname = CharField(required=True)
    dbpassword = CharField(required=False, widget=PasswordInput)
    dbhost = CharField(required=False)
    dbport = IntegerField(required=False)

    def clean(self):
        if self.cleaned_data['superpassword'] != \
                self.cleaned_data['superpasswordconfirm']:
            raise forms.ValidationError("Passwords didn't match")
        return self.cleaned_data

def _verify_project(project):
    """Verifies that the given project name corresponds to a real un-deployed
    project in the base dir.

    """
    fullpath = os.path.join(settings.OPUS_BASE_DIR, project)
    if not project:
        return False
    if project.startswith("."):
        return False
    if not os.path.isdir(fullpath):
        return False
    if os.path.exists(os.path.join(fullpath, "wsgi")):
        # Already deployed?
        return False
    if not os.path.exists(os.path.join(fullpath, "__init__.py")):
        return False
    if not os.path.exists(os.path.join(fullpath, "settings.py")):
        return False
    if "/" in project or "\\" in project:
        return False
    return True

def choose_project(request):
    """Lists the projects in the configured deployment directory that are not
    yet deployed (defined by a wsgi/ directory present)

    """
    undeployed = []
    for item in os.listdir(settings.OPUS_BASE_DIR):
        if _verify_project(item):
            undeployed.append(item)
    
    return render_to_response('projectlist.html', {
        'projects': undeployed,
        }, context_instance=RequestContext(request))

def deploy_project(request):
    """Deploys a project. The project to deploy is given in the GET variable "project"

    """
    badproject = lambda: render_to_response('error.html', {
            'message': "Bad project name",
            }, context_instance=RequestContext(request))
    try:
        project = request.GET['project']
    except KeyError:
        return badproject()
    if not _verify_project(project):
        return badproject()

    if request.method == "POST":
        form = DeploymentForm(request.POST)
        if form.is_valid():
            d = opus.lib.deployer.ProjectDeployer(os.path.join(settings.OPUS_BASE_DIR, project))

            d.configure_database(form.cleaned_data['dbengine'],
                    form.cleaned_data['dbname'],
                    form.cleaned_data['dbpassword'],
                    form.cleaned_data['dbhost'],
                    form.cleaned_data['dbport'],
                    )

            d.sync_database(form.cleaned_data['superusername'],
                    form.cleaned_data['superemail'],
                    form.cleaned_data['superpassword'],
                    )

            d.secure_project(settings.OPUS_SECUREOPS_COMMAND)

            # XXX This is a bit of a hack, the opus libraries should be in the
            # path for the deployed app. TODO: Find a better way to handle
            # this.
            path_additions = "{0}:{1}".format(
                    settings.OPUS_BASE_DIR,
                    os.path.split(opus.__path__[0])[0],
                    )

            d.configure_apache(settings.OPUS_APACHE_CONFD,
                    form.cleaned_data['vhost'],
                    form.cleaned_data['vport'],
                    secureops=settings.OPUS_SECUREOPS_COMMAND,
                    pythonpath=path_additions,
                    )
            
            return render_to_response('deployed.html', {
                'vhost': form.cleaned_data['vhost'],
                }, context_instance=RequestContext(request))
    else:
        form = DeploymentForm()

    return render_to_response('deploymentform.html', {
        'formhtml': form,
        'projectname': '"{0}"'.format(project),
        }, context_instance=RequestContext(request))
