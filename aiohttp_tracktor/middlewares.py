import base64
import aiohttp_jinja2
from aiohttp import web
from db import get_user_by_name
from security import check_password_hash


async def handle_404(request):
    return aiohttp_jinja2.render_template('404.html', request, {})


async def handle_500(request):
    return aiohttp_jinja2.render_template('500.html', request, {})


def create_error_middleware(overriders):

    @web.middleware
    async def error_middleware(request, handler):
        try:
            response = await handler(request)
            override = overriders.get(response.status)

            if override:
                return await override(request)
            return response

        except web.HTTPError as e:
            override = overriders.get(e.status)
            if override:
                return await override(request)
            raise

    return error_middleware


@web.middleware
async def auth_middleware(request, handler):

    if '/api/' not in request.rel_url.path:
        return await handler(request)

    auth_init = request.headers.get('Authorization', '').replace('Basic ', '')
    if not auth_init:
        raise web.HTTPUnauthorized

    user, password = base64.b64decode(auth_init).decode().split(':')
    async with request.app['db'].acquire() as conn:
        current_user = await get_user_by_name(conn, user)
    if not current_user or not check_password_hash(password, current_user[3]):
        raise web.HTTPUnauthorized

    return await handler(request)


def setup_middlewares(app):
    error_middleware = create_error_middleware({
        404: handle_404,
        500: handle_500
    })
    app.middlewares.append(error_middleware)
    app.middlewares.append(auth_middleware)
