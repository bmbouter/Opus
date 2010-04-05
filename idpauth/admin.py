from django.contrib import admin
from django.contrib.admin import widgets

import models

admin.site.register(models.IdentityProviderLocal)
admin.site.register(models.IdentityProviderLDAP)
admin.site.register(models.IdentityProviderOpenID)
admin.site.register(models.Role)
