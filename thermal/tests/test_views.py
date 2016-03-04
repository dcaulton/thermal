import json
from mock import ANY, call, Mock, patch
import pytest
import uuid

from flask import current_app

import thermal.views as tv


class TestViewsUnit(object):

    def test_index_shows_links(self):
        with current_app.test_client() as c:
            resp_object = c.get('/api/v1/')

            response_data_dict = json.loads(resp_object.data)

            assert resp_object.status_code == 200
            assert 'admin' in response_data_dict
            assert 'pictures' in response_data_dict
            assert 'analysis' in response_data_dict
            assert 'merging' in response_data_dict
            assert 'camera' in response_data_dict
            assert 'docs' in response_data_dict
            assert 'calibration' in response_data_dict
            assert len(response_data_dict.keys()) == 7
