# coding: utf-8
import pytest
from common.url import api_url

from yandex_tracker_client.exceptions import OutOfRetries


def test_retries(net_mock, connection):
    url = api_url('/issues/{}'.format('DUMMY-123'))
    net_mock.get(
        url,
        status_code=500
    )

    connection.retries = 10     # default
    with pytest.raises(OutOfRetries):
        connection.get(url)

    assert net_mock.call_count == 10 + 1


def test_no_retries(net_mock, connection):
    url = api_url('/issues/{}'.format('DUMMY-123'))
    net_mock.get(
        url,
        status_code=500
    )

    connection.retries = 0
    with pytest.raises(OutOfRetries):
        connection.get(url)

    assert net_mock.call_count == 1
