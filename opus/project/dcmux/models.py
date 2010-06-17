from django.db import models

from opus.lib.prov.deltacloud import Deltacloud

class Provider(models.Model):
    """Models a deltacloud provider

    uri -- a valid URI entry point for this provider
    username -- username to use with this provider
    password -- password to use with this provider

    """

    uri = models.URLField()
    username = models.CharField(max_length=60)
    password = models.CharField(max_length=60)

    def get_dc_client(self):
        """Returns a deltacloud client object configured for this provider"""

        return Deltacloud(self.username, self.password, self.uri)
