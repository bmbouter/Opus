from django.contrib import admin
from django.contrib.admin import widgets
from django.contrib.auth.models import Permission

from idpauth import models

admin.site.register(models.IdentityProviderLocal)
admin.site.register(models.IdentityProviderLDAP)
admin.site.register(models.IdentityProviderOpenID)
admin.site.register(Permission)
