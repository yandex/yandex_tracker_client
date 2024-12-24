# coding: utf-8

import pytest

from common.url import api_url


@pytest.mark.parametrize('transition_field', ['id', 'display', 'to', 'screen'])
def test_issue_transitions(net_mock, client, fake_issue, transition_field):
    net_mock.get(api_url('/issues/{}'.format(fake_issue.key)),
                 json=fake_issue.json)
    net_mock.get(api_url('/issues/{}/transitions/'.format(fake_issue.key)),
                 json=fake_issue.transitions)

    issue = client.issues[fake_issue.key]
    transitions = issue.transitions.get_all()

    #expected
    expected_value = (
        fake_issue.transitions[0][transition_field]['display']
        if isinstance(fake_issue.transitions[0][transition_field], dict)
        else fake_issue.transitions[0][transition_field])

    #current
    current_field = getattr(transitions[0], transition_field)
    current_value = (
        current_field.display if hasattr(current_field, 'display')
        else current_field)

    assert current_value == expected_value


def test_issue_transition_execute(net_mock, client, fake_issue):
    net_mock.get(api_url('/issues/{}'.format(fake_issue.key)),
                 json=fake_issue.json)
    net_mock.get(api_url('/issues/{}/transitions/reopen'.format(
        fake_issue.key)), json=fake_issue.transitions[0])
    net_mock.post(api_url('/issues/{}/transitions/reopen/_execute'.format(
        fake_issue.key)), json=fake_issue.transitions)

    test_request = {
        'resolution': 'fixed'
    }

    issue = client.issues[fake_issue.key]
    transition = issue.transitions['reopen']
    transition.execute(**test_request)

    real_request = net_mock.request_history[3].json()
    assert real_request == test_request
