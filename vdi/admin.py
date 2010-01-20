from djangoSite.vdi.models import ImageLibrary, Instance, LDAPservers
from django.contrib import admin

admin.site.register(Instance)
admin.site.register(ImageLibrary)
admin.site.register(LDAPservers)
