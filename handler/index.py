from handler.base import AsyncBaseHandler
from service.index import indexService

class IndexHandler(AsyncBaseHandler):

    async def test(self):
        return self.send_json(dict(data=await indexService.test()))

    async def db(self):
        return self.send_json(dict(data=await indexService.db()))

    async def tpl(self):
        return self.jrender('error.html',
                            err_title='test',
                            err_info='test info'
                            )
