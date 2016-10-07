"""
Author: StackFocus
File: forms.py
Purpose: form definitions for the app
"""

from flask_wtf import Form
from wtforms import StringField, PasswordField, SelectField, IntegerField, validators
from wtforms.validators import DataRequired
from postmaster import models
from postmaster.utils import validate_wtforms_password


class LoginForm(Form):
    """ Class for login form on /login
    """
    username = StringField(label='Username', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired(), validate_wtforms_password])
    two_factor = IntegerField(label='2 Factor', validators=(validators.Optional(),))
    auth_source = SelectField('PostMaster User', validators=[DataRequired()])

    @classmethod
    def new(cls):
        # Instantiate the form
        form = cls()
        # Set the default auth_source to local
        form.auth_source.choices = [('PostMaster User', 'PostMaster User')]
        # Check if LDAP is enabled
        ldap_enabled = models.Configs.query.filter_by(setting='Enable LDAP Authentication').first()

        if ldap_enabled is not None and ldap_enabled.value == 'True':
            domain = models.Configs.query.filter_by(setting='AD Domain').first()

            if domain is not None and domain.value is not None:
                # Update the auth_source field to include the LDAP Domain
                form.auth_source.choices = [(domain.value, domain.value), ('PostMaster User', 'PostMaster User')]

        return form
