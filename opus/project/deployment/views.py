import functools
import json
import urllib2

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

    I think this is unnecessary. Django has error handling built in, we should
    be using that outside of debug, and its built in error pages when
    debugging.

    """
    @functools.wraps(f)
    def newf(request, *args, **kwargs):
        try:
            return f(request, *args, **kwargs)
        except (ValidationError, DeploymentException), e:
            log.warning("Caught an error while running view %s, rendering error.html. %s", f.__name__, e)
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

    """
    message = ""
    if 'name' in request.GET:
        if not models.id_re.match(request.GET['name']):
            message = "Bad project name. Project names must consist of only letters, numbers, and the underscore character. They must not begin with a number. And they must be less than 25 characters long."
        else:
            return redirect("opus.project.deployment.views.edit_or_create",
                    projectname=request.GET['name'])


    # Get existing projects and list them
    deployments = models.DeployedProject.objects.all()
    if not request.user.is_superuser:
        deployments = deployments.filter(owner=request.user)

    return render("deployment/list_deployments.html", {
        'deployments': deployments,
        'message': message,
        'suffix': settings.OPUS_APACHE_SERVERNAME_SUFFIX,
        }, request)


@csrf_exempt # XXX XXX REMOVE ME
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

def _get_initial_edit_data(project):
    # Get the initial values for this form, so we can tell what changed when
    # the user submits it
    database = project.config['DATABASES']['default']
    initial = {}
    initial['dbname'] = database['NAME']
    initial['dbengine'] = database['ENGINE'].rsplit(".",1)[1]
    initial['dbpassword'] = "12345" # Nobody would use this password
    initial['dbhost'] = database['HOST']
    initial['dbport'] = database['PORT']
    initial['active'] = project.active
    return initial

@login_required
@get_project_object
def edit(request, project):
    """Configuration editor view for an already deployed project

    """
    initial = _get_initial_edit_data(project)

    if request.method == "POST":
        form = forms.DeploymentForm(request.POST, initial=initial)
        if form.is_valid():
            log.info("Edit form submitted and is valid. Editing project parameters")
            cd = form.cleaned_data
            # Go and modify the project/config parameters. Don't save yet
            for field in form.changed_data:
                if field == "dbengine":
                    database['ENGINE'] = 'django.db.backends.' + cd['dbengine']
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
                if 'active' in form.changed_data:
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
                        'message': "<br />".join(messages),
                        'applist': _get_apps(project),
                        'appform': forms.AppForm(),
                        }, request)
    else:
        form = forms.DeploymentForm(initial=initial)

    newappform = forms.AppForm()
    return render("deployment/edit.html",
            {'project': project,
                'form': form,
                'appform': newappform,
                'applist': _get_apps(project),
                },
            request)

@login_required
def create(request, projectname):
    """Create and deploy a new project. Displays the form to do so on GET, goes
    and does a create + deploy operation on POST.
    Also has the feature to pre-fill out the form from an incomming JSON token.

    """
    if request.method == "POST" and request.META['CONTENT_TYPE'] == \
            "application/x-www-form-urlencoded":
        # If the submitted type is not form encoded data, it's probably a json
        # spec of applications, which should instead go to populate and display
        # the forms.
        pform = forms.ProjectForm(request.POST)
        appsform = forms.AppFormSet(request.POST)
        dform = forms.DeploymentForm(request.POST)
        allforms = [pform, appsform, dform]
        # If forms aren't valid, fall through and display the (invalid) forms
        # with error text
        if all(f.is_valid() for f in allforms):
            log.info("Preparing to create+deploy %s", projectname)
            # Create the deployment object to do some early validation checks
            deployment = models.DeployedProject()
            deployment.name = projectname
            deployment.owner = request.user
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
            try:
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
            except Exception, e:
                # The project didn't deploy for whatever reason. Delete the
                # project directory and re-raise the exception
                # Careful that this method isn't called on an existing project,
                # since it could be tricked into deleting an existing project.
                # edit_or_create() ought to check that for us, this function
                # shouldn't be called on an existing project.
                log.warning("Project didn't fully create or deploy, rolling back deployment. %s", e)
                deployment.destroy()
                raise

            log.info("Project %r successfully deployed", projectname)

            return redirect(deployment)

        else:
            log.debug("Create view called, but forms didn't validate")
        
    else:
        # Request was either a GET, or was a POST with non-form data
        # Display blank forms
        log.debug("create view called, displaying form")
        appsform = forms.AppFormSet()
        pform = forms.ProjectForm()
        dform = forms.DeploymentForm()

        # If a token was passed in to the GET params, try and use it to
        # populate the app list formset
        token = request.GET.get("token", False)
        if token:
            metadata = urllib2.urlopen(opus.COMMUNITY_URL + "/metadata/" + token)
            metaobj = json.load(metadata)
            # Fill the app form set with this initial data
            appsform = forms.AppFormSet(initial=metaobj['applist'])
            pform = forms.ProjectForm(initial={'admin': 
                metaobj.get('admin', False)})

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

