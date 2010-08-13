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

import re

from django import forms
from django.forms.fields import *
from django.forms.widgets import *
from django.core.validators import RegexValidator
from django.forms.formsets import formset_factory
from django.conf import settings

from opus.lib.log import get_logger
log = get_logger()

id_re = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]+$')
validate_identifier = RegexValidator(id_re, u"Enter a valid identifier consisting of letters, numbers, and underscores, not starting with a number.", 'invalid')
class IdentifierField(forms.CharField):
    default_error_messages = {
            'invalid': u"A valid identifier is letters, numbers, and "
            "underscores only. It cannot start with a number."
            }
    default_validators = [validate_identifier]

class ProjectForm(forms.Form):
    """Form to ask for parameters for the project itself"""
    admin = BooleanField(required=False)

class AppForm(forms.Form):
    """Form to ask for parameters about one app within a project"""
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

class EditAppForm(forms.Form):
    appname = CharField(widget=HiddenInput)
    upgradever = CharField(required=False)

EditAppFormSet = formset_factory(EditAppForm, extra=0, can_delete=True)

class DeploymentForm(forms.Form):
    """Form to ask how to deploy a project.
    
    About the database settings. The choices for the engine may be filtered out
    depending on the Django settings. For SQLite, no other options are
    specified (they are ignored). If configured, a postgres choice for the
    dbengine does not require any other database options. If there is only one
    choice for the database, and it is SQLite or postgres, the other options
    are removed.

    If the keyword argument "noactive" is given to the constructor and is True,
    the activate checkbox will be removed.
    
    """
    superusername = CharField(required=False)
    superpassword = CharField(required=False, widget=PasswordInput)
    superpasswordconfirm = CharField(required=False, widget=PasswordInput)
    superemail = CharField(required=False)
    dbengine = ChoiceField((
            ('sqlite3', 'SQLite'),
            ('postgresql_psycopg2', 'PostgreSQL', ),
            ('mysql', 'MySQL', ),
            ('oracle', 'Oracle', ),
            ))
    dbname = CharField(required=False)
    dbuser = CharField(required=False)
    dbpassword = CharField(required=False, widget=PasswordInput)
    dbhost = CharField(required=False)
    dbport = IntegerField(required=False)
    active = BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        noactive = kwargs.pop("noactive", False)
        forms.Form.__init__(self, *args, **kwargs)

        if noactive:
            del self.fields['active']

        # if there is only one option for the database in
        # settings.OPUS_ALLOWED_DATABASES, remove the dbengine field
        if len(settings.OPUS_ALLOWED_DATABASES) == 1:
            del self.fields['dbengine']
        else:
            # Filter out the choices of dbengine according to
            # settings.OPUS_ALLOWED_DATABASES
            cf = self.fields['dbengine']
            cf.choices = [x for x in cf.choices 
                    if x[0] in settings.OPUS_ALLOWED_DATABASES]

        # Additionally, under these conditions the rest of the database options
        # are not used
        if len(settings.OPUS_ALLOWED_DATABASES) == 1:
            if settings.OPUS_ALLOWED_DATABASES[0] == "sqlite3" or \
                    (settings.OPUS_ALLOWED_DATABASES[0] == \
                     "postgresql_psycopg2" and \
                     settings.OPUS_AUTO_POSTGRES_CONFIG):
                del self.fields['dbname']
                del self.fields['dbuser']
                del self.fields['dbpassword']
                del self.fields['dbhost']
                del self.fields['dbport']


    def full_clean(self):
        forms.Form.full_clean(self)
        if not self._errors and self.is_bound and \
                len(settings.OPUS_ALLOWED_DATABASES) == 1:
            # If there was only 1 choice for dbengine, the field wasn't
            # displayed. To retain compatibility with code that uses this
            # class, insert it into cleaned_data here.
            self.cleaned_data['dbengine'] = \
                    settings.OPUS_ALLOWED_DATABASES[0]

    def clean(self):
        """Does some extra checks:
        If superusername is filled in, makes sure the rest of the superuser
        fields are filled in and the passwords match.

        """
        error = 0
        if self.cleaned_data['superusername']:
            required = ('superpassword', 'superpasswordconfirm', 'superemail')
            for f in required:
                if not self.cleaned_data[f]:
                    self._errors[f] = self.error_class(["This field is required when adding a super user"])
                    error = 1

            if self.cleaned_data['superpassword'] != \
                    self.cleaned_data['superpasswordconfirm']:
                        self._errors['superpasswordconfirm'] = \
                                self.error_class(["Passwords did not match"])
                        error = 1

        if error:
            raise forms.ValidationError("There was a problem adding a super user")
        
        return self.cleaned_data

class UserSettingsForm(forms.BaseForm):
    """A form that generates its fields from the constructor given a list of
    tuples in the form (name, prettyname, type). The type field is either "int"
    or "char".
    """
    base_fields = {}
    def __init__(self, fieldlist, *args, **kwargs):
        forms.BaseForm.__init__(self, *args, **kwargs)

        for name, prettyname, type in fieldlist:
            if type == "int":
                self.fields[name] = forms.IntegerField(label=prettyname)
            elif type == "char":
                self.fields[name] = forms.CharField(label=prettyname)
