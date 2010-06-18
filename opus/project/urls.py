from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

import opus.project.projectbuilder.views
import opus.project.projectdeployer.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),

    (r'^deployments/', include('opus.project.deployment.urls')),
)
