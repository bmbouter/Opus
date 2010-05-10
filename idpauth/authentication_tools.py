from django.utils.html import escape
from django.http import get_host
from django.conf import settings

def get_institution(request):
    host_url = get_url_host(request)
    institution = host_url.split('//')[1].split("." + settings.BASE_URL)[0]
    return institution

def get_url_host(request):
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'
    host = escape(get_host(request))
    return '%s://%s' % (protocol, host)

def get_full_url(request):
    return get_url_host(request) + request.get_full_path()

def is_valid_next_url(request, next):
    # When we allow this:
    #   /openid/?next=/welcome/
    # For security reasons we want to restrict the next= bit to being a local 
    # path, not a complete URL.
    absUri = request.build_absolute_uri(next)
    return absUri != next

def get_provider(url):
    
    if str(url).find('google') != -1:
        provider = 'google'
    elif str(url).find('yahoo') != -1:
        provider = 'yahoo'
    else:
        provider = 'unknown'

    return provider

def add_session_username(request, username):
    clean_username = username.split('++')[1]
    request.session['username'] = clean_username
