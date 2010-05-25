from datetime import datetime

from django.db import models
from django.db.models import signals
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from core import log
log = log.getLogger()

class Application(models.Model):
    name = models.CharField(max_length=64) # Pretty name of the application
    image_id = models.CharField(max_length=32, unique=True) # Image id of the image that the actual application lies on
    path = models.CharField(max_length=256,blank=True) # Path of the application to be run on the host
    max_concurrent_instances = models.IntegerField(default=0)
    users_per_small = models.IntegerField(default=10)
    cluster_headroom = models.IntegerField(default=0)
    icon_url = models.URLField()
    ssh_key = models.FileField("SSH Key", upload_to='vdi/sshkeys')
    scale_interarrival = models.IntegerField(default=180)  # The interarrival time of the scale function running
    to_be_run_at = models.DateTimeField(auto_now_add=True)

    def is_time_to_run(self, last_run_at):
        now = datetime.now()
        return False
        #if to_be_run_at > now

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

class UserExperience(models.Model):
    user = models.ForeignKey(User)
    application = models.ForeignKey(Application)
    access_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    file_presented = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    connection_opened = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    connection_closed = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)

class UserFeedback(models.Model):
    application = models.ForeignKey(Application)
    comment = models.TextField("Please leave any comments", blank=True)
    responsiveness = models.IntegerField()
    load_time = models.IntegerField()

######## Signal Handler Functions ############
def create_application_permission(sender, instance, **kwargs):
    try:
        app = sender.objects.get(pk=instance.id)
        perm = Permission.objects.get(codename='use_%s' % app.name)
        if not instance.name == app.name:
            log.debug("Application being saved - name: " + str(app.name))
            perm.name = 'Use %s' % instance.name
            perm.codename = 'use_%s' % instance.name
            perm.save()
    except ObjectDoesNotExist:
        log.debug("No permission")
        log.debug('Use %s' % instance.name)
        log.debug('vdi.use_%s' % instance.name)
        ct = ContentType.objects.get(model='application')
        perm = Permission.objects.create(name='Use %s' % instance.name, content_type = ct, codename='use_%s' % instance.name)

def delete_application_permission(sender, instance, **kwargs):
    perm = Permission.objects.get(codename='use_%s' % instance.name)
    perm.delete()

######## Signal Declarations  ############
signals.pre_save.connect(create_application_permission, sender=Application)
signals.post_delete.connect(delete_application_permission, sender=Application)
