from django.db import models

class Image(models.Model):
    username = models.CharField(max_length=32)
    imageId = models.CharField(max_length=32, unique=True)

class Instance(models.Model):
    username = models.CharField(max_length=32)
    instanceId = models.CharField(max_length=32, unique=True)

class LDAPserver(models.Model):
    url = models.CharField(max_length=60, unique=True)
    name = models.CharField(max_length=60, unique=True)
    class Meta:
        verbose_name = "LDAP Server"
        verbose_name_plural = "LDAP Servers"

class Role(models.Model):
    '''
    Maps an ldap server and role to a number of AMI's which it has access to.
    '''
    ldapServer = models.ForeignKey(LDAPserver)
    ldapRole = models.CharField(max_length=32)
    amis = models.ManyToManyField(Image)
    class Meta:
        unique_together = (("ldapServer", "ldapRole"),)
