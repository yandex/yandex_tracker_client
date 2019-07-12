# coding: utf-8

import pytest

from yandex_tracker_client import TrackerClient
from mock import mock_open, patch

from common.bulkchange import FakeBulkchange
from common.issues import FakeIssue, FakeIssuesCollection
from common.queues import FakeQueue, FakeQueuesCollection
from common.mock import base_mock
from common.url import api_url


@pytest.fixture
def client():
    return TrackerClient(
        token='TEST_TOKEN',
        org_id='15',
    )


@pytest.fixture
def fake_issue():
    return FakeIssue()


@pytest.fixture
def fake_issues():
    return FakeIssuesCollection()


@pytest.yield_fixture
def net_mock():
    with base_mock() as m:
        yield m


@pytest.fixture
def connection(client):
    return client._connection


@pytest.fixture
def fake_queue():
    return FakeQueue()


@pytest.fixture
def fake_queues():
    return FakeQueuesCollection()


@pytest.yield_fixture
def open_mock():
    m = mock_open()
    with patch('yandex_tracker_client.collections.open', m, create=True):
        yield m


@pytest.fixture
def mocked_fake_issue(net_mock, client, fake_issue):
    net_mock.get(api_url('/issues/{}'.format(fake_issue.key)),
                 json=fake_issue.json)

    return client.issues[fake_issue.key]


@pytest.fixture
def fake_bulkchange():
    return FakeBulkchange()
