from opus.project.deployment import models
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

def render(templatename, params, request, code=200):
    response = render_to_response(templatename, params,
            context_instance=RequestContext(request))
    response.status_code = code
    return response

@login_required
def list_or_new(request):
    """This view shoudl render a page that displays currently deployed projects
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
    deployments = models.objects.all()
    if not request.user.is_superuser:
        deployments = deployments.filter(owner=request.user)

    return render("list_deployments.html", {
        'deployments': deployments,
        })


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
    pass
