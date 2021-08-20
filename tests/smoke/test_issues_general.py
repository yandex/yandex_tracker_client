# coding: utf-8

import pytest

from yandex_tracker_client import exceptions
from common.url import api_url


@pytest.mark.parametrize('issue_field', ['key', 'version', 'summary',
                                         'description', 'queue', 'status',
                                         'type', 'createdAt', 'updatedAt',
                                         'createdBy', 'updatedBy', 'priority'])
def test_issue_fields(net_mock, client, fake_issue, issue_field):
    net_mock.get(api_url('/issues/{}'.format(fake_issue.key)),
                 json=fake_issue.json)
    issue = client.issues[fake_issue.key]

    #expected
    expected_value = (
        fake_issue.json[issue_field]['display']
        if isinstance(fake_issue.json[issue_field], dict)
        else fake_issue.json[issue_field])

    #current
    current_field = getattr(issue, issue_field)
    current_value = (
        current_field.display if hasattr(current_field, 'display')
        else current_field)

    assert current_value == expected_value


def test_issue_not_found(net_mock, client):
    net_mock.get(
        api_url('/issues/{}'.format('DUMMY-123')),
        status_code=404)
    with pytest.raises(exceptions.NotFound):
        issue = client.issues['DUMMY-123']

    # No need in assert. Just: no exception - test passed.


def test_create_issue(net_mock, client, fake_issue):
    net_mock.post(api_url('/issues/'), json=fake_issue.json)

    test_request = {
        'queue': fake_issue.queue,
        'summary': fake_issue.json['summary'],
        'type': {'key': fake_issue.json['type']['key']}
    }

    client.issues.create(**test_request)

    real_request = net_mock.request_history[0].json()
    assert real_request.get('unique') is not None
    assert any([real_request[k] == test_request[k] for k in test_request])


def test_create_issue_with_conflict(net_mock, client, fake_issue):
    net_mock.post(api_url('/issues/'), status_code=409)
    net_mock.get(api_url('/issues/'), json=[fake_issue.json])

    test_request = {
        'unique': fake_issue.json['unique'],
        'queue': fake_issue.queue,
        'summary': fake_issue.json['summary'],
    }

    issue = client.issues.create(**test_request)
    assert issue['unique'] == fake_issue.json['unique']


def test_create_issue_with_conflict_not_found(net_mock, client, fake_issue):
    net_mock.post(api_url('/issues/'), status_code=409)
    net_mock.get(api_url('/issues/'), json=[])

    test_request = {
        'unique': fake_issue.json['unique'],
        'queue': fake_issue.queue,
        'summary': fake_issue.json['summary'],
    }

    with pytest.raises(exceptions.Conflict):
        issue = client.issues.create(**test_request)


def test_update_issue(net_mock, client, fake_issue):
    net_mock.get(api_url('/issues/{}'.format(fake_issue.key)),
        json=fake_issue.json)
    net_mock.patch(api_url('/issues/{}'.format(fake_issue.key)),
                   json=fake_issue.json)

    new_summary = 'New summary'
    issue = client.issues[fake_issue.key]
    issue.update(summary=new_summary)

    real_request = net_mock.request_history[1].json()
    assert real_request['summary'] == new_summary


def test_issue_local_fields(net_mock, client, fake_issue):
    net_mock.get(api_url('/issues/{}'.format(fake_issue.key)),
                 json=fake_issue.json)
    issue = client.issues[fake_issue.key]

    assert issue.localTestField == "local_field_value"


def test_update_local_field_issue(net_mock, client, fake_issue):
    net_mock.get(api_url('/issues/{}'.format(fake_issue.key)),
        json=fake_issue.json)
    net_mock.patch(api_url('/issues/{}'.format(fake_issue.key)),
                   json=fake_issue.json)

    new_value = 'new_local_field_value'
    issue = client.issues[fake_issue.key]
    issue.update(localTestField=new_value)

    real_request = net_mock.request_history[1].json()
    assert real_request['6063181a59590573909db929--localTestField'] == new_value
