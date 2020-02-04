import db
from aiohttp import web
from tracktor import main


async def index(request):
    async with request.app['db'].acquire() as conn:
        result = await db.list_packages(conn)
        return web.json_response(result)


async def create(request):
    async with request.app['db'].acquire() as conn:
        data = await request.json()
        try:
            data_to_insert = [
                {
                    'id': None,
                    'tracking_number': each['tracking_number'],
                    'service_name': each['service_name'],
                    'status_text': None,
                    'status_date': None
                }
                for each in data['packages']
            ]
        except KeyError as e:
            raise web.HTTPBadRequest(text='Bad Request!') from e

        await db.create_package(conn, data_to_insert)
        return web.Response(text='Succes!')


async def run_tracktor(request):
    await main(request.app, background=False)
    location = request.app.router['index'].url_for()
    raise web.HTTPFound(location=location)
