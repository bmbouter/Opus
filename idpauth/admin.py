from django.contrib import admin
from django.contrib.auth.models import Permission

from idpauth import models
from idpauth.forms import IdpAdminForm

class IdpAdmin(admin.ModelAdmin):
    form = IdpAdminForm

admin.site.register(models.IdentityProviderLocal, IdpAdmin)
admin.site.register(models.IdentityProviderLDAP, IdpAdmin)
admin.site.register(models.IdentityProviderOpenID, IdpAdmin)
admin.site.register(Permission)
