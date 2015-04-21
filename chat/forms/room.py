# -*_ coding: utf-8 -*-

from wtforms import fields, validators
from wtforms_tornado import Form


class MessageForm(Form):
    # TODO: Implement CSRF protection

    user_name = fields.HiddenField('Username:',
                                   validators=[validators.required('')])
    message = fields.TextField('Message:',
                               validators=[validators.required('please input a message to send')])
    send = fields.SubmitField('send')


class RoomManagerForm(Form):
    # TODO: Implement CSRF protection

    room_name = fields.TextField('Room name:', validators=[
        validators.required('please input a room name')
    ])
    owners = fields.HiddenField('Owners:', validators=[
        validators.required('please input a owner name')
    ])

    def __init__(self, database=None, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.db = database

    def validate_room(self, *args, **kwargs):
        owner = self.db.hget('owner')
        if owner != self.owner.data and owner is not None:
            raise ValueError('The room is already exists')

    def validate(self):
        valid = super(self.__class__, self).validate()
        if not valid:
            return False

        try:
            self.validate_room()
        except ValueError as err:
            self.owners.errors.append(err.message)
            return False

        return True
