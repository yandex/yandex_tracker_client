# coding: utf-8

from common.url import api_url


def _issue():
    return {"self": api_url('/issues/TEST-1'), "id": "1", "key": "TEST-1"}


def _comment():
    return {"self": api_url('/issues/TEST-1/comments/c1'), "id": "c1",
            "longId": "c1", "text": "hi"}


def test_comment_add_reaction(net_mock, client):
    net_mock.get(api_url('/issues/TEST-1'), json=_issue())
    issue = client.issues['TEST-1']
    net_mock.get(api_url('/issues/TEST-1/comments/c1'), json=_comment())
    comment = issue.comments['c1']
    net_mock.post(api_url('/issues/TEST-1/comments/c1/reactions/like'),
                  json=_comment())
    comment.add_reaction('like')
    assert net_mock.last_request.method == 'POST'
    assert net_mock.last_request.path.lower().endswith(
        '/issues/test-1/comments/c1/reactions/like')


def test_comment_remove_reaction(net_mock, client):
    net_mock.get(api_url('/issues/TEST-1'), json=_issue())
    issue = client.issues['TEST-1']
    net_mock.get(api_url('/issues/TEST-1/comments/c1'), json=_comment())
    comment = issue.comments['c1']
    net_mock.delete(api_url('/issues/TEST-1/comments/c1/reactions/like'),
                    json=_comment())
    comment.remove_reaction('like')
    assert net_mock.last_request.method == 'DELETE'
    assert net_mock.last_request.path.lower().endswith(
        '/issues/test-1/comments/c1/reactions/like')
