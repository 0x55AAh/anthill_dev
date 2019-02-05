from . import session_api
import tornado.gen


@session_api(direct=True)
async def sleep(delay, handler=None):
    await tornado.gen.sleep(delay)


@session_api(direct=True)
async def moment(handler=None):
    await tornado.gen.moment
