from vdi.models import Instance
from vdi.log import log
from django.conf import settings
from django.db.models.query import QuerySet
from vdi import user_tools
from boto.ec2.connection import EC2Connection
from vdi.models import Instance

def create_instance(ami_id):
    '''
    ami_id should be a string containing the EC2 ami to be scaled out
    returns the instance id of the newly created instance
    '''
    ec2 = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
    ami = ec2.get_all_images([ami_id])[0]
    reservation = ami.run(instance_type='m1.large')
    return reservation.instances[0].id

def terminate_instances(dm_instances):
    '''
    dm_instances should be either a django QuerySet of vdi.models.Instance
    '''
    ec2 = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
    ids = [i.instanceId for i in dm_instances]
    if ids:
        terminated = ec2.terminate_instances(ids)
        num_del = len(terminated)
        for item in terminated:
            dbitem = Instance.objects.filter(instanceId=item.id)[0]
            log.debug('The node has been deleted on ec2.  I will now delete %s from the local db' % dbitem.instanceId)
            dbitem.delete()
        return num_del
    return 0

def get_ec2_instances(db_instances):
    '''
    db_instances should be a QuerySet of vdi.model.Instances
    '''
    ec2 = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)

    # Create a list of instance id's
    ids = [i.instanceId for i in db_instances]
    if ids:
        reservations = ec2.get_all_instances(ids) 
    else:
        reservations = []

    # Get the instances from the EC2 List of Reservations
    ec2_instances = []
    for reservation in reservations:
        ec2_instances.extend(reservation.instances)

    #log.debug('c\n%s'%[(i.state,i.id) for i in ec2_instances])
    return ec2_instances
