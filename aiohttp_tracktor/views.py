import db
from aiohttp import web
from tracktor import main


async def index(request):
    async with request.app['db'].acquire() as conn:
        result = await db.list_packages(conn, request.query)
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
                    'status_date': None,
                    'update_at': None
                }
                for each in data['packages']
                if not await db.get_package(conn, each['tracking_number'])
            ]
        except KeyError as e:
            raise web.HTTPBadRequest(text='Bad Request!') from e

        if not data_to_insert:
            raise web.HTTPNoContent()

        await db.create_package(conn, data_to_insert)
        raise web.HTTPCreated


async def run_tracktor(request):
    await main(request.app, background=False)
    location = request.app.router['index'].url_for()
    raise web.HTTPFound(location=location)
