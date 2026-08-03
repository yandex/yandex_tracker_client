# coding: utf-8

from common.url import api_url


def _worklog(idx="1"):
    return {"self": api_url('/worklog/{}'.format(idx)), "id": idx,
            "version": 1, "duration": "PT1H"}


def test_worklog_search_body(net_mock, client):
    net_mock.post(api_url('/worklog/_search'),
                  json=[_worklog("1"), _worklog("2")])
    result = client.worklog.search(
        created_by='vasya',
        created_at={'from': '2025-01-01T00:00:00',
                    'to': '2025-02-01T00:00:00'},
    )
    assert [w.id for w in result] == ["1", "2"]
    assert net_mock.last_request.method == 'POST'
    assert net_mock.last_request.path.endswith('/worklog/_search')
    assert net_mock.last_request.json() == {
        "createdBy": "vasya",
        "createdAt": {"from": "2025-01-01T00:00:00",
                      "to": "2025-02-01T00:00:00"},
    }


def test_worklog_search_pagination(net_mock, client):
    net_mock.post(api_url('/worklog/_search'), json=[])
    client.worklog.search(created_by='vasya', page=2, per_page=100)
    qs = net_mock.last_request.qs
    assert qs['page'] == ['2']
    assert qs['perpage'] == ['100']  # requests_mock lowercases query keys
    assert net_mock.last_request.json() == {"createdBy": "vasya"}


def test_worklog_search_start_range_only(net_mock, client):
    net_mock.post(api_url('/worklog/_search'), json=[])
    client.worklog.search(start={'from': '2025-01-01T00:00:00'})
    assert net_mock.last_request.json() == {
        "start": {"from": "2025-01-01T00:00:00"}}
