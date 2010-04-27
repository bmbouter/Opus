from vdi.models import Instance
import core
log = core.log.getLogger()
from django.conf import settings
from django.db.models.query import QuerySet
from idpauth import user_tools
from vdi.models import Instance

from deltacloud import Deltacloud
deltacloud = Deltacloud(settings.DELTACLOUD_USERNAME,
                        settings.DELTACLOUD_PASSWORD,
                        settings.DELTACLOUD_API_URI)
deltacloud.connect()

def create_instance(image_id):
    """Creates an given the instance.

    image_id should be a string identifier of the image to be instantiated.
    Returns the instance id of the newly created instance.

    """
    image = deltacloud.create_instance(image_id)
    return image.id

def terminate_instances(instances):
    """Turns off the list of instances given.

    instances should be an iterable of vdi.models.Instance objects, for
    example, a django queryset.  The number of instances that were successfully
    terminated is returned.

    """
    num = 0
    for instance in instances:
        dcloud_instance = deltacloud.instance(instance.id)
        if dcloud_instance.stop():
            dbitem = Instance.objects.filter(instanceId=instance.id)[0]
            log.debug('The node has been deleted.  I will now move %s into a deleted state' % dbitem.instanceId)
            dbitem.state = 5
            dbitem.save()
            num += 1
        else:
            log.warning('Could not shut down instance "%s"' % instance.id)
    return num

def get_instances(instances):
    """Return instance objects baised on database model.

    instances should be an iterable of vdi.models.Instance objects, for
    example, a django queryset.

    """
    id_list = []
    for instance in instances:
        id_list.append(instance.instanceId)
    all_instances = deltacloud.instances()
    return filter(lambda x: x.id in id_list, all_instances)
