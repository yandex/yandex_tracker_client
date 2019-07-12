# coding: utf-8
import time

import pytest

from common.url import api_url


@pytest.mark.parametrize('queue_field', ['createdBy', 'createdAt', 'status',
                                         'statusText', 'executionChunkPercent',
                                         'executionIssuePercent'])
def test_bulkchange_fields(net_mock, client, fake_bulkchange, queue_field):
    net_mock.get(api_url('/bulkchange/' + fake_bulkchange.key),
                 json=fake_bulkchange.json)

    bulkchange = client.bulkchange[fake_bulkchange.key]
    current_field = getattr(bulkchange, queue_field)
    current_value = (
        current_field.display if hasattr(current_field, 'display')
        else current_field)

    expected_value = (
        fake_bulkchange.json[queue_field]['display']
        if isinstance(fake_bulkchange.json[queue_field], dict)
        else fake_bulkchange.json[queue_field])

    assert current_value == expected_value


def test_bulkchange_update(net_mock, client, fake_bulkchange):
    net_mock.post(api_url('/bulkchange/_update'), json=fake_bulkchange.json)

    client.bulkchange.update(['TEST-1', 'TEST-2'], priority='minor',
                             tags={'add': ['bulktag']})
    real_request = net_mock.request_history[0].json()
    expected_request = {
        'issues': ['TEST-1', 'TEST-2'],
        'values': {
            'priority': 'minor',
            'tags': {
                'add': ['bulktag'],
            },
        },
    }
    assert real_request == expected_request


def test_bulkchange_transition(net_mock, client, fake_bulkchange):
    net_mock.post(api_url('/bulkchange/_transition'), json=fake_bulkchange.json)

    client.bulkchange.transition(
        ['TEST-1', 'TEST-2'], 'need_info', priority='minor',
        tags={'add': ['bulktag']})
    real_request = net_mock.request_history[0].json()
    expected_request = {
        'issues': ['TEST-1', 'TEST-2'],
        'transition': 'need_info',
        'values': {
            'priority': 'minor',
            'tags': {
                'add': ['bulktag'],
            },
        },
    }
    assert real_request == expected_request


def test_bulkchange_move(net_mock, client, fake_bulkchange):
    net_mock.post(api_url('/bulkchange/_move'), json=fake_bulkchange.json)

    client.bulkchange.move(
        ['TEST-1', 'TEST-2'], 'BROWSER', move_all_fields=False,
        priority='minor', tags={'add': ['bulktag']})
    real_request = net_mock.request_history[0].json()
    expected_request = {
        'issues': ['TEST-1', 'TEST-2'],
        'queue': 'BROWSER',
        'values': {
            'priority': 'minor',
            'tags': {
                'add': ['bulktag'],
            },
        },
        'moveAllFields': False,
    }
    assert real_request == expected_request


@pytest.mark.parametrize('terminal_status', ['COMPLETE', 'FAILED'])
def test_bulkchange_wait(net_mock, client, fake_bulkchange,
                         monkeypatch, terminal_status):
    fake_bulkchange_done = fake_bulkchange.set_status(terminal_status)
    net_mock.get(
        api_url('/bulkchange/' + fake_bulkchange.key),
        response_list=[{'json': fake_bulkchange.json},
                       {'json': fake_bulkchange_done.json}])
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    bulkchange = client.bulkchange[fake_bulkchange.key].wait()
    assert bulkchange.status == terminal_status
