# coding: utf-8

import random
import string

import pytest
from common.url import api_url
from common.utils.comments import comment_fields_test, comment_with_attach_test


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
def test_issues_comments_fields(fake_issue, comment_field, mocked_comments, random_comment_num):
    comment_fields_test(fake_issue, mocked_comments, random_comment_num, comment_field)


def test_add_comment_with_attachment(net_mock, mocked_fake_issue, fake_issue,
                                     attachments, random_attachment_num):
    new_attachment = fake_issue.attachments[random_attachment_num]
    net_mock.post(api_url('/issues/{}/comments/'.format(fake_issue.key)))

    comment_with_attach_test(net_mock, new_attachment, mocked_fake_issue, request_index=4)


def test_issues_comment_update(net_mock, fake_issue, mocked_random_comment,
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


def test_issues_comment_delete(net_mock, fake_issue, mocked_random_comment,
                        random_comment_num):
    fake_comment = fake_issue.comments[random_comment_num]
    net_mock.delete(api_url('/issues/{}/comments/{}'.format(
        fake_issue.key, fake_comment['id'])), status_code=204)

    mocked_random_comment.delete()

    # No need in assert. Just: no exception - test passed.
