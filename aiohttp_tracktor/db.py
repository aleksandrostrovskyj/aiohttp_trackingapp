import aiomysql.sa
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Date, Enum
)

from utils import Services


meta = MetaData()

package = Table(
    'package_tracking_package', meta,
    Column('id', Integer, primary_key=True),
    Column('tracking_number', String(100), primary_key=True),
    Column('service_name', Enum(Services), nullable=False),
    Column('status_text', String(200), nullable=True),
    Column('status_date', Date, nullable=True)
)


async def init_pg(app):
    conf = app['config']['mysql']
    engine = await aiomysql.sa.create_engine(
        db=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port']
    )
    app['db'] = engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()
