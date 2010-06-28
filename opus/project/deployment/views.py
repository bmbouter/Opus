import functools
import json

from opus.project.deployment import models, forms
import opus.lib.builder
import opus.lib.deployer
from opus.lib.deployer import DeploymentException
import opus.lib.log
log = opus.lib.log.get_logger()

from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt

def render(templatename, params, request, code=200):
    response = render_to_response(templatename, params,
            context_instance=RequestContext(request))
    response.status_code = code
    return response

# A few decorators that come in handy. Perhaps move these to another file for
# organization
def catch_deployerrors(f):
    """A decorator that catches ValidationError and DeploymentExceptions on
    views and renders error.html instead of letting the error propagate.

    """
    @functools.wraps(f)
    def newf(request, *args, **kwargs):
        try:
            return f(request, *args, **kwargs)
        except (ValidationError, DeploymentException), e:
            return render("error.html",
                    {'message': e},
                    request)
    return newf

def get_project_object(f):
    """A decorator that wraps views which takes a parameter called
    projectname. Attempts to fetch the object from the database and calls the
    view function with the object as the second parameter. Raises 404 if not
    found.

    Also checks access permission.

    """
    @functools.wraps(f)
    def newf(request, projectname, *args, **kwargs):
        obj = get_object_or_404(models.DeployedProject,
                name=projectname)
        if not obj.owner == request.user and not request.user.is_superuser:
            return render("error.html",
                    {"message":"Access Denied"},
                    request)
        return f(request, obj, *args, **kwargs)
    return newf

def debug_view(f):
    """Put this decorator on a view to dump to the log the request, post data,
    headers, and dump the returned data

    """
    @functools.wraps(f)
    def newf(request, *args, **kwargs):
        import pprint
        log.debug("{0} view called".format(f.__name__))
        log.debug(request.raw_post_data)
        log.debug(request.POST)
        log.debug(pprint.pformat(request.META))
        ret = f(request, *args, **kwargs)
        log.debug(ret)
        return ret
    return newf

# The actual views
# ################

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
#@debug_view
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
        return edit(request, projectname)
    else:
        # Project does not exist, we're in create mode
        return create(request, projectname)


@login_required
@get_project_object
def edit(request, project):
    """Configuration editor for an already deployed project

    """
    # Get the initial values for this form, so we can tell what changed when
    # the user submits it
    database = project.config['DATABASES']['default']
    initial = {}
    initial['vhost'] = project.vhost
    initial['vport'] = project.vport
    initial['dbname'] = database['NAME']
    initial['dbengine'] = database['ENGINE'].rsplit(".",1)[1]
    initial['dbpassword'] = "12345" # Nobody would use this password
    initial['dbhost'] = database['HOST']
    initial['dbport'] = database['PORT']
    initial['active'] = project.active

    if request.method == "POST":
        form = forms.DeploymentForm(request.POST, initial=initial)
        if form.is_valid():
            log.info("Edit form submitted and is valid. Editing project parameters")
            cd = form.cleaned_data
            # Go and modify the project/config parameters. Don't save yet
            reactivate = False
            for field in form.changed_data:
                if field == "vhost":
                    project.vhost = cd['vhost']
                    reactivate = True
                    log.debug("vhost changed to %s", cd['vhost'])
                elif field == "vport":
                    project.vport = cd['vport']
                    reactivate = True
                    log.debug("vport changed to %s", cd['vport'])
                elif field == "dbengine":
                    database['ENGINE'] = cd['dbengine']
                    log.debug("dbengine changed to %s", cd['dbengine'])
                elif field == "dbpassword":
                    database['PASSWORD'] = cd['dbpassword']
                    log.debug("dbpassword changed",)
                elif field == "dbhost":
                    database['HOST'] = cd['dbhost']
                    log.debug("dbhost changed to %s", cd['dbhost'])
                elif field == "dbport":
                    database['PORT'] = cd['dbport']
                    log.debug("dbport changed to %s", cd['dbport'])

            messages = []

            # Validate the modified model
            try:
                # This may error if there's a port conflict or something
                project.full_clean()
            except ValidationError, e:
                log.info("Project model didn't clean. %s", e)
                messages.extend(e.messages)
                # Re-load the project object with the old data, for the "Info"
                # section
                project = models.DeployedProject.objects.get(pk=project.pk)
            else:
                log.info("Model cleaned, saving")
                # save model and config, activate/deactivate if requested,
                # add new superuser if requested
                project.save()
                if 'active' in form.changed_data or reactivate:
                    # If the vhost or vport changed, re-write the config file
                    # regardless
                    if cd['active']:
                        log.debug("Activating")
                        project.activate()
                        messages.append("Project activated")
                    else:
                        log.debug("Deactivating")
                        project.deactivate()
                        messages.append("Project deactivated")
                if "superusername" in form.changed_data:
                    # Should this code be offloaded to a method in the model?
                    log.debug("Adding new superuser")
                    deployer = opus.lib.deployer.ProjectDeployer(project.projectdir)
                    try:
                        deployer.create_superuser(cd['superusername'],
                                cd['superemail'],
                                cd['superpassword'],
                                )
                    except DeploymentException, e:
                        if "column username is not unique" in e.message:
                            messages.append("User with that name already exists!")
                        else:
                            raise e
                    else:
                        messages.append("New superuser created")
                        # Don't re-render the username and password in the form
                        # First make it mutable
                        form.data = form.data.copy()
                        # Then delete these properties
                        del form.data['superusername']
                        del form.data['superemail']
                        del form.data['superpassword']
                        del form.data['superpasswordconfirm']
            return render("deployment/edit.html",
                    {'project': project,
                        'form': form,
                        'message': "<br />".join(messages)
                        }, request)
    else:
        form = forms.DeploymentForm(initial=initial)

    return render("deployment/edit.html",
            {'project': project,
                'form': form},
            request)


@login_required
@catch_deployerrors
def create(request, projectname):
    """Create and deploy a new project. Displays the form to do so on GET, goes
    and does a create + deploy operation on POST.

    """
    if request.method == "POST" and "json" not in request.POST:
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
            deployment.full_clean()

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

            deployment.deploy(info, active=dform.cleaned_data['active'])
            log.info("Project %r successfully deployed", projectname)

            return redirect(deployment)
        
    else:
        jsoncontent = request.POST.get("json", False)
        if jsoncontent:
            # Request came from a GWT submit with applications filled in
            selectedapps = json.loads(jsoncontent)
            # Fill the app form set with this initial data
            appsform = forms.AppFormSet(initial=selectedapps)
        else:
            appsform = forms.AppFormSet()
        pform = forms.ProjectForm()
        dform = forms.DeploymentForm()

    return render("deployment/newform.html", dict(
            pform=pform,
            appsform=appsform,
            dform=dform,
            projectname=projectname,
            ), request)

@login_required
@get_project_object
def destroy(request, project):
    """Destroys a project"""
    if request.method == "POST":
        project.destroy()
        return render("deployment/destroyed.html", {
            'projectname': project.name
            }, request)
    else:
        return redirect(project)
