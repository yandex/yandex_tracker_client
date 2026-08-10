# coding: utf-8
import random

import pytest

from common.url import api_url


@pytest.mark.parametrize('queue_field', ['key', 'version', 'name',
                                         'defaultType', 'defaultPriority',
                                         'department'])
def test_queue_fields(net_mock, client, fake_queue, queue_field):
    net_mock.get(api_url('/queues/' + fake_queue.key), json=fake_queue.json)
    queue = client.queues[fake_queue.key]

    #expected
    expected_value = (
        fake_queue.json[queue_field]['display']
        if isinstance(fake_queue.json[queue_field], dict)
        else fake_queue.json[queue_field])

    #current
    current_field = getattr(queue, queue_field)
    current_value = (
        current_field.display if hasattr(current_field, 'display')
        else current_field)

    assert current_value == expected_value


@pytest.mark.parametrize('queue_field', ['key', 'version', 'name',
                                         'defaultType', 'defaultPriority',
                                         'department'])
def test_get_all_queues(net_mock, client, fake_queues, queue_field):
    net_mock.get(api_url('/queues/'), json=fake_queues.json)
    queues = client.queues.get_all()

    queue_num = random.randint(0, fake_queues.count - 1)

    queue = queues[queue_num]
    fake_queue = fake_queues[queue_num]

    #expected
    expected_value = (
        fake_queue.json[queue_field]['display']
        if isinstance(fake_queue.json[queue_field], dict)
        else fake_queue.json[queue_field])

    #current
    current_field = getattr(queue, queue_field)
    current_value = (
        current_field.display if hasattr(current_field, 'display')
        else current_field)

    assert current_value == expected_value

def test_queue_local_field_create(net_mock, mocked_fake_queue):
    data = {
        "name": {
            "en": "test_name_en",
            "ru": "test_name_ru"
        },
        "id": "testLocalFieldId",
        "category": "000000000000000000000001",
        "type": "ru.yandex.startrek.core.fields.IntegerFieldType",
    }
    net_mock.post(
        api_url('/queues/{queue_key}/localFields/'.format(queue_key=mocked_fake_queue.key)),
    )
    mocked_fake_queue.collection.local_fields.create(**data)
    real_request = net_mock.request_history[1].json()
    assert real_request == data


def test_queue_local_field_update(net_mock, mocked_fake_queue):
    data = {
        "name": {
            "en": "test_name_en_upd",
            "ru": "test_name_ru_upd"
        },
        "description": "test description",
        "order": 100,
    }
    net_mock.patch(
        api_url('/queues/{queue_key}/localFields/testLocalFieldId'.format(queue_key=mocked_fake_queue.key)),
    )
    mocked_fake_queue.collection.local_fields.update_field('testLocalFieldId', **data)
    real_request = net_mock.request_history[1]
    assert real_request.json() == data


def test_queue_local_field_update_uses_queue_scoped_path(net_mock, mocked_fake_queue):
    # The field's own `self` link points at the global /localFields/{id} handle, which serves
    # GET only, so the PATCH has to go to the queue-scoped one addressed by the field key.
    net_mock.patch(
        api_url('/queues/{queue_key}/localFields/testLocalFieldId'.format(queue_key=mocked_fake_queue.key)),
    )
    mocked_fake_queue.collection.local_fields.update_field('testLocalFieldId', order=1)

    real_request = net_mock.request_history[1]
    assert real_request.method == 'PATCH'
    # requests_mock lowercases the path it reports
    assert real_request.path.endswith(
        '/queues/{queue_key}/localfields/testlocalfieldid'.format(queue_key=mocked_fake_queue.key.lower())
    )


def test_queue_autoactions_create__with_filter(net_mock, mocked_fake_queue):
    data = {
        "name": "Test auto action",
        "filter": {
            "priority": ["critical"],
            "status": ["inProgress"],
        },
        "actions": [
            {
                "type": "Transition",
                "status": {
                    "key": "needInfo"
                },
            },
        ],
    }
    net_mock.post(
        api_url('/queues/{queue_key}/autoactions/'.format(queue_key=mocked_fake_queue.key)),
    )
    mocked_fake_queue.collection.autoactions.create(**data)
    real_request = net_mock.request_history[1].json()
    assert real_request == data


def test_queue_autoactions_create__with_query(net_mock, mocked_fake_queue):
    data = {
        "name": "Test auto action",
        "query": "Resolution: resolved AND Status: closed",
        "actions": [
            {
                "type": "Transition",
                "status": {
                    "key": "needInfo"
                },
            },
        ],
    }
    net_mock.post(
        api_url('/queues/{queue_key}/autoactions/'.format(queue_key=mocked_fake_queue.key)),
    )
    mocked_fake_queue.collection.autoactions.create(**data)
    real_request = net_mock.request_history[1].json()
    assert real_request == data


