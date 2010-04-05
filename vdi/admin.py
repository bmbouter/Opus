from django.contrib import admin
from django.contrib.admin import widgets

import models

admin.site.register(models.Instance)
admin.site.register(models.Application)
