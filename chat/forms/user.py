# -*_ coding: utf-8 -*-

from wtforms import fields, validators
from wtforms_tornado import Form


class LoginForm(Form):
    # TODO: Implement csrf protection
    # TODO: Implement activation state user validation
    # TODO: Implement password encrypt

    user_name = fields.TextField('Nick Name:',
                                 validators=[validators.required('please input a user_name')])
    password = fields.PasswordField('Password:',
                                    validators=[validators.required('please input a password')])
    submit = fields.SubmitField('ok')

    def __init__(self, database=None, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.db = database

    def validate_password(self, *args, **kwargs):
        password = self.db.hget('user:%s' % self.user_name.data)
        if password != self.password.data:
            raise ValueError('Invalid user name or password')
        yield True

    def validate(self):
        valid = super(self.__class__, self).validate()
        if not valid:
            return False

        try:
            self.validate_password()
        except ValueError as err:
            self.password.errors.append(err.message)
            return False

        return True


class RegistrationForm(Form):
    # TODO: Implement csrf protection
    user_name = fields.TextField('Nick Name:',
                                 validators=[validators.required('Please input a user_name')])
    password = fields.PasswordField(
        'Password',
        validators=[validators.required('Please input a password'),
                    validators.EqualTo('confirm_password', message='Passwords must match')])

    confirm_password = fields.PasswordField('Repeat Password')
    submit = fields.SubmitField('ok')

    def __init__(self, database=None, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.db = database

    def validate_user_name(self):
        exists_user = self.db.exists('user:%s' % self.user_name.data)

        if exists_user:
            raise ValueError('User name is already registrated!')

        yield True

    def validate(self):
        valid = super(self.__class__, self).validate()
        if not valid:
            return False

        try:
            self.validate_user_name()
        except ValueError as err:
            self.user_name.errors.append(err.message)
            return False

        return True


class ResetPasswordForm(Form):
    # TODO implement this
    pass
