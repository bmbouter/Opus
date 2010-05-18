from django.conf.urls.defaults import *

urlpatterns = patterns('vdi',
    (r'^$', 'views.applicationLibrary'),
    (r'^show_cost$', 'views.show_cost'),
    (r'^(?P<app_pk>(\d)+)/connect$', 'views.connect'),
    (r'^(?P<app_pk>(\d)+)/connect/(?P<conn_type>(nx|nxweb|rdp|rdpweb)+)$', 'views.connect'),
    (r'^calculate_cost/(?P<start_date>(\d{4}-\d{2}-\d{2}[T]\d{2}:\d{2}:\d{2}){1}),(?P<end_date>(\d{4}-\d{2}-\d{2}[T]\d{2}:\d{2}:\d{2}){1})', 'views.calculate_cost'),
    (r'^testing_tools/(?P<app_pk>(\d)+)/clusterSize/(?P<date_time>(\d{4}-\d{2}-\d{2}[T]\d{2}:\d{2}:\d{2}){1})$', 'testing_tools.get_nodesInCluster'),
    (r'^testing_tools/(?P<app_pk>(\d)+)/provEvents/(?P<start_date>(\d{4}-\d{2}-\d{2}[T]\d{2}:\d{2}:\d{2}){1}),(?P<end_date>(\d{4}-\d{2}-\d{2}[T]\d{2}:\d{2}:\d{2}){1})$', 'testing_tools.get_provisioningEventsInDateRange'),
    (r'^testing_tools/(?P<app_pk>(\d)+)/deprovEvents/(?P<start_date>(\d{4}-\d{2}-\d{2}[T]\d{2}:\d{2}:\d{2}){1}),(?P<end_date>(\d{4}-\d{2}-\d{2}[T]\d{2}:\d{2}:\d{2}){1})$', 'testing_tools.get_deprovisioningEventsInDateRange'),
    (r'^user_feedback/', 'views.user_feedback'),
)
