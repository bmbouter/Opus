from django import forms
from django.core.exceptions import ObjectDoesNotExist

from idpauth.models import IdentityProvider

from core import log
log = log.getLogger()

class IdpAdminForm(forms.ModelForm):
    class Meta:
        model = IdentityProvider

    def clean_institution(self):
        if not self.cleaned_data["institution"].islower():
            institution_lowered = self.cleaned_data["institution"].lower()
            try:
                IdentityProvider.objects.get(institution__iexact=institution_lowered)
                raise forms.ValidationError("Institution \"%s\" exists already" 
                                            % self.cleaned_data["institution"].lower())
            except ObjectDoesNotExist:
                pass
        return self.cleaned_data["institution"].lower()
