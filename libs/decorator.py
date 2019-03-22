#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import pickle
from sqlalchemy.orm import class_mapper

from service.base import BaseService
from settings import RATELIMIT_SHA1


def model2dict(model):
    if not model:
        return {}
    fields = class_mapper(model.__class__).columns.keys()
    return dict((col, getattr(model, col)) for col in fields)


def model_to_dict(func):
    def wrap(*args, **kwargs):
        ret = func(*args, **kwargs)
        return model2dict(ret)

    return wrap


def models_to_list(func):
    def wrap(*args, **kwargs):
        ret = func(*args, **kwargs)
        return [model2dict(r) for r in ret]

    return wrap


def tuples_first_to_list(func):
    def wrap(*args, **kwargs):
        ret = func(*args, **kwargs)
        return [item[0] for item in ret]

    return wrap


def filter_update_data(func):
    def wrap(*args, **kwargs):
        if 'data' in kwargs:
            data = kwargs['data']
            data = dict([(key, value) for key, value in data.items() if
                         value or value == 0])
            kwargs['data'] = data
        return func(*args, **kwargs)

    return wrap


def tuple_to_dict(func):
    def wrap(*args, **kwargs):
        ret = func(*args, **kwargs)
        return [dict(zip(i.keys(), i.values())) for i in ret]

    return wrap


# 获取redis缓存的装饰器
def redis_cache(prefix, postfix, timeout=60 * 60):
    def __redis_cache(func):
        def warpper(*args, **kw):
            key = prefix % kw.get(postfix, '')
            res = BaseService().rs.get(key)
            if res:
                data = res.decode()
                try:
                    data = eval(data)
                except Exception as e:
                    logging.error(e)
                    data = data
            else:
                data = func(*args, **kw)
                if data:
                    BaseService().rs.set(key, data, timeout)
            return data

        return warpper

    return __redis_cache


# 获取redis缓存的装饰器
def async_redis_cache(prefix, postfixs, timeout=60 * 60):
    def __redis_cache(func):
        async def warpper(*args, **kw):
            key = prefix.format(*[kw.get(postfix, '') for postfix in postfixs])
            res = BaseService().rs.get(key)
            if res:
                data = pickle.loads(res)
            else:
                data = await func(*args, **kw)
                if data:
                    BaseService().rs.set(key, pickle.dumps(data), timeout)
            return data

        return warpper

    return __redis_cache


def split_time(time_str=None):
    line = time_str.split(":")
    seconds = int(line[0]) * 3600 + int(line[1]) * 60 + int(line[2])
    return seconds


# 异步限流策略 2个/2秒
def async_ratelimit(key_str, limit=2, expire=10, sha1=RATELIMIT_SHA1):
    def decorator(func):
        async def wrap(*args, **kw):
            self = args[0]
            mac_id = self.get_argument('mac_id')
            assert mac_id
            key = key_str % (self.__class__.__name__, func.__name__,
                             self.get_argument('mac_id'))
            raw = BaseService().rs.evalsha(sha1, 1, key, limit, expire)
            if raw == 0:
                return self.send_json(errcode=10001, errmsg='访问过于频繁')
            else:
                await func(*args, **kw)

        return wrap

    return decorator


# 限流策略 2个/2秒
def ratelimit(key_str, limit=2, expire=10, sha1=RATELIMIT_SHA1):
    def decorator(func):
        def wrap(*args, **kw):
            self = args[0]
            key = key_str % (self.__class__.__name__, func.__name__,
                             self.get_argument('mac_id'))
            raw = BaseService().rs.evalsha(sha1, 1, key, limit, expire)
            if raw == 0:
                return self.send_json(errcode=10001, errmsg='访问过于频繁')
            else:
                func(*args, **kw)

        return wrap

    return decorator
