from aiohttp import web
from routes import setup_routes
from db import init_pg, close_pg
from settings import config, BASE_DIR
from middlewares import setup_middlewares
from tracktor import start_background_tasks

app = web.Application()
app['config'] = config
setup_middlewares(app)
setup_routes(app)
app.on_startup.append(init_pg)
app.on_startup.append(start_background_tasks)
app.on_cleanup.append(close_pg)
web.run_app(app)
