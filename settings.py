#!/usr/bin/env python
# -*- coding: utf-8 -*-

# redis
import logging

REDIS = {
    'host': '10.9.36.222',
    'port': 6379
}

# mysql
DB_BAR = 'douban'
MYSQL = {
    DB_BAR: {
        'master': {
            'host': '127.0.0.1',
            'user': 'root',
            'pass': 'wangfei66',
            'port': 3306
        },
        'slaves': [
            {
                'host': '127.0.0.1',
                'user': 'root',
                'pass': 'wangfei66',
                'port': 3306
            },
            {
                'host': '127.0.0.1',
                'user': 'root',
                'pass': 'wangfei66',
                'port': 3306
            }
        ]
    },
}

ERR_MSG = {
    200: '服务正常',
    10001: '请求参数错误',
    10002: '门店未设置计费方式',
    10020: '机器未登记',
    18000: '请申请有效的账号',
    18001: '需要重置密码',
    18002: '重置密码失败',
    18003: '您在绑定非法机器，或该机器不在您名下',
    18004: '账号或者密码有误',
    19003: '下单失败',
    19004: '查单失败',
    19005: '关单失败',
    19006: '订单未支付',
    40004: '无数据',
    50001: '系统错误',
    50002: '非法请求'
}

# time
A_MINUTE = 60
A_HOUR = 3600
A_DAY = 24 * A_HOUR

# ratelimit script sha1
RATELIMIT_SHA1 = 'f35e860693f97071c35ec8a68ebf34a3f392f993'


COMMON_URL = ''

NotFound = dict(status_code=404, errcode=404, errmsg='Not Found')


# try to load debug settings
try:
    from tornado.options import options

    if options.debug:
        exec(compile(open('settings.debug.py', encoding='utf8')
                     .read(), 'settings.debug.py', 'exec'))
except Exception as e:
    logging.error(e)
    pass
