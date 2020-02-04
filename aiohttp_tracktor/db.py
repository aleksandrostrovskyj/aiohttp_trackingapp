import aiomysql.sa
from sqlalchemy import (
    MetaData, Table, Column,
    Integer, String, Date, Enum
)
from utils import Services
from serializers import serialize

meta = MetaData()

users = Table(
    'users', meta,

    Column('id', Integer, primary_key=True),
    Column('username', String(50), nullable=False, unique=True),
    Column('email', String(120)),
    Column('password_hash', String(128))
)


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


async def get_user_by_name(conn, username):
    cursor = await conn.execute(users.select().where(users.c.username == username))
    return await cursor.fetchone()


async def list_packages(conn):
    cursor = await conn.execute(package.select())
    records = await cursor.fetchall()
    packages = [dict(p) for p in records]
    return [serialize(each) for each in packages]


async def create_package(conn, data):
    await conn.execute(package.insert(), data)
    await conn.execute('commit')
