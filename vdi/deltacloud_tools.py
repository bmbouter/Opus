from vdi.models import Instance
import core
log = core.log.getLogger()
from django.conf import settings
from django.db.models.query import QuerySet
from idpauth import user_tools
from vdi.models import Instance

from boto.ec2.connection import EC2Connection

def create_instance(image_id):
    """Creates an given the instance.

    image_id should be a string identifier of the image to be instantiated.
    Returns the instance id of the newly created instance.

    """
    ec2 = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
    ami = ec2.get_all_images([image_id])[0]
    reservation = ami.run(instance_type='m1.large')
    return reservation.instances[0].id

def terminate_instances(instances):
    """Turns off the list of instances given.

    instances should be an iterable of vdi.models.Instance objects, for
    example, a django queryset.  The number of instances that were successfully
    terminated is returned.

    """
    ec2 = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
    ids = [i.instanceId for i in instances]
    if ids:
        terminated = ec2.terminate_instances(ids)
        num_del = len(terminated)
        for item in terminated:
            dbitem = Instance.objects.filter(instanceId=item.id)[0]
            log.debug('The node has been deleted.  I will now move %s into a deleted state' % dbitem.instanceId)
            dbitem.state = 5
            dbitem.save()
        return num_del
    return 0

def get_instances(instances):
    """Return instance objects baised on database model.

    instances should be an iterable of vdi.models.Instance objects, for
    example, a django queryset.

    """
    ec2 = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)

    # Create a list of instance id's
    ids = [i.instanceId for i in instances]
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
