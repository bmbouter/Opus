from django.db import models

class Application(models.Model):
    name = models.CharField(max_length=64) # Pretty name of the application
    ec2ImageId = models.CharField(max_length=32, unique=True) # Amazon ec2 ID
    path = models.CharField(max_length=256,blank=True) # Path of the application to be run on the host
    max_concurrent_instances = models.IntegerField()
    users_per_small = models.IntegerField()
    cluster_headroom = models.IntegerField()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class Instance(models.Model):
    instanceId = models.CharField(max_length=32, unique=True) # Amazon ec2 ID
    ldap = models.ForeignKey('LDAPserver')
    application = models.ForeignKey('Application')
    priority = models.IntegerField()
    STATUS_CHOICES = (
        (u'1', u'booting'),
        (u'2', u'active'),
        (u'3', u'maintenance'),
        (u'3', u'shutting-down'),
    )
    state = models.IntegerField(max_length=2, choices=STATUS_CHOICES, default=1)
    ip = models.IPAddressField(blank=True,null=True)

    class Meta:
        unique_together = (("application","priority"),)

    def __str__(self):
        return 'Instance(instanceId=%s, ldap=%s)' % (self.instanceId, self.ldap)

    def __repr__(self):
        return self.instanceId

class LDAPserver(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=60, unique=True)
    name = models.CharField(max_length=60, unique=True)
    class Meta:
        verbose_name = "LDAP Server"
        verbose_name_plural = "LDAP Servers"

    def __str__(self):
        return self.name

class Role(models.Model):
    '''
    Maps an ldap server and role to a number of image which it has access to.
    '''
    ldap = models.ForeignKey(LDAPserver)
    name = models.CharField(max_length=128)
    applications = models.ManyToManyField(Application)
    PERM_CHOICES = (
        (u'1', u'Use'),
        (u'2', u'Use and Save'),
    )
    permissions = models.IntegerField(max_length=2, choices=PERM_CHOICES, default=2)
    class Meta:
        unique_together = (("ldap", "name"),)
    #TODO: Add __str__()
