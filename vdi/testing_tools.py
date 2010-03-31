from vdi.models import Instance, Application
from datetime import datetime
from cost_tools import convertToDateTime



def get_nodesInCluster(application, date_time):
    instances = Instances.objects.filter(application=application_pk)
    num_nodes = 0

    for instance in instances:
        if instance.state == 5:
            if instance.startUpDateTime < date_time and instance.shutdownDateTime > date_time:
                num_nodes += 1
        else:
            if instance.startUpDateTime < date_time:
                num_nodes += 1
    return num_nodes


def get_provisioningEventsInDateRange(application, start_date, end_date):
    instances = Instances.objects.filter(application=application_pk)
    num_events = 0

    starting_dateTime = convertToDateTime(start_date)
    ending_dateTime = convertToDateTime(end_date)

    for instance in instances:
        if instance.startUpDateTime > start_date and instance.startUpDateTime < end_date:
            num_events += 1

    return num_events



def get_deprovisioningEventsInDateRange(application, start_date, end_date):
    instances = Instances.objects.filter(application=application_pk)
    num_events = 0

    starting_dateTime = convertToDateTime(start_date)
    ending_dateTime = convertToDateTime(end_date)

    for instance in instances:
        if instance.shutdownDateTime > start_date and instance.shutdownDateTime < end_date:
            num_events += 1

    return num_events

