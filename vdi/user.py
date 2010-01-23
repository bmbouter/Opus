from django.http import HttpResponse

def login(request, username, ldap, role):
    request.session["logged_in"] = True
    request.session["username"] = username
    request.session["ldap"] = ldap
    request.session["role"] = role

def logout(request):
    del request.session["logged_in"]
    del request.session["username"]
    del request.session["ldap"]
    del request.session["role"]

def is_logged_in(request):
    return "logged_in" in request.session
    
def can_access_image(request, desktop):
    #TODO
    pass

def can_access_instance(request, instance):
    #TODO
    pass

def require_user(func):
    '''
    A decorator that redirects to the login page if the user isn't logged in.
    Meant to be used on a django view function, hence the first argument being
    "request".
    '''
    def check_func(request, *args, **kwargs):
        if is_logged_in(request):
            return func(request, *args, **kwargs)
        else:
            return HttpResponse("You have to log in.  IN the future, this will be a redirect.")
    return check_func
