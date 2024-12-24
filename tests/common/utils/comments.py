import random
import string

from common.url import api_url
from mock import mock_open, patch


def comment_fields_test(obj_with_comments, mocked_comments, random_comment_num, comment_field):
    comment = mocked_comments[random_comment_num]
    fake_comment = obj_with_comments.comments[random_comment_num]

    # expected
    expected_value = (
        fake_comment[comment_field]['display']
        if isinstance(fake_comment[comment_field], dict)
        else fake_comment[comment_field])

    # current
    current_field = getattr(comment, comment_field)
    current_value = (
        current_field.display if hasattr(current_field, 'display')
        else current_field)

    assert current_value == expected_value


def comment_with_attach_test(net_mock, new_attachment, mocked_fake_object, request_index):
    attach_id = new_attachment['id']
    net_mock.post(api_url('/attachments/'.format(attach_id)), json=new_attachment)

    test_content = ''.join([random.choice(string.ascii_letters)
                            for _ in range(new_attachment['size'])])
    m = mock_open(read_data=test_content)

    test_comment_text = 'Test text'
    with patch('yandex_tracker_client.collections.open', m, create=True), \
        patch('requests.utils.os.path.basename',
              return_value='dymmy-file.txt'):
        mocked_fake_object.comments.create(
            text=test_comment_text,
            attachments=['/dummy-file.txt'])

    real_request = net_mock.request_history[request_index].json()

    # expected request
    expected_request = {'text': test_comment_text,
                        'attachmentIds': [attach_id]}
    assert all([real_request[k] == expected_request[k]
                for k in expected_request])
