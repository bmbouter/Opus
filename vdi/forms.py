from django import forms
from django.forms import RadioSelect
from django.conf import settings
from django.contrib.admin import widgets
from django.utils.safestring import mark_safe

from datetime import datetime, timedelta

from vdi.models import Instance, UserFeedback
import core
log = core.log.getLogger()

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

class HorizRadioRenderer(forms.RadioSelect.renderer):
    def render(self):
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))

class UserFeedbackForm(forms.ModelForm):
    feedback_choices = (
        (u'1', u'1'),
        (u'2', u'2'),
        (u'3', u'3'),
        (u'4', u'4'),
        (u'5', u'5'),
    )
    responsiveness = forms.IntegerField(label="How fast did you feel the application responded to your actions? (1 being slow and 5 being fast)", widget=forms.RadioSelect(renderer=HorizRadioRenderer, choices=feedback_choices))
    load_time = forms.IntegerField(label="How long did you feel the wait time to load your application was? (1 being too long and 5 being fast)", widget=forms.RadioSelect(renderer=HorizRadioRenderer, choices=feedback_choices))

    class Meta:
        model = UserFeedback
