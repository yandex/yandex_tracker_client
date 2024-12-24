# coding: utf-8

import pytest
from common.url import api_url


def test_entities_attach_create(net_mock, client, fake_entity, mocked_fake_entity):
    with pytest.raises(NotImplementedError):
        mocked_fake_entity.attachments.create()


def test_entities_attach_update(net_mock, client, fake_entity, mocked_fake_entity):
    with pytest.raises(NotImplementedError):
        mocked_fake_entity.attachments.update()


def test_entities_attach_delete(net_mock, client, fake_entity, mocked_fake_entity):
    file_id = 1
    net_mock.delete(api_url(
        '/entities/{entity_type}/{idx}/attachments/{file_id}'.format(entity_type=fake_entity.entity_type,
                                                                     idx=fake_entity.idx, file_id=file_id)),
        status_code=204)
    mocked_fake_entity.attachments.delete(file_id=file_id)


def test_entities_attach(net_mock, client, fake_entity, mocked_fake_entity, attachments):
    attachment = attachments[0]
    net_mock.post(api_url(
        '/entities/{entity_type}/{idx}/attachments/{file_id}'.format(entity_type=fake_entity.entity_type,
                                                                     idx=fake_entity.idx, file_id=attachment.id)),
        json=fake_entity.json)
    mocked_fake_entity.attachments.attach(attachment.id)
