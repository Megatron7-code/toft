#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pprint
import sys
import uuid
import base64

from tornado import web
from tornado.log import access_log
from tornado.options import options
from libs import uimodules, uimethods
from tornado.httpserver import HTTPServer
from raven.contrib.tornado import AsyncSentryClient

STATIC_PATH = os.path.join(sys.path[0], 'static')
URLS = [
    (r'k\.ktvsky\.com',
     # wow_admin
     (r'/index/?(test|db|tpl)?', 'handler.index.IndexHandler'),
     )
]


class BaseApplication(web.Application):

    def log_request(self, handler):
        if "log_function" in self.settings:
            self.settings["log_function"](handler)
            return
        if handler.get_status() < 400:
            log_method = access_log.info
        elif handler.get_status() < 500:
            log_method = access_log.warning
        else:
            log_method = access_log.error
        request_time = 1000.0 * handler.request.request_time()
        args = [
            "%d  %s  %s  %.2fms \n (%s) \n %s",
            handler.get_status(),
            handler.request.method,
            handler.request.remote_ip,
            request_time,
            handler.request.uri,
            pprint.pformat(handler.request.arguments)]
        if handler.request.method == 'POST' and handler.request.body:
            args[0] += ' \n body: %s'
            args.append(handler.request.body.decode())
        log_method(*args)


class Application(BaseApplication):

    def __init__(self):
        settings = {
            'login_url': '/sp/page/login',
            'xsrf_cookies': False,
            'compress_response': True,
            'debug': options.debug,
            'ui_modules': uimodules,
            'ui_methods': uimethods,
            'static_path': STATIC_PATH,
            'template_path': os.path.join(sys.path[0], 'view'),
            'cookie_secret': base64.b64encode(
                uuid.uuid3(uuid.NAMESPACE_DNS, 'test').bytes),
            'sentry_url': 'http://c6ad070ac58b431e8ab61a42cb4e433c'
                          ':ed47935f502b48a1970f250431790348@wowsentry'
                          '.ktvsky.com/41111' if not options.debug else ''
        }
        web.Application.__init__(self, **settings)
        for spec in URLS:
            host = '.*$'
            handlers = spec[1:]
            self.add_handlers(host, handlers)


def run():
    app = Application()
    app.sentry_client = AsyncSentryClient(app.settings['sentry_url'])
    http_server = HTTPServer(app, xheaders=True)
    http_server.listen(options.port)
    print('Running on port %d' % options.port)
