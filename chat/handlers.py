# -*- coding: utf-8 -*-
import time
import tornado.escape
import tornado.gen
import tornado.web
import tornado.websocket


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.connection

    def get_current_user(self):
        return self.get_secure_cookie("user_name")


class MainHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.render('main.html')


class LoginHandler(BaseHandler):

    # TODO: Implement OAUTH
    def get(self):
        from chat.forms.user import LoginForm
        form = LoginForm()
        self.render('login.html', form=form)

    def post(self):
        from chat.forms.user import LoginForm
        data = self.request.arguments
        form = LoginForm(self.db, data)

        if form.validate():
            self.set_secure_cookie("user_name", self.get_argument('user_name'))
            self.redirect("/")
        else:
            self.render('login.html', data=data, form=form)


class RegistrationHandler(BaseHandler):

    def get(self):
        from chat.forms.user import RegistrationForm
        form = RegistrationForm()
        self.render('registration.html', form=form)

    def post(self):
        from chat.forms.user import RegistrationForm
        data = self.request.arguments
        form = RegistrationForm(self.db, data)

        if form.validate():
            id = self.db.incr('k:users')
            hash_user = {
                'id': id,
                'password': form.password.data
            }
            self.db.hmset('user:%s' % form.user_name.data, hash_user)
            self.render('registration.html', form=None)
        else:
            self.render('registration.html', form=form)


class LogoutHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.clear_cookie('user_name')
        self.redirect("/")


class RoomManagerHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, room=None):
        # TODO: Implement room edit
        from chat.forms.room import RoomManagerForm
        form = RoomManagerForm()
        data = {}
        data['rooms'] = self.db.keys('room:*')
        self.render('room-manager.html', form=form, data=data)

    def post(self):
        # hmset room:#room1 owner 'user:root' users "" private 0 active 1
        from chat.forms.room import RoomManagerForm
        form = RoomManagerForm(self.db, self.request.data)
        if form.validate():
            self.redirect('/room-manager')

        self.render('room-manager.html', form=form)

    def put(self):
        from chat.forms.room import RoomManagerForm
        form = RoomManagerForm(self.db, self.request.data)
        if form.validate():
            self.redirect('/room-manager')

        self.render('room-manager.html', form=form)


class RoomHandler(BaseHandler):

    def get_conversation_list():
        pass

    @tornado.web.authenticated
    def get(self, destination):
        from chat.forms.room import MessageForm

        data = {
            'user_name': self.current_user,
            'message': self.get_argument('message', None)
        }
        form = MessageForm()
        form.user_name.data = data['user_name']
        if data['message'] is not None:
            form.validate()

        self.render('room.html', data=data, form=form)


class PrivateMessageHandler(BaseHandler):

    def get_conversation_list():
        pass

    @tornado.web.authenticated
    def get(self):
        from chat.forms.room import MessageForm
        form = MessageForm()
        message = self.get_arguments('message', None)
        if message:
            form = MessageForm(message)
            form.validate()

        data = {}
        self.render('private-message.html', data=data, form=form)


class WebSocketHandler(tornado.websocket.WebSocketHandler):

    MESSAGE_ROOM_TYPE = 'room'
    MESSAGE_USER_TYPE = 'user'

    def _format_destination(self, message_type, destination):
        return '#%s' % destination if message_type == self.MESSAGE_ROOM_TYPE else destination

    @tornado.gen.engine
    def open(self, message_type, destination):
        from app import get_connection
        """ example: open(message_type='room', destination='room1') or
                     open(message_type='user' destination='fred')"""
        if not destination or not message_type:
            self.write_message({'error': 1, 'text': 'Error: No room or user specified'})
            self.close()

        self.connection = get_connection()
        self.destination = self._format_destination(message_type, destination)
        self.message_type = message_type
        yield tornado.gen.Task(self.connection.subscribe, self.destination)
        self.connection.listen(self.on_messages_published)

    def on_messages_published(self, message):
        if message.kind == 'message':
            self.write_message(str(message.body))
        if message.kind == 'disconnect':
            self.close()

    def on_message(self, data):
        """ on_message(data={'from': 'x', 'text': 'y'}) """
        data_decoded = tornado.escape.json_decode(data)
        message = {
            # '_id': '%s' % get_random_string(),
            'from': data_decoded['from'],
            'text': data_decoded['text'],
            'type': self.message_type,
            'to': self.destination,
        }
        message_encoded = tornado.escape.json_encode(message)
        score = self.application.connection.incr('messages:score')
        key = tornado.escape.json_encode('messages:%s:%s:%s' % (message['type'],
                                                                message['from'], message['to']))
        self.application.connection.zadd(key, score, {'text': message['text'], 'timestamp': time.time()})
        self.application.connection.publish(self.destination, message_encoded)
        self.write_message(message)

    def on_close(self):
        if hasattr(self, 'connection') and self.connection.subscribed:
            self.connection.unsubscribe(self.destination)
            self.subscribed = False
