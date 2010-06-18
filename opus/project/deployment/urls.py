from django.conf.urls.defaults import *

urlpatterns = patterns('opus.project.deployment.views',
        url(r'^$', 'list_or_new'),
        url(r'^(?P<projectname>[a-xA-Z_][a-zA-Z0-9_]*)$', 'edit_or_create'),
)
