from vdi.models import Instance
from vdi.log import log
from django.conf import settings
from django.db.models.query import QuerySet
from vdi import user_tools
from boto.ec2.connection import EC2Connection
from vdi.models import Instance

def terminate_instances(dm_instances):
    '''
    dm_instances should be either a django QuerySet of vdi.models.Instance
    '''
    ec2 = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
    ids = [i.instanceId for i in dm_instances]
    if ids:
        num_del = len(ec2.terminate_instances(ids))
        dm_instances.delete()
        return num_del
    return 0

def get_filtered_results(dm_instances):
    '''
    dm_instances should be either a django QuerySet of vdi.models.Instance
    '''
    ec2 = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)

    # Create a list of instance id's
    ids = [i.instanceId for i in dm_instances]
    if ids:
        reservations = ec2.get_all_instances(ids) 
    else:
        reservations = []

    # Get the instances from the EC2 List of Reservations
    ec2_instances = []
    for reservation in reservations:
        ec2_instances.extend(reservation.instances)

    #log.debug('c\n%s'%[(i.state,i.id) for i in ec2_instances])
    for ec2_instance in ec2_instances:
        # Remove desktops in the terminated state.  Other valid states include 'running' and 'pending'
        if ec2_instance.state == "terminated":
            ec2_instances.remove(ec2_instance)
    #log.debug('a\n%s'%[i.state for i in ec2_instances])

    return ec2_instances