def test_queue_triggers_create(net_mock, mocked_fake_queue):
    data = {
        "name": "TriggerName",
        "actions": [
            {
                "type": "Transition",
                "status": {"key": "open"}
            }
        ],
        "conditions": [
             {
                "type": "CommentFullyMatchCondition",
                "word": "Open"
             }
        ]
    }
    net_mock.post(
        api_url('/queues/{queue_key}/triggers/'.format(queue_key=mocked_fake_queue.key)),
    )
    mocked_fake_queue.collection.triggers.create(**data)
    real_request = net_mock.request_history[1].json()
    assert real_request == data


def test_queue_forms_get(net_mock, mocked_fake_queue):
    net_mock.get(
        api_url('/queues/{}/forms'.format(mocked_fake_queue.key)),
        json=[],
    )
    forms = mocked_fake_queue.forms
    assert forms == []


def test_queue_forms_get_envelope(net_mock, mocked_fake_queue):
    body = {
        'queue': {
            'self': api_url('/queues/{}'.format(mocked_fake_queue.key)),
            'id': 39619,
            'key': mocked_fake_queue.key,
            'display': 'Test queue',
        },
        'forms': [
            {'id': 173454, 'name': 'Form A', 'path': 'surveys/173454'},
        ],
        'version': 2,
        'showDefaultCreationForm': False,
    }
    net_mock.get(
        api_url('/queues/{}/forms'.format(mocked_fake_queue.key)),
        json=body,
    )
    forms = mocked_fake_queue.forms
    assert len(forms) == 1
    assert forms[0]['id'] == 173454
    assert forms[0]['name'] == 'Form A'


def test_queue_forms_get_list_with_self(net_mock, mocked_fake_queue):
    from yandex_tracker_client.objects import Resource

    net_mock.get(
        api_url('/queues/{}/forms'.format(mocked_fake_queue.key)),
        json=[
            {
                'self': api_url('/queues/{}/forms/173454'.format(mocked_fake_queue.key)),
                'id': 173454,
                'name': 'Form A',
            },
        ],
    )
    forms = mocked_fake_queue.forms
    assert len(forms) == 1
    assert isinstance(forms[0], Resource)
    assert forms[0].id == 173454


def test_queue_show_default_creation_form_false(net_mock, mocked_fake_queue):
    net_mock.get(
        api_url('/queues/{}/forms'.format(mocked_fake_queue.key)),
        json={
            'queue': {
                'self': api_url('/queues/{}'.format(mocked_fake_queue.key)),
                'key': mocked_fake_queue.key,
            },
            'forms': [{'id': 173454, 'name': 'Form A'}],
            'version': 2,
            'showDefaultCreationForm': False,
        },
    )
    assert mocked_fake_queue.show_default_creation_form is False


def test_queue_show_default_creation_form_true(net_mock, mocked_fake_queue):
    net_mock.get(
        api_url('/queues/{}/forms'.format(mocked_fake_queue.key)),
        json={
            'queue': {'key': mocked_fake_queue.key},
            'forms': [],
            'version': 0,
            'showDefaultCreationForm': True,
        },
    )
    assert mocked_fake_queue.show_default_creation_form is True


def test_queue_show_default_creation_form_defaults_true(net_mock, mocked_fake_queue):
    # Absent flag (e.g. bare list response) is treated as "form available".
    net_mock.get(
        api_url('/queues/{}/forms'.format(mocked_fake_queue.key)),
        json=[],
    )
    assert mocked_fake_queue.show_default_creation_form is True


def test_queue_macros_create(net_mock, mocked_fake_queue):
    data = {
        "name": "Test macro",
        "body": "Test comment\n{{currentDateTime}}\n{{issue.author}}",
        "issueUpdate": [
            {
                "field": {"id": "tags"},
                "update": {"add": ["tag 1", "tag 2"]}
            }
        ]
    }
    net_mock.post(
        api_url('/queues/{queue_key}/macros/'.format(queue_key=mocked_fake_queue.key)),
    )
    mocked_fake_queue.collection.macros.create(**data)
    real_request = net_mock.request_history[1].json()
    assert real_request == data


def test_queue_update_permissions(net_mock, client, mocked_fake_queue):
    permissions_data = {
        "create": {
            "users": ["user1"]
        },
        "write": {
            "users": {
                "add": ["user2"],
                "remove": ["user3"]
            },
            "groups": {
                "add": [4]
            },
            "roles": {
                "add": ["author", "assignee"]
            }
        },
        "read": {
            "groups": {
                "add": [4]
            },
            "roles": {
                "add": ["follower"]
            }
        },
        "grant": {
            "users": {
                "remove": ["username3", "username4"]
            }
        }
    }

    net_mock.patch(
        api_url('/queues/{}/permissions'.format(mocked_fake_queue.key)),
        json={"version": 11}
    )

    client.queues.update_permissions(mocked_fake_queue, permissions_data)

    real_request = net_mock.request_history[1].json()
    assert real_request == permissions_data
