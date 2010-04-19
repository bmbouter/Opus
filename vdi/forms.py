from django import forms
from vdi.models import Instance
from django.contrib.admin import widgets
from datetime import datetime, timedelta
import core
log = core.log.getLogger()
from django.conf import settings

class InstanceForm(forms.ModelForm):

    expire = forms.DateTimeField(label='Expiration Day/Time',widget=widgets.AdminSplitDateTime)

    def clean_expire(self):
        # VALIDATE data WITH THE DATETIME VALIDATIOR
        data = self.cleaned_data['expire']
        # The extra hour is an easy way to correct for DST temporary.
        # TODO: fix daylight savings time hack in the next line
        diff = (data - datetime.now() + timedelta(hours = 1))
        min_res_time_sec = settings.MINIMUM_RESERVATION_LEN * 60
        if diff.days > 0 or diff.days == 0 and diff.seconds >= min_res_time_sec:
            return data
        else:
            raise forms.ValidationError('Reservations Must be at least 15 minutes in the future')

    class Meta:
        model = Instance
        fields = ('expire',)
