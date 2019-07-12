# coding: utf-8

import pytest
import random

from common.url import api_url


@pytest.fixture
def mocked_links(net_mock, mocked_fake_issue, fake_issue):
    net_mock.get(api_url('/issues/{}/links/'.format(fake_issue.key)),
                 json=fake_issue.links)

    return list(mocked_fake_issue.links)


@pytest.fixture
def random_link_num(fake_issue):
    return random.randint(0, len(fake_issue.comments) - 1)


@pytest.fixture
def mocked_random_link(net_mock, fake_issue, mocked_links, random_link_num):
    fake_link = fake_issue.links[random_link_num]
    net_mock.get(
        api_url('/issues/{}/links/{}'.format(fake_issue.key, fake_link['id'])),
        json=fake_link)

    return mocked_links[random_link_num]


@pytest.mark.parametrize('link_field', ['direction', 'object', 'updatedBy',
                                        'createdBy', 'createdAt', 'updatedAt'])
def test_links_fields(fake_issue, link_field, mocked_links, random_link_num):

    comment = mocked_links[random_link_num]
    fake_link = fake_issue.links[random_link_num]

    #expected
    expected_value = (
        fake_link[link_field]['display']
        if isinstance(fake_link[link_field], dict)
        else fake_link[link_field])

    #current
    current_field = getattr(comment, link_field)
    current_value = (
        current_field.display if hasattr(current_field, 'display')
        else current_field)

    assert current_value == expected_value


def test_add_link(net_mock, mocked_fake_issue, fake_issue, mocked_links,
                  random_link_num):
    fake_link = fake_issue.links[random_link_num]

    post_json = {
        "relationship": fake_link['type']['id'],
        "issue": fake_link['object']['key']
    }

    net_mock.post(api_url('/issues/{}/links/'.format(fake_issue.key)),
                  json=post_json, status_code=204)

    mocked_fake_issue.links.create(**post_json)

    real_request = net_mock.request_history[3].json()

    assert any([real_request[k] == post_json[k]
                for k in post_json])


def test_link_delete(net_mock, fake_issue, mocked_random_link,
                     random_link_num):
    fake_link = fake_issue.links[random_link_num]
    net_mock.delete(api_url('/issues/{}/links/{}'.format(
        fake_issue.key, fake_link['id'])), status_code=204)

    mocked_random_link.delete()

    # No need in assert. Just: no exception - test passed.
