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
    - Registers itself with the admin pannel.  Explained at the bottom of this file.
    - Registers a signal that sets the "type" field.  Explained at the bottom
      of this file.
    - Contains documentation and descriptions in places that will be seen in
      the admin panel.
        - Set model metadata fields
        - Use help_text on model fields
    - Sets the app_label to "dcmux" in the Meta class.  This is needed because
      the models are in different files, and django needs to know which app
      they belong to.

"""

from django.contrib import admin
from django.db.models.signals import pre_save
from django.db import models

from opus.project.dcmux.models import Policy
from opus.project.dcmux.signals import set_policy_type

class SingleProviderPolicy(Policy):
    """A policy that maps one to one with a provider.

    When an instance is started using this policy, it will always go to the
    provider which is given for the policy.

    """

    # The associated provider
    provider = models.ForeignKey("Provider")

    class Meta:
        app_label = "dcmux"
        verbose_name = "Single provider policy"
        verbose_name_plural = "Single provider policies"

    def get_next_provider(self, image_id):
        return self.provider


# Register with admin panel
# Every policy type needs to register with the admin panel here in the
# following form:
# >>> admin.site.register(<policy class>)
admin.site.register(SingleProviderPolicy)

# Register signals
# Every policy type needs to register a signal here in the following form:
# >>> pre_save.connect(Policy.set_policy_type, sender=<policy class>)
pre_save.connect(set_policy_type, sender=SingleProviderPolicy)
