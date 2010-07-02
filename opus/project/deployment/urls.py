from django.conf.urls.defaults import *

# The regex that matches project names in the URL. This needs to be a python
# identifier, since it translates to a python package. It also needs to be
# less than 30 characters or so, since it translates into a system user (this
# is checked in the edit_or_create view to give a better error message)
projectpattern = "[a-zA-Z_][a-zA-Z0-9_]*"

urlpatterns = patterns('opus.project.deployment.views',
        url(r'^$', 'list_or_new'),
        url(r'^(?P<projectname>{0})/$'.format(projectpattern), 'edit_or_create'),
        url(r'^(?P<projectname>{0})/destroy$'.format(projectpattern), 'destroy'),
        url(r'^(?P<projectname>{0})/addapp$'.format(projectpattern), 'addapp'),
        url(r'^(?P<projectname>{0})/delapp$'.format(projectpattern), 'delapp'),
)
