from . import session_api
import tornado.gen


@session_api()
async def sleep(delay, handler=None):
    await tornado.gen.sleep(delay)


@session_api()
async def moment(handler=None):
    await tornado.gen.moment
