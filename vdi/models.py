from django.db import models

class Image(models.Model):
    imageId = models.CharField(max_length=32, unique=True) # Amazon ec2 ID
    name = models.CharField(max_length=64)
    os = models.CharField(max_length=32)
    description = models.TextField()

class Instance(models.Model):
    instanceId = models.CharField(max_length=32, unique=True) # Amazon ec2 ID
    ldap = models.ForeignKey('LDAPserver')
    username = models.CharField(max_length=64)

class LDAPserver(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=60, unique=True)
    name = models.CharField(max_length=60, unique=True)
    class Meta:
        verbose_name = "LDAP Server"
        verbose_name_plural = "LDAP Servers"

class Role(models.Model):
    '''
    Maps an ldap server and role to a number of image which it has access to.
    '''
    ldap = models.ForeignKey(LDAPserver)
    name = models.CharField(max_length=128)
    images = models.ManyToManyField(Image)
    class Meta:
        unique_together = (("ldap", "name"),)
