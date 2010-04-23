from django.conf import settings

def context_preprocessor(request):
    d = {
        'vdi_media_dir': settings.VDI_MEDIA_PREFIX,
    }
    if request.user.is_authenticated():
        institution = request.user.username.split('++')
        if len(institution) == 1:
            institution = 'local'
        else:
            institution = institution[0]
        d['institution'] = institution
    return d
