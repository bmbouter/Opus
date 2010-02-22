from django.db import models

class NXNode(models.Model):
    instanceId = models.CharField(max_length=20)
    priority = models.IntegerField()
    ip = models.IPAddressField()

    def __unicode__(self):
        return self.instanceId
