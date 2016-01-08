import uuid

from flask import current_app
import pytest 

import admin.services
import conftest
from thermal.exceptions import DocumentConfigurationError, NotFoundError


class TestSettingsIntegration(object):
    def test_get_settings_fetches_a_real_settings_document(self):
        settings_doc = admin.services.get_settings_document()
        assert '_id' in settings_doc.keys()
        assert '_rev' in settings_doc.keys()
        assert 'current_group_id' in settings_doc.keys()
        assert settings_doc['type'] == 'settings'

    def test_settings_points_to_a_real_group_document(self):
        settings_doc = admin.services.get_settings_document()
        group_doc = current_app.db[settings_doc['current_group_id']]
        assert group_doc['type'] == 'group'

    def test_get_settings_creates_new_settings_document_if_document_is_missing(self):
        old_settings_doc = admin.services.get_settings_document()
        old_settings_id = old_settings_doc['_id']
        current_app.db.delete(old_settings_doc)
        new_settings_doc = admin.services.get_settings_document()
        new_settings_id = new_settings_doc['_id']
        assert old_settings_id != new_settings_id

    def test_get_group_document_fails_if_doc_is_not_of_type_group(self):
        the_id = str(uuid.uuid4())
        the_doc = {'type': 'not_group'}
        current_app.db[the_id] = the_doc
        with pytest.raises(NotFoundError):
            the_returned_doc = admin.services.get_group_document(the_id)

    def test_get_group_document_succeeds_if_doc_is_of_type_group(self):
        the_id = str(uuid.uuid4())
        the_doc = {'type': 'group'}
        current_app.db[the_id] = the_doc
        the_returned_doc = admin.services.get_group_document(the_id)
        assert the_returned_doc['_id'] == the_id

    def test_get_group_document_current_gets_the_current_group_document(self):
        settings_doc = admin.services.get_settings_document()

        some_other_group_id = str(uuid.uuid4())
        some_other_group_doc = {'type': 'group'}
        current_app.db[some_other_group_id] = some_other_group_doc

        group_doc_from_current = admin.services.get_group_document('current')

        assert group_doc_from_current['_id'] != some_other_group_id
        assert group_doc_from_current['_id'] == settings_doc['current_group_id']

    def test_save_document_fails_if_document_type_is_being_altered(self):
        the_id = str(uuid.uuid4())
        the_doc = {'_id': the_id, 'type': 'something'}
        current_app.db[the_id] = the_doc
        the_doc['type'] = 'something else'
        with pytest.raises(DocumentConfigurationError):
            admin.services.save_document(the_doc)
