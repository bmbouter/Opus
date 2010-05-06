from django.db import models
from django.db.models import signals
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from core import log
log = log.getLogger()

class Application(models.Model):
    name = models.CharField(max_length=64) # Pretty name of the application
    image_id = models.CharField(max_length=32, unique=True) # Image id of the image that the actual application lies on
    path = models.CharField(max_length=256,blank=True) # Path of the application to be run on the host
    max_concurrent_instances = models.IntegerField()
    users_per_small = models.IntegerField()
    cluster_headroom = models.IntegerField()
    icon_url = models.URLField()
    ssh_key = models.FileField("SSH Key", upload_to='vdi/sshkeys', blank=True)

    class Meta:
        permissions = (('view_applications','Can View Applications'),)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class Instance(models.Model):
    instanceId = models.CharField(max_length=32, unique=True)
    application = models.ForeignKey('Application')
    priority = models.IntegerField()
    STATUS_CHOICES = (
        (u'1', u'booting'),
        (u'2', u'active'),
        (u'3', u'maintenance'),
        (u'4', u'shutting-down'),
        (u'5', u'deleted'),
    )
    state = models.IntegerField(max_length=2, choices=STATUS_CHOICES, default=1)
    ip = models.IPAddressField(blank=True,null=True)
    startUpDateTime = models.DateTimeField(auto_now=False, auto_now_add=True, editable=False)
    shutdownDateTime = models.DateTimeField(auto_now=False, auto_now_add=True, editable=False, blank=True)

    class Meta:
        unique_together = (("application","priority","state"),)

    def __str__(self):
        return 'Instance(application=%s, instanceId=%s)' % (self.application, self.instanceId)

    def __repr__(self):
        return self.instanceId


######## Signal Handler Functions ############
def create_application_permission(sender, instance, created, **kwargs):
    log.debug("App created")
    if created:
        log.debug('Application created')
        log.debug('Use %s' % instance.name)
        log.debug('vdi.use_%s' % instance.name)
        ct = ContentType.objects.get(model='application')
        log.debug(ct)
        perm = Permission.objects.create(name='Use %s' % instance.name, content_type = ct, codename='use_%s' % instance.name)
        log.debug(perm)

def delete_application_permission(sender, instance, **kwargs):
    perm = Permission.objects.get(codename='vdi.use_%s' % instance.name)
    perm.delete()

######## Signal Declarations  ############
signals.post_save.connect(create_application_permission, sender=Application)
signals.post_delete.connect(delete_application_permission, sender=Application)

