from .appmodule import create_app, make_celery
#from .appmodule import create_app, make_celery, celery

app = create_app()
celery = make_celery(app)
