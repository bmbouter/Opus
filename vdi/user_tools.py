from django.http import HttpResponse, HttpResponseRedirect

def login(request, username, ldap, role):
    request.session["logged_in"] = True
    request.session["username"] = username
    request.session["ldap"] = ldap
    request.session["role"] = role

def logout(request):
    if "logged_in" in request.session:
        del request.session["logged_in"]
    if "username" in request.session:
        del request.session["username"]
    if "ldap" in request.session:
        del request.session["ldap"]
    if "role" in request.session:
        del request.session["role"]

def is_logged_in(request):
    return "logged_in" in request.session
    
def can_access_image(request, desktop):
    #TODO
    pass

def can_access_instance(request, instance):
    #TODO
    pass

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
