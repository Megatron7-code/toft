#!/usr/bin/env python
# -*- coding: utf-8 -*-

REDIS = {
    'host': '127.0.0.1',
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

# ratelimit script sha1
RATELIMIT_SHA1 = 'f35e860693f97071c35ec8a68ebf34a3f392f993'