# coding: utf-8

import pytest
from common.url import api_url

from yandex_tracker_client import exceptions


@pytest.mark.parametrize('entity_field', ['version', 'summary',
                                          'description', 'status',
                                          'createdAt', 'updatedAt',
                                          'createdBy', 'updatedBy',
                                          'shortId'])
def test_entity_fields(client, fake_entity, mocked_fake_entity, entity_field):
    # expected
    expected_value = (
        fake_entity.json[entity_field]['display']
        if isinstance(fake_entity.json[entity_field], dict)
        else fake_entity.json[entity_field])

    # current
    current_field = getattr(mocked_fake_entity, entity_field)
    current_value = (
        current_field.display if hasattr(current_field, 'display')
        else current_field)

    assert current_value == expected_value


def test_entity_not_found(net_mock, client, entity_type):
    net_mock.get(
        api_url('/entities/{entity_type}/{idx}'.format(entity_type=entity_type, idx='1703')),
        status_code=404)
    with pytest.raises(exceptions.NotFound):
        entity = getattr(client, entity_type)['1703']


def test_create_entity(net_mock, client, fake_entity):
    net_mock.post(api_url('/entities/{entity_type}/'.format(entity_type=fake_entity.entity_type)),
                  json=fake_entity.json)
    test_request = {
        'summary': fake_entity.json['summary'],
    }
    getattr(client, fake_entity.entity_type).create(**test_request)
    real_request = net_mock.request_history[0].json()
    assert real_request['summary'] == test_request['summary']


def test_update_entity(net_mock, client, mocked_fake_entity, fake_entity):
    net_mock.patch(
        api_url('/entities/{entity_type}/{idx}'.format(entity_type=fake_entity.entity_type, idx=fake_entity.idx)),
        json=fake_entity.json)

    new_summary = 'New summary'
    mocked_fake_entity.update(summary=new_summary)

    real_request = net_mock.request_history[1].json()
    assert real_request['summary'] == new_summary


def test_entity_bulk_update(net_mock, client, fake_entities):
    entity_type = fake_entities[0].entity_type
    net_mock.post(api_url('/entities/{entity_type}/bulkchange/_update'.format(entity_type=entity_type)))

    meta_entities = [fake_entity.idx for fake_entity in fake_entities]
    values = {"fields": {"summary": "new_summary"}}

    getattr(client, entity_type).bulk_update(meta_entities=meta_entities, values=values)

    real_request = net_mock.request_history[0].json()
    assert set(real_request.get('metaEntities')) == set(meta_entities)
    assert real_request.get('values') == values


def test_entity_get_event_history(net_mock, client, mocked_fake_entity, fake_entity):
    # It is enough to check here that we have reached the URL.
    # In the mock, the query will be in lowercase, and we don't want to make such an assert.
    net_mock.get(
        api_url('/entities/{entity_type}/{idx}/events/_relative'.format(entity_type=fake_entity.entity_type,
                                                                        idx=fake_entity.idx)), json=fake_entity.events
    )
    result = mocked_fake_entity.get_event_history()
    assert result == fake_entity.events


def test_import_entity(net_mock, client, fake_entity):
    import_path = '/v2/entities/{entity_type}/_import'.format(entity_type=fake_entity.entity_type)
    net_mock.post(api_url('/entities/{entity_type}/_import'.format(entity_type=fake_entity.entity_type)),
                  json=fake_entity.json)

    test_request = {
        'createdAt': fake_entity.json['createdAt'],
        'createdBy': fake_entity.json['createdBy'],
        'summary': fake_entity.json['summary'],
        'description': fake_entity.json['description'],
    }

    entity_collection = getattr(client, fake_entity.entity_type)
    entity_collection.import_object(**test_request)
    assert net_mock.request_history[0].path == import_path
    real_request = net_mock.request_history[0].json()
    assert real_request['createdAt'] == test_request['createdAt']
    assert real_request['createdBy'] == test_request['createdBy']
    assert real_request['summary'] == test_request['summary']
    assert real_request['description'] == test_request['description']


def test_entity_extended_permissions(net_mock, client, mocked_fake_entity, fake_entity):
    net_mock.get(
        api_url('/entities/{entity_type}/{idx}/extendedPermissions'.format(
            entity_type=fake_entity.entity_type,
            idx=fake_entity.idx
        )),
        json=fake_entity.extended_permissions
    )
    result = mocked_fake_entity.extended_permissions
    assert result == fake_entity.extended_permissions


def test_entity_update_extended_permissions(net_mock, client, mocked_fake_entity, fake_entity):
    net_mock.patch(
        api_url('/entities/{entity_type}/{idx}/extendedPermissions'.format(
            entity_type=fake_entity.entity_type,
            idx=fake_entity.idx
        )),
        json=fake_entity.extended_permissions
    )

    new_permissions = {
        "acl": {
            "READ": {
                "users": ["newuser"],
                "groups": [2],
            },
            "GRANT": {
                "groups": [2],
                "roles": ["OWNER"],
            },
        },
        "permissionSources": [999],
    }
    mocked_fake_entity.update_extended_permissions(data=new_permissions)

    real_request = net_mock.request_history[1].json()
    assert real_request == new_permissions
