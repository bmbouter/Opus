from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/login', 'django.contrib.auth.views.login'),
    (r'^accounts/logout', 'django.contrib.auth.views.logout'),

    (r'^deployments/', include('opus.project.deployment.urls')),
    (r'^json/', include('opus.project.deployment.jsonurls')),
    (r'^dcmux/', include("opus.project.dcmux.urls")),
    (r'^community/', "opus.project.deployment.views.gwt"),
    (r'^$', 'opus.project.deployment.views.gwt'),
)
