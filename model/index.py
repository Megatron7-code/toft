#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, FLOAT, TEXT
from model.base import NotNullColumn, Base, BaseModel
from libs.decorator import tuple_to_dict


class TechBook(Base):
    __tablename__ = 'tech_book'

    id = Column(INTEGER(11), primary_key=True)
    name = NotNullColumn(VARCHAR(255), default='')
    star = NotNullColumn(FLOAT(50), default=0)
    num = NotNullColumn(INTEGER(11), default=0)
    price = NotNullColumn(VARCHAR(255), default='')
    link = NotNullColumn(VARCHAR(255), default='')
    desc = NotNullColumn(TEXT(999), default='')
    tag = NotNullColumn(VARCHAR(255), default='')


class IndexModel(BaseModel):
    @tuple_to_dict
    def get_bar_sql(self, sql=''):
        return self.slave.execute(sql).fetchall()


indexModel = IndexModel()
