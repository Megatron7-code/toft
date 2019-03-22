#!/usr/bin/env python
# -*- coding: utf-8 -*-
import redis

from model import pdb
from settings import REDIS


class BaseService(object):

    def __init__(self):
        self.pdb = pdb
        self.rs = self._get_redis_client(REDIS['host'], REDIS['port'])

    def _get_redis_client(self, host, port, password=None):
        print('redis: %s' % host)
        return redis.StrictRedis(host=host, port=port, password=password)

