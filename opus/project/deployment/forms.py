import re

from django import forms
from django.forms.fields import *
from django.forms.widgets import *
from django.core.validators import RegexValidator
from django.forms.formsets import formset_factory

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

class DeploymentForm(forms.Form):
    """Form to ask how to deploy a project"""
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
    dbpassword = CharField(required=False, widget=PasswordInput)
    dbhost = CharField(required=False)
    dbport = IntegerField(required=False)
    active = BooleanField(required=False, initial=True)

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

