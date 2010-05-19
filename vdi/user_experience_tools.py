import math
from datetime import datetime
import time
#import datetime

import core
log = core.log.getLogger()

from vdi.models import UserExperience


def get_all_user_wait_times(application):
    user_experience = UserExperience.objects.filter(application=application)
    
    wait_times = []
    for ue in user_experience:
        wait_times.append(convert_timedelta_to_seconds(ue.file_presented - ue.access_date))

    return wait_times

def get_user_applications_in_date_range(user, start_date, end_date):
    user_experience = UserExperience.objects.filter(user=user, access_date__gte=start_date).filter(access_date__lte=end_date)
    log.debug(user_experience)
    apps = []
    for ue in user_experience:
        apps.append(ue.application)

    return apps

def get_application_service_times(application):
    user_experience = UserExperience.objects.filter(application=application)
    
    service_times = []
    for ue in user_experience:
        service_times.append(convert_timedelta_to_seconds(ue.connection_closed - ue.file_presented))

    return service_times

def get_user_application_arrival_times(application):
    user_experience = UserExperience.objects.filter(application=application)
    
    access_times = []
    for ue in user_experience:
        access_times.append(ue.access_date)

    return access_times

def get_concurrent_users(application, date_time):
    log.debug("DATETIME = " + str(date_time))
    user_experience = UserExperience.objects.filter(application=application, file_presented__lte=date_time).filter(connection_closed__gt=date_time)
    
    return len(user_experience)

def get_concurrent_users_over_date_range(application, start_date, end_date, resolution):
    start_date_seconds = time.mktime(start_date.timetuple())
    end_date_seconds = time.mktime(end_date.timetuple())
    num_timestamps = (end_date_seconds - start_date_seconds)/resolution

    concurrent_users = []
    for i in range(0, num_timestamps):
        concurrent_users.append(get_concurrent_users(application, datetime.fromtimestamp(start_date_seconds + i*resolution)))
        
    return concurrent_users
    

def convert_timedelta_to_seconds(timedelta):
    seconds = timedelta.days * 86400 + timedelta.seconds
    return seconds

def process_user_connections(app_node):
    user_experience = UserExperience.objects.exclude(connection_closed__isnull=False)
    log.debug("Users who have not closed connections and/or opened connections are: " + str(user_experience))
    for user_exp in user_experience:
        for session in app_node.sessions:
            log.debug(session['username'])
            log.debug(user_exp.user.username.split('++')[1].split('@')[0])
            if user_exp.user.username.split('++')[1].split('@')[0] == session['username']:
                if user_exp.connection_opened == None:
                    log.debug("Setting the connection_opened parameter")
                    user_exp.connection_opened = datetime.today()
                    user_exp.save()
                    log.debug("Connection opened after setting is: " + str(user_exp.connection_opened))
                user_experience = user_experience.exclude(user=user_exp.user)
        log.debug(user_experience)
                
    user_experience = user_experience.exclude(connection_opened__isnull=True)
    for user_exp in user_experience:
        user_exp.connection_closed = datetime.today()
        user_exp.save()
        log.debug("Connection closed was set to: " + str(user_exp.connection_closed))
    
