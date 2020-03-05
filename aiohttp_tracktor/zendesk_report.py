import aiomysql
from settings import config


async def request_report(date_from, date_to):
    config_zendesk = config['mysql']
    config_zendesk['db'] = 'zendesk'
    conn = await aiomysql.connect(**config_zendesk, autocommit=True)
    cursor = await conn.cursor()
    await cursor.callproc('zendesk_general_report', (date_from, date_to))

    column_names = [tuple([each[0] for each in cursor.description])]
    column_data = await cursor.fetchall()
    return column_names + list(column_data)
