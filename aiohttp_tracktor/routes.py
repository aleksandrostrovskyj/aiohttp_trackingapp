from views import index, create, run_tracktor


def setup_routes(app):
    app.router.add_get('/', index, name='index')
    app.router.add_post('/create', create, name='create'),
    app.router.add_get('/run_tracktor', run_tracktor, name='run_tracktor')

