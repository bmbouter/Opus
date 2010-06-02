import re
import tempfile

import opus.lib.builder

from django import forms
from django.forms.fields import *
from django.forms.widgets import *
from django.core.validators import RegexValidator
from django.shortcuts import render_to_response
from django.template import RequestContext

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
    appname = IdentifierField(required=True)
    apppath = CharField(required=True)

def createproject(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():

            pb = opus.lib.builder.ProjectBuilder(form.cleaned_data['projectname'])
            pb.add_app_by_path(form.cleaned_data['apppath'],
                    form.cleaned_data['appname'])
            pb.configure_database(form.cleaned_data['dbengine'],
                    form.cleaned_data['dbname'],
                    form.cleaned_data['dbpassword'],
                    form.cleaned_data['dbhost'], form.cleaned_data['dbport'])
            target = tempfile.mkdtemp(prefix="projectbuilder-",
                    suffix=".deleteme")
            d = pb.create(target)

            return render_to_response('submitted.html', {
                    'path': d,
                    }, context_instance=RequestContext(request))
    else:
        form = ProjectForm()

    return render_to_response('form.html', {
        'formhtml': form
        }, context_instance=RequestContext(request))

