##############################################################################
# Copyright 2010 North Carolina State University                             #
#                                                                            #
#   Licensed under the Apache License, Version 2.0 (the "License");          #
#   you may not use this file except in compliance with the License.         #
#   You may obtain a copy of the License at                                  #
#                                                                            #
#       http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                            #
#   Unless required by applicable law or agreed to in writing, software      #
#   distributed under the License is distributed on an "AS IS" BASIS,        #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
#   See the License for the specific language governing permissions and      #
#   limitations under the License.                                           #
##############################################################################

"""This file contains policy types.

======================
Creating a Policy Type
======================
A well made policy type does the following things:
    - Inherits from Policy
    - Implements a function get_next_provider(self, image_id) that returns the
      next provider that should be used to create an instance.
    - Has extra fields (if needed) to help determine the next provider.
    - Registers itself with the admin pannel.  Explained at the bottom of this
      file.
    - Registers a signal that sets the "type" field.  Explained at the bottom
      of this file.
    - Contains documentation and descriptions in places that will be seen in
      the admin panel.
        - Set model metadata fields
        - Use help_text on model fields when needed
    - Sets the app_label to "dcmux" in the Meta class.  This is needed because
      the models are in different files, and django needs to know which app
      they belong to.

"""

from collections import defaultdict

from django.contrib import admin
from django.db.models.signals import pre_save
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from opus.project.dcmux.models import Policy, Provider, Instance, RealImage
from opus.project.dcmux.signals import set_policy_type
import opus.lib.log
log = opus.lib.log.get_logger()


###################### Single Provider Policy ######################

class PolicySingleProvider(Policy):
    """A policy that maps one to one with a provider.

    When an instance is started using this policy, it will always go to the
    provider which is given for the policy.

    """

    # The associated provider
    provider = models.ForeignKey("Provider")

    class Meta:
        app_label = "dcmux"
        verbose_name = "Policy: Single Provider"
        verbose_name_plural = "Policies: Single Provider"

    def get_next_provider(self, image_id):
        return self.provider

###################### Bursting Policy ######################

class PolicyBursting(Policy):
    """Policy that bursts to a different cloud, when one fills up.

    A list of providers and their capacities are given.  And they are looked at
    in the given order.

    """

    providers = models.ManyToManyField(Provider,
            through="PolicyBurstingProviders")

    def get_next_provider(self, image_id):
        try:
            instances = Instance.objects.filter(policy=self).all()
        except ObjectDoesNotExist:
            instances = []
        num_provider_instances = defaultdict(lambda:0)
        for instance in instances:
            num_provider_instances[instance.provider] += 1
        for policyburstingprovider in self.policyburstingproviders_set.all():

            # Check for capacity
            if policyburstingprovider.capacity < 0 or \
                    num_provider_instances[policyburstingprovider.provider] < \
                    policyburstingprovider.capacity:
                provider = policyburstingprovider.provider

                # Make sure there is a matching upstream image
                count = RealImage.objects.filter(provider=provider,
                        downstream_image__id=image_id).count()
                if count >= 1:
                    return policyburstingprovider.provider
                else:
                    #TODO: Return error code
                    log.error('No upstream image found for provider "%s" and ' \
                            'image_id "%s"' % (provider, image_id))

        log.error("No suitable provider found in cloudbursting policy %s." %
                self.id)
        return None #TODO: Return error code

    class Meta:
        app_label = "dcmux"
        verbose_name = "Policy: Bursting"
        verbose_name_plural = "Policies: Bursting"

class PolicyBurstingProviders(models.Model):

    provider = models.ForeignKey(Provider)
    bursting_policy = models.ForeignKey(PolicyBursting)

    order = models.IntegerField()
    capacity = models.IntegerField()

    class Meta:
        app_label = "dcmux"
        ordering = ["order"]
        verbose_name = "Provider"
        verbose_name_plural = "Providers"

class ProvidersInline(admin.TabularInline):
    model = PolicyBurstingProviders

class PolicyBurstingAdmin(admin.ModelAdmin):
    inlines=[
        ProvidersInline,
    ]

############################################


# Register with admin panel
# Every policy type needs to register with the admin panel here in the
# following form:
# >>> admin.site.register(<policy class>)
admin.site.register(PolicySingleProvider)
admin.site.register(PolicyBursting, PolicyBurstingAdmin)

# Register signals
# Every policy type needs to register a signal here in the following form:
# >>> pre_save.connect(Policy.set_policy_type, sender=<policy class>)
pre_save.connect(set_policy_type, sender=PolicySingleProvider)
pre_save.connect(set_policy_type, sender=PolicyBursting)
