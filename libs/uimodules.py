#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado import web
from tornado.options import options


class PageModule(web.UIModule):

    def render(self, page, page_total, base_url='', max_display=20):
        return self.render_string('ui-mod/page-module.tpl',
            page=page,
            page_total=page_total,
            base_url=base_url,
            max_display=max_display)


class WithdrawMenuModule(web.UIModule):

    def render(self, action):
        return self.render_string('ui-mod/withdraw-menu-module.tpl', action=action)


class GoogleAnalyticsModule(web.UIModule):

    def render(self, ga_id):
        return self.render_string('ui-mod/ga.tpl', ga_id=ga_id)


class WeixinConsoleModule(web.UIModule):

    def render(self, force_show=False):
        if options.debug or force_show:
            return self.render_string('ui-mod/vconsole.tpl')
        return ''


class BaiduStatModule(web.UIModule):

    def render(self, code):
        return self.render_string('ui-mod/hm.tpl', code=code)
