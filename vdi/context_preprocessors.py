from django.conf import settings
from idpauth import user_tools

def context_preprocessor(request):
    d = {
        'vdi_media_dir': settings.VDI_MEDIA_PREFIX,
    }
    if user_tools.is_logged_in(request):
        d['institution'] = request.session['institution']
    return d
