# -*- coding: utf-8 -*-

import tornado.gen
import tornadoredis
import settings

from chat import handlers
from chat.utils import get_random_string

from tornado.web import url, Application as BaseApplication


CONNECTION_POOL = tornadoredis.ConnectionPool(max_connections=500,
                                              wait_for_available=True)


class Redis(tornadoredis.Client):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    def hget(self, key, field):
        hget_func = super(self.__class__, self).hget
        yield tornado.gen.task(hget_func, key, field)

    def hgetall(self, key):
        hgetall_func = super(self.__class__, self).hgetall
        yield tornado.gen.task(hgetall_func, key)

    def hmset(self, key, fields):
        hmset_func = super(self.__class__, self).hmset
        yield tornado.gen.task(hmset_func, key, fields)

    def exists(self, key):
        exists_func = super(self.__class__, self).exists
        yield tornado.gen.task(exists_func, key)

    def zadd(self, key, score, value):
        zadd_func = super(self.__class__, self).zadd
        yield tornado.gen.task(zadd_func, key, score, value)


def get_connection():
    client = Redis(connection_pool=CONNECTION_POOL,
                   host=settings.REDIS_HOST,
                   port=int(settings.REDIS_PORT),
                   selected_db=settings.REDIS_DB)
    client.connect()
    return client


class Application(BaseApplication):

    def __init__(self):
        from os import path

        handlers_routes = [
            url(r"/", handlers.MainHandler),
            url(r"/login", handlers.LoginHandler),
            url(r"/logout", handlers.LogoutHandler),
            url(r"/registration", handlers.RegistrationHandler),
            url(r"/room-manager/(?P<room>[^\/]+)", handlers.RoomManagerHandler),
            url(r"/room/(?P<destination>[^\/]+)", handlers.RoomHandler),
            url(r"/private-message/(?P<destination>[^\/]+)", handlers.PrivateMessageHandler),
            url(r"/websocket/(?P<message_type>[^\/]+)/?(?P<destination>[^\/]+)?",
                handlers.WebSocketHandler),
        ]

        settings = {
            'debug': True,
            'template_path': path.join(path.dirname(__file__), 'templates'),
            'static_path': path.join(path.dirname(__file__), 'static'),
            "cookie_secret": get_random_string(),
            'login_url': '/login',
        }

        super(self.__class__, self).__init__(handlers_routes, **settings)
        self.connection = get_connection()
