#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging

from settings import COMMON_URL
from tornado import web, gen, httpclient
from tornado.httputil import url_concat
from datetime import datetime, date, timedelta

httpclient.AsyncHTTPClient.configure('tornado.simple_httpclient.SimpleAsyncHTTPClient', max_clients=300)

is_fake_id = lambda sp_id: len(str(sp_id)) > 11

to_slist = lambda sp_id: [int(o) for o in str(sp_id).split('_')[1:]]


class APIError(web.HTTPError):
    '''
    自定义API异常
    '''
    def __init__(self, status_code=200, *args, **kwargs):
        super(APIError, self).__init__(status_code, *args, **kwargs)
        self.kwargs = kwargs

def dict_filter(target, attr=()):
    result = dict()
    for p in attr:
        if type(p) is dict:
            key = list(p.keys())[0]
            value = list(p.values())[0]
            result[value] = target[key] if key in target else ''
        elif p in target:
            result[p] = target[p]
    return result

def toNone(va):
    # empty to none
    return None if not va else va

def http_request(url, method='GET', **wargs):
    return httpclient.HTTPRequest(url=url, method=method, connect_timeout=15, request_timeout=15, **wargs)

def get_async_client():
    http_client = httpclient.AsyncHTTPClient()
    return http_client

async def fetch(http_client, request):
    r = await http_client.fetch(request)
    logging.info('\treq_url=%s\trequest_time=%s' % (r.effective_url, r.request_time))
    # logging.info('\tbody=%s' % (r.body))
    return r

async def async_common_api(path, params={}, URL=COMMON_URL):
    url = url_concat(URL + path, params)
    http_client = get_async_client()
    try:
        request = http_request(url)
        response = await fetch(http_client, request)
        response = json.loads(response.body.decode())
        return response
    except Exception as e:
        logging.error('url=%s, error=%s' % (url, e))
        raise APIError(errcode=10001, errmsg='公共接口请求失败')


async def async_post(url, params=None):
    http_client = get_async_client()
    logging.info('\treq_url=%s\tparams=%s' % (url, params))
    try:
        request = http_request(
            url,
            method='POST',
            headers={'content-type': "application/json"},
            body=json.dumps(params, ensure_ascii=False).encode()
        )
        response = await http_client.fetch(request)
        response = json.loads(response.body.decode())
        return response
    except Exception as e:
        logging.error('url=%s  error=%s' % (url, e))
        raise APIError(errcode=50003, errmsg='机器网络信号不良')

def common_api(path, params={}):
    url = url_concat(COMMON_URL+path, params)
    http_client = httpclient.HTTPClient()
    try:
        request = http_request(url)
        response = http_client.fetch(request)
        response = json.loads(response.body.decode())
        return response
    except Exception as e:
        logging.error('url=%s, error=%s'%(url, e))
        raise APIError(errcode=10001, errmsg='公共接口请求失败')
    finally:
        http_client.close()

def common_post_api(path, params={}, host=COMMON_URL):
    url = host+path
    print('----------------------->',url)
    print('----------------------->',params)
    http_client = httpclient.HTTPClient()
    try:
        request = http_request(url, method='POST', body=json.dumps(params))
        response = http_client.fetch(request)
        response = json.loads(response.body.decode())
        return response
    except Exception as e:
        logging.error('url=%s, error=%s'%(url, e))
        raise APIError(errcode=10001, errmsg='公共接口请求失败')
    finally:
        http_client.close()

async def async_fetch_url(url, method='GET', params={}, body={}):
    url = url_concat(url, params)
    client = get_async_client()
    try:
        request = http_request(url, method=method, body=json.dumps(body) if method!='GET' else None)
        response = await client.fetch(request)
        response = json.loads(response.body.decode())
        if isinstance(response, str):
            response = json.loads(response)
        return response
    except Exception as e:
        logging.error('url=%s, method=%s, body=%s, error=%s' % (url, method, body, e))
        raise APIError(errcode=10001, errmsg='接口请求失败')

def is_success_pay(tp, res):

    if int(res['errcode']) != 200:
        return False

    if ((tp=='ali' and
            res['trade_status'] == 'TRADE_SUCCESS') or
        (tp == 'wx' and
            res['return_code'] == 'SUCCESS' and
            res['result_code'] == 'SUCCESS' and
            res['trade_state'] == 'SUCCESS')):
        return True

    return False

def get_week_day(dt):
    week_day_dict = {
        0: '周一',
        1: '周二',
        2: '周三',
        3: '周四',
        4: '周五',
        5: '周六',
        6: '周日',
    }
    day = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S").date().weekday()
    return week_day_dict[day]

def _format_price(price):
    read_package = price.get('read_package', '')
    time_package = price['time_package']
    count_package = price['count_package']
    price['read_package'] = json.loads(read_package) if read_package else []
    price['time_package'] = json.loads(time_package) if time_package else []
    price['count_package'] = json.loads(count_package) if count_package else []
    return price

def getYesterday():
    today=date.today()
    oneday=timedelta(days=1)
    yesterday=today-oneday
    return yesterday
