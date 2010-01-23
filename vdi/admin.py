from django.contrib import admin

import models

admin.site.register(models.Instance)
admin.site.register(models.Image)
admin.site.register(models.LDAPserver)
admin.site.register(models.Role)
