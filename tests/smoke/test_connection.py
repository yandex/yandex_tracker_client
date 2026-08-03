# coding: utf-8
import pytest
from common.url import api_url

from yandex_tracker_client.exceptions import Forbidden, OutOfRetries, InvalidJSONResponse


def test_retries(net_mock, connection):
    url = api_url('/issues/{}'.format('DUMMY-123'))
    net_mock.get(
        url,
        status_code=500
    )

    connection.retries = 10  # default
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


def test_invalid_json_response(net_mock, connection):
    url = api_url('/issues/{}'.format('DUMMY-123'))
    net_mock.get(
        url,
        status_code=200,
        text="<html><body><h1>Hello</h1></body></html>"
    )

    with pytest.raises(InvalidJSONResponse):
        connection.get(url)


def test_errors_data_from_error_response(net_mock, connection):
    url = api_url('/queues/{}'.format('DUMMY'))
    net_mock.get(
        url,
        status_code=403,
        json={
            'errors': {},
            'errorMessages': ["You don't have permissions in DUMMY queue."],
            'errorsData': {'securityLevel': 'protect_sensitive_data'},
        }
    )

    with pytest.raises(Forbidden) as excinfo:
        connection.get(url)

    assert excinfo.value.errors_data == {'securityLevel': 'protect_sensitive_data'}


def test_errors_data_absent_in_error_response(net_mock, connection):
    url = api_url('/queues/{}'.format('DUMMY'))
    net_mock.get(
        url,
        status_code=403,
        json={'errors': {}, 'errorMessages': ["You don't have permissions in DUMMY queue."]}
    )

    with pytest.raises(Forbidden) as excinfo:
        connection.get(url)

    assert excinfo.value.errors_data is None
