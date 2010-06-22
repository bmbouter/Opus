import functools

from opus.project.deployment import models, forms
import opus.lib.builder
import opus.lib.log
log = opus.lib.log.get_logger()

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

def render(templatename, params, request, code=200):
    response = render_to_response(templatename, params,
            context_instance=RequestContext(request))
    response.status_code = code
    return response

@login_required
def list_or_new(request):
    """This view should render a page that displays currently deployed projects
    available to edit, and a form to create+deploy a new project.

    It is an error to call this view with a POST method

    """
    if request.method == "POST":
        return render("error.html", {
            'message': "Method Not Allowed",
            },
            code=405
            )

    # Get existing projects and list them
    deployments = models.DeployedProject.objects.all()
    if not request.user.is_superuser:
        deployments = deployments.filter(owner=request.user)

    return render("deployment/list_deployments.html", {
        'deployments': deployments,
        }, request)


@login_required
def edit_or_create(request, projectname):
    """This view does four things:
    When called with a GET method and a projectname that doesn't exist,
    displays the necessary forms for creating and deploying a new project

    When called with a POST method and a projectname that doesn't exist, uses
    the POST data to create and deploy a new project

    When called with a GET method and a projectname that does exist, displays a
    form to edit attributes of a depolyed project.

    When called with a POST method and a projectname that does exist, uses the
    POST data to edit the project attributes.

    """
    # Check the max length of the project name to provide a better error
    # message. Let me know if anyone knows an easier way to extract the
    # max_length attribute of the 'name' field of a database model object.
    max_length = models.DeployedProject._meta.get_field_by_name('name')[0].max_length
    if len(projectname) > max_length:
        return render("error.html", {
            "message": "Project names must be less than {0} characters"\
                    .format(max_length),
            }, request)

    # Try and fetch the database object to see if the project exists
    projectquery = models.DeployedProject.objects.filter(
            name=projectname)
    if projectquery.exists():
        # Project does exist, we're in edit mode
        return edit(request, projectquery.get())
    else:
        # Project does not exist, we're in create mode
        return create(request, projectname)


@login_required
def edit(request, project):
    """Configuration editor for an already deployed project

    """
    # Check permissions
    if not project.owner == request.user:
        return render("error.html",
                {"message":"Access Denied"},
                request)

    return render("deployment/edit.html",
            {'project': project},
            request)

def catch_deployerrors(f):
    """A decorator that catches ValidationError and DeploymentExceptions on
    views and renders error.html instead of letting the error propagate.

    """
    @functools.wraps(f)
    def newf(request, *args, **kwargs):
        try:
            return f(request, *args, **kwargs)
        except (ValidationError, models.DeploymentException), e:
            return render("error.html",
                    {'message': e},
                    request)
    return newf

@login_required
@catch_deployerrors
def create(request, projectname):
    """Create and deploy a new project. Displays the form to do so on GET, goes
    and does a create + deploy operation on POST.

    """
    if request.method == "POST":
        pform = forms.ProjectForm(request.POST)
        appsform = forms.AppFormSet(request.POST)
        dform = forms.DeploymentForm(request.POST)
        allforms = [pform, appsform, dform]
        if all(f.is_valid() for f in allforms):
            log.info("Preparing to create+deploy %s", projectname)
            # Create the deployment object to do some early validation checks
            deployment = models.DeployedProject()
            deployment.name = projectname
            deployment.owner = request.user
            deployment.vhost = dform.cleaned_data['vhost']
            deployment.vport = dform.cleaned_data['vport']
            deployment.verify_deploy()

            # Create a new project
            pdata = pform.cleaned_data
            builder = opus.lib.builder.ProjectBuilder(projectname)
            for appdata in appsform.cleaned_data:
                if not appdata:
                    # Left blank, nothing to add
                    continue
                log.debug(" ... with app %r", appdata['apppath'])
                builder.add_app(appdata['apppath'], appdata['apptype'])
            if pdata['admin']:
                log.debug(" ... and the admin app")
                builder.set_admin_app()
            log.debug("Executing create action on %r...", projectname)
            projectdir = builder.create(settings.OPUS_BASE_DIR)
            log.info("%r created, starting deploy process", projectname)

            # Deploy it
            info = models.DeploymentInfo()
            info.dbengine = dform.cleaned_data['dbengine']
            info.dbname = dform.cleaned_data['dbname']
            info.dbpassword = dform.cleaned_data['dbpassword']
            info.dbhost = dform.cleaned_data['dbhost']
            info.dbport = dform.cleaned_data['dbport']
            info.superusername = dform.cleaned_data['superusername']
            info.superemail = dform.cleaned_data['superemail']
            info.superpassword = dform.cleaned_data['superpassword']

            deployment.deploy(info)
            log.info("Project %r successfully deployed", projectname)

            return render("deployment/newsuccess.html", {}, request)
        
    else:
        pform = forms.ProjectForm()
        appsform = forms.AppFormSet()
        dform = forms.DeploymentForm()

    return render("deployment/newform.html", dict(
            pform=pform,
            appsform=appsform,
            dform=dform,
            projectname=projectname,
            ), request)
