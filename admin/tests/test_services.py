from flask import current_app

import admin.services
import conftest


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
