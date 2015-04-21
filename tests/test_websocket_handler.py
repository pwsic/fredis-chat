# -*- coding: utf-8 -*-

from chat.app import Application
from tornado import escape, testing, websocket


class TestWebSocketServerHandler(testing.AsyncHTTPTestCase):

    def get_app(self):
        return Application()

    @testing.gen_test
    def test_websocket_send_message_to_room(self):
        client = yield websocket.websocket_connect(url='ws://127.0.0.1:8000/websocket/room/room1')
        encoded_message = escape.json_encode({'from': 'fred', 'text': 'hello room1'})
        client.write_message(encoded_message)
        result = yield client.read_message()
        decoded_result = escape.json_decode(result)

        self.assertEqual(decoded_result['from'], 'fred')
        self.assertEqual(decoded_result['text'], 'hello room1')
        self.assertEqual(decoded_result['to'], '#room1')

    @testing.gen_test
    def test_web_socket_send_message_to_user(self):
        client = yield websocket.websocket_connect(url='ws://127.0.0.1:8000/websocket/user/guest')
        encoded_message = escape.json_encode({'from': 'fred', 'text': 'hello guest'})
        client.write_message(encoded_message)
        result = yield client.read_message()
        decoded_result = escape.json_decode(result)

        self.assertEqual(decoded_result['from'], 'fred')
        self.assertEqual(decoded_result['text'], 'hello guest')
        self.assertEqual(decoded_result['to'], 'guest')
