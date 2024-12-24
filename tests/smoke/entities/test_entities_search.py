# coding: utf-8

import random

import pytest
from common.url import api_url


@pytest.mark.parametrize('request_params', [
    {'filter': {'status': 'open'}},
    {'filter': {'summary': "fake summary"}},
])
def test_entities_search_request(net_mock, client, fake_entities, request_params):
    entity_type = fake_entities[0].entity_type
    net_mock.post(api_url('/entities/{entity_type}/_search'.format(entity_type=entity_type)), json=fake_entities.json)

    entities = getattr(client, entity_type).find(**request_params)
    real_request = net_mock.request_history[0].json()
    assert all([real_request[k] == request_params[k] for k in request_params])


@pytest.mark.parametrize('entity_field', ['version', 'summary',
                                          'description', 'status',
                                          'createdAt', 'updatedAt',
                                          'createdBy', 'updatedBy',
                                          'shortId'])
def test_entities_search_response(net_mock, client, fake_entities, entity_field):
    entity_type = fake_entities[0].entity_type
    net_mock.post(api_url('/entities/{entity_type}/_search'.format(entity_type=entity_type)), json=fake_entities.json)

    entities = getattr(client, entity_type).find(summary='Simple Title')
    entity_num = random.randint(0, fake_entities.count - 1)

    entity = entities[entity_num]
    fake_entity = fake_entities[entity_num]

    # expected
    expected_value = (
        fake_entity.json[entity_field]['display']
        if isinstance(fake_entity.json[entity_field], dict)
        else fake_entity.json[entity_field]
    )

    # current
    current_field = getattr(entity, entity_field)
    current_value = (
        current_field.display if hasattr(current_field, 'display')
        else current_field)

    assert current_value == expected_value
