#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from decimal import Decimal
from datetime import datetime, date

def datetime_str(handler, time_obj):
    return time_obj.strftime('%Y-%m-%d %H:%M:%S')

def json_format(handler, res):

    def _format(obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(obj, Decimal):
            return ('%.2f' % obj)
        if isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')

    return json.dumps(res, default=_format)

def date_time_to_date(handler, date_time):
    return datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S').date()

def to_https(handler, url):
    return url.split(':')[-1]

# 根据年月日生成起止日期
def get_datetime(handler, select_type='4', y='', m='', d='', date=''):
    t_date = f_date = ''

    # try:
    # 按年查询
    if select_type == '1':
        f_date = datetime(y, 1, 1)
        t_date = datetime(y, 12, 31, 23, 59, 59)
    # 按月查询
    elif select_type == '2':
        f_date = datetime(y, m, 1)
        t_date = datetime(y, m+1, 1, 23, 59, 59) - datetime.timedelta(1)
    # 按日查询
    elif select_type == '3':
        f_date = datetime(y, m, d)
        t_date = datetime(y, m, d, 23, 59, 59)
    # 查询当天
    elif select_type == '4':
        n = datetime.now()
        f_date = datetime(n.year, n.month, n.day)
        t_date = datetime(n.year, n.month, n.day, 23, 59, 59)
    # 查询指定起止日期
    elif select_type == '5':
        f_date, t_date = date.split(',')
        f_date += ' 00:00:00'
        t_date += ' 23:59:59'
    # except Exception as e:
    #     pass

    return str(f_date), str(t_date)
