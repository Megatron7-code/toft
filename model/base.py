#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from sqlalchemy import Column, text, func
from functools import partial
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.dialects.mysql import TIMESTAMP, DATETIME
from tornado.util import ObjectDict

from libs import decorator
from model import pdb

from settings import DB_BAR

NotNullColumn = partial(Column, nullable=False, server_default='')


class declare_base(object):
    create_time = NotNullColumn(DATETIME)
    update_time = NotNullColumn(TIMESTAMP,
                                server_default='CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')

    @declared_attr
    def __table_args__(cls):
        return {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8'
        }

    @property
    def to_dict(self):
        return {k: getattr(self, k) for k in self.__table__.columns.keys()}


Base = declarative_base(cls=declare_base)


class DeclareBase(object):
    create_time = NotNullColumn(
        TIMESTAMP,
        server_default=text('CURRENT_TIMESTAMP'),
    )
    update_time = NotNullColumn(
        TIMESTAMP,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
    )

    def __init__(self):
        self.__table__ = None

    @property
    def to_dict(self):
        keys = self.__table__.columns.keys()
        return ObjectDict(zip(keys, (getattr(self, k) for k in keys)))


class BaseModel(object):

    def __init__(self):
        self.pdb = pdb
        self.master = pdb.get_session(DB_BAR, master=True)
        self.slave = pdb.get_session(DB_BAR)

    def fetch_table(self, tb):
        raise Exception

    def exec_sql(self, sql=''):
        self.master.execute(sql)
        self.master.commit()

    def get_bar_sql(self, sql=''):
        return self.slave.execute(sql).fetchall()

    @decorator.tuple_to_dict
    def fetch_sql(self, sql=''):
        return self.slave.execute(sql).fetchall()

    def add_table(self, tb, data, rt=0):
        try:
            tb = self.fetch_table(tb)
            one = tb(**data)
            self.master.add(one)
            self.master.commit()
            return one.to_dict if rt else 1
        except Exception as e:
            logging.error(e)
            self.master.rollback()

    def update_table(self, tb, k, v, data):
        try:
            tb = self.fetch_table(tb)
            q = self.master.query(tb).filter(getattr(tb, k) == v)
            q.update(data)
            self.master.commit()
            self.pdb.close()
        except Exception as e:
            self.master.rollback()
            return e, 0

    def mget(self, tb, filte, limit=None, master=0):
        tb = self.fetch_table(tb)
        q = getattr(self, 'master' if master else 'slave').query(tb)
        for i in filte.keys():
            if hasattr(tb, i) and isinstance(filte[i], (list, tuple)):
                q = q.filter(getattr(tb, i).in_(filte[i]))
            elif hasattr(tb, i) and isinstance(filte[i], (str, int)):
                q = q.filter(getattr(tb, i) == filte[i])
            elif i == 'st':
                q = q.filter(tb.create_time >= filte['st'])
            elif i == 'ed':
                q = q.filter(tb.create_time <= filte['ed'])
            else:
                logging.error(i)
        if limit and limit.get('orderby', ''):
            if limit.get('orderby') == 'create_time':
                q = q.order_by(tb.create_time.desc())
            else:
                q = q.order_by(tb.create_time.desc())
        if not isinstance(limit, dict):
            offset, size = 0, 1
            q = q.offset(offset).limit(size)
        elif limit and limit.get('all'):
            pass
        else:
            size = limit.get('size', 1)
            offset = (limit.get('page', 1) - 1) * size
            q = q.offset(offset).limit(size)
        data = q.all()
        if not data:
            return None
        elif len(data) == 1:
            return [data[0].to_dict]
        else:
            return [i.to_dict for i in data]

    def mcount(self, tb, filte, master=0):
        tb = self.fetch_table(tb)
        q = getattr(self, 'master' if master else 'slave').query(
            func.count('1')).select_from(tb)
        for i in filte.keys():
            if hasattr(tb, i) and isinstance(filte[i], (list, tuple)):
                q = q.filter(getattr(tb, i).in_(filte[i]))
            elif hasattr(tb, i) and isinstance(filte[i], (str, int)):
                q = q.filter(getattr(tb, i) == filte[i])
            else:
                logging.error(i)
        data = q.scalar()
        if not data:
            return None
        else:
            return data
