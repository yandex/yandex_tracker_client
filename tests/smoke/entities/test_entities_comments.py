# coding: utf-8

import random

import pytest
from common.url import api_url
from common.utils.comments import comment_fields_test, comment_with_attach_test


# comments fixtures:

@pytest.fixture
def mocked_comments(net_mock, fake_entity, mocked_fake_entity):
    net_mock.get(api_url(
        '/entities/{entity_type}/{idx}/comments'.format(entity_type=fake_entity.entity_type, idx=fake_entity.idx)),
        json=fake_entity.comments)

    return list(mocked_fake_entity.comments)


@pytest.fixture
def random_comment_num(fake_entity):
    return random.randint(0, len(fake_entity.comments) - 1)


@pytest.fixture
def mocked_random_comment(net_mock, fake_entity, mocked_comments, random_comment_num):
    fake_comment = fake_entity.comments[random_comment_num]
    net_mock.get(
        api_url('/entity/{entity_type}/{idx}/comments/{comment_id}'.format(entity_type=fake_entity.entity_type,
                                                                           idx=fake_entity.idx,
                                                                           comment_id=fake_comment['id'])),
        json=fake_comment)
    return mocked_comments[random_comment_num]


# tests:
@pytest.mark.parametrize('comment_field', ['text', 'createdBy', 'updatedBy',
                                           'createdAt', 'updatedAt'])
def test_entities_comments_fields(fake_entity, comment_field, mocked_comments, random_comment_num):
    comment_fields_test(fake_entity, mocked_comments, random_comment_num, comment_field)


def test_add_comment_with_attachment(net_mock, mocked_fake_entity, fake_entity,
                                     random_attachment_num):
    net_mock.get(api_url(
        '/entities/{entity_type}/{idx}/attachments/'.format(entity_type=fake_entity.entity_type,
                                                            idx=fake_entity.idx).format(
            fake_entity.idx)), json=fake_entity.attachments)

    new_attachment = fake_entity.attachments[random_attachment_num]
    net_mock.post(
        api_url('/entities/{entity}/{idx}/comments'.format(entity=fake_entity.entity_type, idx=fake_entity.idx))
    )

    comment_with_attach_test(net_mock, new_attachment, mocked_fake_entity, request_index=2)


def test_entities_comment_update(net_mock, fake_entity, mocked_fake_entity, mocked_random_comment, random_comment_num):
    expected_text = 'New text'
    updated_comment = fake_entity.comments[random_comment_num]
    updated_comment['text'] = expected_text
    url = api_url('/entities/{entity_type}/{entity_id}/comments/{comment_id}'.format(
        entity_type=fake_entity.entity_type, entity_id=fake_entity.idx, comment_id=updated_comment['id']))

    net_mock.patch(url, json=updated_comment)
    mocked_random_comment.update(text=expected_text)

    real_request = net_mock.request_history[2].json()
    assert real_request['text'] == expected_text


def test_entities_comment_delete(net_mock, fake_entity, mocked_random_comment, random_comment_num):
    fake_comment = fake_entity.comments[random_comment_num]
    net_mock.delete(api_url('/entities/{entity_type}/{idx}/comments/{comment_id}'.format(
        entity_type=fake_entity.entity_type, idx=fake_entity.idx, comment_id=fake_comment['id'])), status_code=204)

    mocked_random_comment.delete()
