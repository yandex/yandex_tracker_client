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


def test_queue_autoactions_create(net_mock, mocked_fake_queue):
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
    mocked_fake_queue.collection.macros.create(**data)
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
