from enum import Enum
import db
from aiohttp import web
from aiohttp_session import get_session


class Services(Enum):
    UPS = 'UPS'
    USPS = 'USPS'


def login_required(func):
    async def wrapper(request, *args, **kwargs):
        app = request.app
        router = app.router

        session = await get_session(request)
        if 'user_id' not in session:
            return web.HTTPFound(router['login'].url_for())

        user_id = session['user_id']
        async with request.app['db'].acquire() as conn:
            user = await db.get_user_by_id(conn, user_id)

        app['user'] = user

        return await func(request, *args, **kwargs)

    return wrapper
