from django.db import models


class IdentityProvider(models.Model):
    '''
    Identity provider base class.
    '''
    institution = models.CharField(max_length=60, primary_key=True, unique=True)
    name = models.CharField(max_length=60, unique=True)

    TYPE_CHOICES = (
         (u'ldap', u'LDAP'),
         (u'local', u'Local'),
         (u'openid', u'OpenID'),
    )

    type = models.CharField(choices=TYPE_CHOICES,max_length=64, unique=True)
    
    class Meta:
        unique_together = (("institution", "type"),)

    def __str__(self):
        return self.name

class IdentityProviderLDAP(IdentityProvider):
    url = models.CharField("Server Url",max_length=60, unique=True)
    authentication = models.CharField("Authentication Code",max_length=128, unique=True)


    class Meta:
        verbose_name = "LDAP Identity Provider"

class IdentityProviderLocal(IdentityProvider):
    
    class Meta:
        verbose_name = "Local Identity Provider"

class IdentityProviderOpenID(IdentityProvider):
        
    class Meta:
        verbose_name = "OpenID Identity Provider"

class Role(models.Model):
    '''
    Maps an ldap server and role to a number of image which it has access to.
    '''
    name = models.CharField(max_length=60, unique=True)
    idp = models.ForeignKey(IdentityProvider)
    permissions = models.CharField(max_length=128, blank=True)
    resources = models.ManyToManyField('Resource')

    class Meta:
        unique_together = (("idp", "permissions"),)
    
    def __str__(self):
        return self.name

class Resource(models.Model):
    name = models.CharField(max_length=64)
    
    def __str__(self):
        return self.name

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
