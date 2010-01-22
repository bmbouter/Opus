from django.db import models

class Image(models.Model):
    username = models.CharField(max_length=32)
    imageId = models.CharField(max_length=32)

class Instance(models.Model):
    username = models.CharField(max_length=32)
    instanceId = models.CharField(max_length=32)

class LDAPserver(models.Model):
    url = models.CharField(max_length=60)
    name = models.CharField(max_length=60)

class Permission(models.Model):
    '''
    Maps an ldap server and role to a number of AMI's which it has access to.
    '''
    ldapServer = models.ForeignKey(LDAPserver)
    ldapRole = models.CharField(max_length=32)
    amis = models.ManyToManyField(Image)
