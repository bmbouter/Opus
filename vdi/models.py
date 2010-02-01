from django.db import models

class Image(models.Model):
    imageId = models.CharField(max_length=32, unique=True) # Amazon ec2 ID

    def __str__(self):
        return self.imageId

    def __repr__(self):
        return self.imageId

class Instance(models.Model):
    instanceId = models.CharField(max_length=32, unique=True) # Amazon ec2 ID
    ldap = models.ForeignKey('LDAPserver')
    username = models.CharField(max_length=64)
    expire = models.DateTimeField()

    def __str__(self):
        return 'Instance(instanceId=%s, ldap=%s, username=%s, expire=%s)' % (self.instanceId,self.ldap,self.username,self.expire)

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
    images = models.ManyToManyField(Image)
    PERM_CHOICES = (
        (u'1', u'Use'),
        (u'2', u'Use and Save'),
    )
    permissions = models.IntegerField(max_length=2, choices=PERM_CHOICES, default=2)
    class Meta:
        unique_together = (("ldap", "name"),)
    #TODO: Add __str__()
