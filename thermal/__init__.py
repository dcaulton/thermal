from .appmodule import create_app, make_celery

app = create_app()
celery = make_celery(app)
