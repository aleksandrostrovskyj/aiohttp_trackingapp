import base64
from aiohttp import web
from cryptography import fernet
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

import jinja2
import aiohttp_jinja2
from routes import setup_routes
from db import init_pg, close_pg
from settings import config, BASE_DIR
from middlewares import setup_middlewares
from tracktor import start_background_tasks


app = web.Application()

fernet_key = fernet.Fernet.generate_key()
secret_key = base64.urlsafe_b64decode(fernet_key)
setup(app, EncryptedCookieStorage(secret_key, max_age=300))

app['config'] = config
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(str(BASE_DIR / 'aiohttp_tracktor' / 'templates')))
setup_middlewares(app)
setup_routes(app, BASE_DIR)
app.on_startup.append(init_pg)
app.on_startup.append(start_background_tasks)
app.on_cleanup.append(close_pg)
web.run_app(app)
