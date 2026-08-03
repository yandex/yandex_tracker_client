# coding: utf-8

from common.url import api_url


def _filter():
    return {"self": api_url('/filters/10'), "id": "10", "name": "F"}


def test_filter_favorite(net_mock, client):
    net_mock.get(api_url('/filters/10'), json=_filter())
    flt = client.filters['10']
    net_mock.post(api_url('/filters/10/_favorite'), json=_filter())
    flt.favorite()
    assert net_mock.last_request.method == 'POST'
    assert net_mock.last_request.path.endswith('/filters/10/_favorite')


def test_filter_unfavorite(net_mock, client):
    net_mock.get(api_url('/filters/10'), json=_filter())
    flt = client.filters['10']
    net_mock.post(api_url('/filters/10/_unfavorite'), json=_filter())
    flt.unfavorite()
    assert net_mock.last_request.method == 'POST'
    assert net_mock.last_request.path.endswith('/filters/10/_unfavorite')


def test_get_favorite_filters(net_mock, client):
    net_mock.get(api_url('/myself/favorites/filters'), json=[])
    client.filters.get_favorites()
    assert net_mock.last_request.method == 'GET'
    assert net_mock.last_request.path.endswith('/myself/favorites/filters')
