from service.base import BaseService
from model.index import indexModel


class IndexService(BaseService):
    async def test(self):
        return {'a': 'apple', 'xm': 'xiaomi', 'horn': 'huawei'}

    async def db(self):
        sql = '''
        select * from tech_book limit 10;
        '''
        return indexModel.get_bar_sql(sql)


indexService = IndexService()
