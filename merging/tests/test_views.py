import json
from mock import ANY, call, Mock, patch
import uuid

from flask import current_app, request

import merging.views as mv


class TestViewsUnit(object):

    @patch('merging.views.merge_images_task.delay')
    @patch('merging.views.item_exists')
    def test_call_merge_images_calls_appropriate_methods(self,
                                                         mv_item_exists,
                                                         mv_merge_images_task_delay):
        mv_item_exists.return_value = True

        with current_app.test_client() as c:
            resp_object = c.get('/api/v1/merging/merge_images?img1_id=a&img2_id=b')
#            resp_object = c.get('/api/v1/merging/merge_images')
            call1 = call('a', 'picture')
            call2 = call('b', 'picture')

            mv_item_exists.assert_has_calls([call1, call2])

            call3 = call(img1_primary_id_in='a',
                         img1_alternate_id_in=ANY,
                         img2_id_in='b',
                         img_id_out=ANY,
                         group_id='current')
            mv_merge_images_task_delay.assert_has_calls([call3])

#            import pdb; pdb.set_trace()
            assert resp_object.status_code == 200
            response_data_dict = json.loads(resp_object.data)
            assert 'result_id' in response_data_dict
            assert len(response_data_dict.keys()) == 1
"""
@merging.route('/merge_images')
def call_merge_images():
    '''
    Merges to images into a third one
    '''
    img1_id, img2_id = None, None
    if 'img1_id' in request.args:
        img1_id = request.args.get('img1_id')
    if 'img2_id' in request.args:
        img2_id = request.args.get('img2_id')

    if not item_exists(img1_id, 'picture'):  # TODO add testing for no picture id and invalid picture id
        err_msg = 'Source image 1 not found.  A valid id for a source image must be supplied to this endpoint as a get parameter'\
                  ' named img1_id in order to call this endpoint'
        return Response(json.dumps(err_msg), status=404, mimetype='application/json')

    if not item_exists(img2_id, 'picture'):  # TODO add testing for no picture id and invalid picture id
        err_msg = 'Source image 2 not found.  A valid id for a source image must be supplied to this endpoint as a get parameter'\
                  ' named img2_id in order to call this endpoint'
        return Response(json.dumps(err_msg), status=404, mimetype='application/json')

    result_id = uuid.uuid4()

    merge_images_task.delay(
        img1_primary_id_in=img1_id,
        img1_alternate_id_in=uuid.uuid4(),
        img2_id_in=img2_id,
        img_id_out=result_id,
        group_id='current'
    )
    accept_json = {'result_id': result_id}
    return Response(json.dumps(accept_json), status=202, mimetype='application/json')
"""

