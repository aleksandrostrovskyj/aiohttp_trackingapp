import db
import io
import csv
import aiohttp_jinja2
from aiohttp import web
from aiohttp_session import new_session

from tracktor import main
from utils import login_required
from forms import validate_login_form
from zendesk_report import request_report


async def login(request):
    csrf_token = 'aaaa1'
    if request.method == 'GET':
        return aiohttp_jinja2.render_template('login.html', request, context={'csrf_token': csrf_token})

    if request.method == 'POST':
        form = await request.post()

        async with request.app['db'].acquire() as conn:
            error = await validate_login_form(conn, form, csrf_token)

            if error == 'Invalid csrf_token':
                raise web.HTTPUnauthorized

            if error:
                return aiohttp_jinja2.render_template('login.html', request, context={'error': error})

            user = await db.get_user_by_name(conn, form['username'])

        session = await new_session(request)
        session['user_id'] = user['id']
        return web.HTTPFound(request.app.router['zendesk_report'].url_for())


@login_required
async def index(request):
    async with request.app['db'].acquire() as conn:
        result = await db.list_packages(conn, request.query)
        return web.json_response(result)


@login_required
async def zendesk_request_report(request):
    if request.method == 'GET':
        return aiohttp_jinja2.render_template('zendesk_request_report.html', request, context={})

    if request.method == 'POST':
        form = await request.post()

        report_data = await request_report(form['date_from'], form['date_to'])

        buf = io.StringIO()
        writer = csv.writer(buf, dialect='excel')
        writer.writerows(report_data)
        return web.Response(content_type='text/csv', charset='utf-8',
                            headers={'Content-Disposition': 'Attachment; filename="zendesk_report.csv"'},
                            body=buf.getvalue())


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

        # Remove duplicates element
        [data_to_insert.remove(each) for each in data_to_insert if data_to_insert.count(each) > 1]

        if not data_to_insert:
            raise web.HTTPNoContent()

        await db.create_package(conn, data_to_insert)
        raise web.HTTPCreated


async def run_tracktor(request):
    await main(request.app, background=False)
    location = request.app.router['index'].url_for()
    raise web.HTTPFound(location=location)
