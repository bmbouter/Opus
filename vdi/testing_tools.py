from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime

from vdi.models import Instance, Application

import core
log = core.log.getLogger()

from cost_tools import convert_to_date_time
from app_cluster_tools import AppCluster


def get_nodesInCluster(request, app_pk, date_time):
    instances = AppCluster(app_pk).nodes
    date_time = convert_to_date_time(date_time)
    num_nodes = 0

    for instance in instances:
        if instance.state == 5:
            if instance.startUpDateTime < date_time and instance.shutdownDateTime > date_time:
                num_nodes += 1
        else:
            if instance.startUpDateTime < date_time:
                num_nodes += 1
    return HttpResponse(num_nodes)


def get_provisioningEventsInDateRange(request, app_pk, start_date, end_date):
    instances = AppCluster(app_pk).nodes
    num_events = 0

    starting_dateTime = convert_to_date_time(start_date)
    ending_dateTime = convert_to_date_time(end_date)

    for instance in instances:
        if instance.startUpDateTime > starting_dateTime and instance.startUpDateTime < ending_dateTime:
            num_events += 1

    return HttpResponse(num_events)


def get_deprovisioningEventsInDateRange(request, app_pk, start_date, end_date):
    instances = AppCluster(app_pk).deleted
    num_events = 0

    starting_dateTime = convert_to_date_time(start_date)
    ending_dateTime = convert_to_date_time(end_date)

    for instance in instances:
        if instance.shutdownDateTime > starting_dateTime and instance.shutdownDateTime < ending_dateTime:
            num_events += 1

    return HttpResponse(num_events)

