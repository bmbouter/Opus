from django.contrib import admin

import models

admin.site.register(models.Provider)
admin.site.register(models.UpstreamImage)
admin.site.register(models.DownstreamImage)
admin.site.register(models.Instance)
admin.site.register(models.SingleProviderPolicy)
