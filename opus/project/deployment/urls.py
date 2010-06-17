from django.conf.urls.defaults import *

urlpatterns = patterns('opus.project.deployment.views',
        url(r'^$', 'list_or_new'),
        url(r'^(?P<projectname>\d+)$', 'edit_or_create'),
)
