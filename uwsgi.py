# -*- coding: utf-8 -*-
# import tornado.httpserver
# import tornado.ioloop
import tornado.wsgi
import wsgiref.simple_server

from chat.app import Application

if __name__ == "__main__":
    wsgi_app = tornado.wsgi.WSGIAdapter(Application)
    server = wsgiref.simple_server.make_server('fredis.dev', 8000, wsgi_app)
    server.serve_forever()
