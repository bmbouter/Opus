from django import forms
from vdi.models import Instance
from django.contrib.admin import widgets
import datetime

class InstanceForm(forms.ModelForm):
    expire = forms.DateTimeField(label='Expiration Day/Time',widget=widgets.AdminSplitDateTime)
    class Meta:
        model = Instance
        fields = ('expire',)
