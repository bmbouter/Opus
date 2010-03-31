import math
from datetime import datetime
import datetime

from vdi.log import log
from vdi.app_cluster_tools import AppCluster, AppNode
from vdi.models import Instance


def convertToDateTime(date):
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

def getInstanceHoursInDateRange(start_date, end_date):
    
    instances = Instance.objects.exclude(shutdownDateTime__lt=start_date).exclude(startUpDateTime__gt=end_date)
    total_hours = get_totalInstanceHours(instances, start_date, end_date)

    return (total_hours)


def get_totalInstanceHours(instances, start_date, end_date):
    
    hoursInTimePeriod = 0

    for instance in instances:
        if instance.state == 5:
            hoursInTimePeriod += calculate_deletedNodeHours(instance, start_date)
        else:
            hoursInTimePeriod += calculate_activeNodeHours(instance, start_date, end_date)
    return hoursInTimePeriod

def calculate_deletedNodeHours(instance, start_date):

    if instance.startUpDateTime > start_date:
        hoursInTimePeriod = instance.shutdownDateTime - instance.startUpDateTime
    else:
        hoursInTimePeriod = instance.shutdownDateTime - start_date 
    return convertTimeToNumberHours(hoursInTimePeriod)

def calculate_activeNodeHours(instance, start_date, end_date):

    if instance.startUpDateTime < start_date:
        hoursInTimePeriod = end_date - start_date
    else:
        hoursInTimePeriod = end_date - instance.startUpDateTime
    return convertTimeToNumberHours(hoursInTimePeriod)

def convertTimeToNumberHours(time):
    '''
    Time is a timedelta object.
    '''
    days = time.days
    seconds = float(time.seconds)
    hours = float(days*24) + math.ceil(seconds/3600)

    return hours

def generateCost(hoursUsed):
    perHourCharge = 0.48
    cost = hoursUsed * perHourCharge
    return cost
