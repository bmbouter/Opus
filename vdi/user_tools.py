from django.http import HttpResponse, HttpResponseRedirect
from vdi.models import Role, Instance

def login(request, username, ldap, roles):
    request.session["logged_in"] = True
    request.session["username"] = username
    request.session["ldap"] = ldap # Server object.  Not the url
    request.session["roles"] = roles

def logout(request):
    if "logged_in" in request.session:
        del request.session["logged_in"]
    if "username" in request.session:
        del request.session["username"]
    if "ldap" in request.session:
        del request.session["ldap"]
    if "roles" in request.session:
        del request.session["roles"]

def is_logged_in(request):
    return "logged_in" in request.session
    
def can_access_image(instance, roles):
    #TODO
    return True

def can_access_instance(instance, roles):
    #TODO
    return True

def get_user_images(request):
    '''
    Returns a list of images the user has access to.
    '''
    if not request.session["roles"]:
        return []
    print request.session["roles"]
    roles = Role.objects.filter(ldap=request.session['ldap'],
                                name__in=request.session['roles'])
    #TODO: Optimize this query
    images = []
    for role in roles:
        images += role.images.all()
    return images

def get_user_instances(request):
    '''
    Returns a list of the user's instances
    '''
    return Instance.objects.filter(username=request.session['username'],
                                   ldap=request.session['ldap'])

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
            return HttpResponseRedirect("/vdi/ldap_login")
    return check_func
