from django.contrib import admin
from django.contrib.admin import widgets

import models

class ApplicationAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'image_id', 'path', 'icon_url', 'ssh_key']}),
        ('Advanced', {'fields': ['max_concurrent_instances', 'users_per_small', 'cluster_headroom', 'scale_interarrival'], 'classes': ['collapse']}),
    ]

admin.site.register(models.Instance)
admin.site.register(models.Application, ApplicationAdmin)
