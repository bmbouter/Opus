from django.contrib import admin
from django.contrib.admin import widgets

import models

admin.site.register(models.Instance)
admin.site.register(models.LDAPserver)
admin.site.register(models.Role)
admin.site.register(models.Application)
