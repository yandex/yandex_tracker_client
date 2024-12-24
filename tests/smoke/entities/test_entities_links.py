# coding: utf-8

import random

import pytest
from common.url import api_url


@pytest.fixture
def mocked_links(net_mock, mocked_fake_entity, fake_entity):
    net_mock.get(
        api_url('/entities/{entity_type}/{idx}/links'.format(entity_type=fake_entity.entity_type, idx=fake_entity.idx)),
        json=fake_entity.links)

    return list(mocked_fake_entity.links)


@pytest.fixture
def random_link_num(fake_entity):
    return random.randint(0, len(fake_entity.links) - 1)


@pytest.fixture
def mocked_random_link(net_mock, fake_entity, mocked_links, random_link_num):
    fake_link = fake_entity.links[random_link_num]
    net_mock.get(
        api_url('/entities/{entity_type}/{idx}/links/{link_id}'.format(entity_type=fake_entity.entity_type,
                                                                       idx=fake_entity.idx, link_id=fake_link['id'])),
        json=fake_link)

    return mocked_links[random_link_num]


@pytest.mark.parametrize('link_field', ['direction', 'object', 'updatedBy',
                                        'createdBy', 'createdAt', 'updatedAt'])
def test_entities_links_fields(fake_entity, link_field, mocked_links, random_link_num):
    comment = mocked_links[random_link_num]
    fake_link = fake_entity.links[random_link_num]

    # expected
    expected_value = (
        fake_link[link_field]['display']
        if isinstance(fake_link[link_field], dict)
        else fake_link[link_field])

    # current
    current_field = getattr(comment, link_field)
    current_value = (
        current_field.display if hasattr(current_field, 'display')
        else current_field)

    assert current_value == expected_value


def test_entities_add_link(net_mock, mocked_fake_entity, fake_entity, mocked_links,
                           random_link_num):
    fake_link = fake_entity.links[random_link_num]

    post_json = {
        "relationship": fake_link['type']['id'],
        "entity": fake_entity.idx
    }

    net_mock.post(
        api_url('/entities/{entity_type}/{idx}/links'.format(entity_type=fake_entity.entity_type, idx=fake_entity.idx)),
        json=post_json, status_code=201)

    mocked_fake_entity.links.create(**post_json)
    real_request = net_mock.request_history[2].json()

    assert all([real_request[k] == post_json[k]
                for k in post_json])


def test_entities_link_delete(net_mock, fake_entity, mocked_random_link,
                              random_link_num):
    fake_link = fake_entity.links[random_link_num]
    net_mock.delete(api_url('/entities/{entity_type}/{idx}/links/{comment_id}'.format(
        entity_type=fake_entity.entity_type, idx=fake_entity.idx, comment_id=fake_link['id'])), status_code=204)

    mocked_random_link.delete()
