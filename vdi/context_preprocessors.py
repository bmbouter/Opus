from django.conf import settings

def context_preprocessor(request):
    d = {
        'vdi_media_dir': settings.VDI_MEDIA_PREFIX,
    }
    if request.user.is_authenticated():
        d['institution'] = request.user.username.split('++')[0]
    return d
