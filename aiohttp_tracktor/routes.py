from views import index, create, run_tracktor, login, zendesk_request_report


def setup_routes(app, project_root):
    app.router.add_get('/login', login, name='login')
    app.router.add_post('/login', login, name='login')
    app.router.add_get('/zendesk/report', zendesk_request_report, name='zendesk_report')
    app.router.add_post('/zendesk/report', zendesk_request_report, name='zendesk_report')
    app.router.add_get('/api/', index, name='index')
    app.router.add_post('/api/tracking/create', create, name='create')
    app.router.add_get('/api/tracking/run_tracktor', run_tracktor, name='run_tracktor')
    app.router.add_static('/static/', path=str(project_root / 'static'), name='static')
