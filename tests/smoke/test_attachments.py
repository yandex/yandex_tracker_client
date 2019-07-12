# coding: utf-8

import string
import random

import pytest
from six.moves import range
from mock import mock_open, patch

from common.url import api_url


@pytest.mark.parametrize('attachment_field', ['name', 'content', 'createdBy',
                                              'createdAt', 'mimetype', 'size'])
def test_attachments_fields(fake_issue, attachment_field, attachments,
                            random_attachment_num):
    attachment = attachments[random_attachment_num]
    fake_attachment = fake_issue.attachments[random_attachment_num]

    #expected
    expected_value = (
        fake_attachment[attachment_field]['display']
        if isinstance(fake_attachment[attachment_field], dict)
        else fake_attachment[attachment_field])

    #current
    current_field = getattr(attachment, attachment_field)
    current_value = (
        current_field.display if hasattr(current_field, 'display')
        else current_field)

    assert current_value == expected_value


def test_attachments_download(net_mock, open_mock, fake_issue, attachments,
                              random_attachment_num):
    attachment = attachments[random_attachment_num]

    attachment_content = ''.join(
        [random.choice(string.ascii_letters) for _ in range(attachment.size)])
    net_mock.get(attachment.content, text=attachment_content)
    net_mock.get(attachment.self,
                 json=fake_issue.attachments[random_attachment_num])

    attachment.download_to('dummy_dir/')

    handle = open_mock()
    handle.write.assert_called_with(attachment_content.encode())


def test_attachment_upload(net_mock, mocked_fake_issue, fake_issue,
                           attachments, random_attachment_num):
    attachment = fake_issue.attachments[random_attachment_num]

    test_content = ''.join([random.choice(string.ascii_letters)
                            for _ in range(attachment['size'])])

    net_mock.post(api_url('/issues/{}/attachments/'.format(fake_issue.key)))

    m = mock_open(read_data=test_content)

    with patch('yandex_tracker_client.collections.open', m, create=True), \
            patch('requests.utils.os.path.basename',
                  return_value='dymmy-file.txt'):
        mocked_fake_issue.attachments.create('/dummy-file.txt')

    assert test_content in net_mock.request_history[3].text


def test_attachment_delete(net_mock, mocked_fake_issue, fake_issue,
                           random_attachment_num):
    attachment = fake_issue.attachments[random_attachment_num]

    net_mock.get(api_url('/issues/{}/attachments/{}'.format(
        fake_issue.key, attachment['id'])), json=attachment)
    net_mock.delete(api_url('/issues/{}/attachments/{}'.format(
        fake_issue.key, attachment['id'])), status_code=204)

    mocked_fake_issue.attachments[attachment['id']].delete()

    # No need in assert. Just: no exception - test passed.
