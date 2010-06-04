import re
import tempfile

import opus.lib.builder

from django import forms
from django.forms.fields import *
from django.forms.widgets import *
from django.forms.formsets import formset_factory
from django.core.validators import RegexValidator
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

id_re = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]+$')
validate_identifier = RegexValidator(id_re, u"Enter a valid identifier consisting of letters, numbers, and underscores, not starting with a number.", 'invalid')

class IdentifierField(forms.CharField):
    default_error_messages = {
            'invalid': u"A valid identifier is letters, numbers, and "
            "underscores only. It cannot start with a number."
            }
    default_validators = [validate_identifier]

class ProjectForm(forms.Form):
    projectname = IdentifierField(required=True)
    admin = BooleanField()

class AppForm(forms.Form):
    apppath = CharField(required=True)
    apptype = ChoiceField(
            required=True,
            widget=RadioSelect(),
            choices = (
                ("git", "Git Repository URL"),
                ("file", "Local Filesystem Path"),
            )
        )
AppFormSet = formset_factory(AppForm, extra=2)

def createproject(request):
    if request.method == "POST":
        pform = ProjectForm(request.POST)
        aform = AppFormSet(request.POST)
        if pform.is_valid() and aform.is_valid():

            pb = opus.lib.builder.ProjectBuilder(pform.cleaned_data['projectname'])
            cd = aform.cleaned_data
            for appdata in aform.cleaned_data:
                if not appdata:
                    # That one left blank
                    continue
                source = appdata['apptype']
                pb.add_app(appdata['apppath'], appdata['apptype'])

            if pform.cleaned_data['admin']:
                pb.set_admin_app()
            d = pb.create(settings.OPUS_BASE_DIR)

            return render_to_response('submitted.html', {
                    'path': d,
                    }, context_instance=RequestContext(request))
    else:
        aform = AppFormSet()
        pform = ProjectForm()

    return render_to_response('form.html', {
        'projectform': pform,
        'appform': aform,
        }, context_instance=RequestContext(request))

