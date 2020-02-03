import db
from aiohttp import web
from serializers import serialize
from tracktor import main


async def index(request):
    async with request.app['db'].acquire() as conn:
        cursor = await conn.execute(db.package.select())
        records = await cursor.fetchall()
        packages = [dict(p) for p in records]
        result = [serialize(each) for each in packages]
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

        await conn.execute(db.package.insert(), data_to_insert)
        await conn.execute('commit')
        await main(request.app, background=False)
        return web.Response(text='Succes!')
