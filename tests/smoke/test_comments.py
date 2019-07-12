# coding: utf-8

import string
import random

import pytest
from mock import mock_open, patch

from common.url import api_url


# comments fixtures:

@pytest.fixture
def mocked_comments(net_mock, mocked_fake_issue, fake_issue):
    net_mock.get(api_url('/issues/{}/comments/'.format(fake_issue.key)),
                 json=fake_issue.comments)

    return list(mocked_fake_issue.comments)


@pytest.fixture
def random_comment_num(fake_issue):
    return random.randint(0, len(fake_issue.comments) - 1)


@pytest.fixture
def mocked_random_comment(net_mock, fake_issue, mocked_comments,
                          random_comment_num):
    fake_comment = fake_issue.comments[random_comment_num]
    net_mock.get(
        api_url('/issues/{}/comments/{}'.format(fake_issue.key,
                                                fake_comment['id'])),
        json=fake_comment)

    return mocked_comments[random_comment_num]


# tests:

@pytest.mark.parametrize('comment_field', ['text', 'createdBy', 'updatedBy',
                                           'createdAt', 'updatedAt'])
def test_comments_fields(fake_issue, comment_field, mocked_comments,
                         random_comment_num):
    comment = mocked_comments[random_comment_num]
    fake_comment = fake_issue.comments[random_comment_num]

    #expected
    expected_value = (
        fake_comment[comment_field]['display']
        if isinstance(fake_comment[comment_field], dict)
        else fake_comment[comment_field])

    #current
    current_field = getattr(comment, comment_field)
    current_value = (
        current_field.display if hasattr(current_field, 'display')
        else current_field)

    assert current_value == expected_value


def test_add_comment_with_attachment(net_mock, mocked_fake_issue, fake_issue,
                                     attachments, random_attachment_num):
    new_attachment = fake_issue.attachments[random_attachment_num]

    test_content = ''.join([random.choice(string.ascii_letters)
                            for _ in range(new_attachment['size'])])

    net_mock.post(api_url('/attachments/'.format(fake_issue.key)),
                  json=new_attachment)
    net_mock.post(api_url('/issues/{}/comments/'.format(
        fake_issue.key)))

    m = mock_open(read_data=test_content)

    test_comment_text = 'Test text'
    with patch('yandex_tracker_client.collections.open', m, create=True), \
         patch('requests.utils.os.path.basename',
               return_value='dymmy-file.txt'):
        mocked_fake_issue.comments.create(
            text=test_comment_text,
            attachments=['/dummy-file.txt'])

    real_request = net_mock.request_history[4].json()

    #expected request
    expected_request = {'text': test_comment_text,
                        'attachmentIds': [fake_issue.key]}
    assert any([real_request[k] == expected_request[k]
                for k in expected_request])


def test_comment_update(net_mock, fake_issue, mocked_random_comment,
                        random_comment_num):
    expected_text = 'New text'
    updated_comment = fake_issue.comments[random_comment_num]
    updated_comment['text'] = expected_text

    net_mock.patch(api_url('/issues/{}/comments/{}'.format(
        fake_issue.key, fake_issue.comments[random_comment_num]['id'])),
        json=updated_comment)

    mocked_random_comment.update(text=expected_text)

    real_request = net_mock.request_history[3].json()
    assert real_request['text'] == expected_text


def test_comment_delete(net_mock, fake_issue, mocked_random_comment,
                        random_comment_num):
    fake_comment = fake_issue.comments[random_comment_num]
    net_mock.delete(api_url('/issues/{}/comments/{}'.format(
        fake_issue.key, fake_comment['id'])), status_code=204)

    mocked_random_comment.delete()

    # No need in assert. Just: no exception - test passed.
