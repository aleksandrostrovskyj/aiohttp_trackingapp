from views import index, create


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_post('/create', create)
