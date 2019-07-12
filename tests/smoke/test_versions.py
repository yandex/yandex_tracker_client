# coding: utf-8

from common.url import api_url


def test_archive_version(net_mock, client):
    net_mock.get(
        api_url('/versions/1'),
        json={
            "self": api_url('/versions/1'),
            "id": 1, "version": 1,
            "queue": {
                "self": api_url('/queues/TEST'),
                "id": "138", "key": "TEST", "display": "TEST"},
            "name": "1.0", "description": "test version", "released": False,
            "archived": False,
        }
    )
    version = client.versions['1']

    net_mock.post(
        api_url('/versions/1/_archive'),
    )

    version.perform_action('_archive', 'post', ignore_empty_body=True)

