#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


@click.group()
def cli():
    pass


@cli.command()
def runserver():
    from chat.app import Application
    click.echo('Running tornado http server')
    http_server = HTTPServer(Application())
    http_server.listen(8000)
    IOLoop.instance().start()


if __name__ == '__main__':
    cli()
