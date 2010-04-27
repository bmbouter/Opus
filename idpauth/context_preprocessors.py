from django.conf import settings
from idpauth import authentication_tools

def context_preprocessor(request):
    d = {
        'opus_media_dir': settings.OPUS_MEDIA_PREFIX,
    }
    '''
    if request.user.is_authenticated():
        institution = request.user.username.split('++')
        if len(institution) == 1:
            institution = 'local'
        else:
            institution = institution[0]
        d['institution'] = institution
    '''
    institution = authentication_tools.get_institution(request)
    if institution != None:
        d['institution'] = institution
        return d
