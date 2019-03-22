#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import logging
import traceback
import datetime
import hashlib

from decimal import Decimal
from tornado import web
from service.base import BaseService
from libs import uimethods, utils
from settings import ERR_MSG
from raven.contrib.tornado import SentryMixin
from tornado.options import options
from settings import NotFound

now = datetime.datetime.now
gen_code = lambda i: ''.join([i[-1], i[-5], i[-2], i[-4]])


class BaseHandler(web.RequestHandler, SentryMixin):

    def _get_arguments(self, name, source, strip=True):
        from tornado.util import unicode_type
        values = []
        for v in source.get(name, []):
            v = self.decode_argument(v, name=name)
            if isinstance(v, unicode_type):
                # Get rid of any weird control chars (unless decoding gave
                # us bytes, in which case leave it alone)
                v = web.RequestHandler._remove_control_chars_regex.sub(" ", v)
            if strip:
                v = v.strip()
            values.append(v) if v else None
        return values

    def dict_args(self):
        _rq_args = self.request.arguments
        rq_args = dict([(k, _rq_args[k][0].decode()) for k in _rq_args])
        logging.info(rq_args)
        return rq_args

    def initialize(self):
        BaseService().pdb.close()

    def on_finish(self):
        BaseService().pdb.close()

    def json_format(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(obj, Decimal):
            return ('%.2f' % obj)
        if isinstance(obj, bytes):
            return obj.decode()
        if isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')

    def has_argument(self, name):
        return name in self.request.arguments

    def send_json(self, data={}, errcode=200, errmsg='', status_code=200):
        res = {
            'errcode': errcode,
            'errmsg': errmsg if errmsg else ERR_MSG[errcode]
        }
        res.update(data)

        json_str = json.dumps(res, default=self.json_format, sort_keys=True)
        compare_md5 = hashlib.md5(
            json_str.encode(encoding='utf-8')).hexdigest()
        md5 = self.get_argument('md5', '')
        if md5 and compare_md5 == md5:
            json_str = '{"errcode": 200, "errmsg": "服务正常","md5": "%s"}' % compare_md5
        else:
            json_str = json_str[:-1] + ', "md5": "%s"}' % compare_md5
        # if options.debug:
        #     logging.info('path: %s, arguments: %s, response: %s' % (self.request.path, self.request.arguments, json_str))

        jsonp = self.get_argument('jsonp', '')
        if jsonp:
            jsonp = re.sub(r'[^\w\.]', '', jsonp)
            self.set_header('Content-Type', 'text/javascript; charet=UTF-8')
            json_str = '%s(%s)' % (jsonp, json_str)
        else:
            self.set_header('Content-Type', 'application/json')

        origin = self.request.headers.get("Origin")
        origin = '*' if not origin else origin
        self.set_header("Access-Control-Allow-Origin", origin)
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header('Access-Control-Allow-Headers',
                        'X-Requested-With, Content-Type')
        self.set_header('Access-Control-Allow-Methods',
                        'OPTIONS, GET, POST, PUT, DELETE')

        self.set_status(status_code)
        self.finish(json_str)

    def finish(self, chunk=None):
        """Finishes this response, ending the HTTP request."""
        if self._finished:
            raise RuntimeError("finish() called twice")

        if chunk is not None:
            self.write(chunk)

        if not self._headers_written:
            if (self._status_code == 200 and
                    self.request.method in ("GET", "HEAD") and
                    "Etag" not in self._headers):
                self.set_etag_header()
                if self.check_etag_header():
                    self._write_buffer = []
                    self.set_status(304)
            if self._status_code in (204, 304):
                assert not self._write_buffer, "Cannot send body with %s" % self._status_code
                self._clear_headers_for_304()
            elif "Content-Length" not in self._headers:
                content_length = sum(len(part) for part in self._write_buffer)
                self.set_header("Content-Length", content_length)

        if hasattr(self.request, "connection"):
            self.request.connection.set_close_callback(None)

        self.flush(include_footers=True)
        self.request.finish()
        self._log()
        logging.info('response: %s' % chunk) \
            if chunk and isinstance(chunk, str) else None
        self._finished = True
        self.on_finish()
        self.ui = None

    def write_error(self, status_code=200, **kwargs):
        if 'exc_info' in kwargs:
            err_object = kwargs['exc_info'][1]
            traceback.format_exception(*kwargs['exc_info'])

            if isinstance(err_object, utils.APIError):
                err_info = err_object.kwargs
                self.send_json(**err_info)
                return

        self.send_json(status_code=500, errcode=50001)
        if not options.debug:
            self.captureException(**kwargs)

    def render_err(self, err_title='抱歉，出错了', err_msg='页面不存在'):
        self.render('error.html', err_title=err_title, err_msg=err_msg)

    def render(self, template_name, **kwargs):
        if options.debug:
            logging.info('render args: %s' % kwargs)
        return super(BaseHandler, self).render(template_name, **kwargs)

    def _full_url(self):
        try:
            return self.full_url
        except Exception as e:
            logging.error(e)
            return self.request.full_url()

    def jrender(self, tpl, **kwargs):
        if self.get_argument('js', ''):
            if 'sp' in kwargs:
                kwargs['sp'].pop('password', '')
            self.send_json(kwargs)
        else:
            self.render(tpl, **kwargs)

    def log_sentry(self, data):
        try:
            self.captureMessage(data, stack=True)
        except Exception as e:
            logging.error(e)
            pass

    def send_xml(self, response):
        self.set_header("Content-Type", "application/xml;charset=utf-8")
        self.write(response)
        self.finish()

    async def get(self, *args, **kwargs):
        return self.send_json(NotFound)

    async def post(self, *args, **kwargs):
        return self.send_json(NotFound)

    async def head(self, *args, **kwargs):
        return self.send_json(NotFound)

    async def put(self, *args, **kwargs):
        return self.send_json(NotFound)

    async def delete(self, *args, **kwargs):
        return self.send_json(NotFound)

    async def options(self, *args, **kwargs):
        return self.send_json(NotFound)


class AsyncBaseHandler(BaseHandler):

    async def get(self, method):
        logging.error(method)
        if not method:
            return self.send_json(**NotFound)
        if not hasattr(self, method):
            return self.send_json(**NotFound)
        await getattr(self, method)()

    async def post(self, method):
        if not method:
            return self.send_json(**NotFound)
        if not hasattr(self, '_%s' % method):
            return self.send_json(**NotFound)
        await getattr(self, '_%s' % method)()
