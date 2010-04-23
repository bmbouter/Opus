from django.db import models, IntegrityError
from django.db.models import signals
from django.contrib.auth.models import Group

from vdi.models import Application

import core
log = core.log.getLogger()

class IdentityProvider(models.Model):
    '''
    Identity provider base class.
    '''
    institution = models.CharField(max_length=60, primary_key=True)
    name = models.CharField(max_length=60, unique=True)
    type = models.CharField(max_length=64, editable=False, blank=True)
    roles = models.ManyToManyField(Group)

    class Meta:
        unique_together = ("type", "institution")
    
    def __str__(self):
        return self.name

class IdentityProviderLDAP(IdentityProvider):
    url = models.CharField("Server Url",max_length=60, unique=True)
    authentication = models.CharField("Authentication Code",max_length=128, unique=True)
    ssl = models.BooleanField("Require SSl Certificate", default=False)

    class Meta:
        verbose_name = "LDAP Identity Provider"

class IdentityProviderLocal(IdentityProvider):
    
    class Meta:
        verbose_name = "Local Identity Provider"

class IdentityProviderOpenID(IdentityProvider):
        
    class Meta:
        verbose_name = "OpenID Identity Provider"

class IdentityProviderShibboleth(IdentityProvider):

    class Meta:
        verbose_name = "Shibboleth Identity Provider"

class Role(models.Model):
    '''
    Maps an ldap server and role to a number of image which it has access to.
    '''
    name = models.CharField(max_length=60, unique=True)
    idp = models.ForeignKey(IdentityProvider)
    permissions = models.CharField(max_length=128, blank=True)
    applications = models.ManyToManyField(Application)

    class Meta:
        unique_together = (("idp", "permissions"),)
    
    def __str__(self):
        return self.name

####### OpenID Required Models ##############
class Nonce(models.Model):
    server_url = models.URLField()
    timestamp  = models.IntegerField()
    salt       = models.CharField( max_length=50 )

    def __unicode__(self):
        return "Nonce: %s" % self.nonce

class Association(models.Model):
    server_url = models.TextField(max_length=2047)
    handle = models.CharField(max_length=255)
    secret = models.TextField(max_length=255) # Stored base64 encoded
    issued = models.IntegerField()
    lifetime = models.IntegerField()
    assoc_type = models.TextField(max_length=64)

    def __unicode__(self):
        return "Association: %s, %s" % (self.server_url, self.handle)


######## Signal Handler Functions ############
def set_identityprovider_type(sender, instance, **kwargs):
    idp_type = sender.__name__.split('IdentityProvider')[1].lower()
    
    instance.institution = instance.institution.lower()

    if idp_type == 'openid':
        instance.type = 'openid'
    elif idp_type == 'local':
        instance.type = 'local'
    elif idp_type == 'ldap':
        instance.type = 'ldap'
    else:
        instance.type = ''

######## Signal Declarations  ############
signals.pre_save.connect(set_identityprovider_type, sender=IdentityProviderOpenID)
signals.pre_save.connect(set_identityprovider_type, sender=IdentityProviderLocal)
signals.pre_save.connect(set_identityprovider_type, sender=IdentityProviderLDAP)
