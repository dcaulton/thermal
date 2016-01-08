import couchdb
import pytest

from thermal.appmodule import create_app, register_db

def drop_and_rebuild_test_database():
    print 'resetting test database'
    from config import TestingConfig
    test_database_name = TestingConfig.COUCHDB_DATABASE
    couch = couchdb.Server()
    try:
        couch.delete(test_database_name)
    except Exception as e:
        pass
    couch.create(test_database_name)

@pytest.fixture(autouse=True, scope='session')
def app(request):
    drop_and_rebuild_test_database()

    app = create_app('testing')
    register_db(app)

    ctx = app.app_context()
    ctx.push()

    def teardown():
        print 'tearing down app'
        ctx.pop()

    request.addfinalizer(teardown)
    return app
