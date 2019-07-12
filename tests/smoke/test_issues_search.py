# coding: utf-8

import random

import pytest

from common.url import api_url


@pytest.mark.parametrize('request_params', [
    {'filter': {'status': 'open'}},
    {'query': 'Status: Open'}
])
def test_issues_search_request(net_mock, client, fake_issues, request_params):
    net_mock.post(api_url('/issues/_search'), json=fake_issues.json)

    issues = client.issues.find(**request_params)
    real_request = net_mock.request_history[0].json()
    assert all([real_request[k] == request_params[k] for k in request_params])


def test_issues_search_response_count(net_mock, client, fake_issues):
    net_mock.post(api_url('/issues/_search'), json=fake_issues.json)

    issues = client.issues.find(query='Status: Open')
    assert len(issues) == fake_issues.count


@pytest.mark.parametrize('issue_field', ['key', 'version', 'summary',
                                         'description', 'queue', 'status',
                                         'type', 'createdAt', 'updatedAt',
                                         'createdBy', 'updatedBy', 'priority'])
def test_issues_search_response(net_mock, client, fake_issues, issue_field):
    net_mock.post(api_url('/issues/_search'), json=fake_issues.json)

    issues = client.issues.find(query='Status: Open')
    issue_num = random.randint(0, fake_issues.count - 1)

    issue = issues[issue_num]
    fake_issue = fake_issues[issue_num]

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
