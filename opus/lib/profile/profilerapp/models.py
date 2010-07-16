from django.db import models

class Request(models.Model):
    timestamp = models.DateTimeField()
    uri = models.CharField(max_length=150)
    method = models.CharField(max_length=10)
    responsetime = models.FloatField()
