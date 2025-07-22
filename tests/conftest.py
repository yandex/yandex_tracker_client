# coding: utf-8

import pytest
from mock import mock_open, patch

from common.bulkchange import FakeBulkchange
from common.field_categories import FakeFieldCategory, FakeFieldCategoriesCollection
from common.entities import FakeEntity, FakeEntitiesCollection
from common.issues import FakeIssue, FakeIssuesCollection
from common.mock import base_mock
from common.queues import FakeQueue, FakeQueuesCollection
from common.url import api_url
from yandex_tracker_client import TrackerClient


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


@pytest.fixture(params=['project', 'portfolio', 'goal'])
def entity_type(request):
    return request.param


@pytest.fixture
def fake_entity(entity_type):
    return FakeEntity(entity_type)


@pytest.fixture
def fake_entities(entity_type):
    return FakeEntitiesCollection(entity_type)


@pytest.fixture
def mocked_fake_entity(request, net_mock, client, fake_entity):
    net_mock.get(
        api_url('/entities/{entity_type}/{idx}'.format(entity_type=fake_entity.entity_type, idx=fake_entity.idx)),
        json=fake_entity.json)
    entity = getattr(client, fake_entity.entity_type).get(fake_entity.idx)

    return entity


@pytest.fixture
def fake_field_category():
    return FakeFieldCategory()


@pytest.fixture
def fake_field_categories():
    return FakeFieldCategoriesCollection()


@pytest.fixture
def mocked_fake_field_categories(net_mock, client, fake_field_categories):
    net_mock.get(api_url('/fields/categories/'), json=fake_field_categories.json)

    return client.field_categories