@login_required
@get_project_object
def addapp(request, project):
    """Adds an application on submission of an app form"""
    if request.method == "POST":
        appform = forms.AppForm(request.POST)
        if appform.is_valid():
            # Go and add an app
            editor = opus.lib.builder.ProjectEditor(project.projectdir)
            editor.add_app(appform.cleaned_data['apppath'],
                    appform.cleaned_data['apptype'])
            return render("deployment/addappform.html", dict(
                message='Application added',
                appform=forms.AppForm(),
                project=project,
                ), request)
    else:
        appform = forms.AppForm()



    return render("deployment/addappform.html", dict(
        appform=appform,
        project=project,
        ), request)


def _get_apps(project):
    apps = []
    for potential in project.config['INSTALLED_APPS']:
        if potential.startswith(project.name + "."):
            apps.append(dict(appname=potential))
    return apps

@login_required
@get_project_object
def editapp(request, project):
    if request.method == "POST":
        form = forms.EditAppFormSet(request.POST, initial=_get_apps(project))
        if form.is_valid():
            editor = opus.lib.builder.ProjectEditor(project.projectdir)
            deletecount = 0
            upgradecount = 0
            failures = []
            for appform in form.forms:

                if appform in form.deleted_forms:
                    # So that cleaned_data gets populated
                    appform.full_clean()
                    try:
                        editor.del_app(appform.cleaned_data['appname'])
                    except opus.lib.builder.BuildException, e:
                        failures.append((appform.cleaned_data['appname'], 'delete', e))
                    else:
                        deletecount += 1
                        # Remove the app from the installed app in the config.
                        # This is also done by the call to del_app(), but since
                        # the config has been loaded into memory already by the
                        # model object, that data becomes stale. This line is
                        # mostly just a hack so the next call to _get_apps()
                        # returns correct data. This change isn't saved, since
                        # there's no reason to. The change was already saved by
                        # del_app()
                        project.config['INSTALLED_APPS'].remove(
                                appform.cleaned_data['appname'])
                elif appform.cleaned_data['upgradever']:
                    try:
                        editor.upgrade_app(appform.cleaned_data['appname'],
                                appform.cleaned_data['upgradever'])
                    except opus.lib.builder.BuildException, e:
                        failures.append((appform.cleaned_data['appname'], 'upgrade', e))
                    else:
                        upgradecount += 1

            message = "{upcnt} {upproj} upgraded successfully. {delcnt} {delproj} deleted successfully.".format(
                    upcnt = upgradecount,
                    upproj = "projects" if upgradecount != 1 else "project",
                    delcnt = deletecount,
                    delproj = "projects" if deletecount != 1 else "project",
                    )

            # Render a new formset, to get the upgraded info and to not render
            # any recently deleted projects
            form = forms.EditAppFormSet(initial=_get_apps(project))
            return render("deployment/appedit.html", dict(
                form=form,
                project=project,
                message=message,
                failures=failures,
                ), request)
    else:
        form = forms.EditAppFormSet(initial=_get_apps(project))
    return render("deployment/appedit.html", dict(
        form=form,
        project=project,
        ), request)
