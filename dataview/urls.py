#import dataview.views
from django.conf.urls.defaults import *

urlpatterns = patterns('dataview.views',
    (r'^create/(?P<table_name>\w+)/$','create_service'),
    (r'^tables/$','list_tables'),
    (r'^(?P<table_name>\w+)/(?P<row_key>\w*)/(?P<partition_key>\w*)/$','get_entry'),
    (r'^(?P<table_name>\w+)/insert/$', 'insert'),
    (r'^(?P<table_name>\w+)/$', 'get_all'),
)
