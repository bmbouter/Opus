from django.http import HttpResponse, HttpResponseRedirect
from idpauth.models import Role, IdentityProvider
import core
log = core.log.getLogger()

def login(request, username, roles, institution):
    request.session["logged_in"] = True
    request.session["username"] = username
    request.session["roles"] = roles
    request.session["institution"] = institution

def logout(request):
    if "logged_in" in request.session:
        del request.session["logged_in"]
    if "username" in request.session:
        del request.session["username"]
    if "roles" in request.session:
        del request.session["roles"]
    if "institution" in request.session:
        del request.session["institution"]
    request.session.flush()

def is_logged_in(request):
    return "logged_in" in request.session
    
def can_access_image(instance, roles):
    #TODO
    return True

def can_access_instance(instance, roles):
    #TODO
    return True

def get_user_apps(request):
    '''
    Returns a list of applications the user has access to.
    '''
    log.debug("Getting User Apps")
    log.debug(request.session["roles"])
    if not request.session["roles"]:
        return []
    log.debug("Roles = " + str(request.session["roles"]))
    institution = request.session["institution"]
    institutional_IdP = IdentityProvider.objects.filter(institution__iexact=str(institution))
    authentication_type = institutional_IdP[0].type
    log.debug(authentication_type)
    
    if authentication_type == 'ldap':
        log.debug("ldap")
        roles = Role.objects.filter(permissions__in=request.session['roles'])
    else:
        roles = Role.objects.filter(permissions__iexact=request.session['roles'])
    log.debug(str(roles))

    #TODO: Optimize this query
    apps = []
    for role in roles:
        apps += role.applications.all()
    return apps

def login_required(func):
    '''
    A decorator that redirects to the login page if the user isn't logged in.
    Meant to be used on a django view function, hence the first argument being
    "request".
    '''
    def check_func(request, *args, **kwargs):
        if is_logged_in(request):
            return func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/idpauth/login/")
    return check_func
