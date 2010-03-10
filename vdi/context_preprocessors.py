from django.conf import settings
from vdi import user_tools

def context_preprocessor(request):
    d = {
        'vdi_media_dir': settings.VDI_MEDIA_PREFIX,
    }
    if user_tools.is_logged_in(request):
        d['ldap_object'] = request.session['ldap']
        d['school_name'] = request.session['ldap'].name.lower()
    return d
