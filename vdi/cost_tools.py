import math
from datetime import datetime
import datetime

import core
log = core.log.getLogger()
from vdi.app_cluster_tools import AppCluster, AppNode
from vdi.models import Instance


def convert_to_date_time(date):
    '''
    Assumes the date comes in the form month-day-yearThour:minute:second
    '''
    year = str(date[0]) + str(date[1]) + str(date[2]) + str(date[3])
    month = str(date[5]) + str(date[6])
    day = str(date[8]) + str(date[9])
    hour = str(date[11]) + str(date[12])
    minute = str(date[14]) + str(date[15])
    second = str(date[17]) + str(date[18])

    new_datetime = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
    return new_datetime

def get_instance_hours_in_date_range(start_date, end_date):
    instances = Instance.objects.exclude(shutdownDateTime__gt=end_date).exclude(startUpDateTime__lt=start_date)
    total_hours = get_total_instance_hours(instances, start_date, end_date)
    
    return (total_hours)

def get_total_instance_hours(instances, start_date, end_date):
    hours_in_time_period = 0

    for instance in instances:
        if instance.state == 5:
            hours_in_time_period += calculate_deleted_node_hours(instance, start_date)
        else:
            hours_in_time_period += calculate_active_node_hours(instance, start_date, end_date)
    return hours_in_time_period

def calculate_deleted_node_hours(instance, start_date):
    if instance.startUpDateTime > start_date:
        hours_in_time_period = instance.shutdownDateTime - instance.startUpDateTime
    else:
        hours_in_time_period = instance.shutdownDateTime - start_date 
    return convert_time_to_hours(hours_in_time_period)

def calculate_active_node_hours(instance, start_date, end_date):
    if instance.startUpDateTime < start_date:
        hours_in_time_period = end_date - start_date
    else:
        hours_in_time_period = end_date - instance.startUpDateTime
    return convert_time_to_hours(hours_in_time_period)

def convert_time_to_hours(time):
    '''
    Time is a timedelta object.
    '''
    days = time.days
    seconds = float(time.seconds)
    hours = float(days*24) + math.ceil(seconds/3600)

    return hours

def generate_cost(hours_used):
    per_hour_charge = 0.48
    cost = hours_used * per_hour_charge
    return cost
