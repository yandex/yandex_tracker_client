# coding: utf-8

from __future__ import unicode_literals

import random
import time

from .tracker import FakeObject, random_id
from .url import api_url


class FakeEntity(FakeObject):
    @property
    def self_(self):
        return api_url('/entities/{entity}/{idx}'.format(entity=self.entity_type, idx=self.idx))

    @property
    def attachments(self):
        if not hasattr(self, '_attachments'):
            self._attachments = [{
                "self": '{}/attachments/{}'.format(self.self_, random_id()),
                "id": random_id._last_res,
                "name": "file1.txt",
                "content": '{}/attachments/{}/file1.txt'.format(
                    self.self_, random_id._last_res),
                "createdBy": {
                    "self": api_url('/users/1120000000003939'),
                    "id": "testuser",
                    "display": "Test User"
                },
                "createdAt": "2012-08-03T10:25:03.994+0000",
                "mimetype": "plain/text",
                "size": random.randint(1, 1024)
            }, {
                "self": '{}/attachments/{}'.format(self.self_, random_id()),
                "id": random_id._last_res,
                "name": "file1.txt",
                "content": '{}/attachments/{}/file2.txt'.format(
                    self.self_, random_id._last_res),
                "createdBy": {
                    "self": api_url('/users/1120000000003940'),
                    "id": "testuser",
                    "display": "Test User 2"
                },
                "createdAt": "2012-08-03T10:25:03.994+0000",
                "mimetype": "plain/text",
                "size": random.randint(1, 1024)
            }]

        return self._attachments

    @property
    def comments(self):
        if not hasattr(self, '_comments'):
            self._comments = [{
                "self": '{}/comments/{}'.format(self.self_, random_id()),
                "id": random_id._last_res,
                "text": "Comment text 1",
                "createdBy": {
                    "self": api_url('/users/1120000000003940'),
                    "id": "testuser",
                    "display": "Test User"
                },
                "updatedBy": {
                    "self": api_url('/users/1120000000003940'),
                    "id": "testuser",
                    "display": "Test User"
                },
                "createdAt": "2015-03-05T17:17:16.764+0000",
                "updatedAt": "2015-03-05T17:17:16.764+0000"
            }, {
                "self": '{}/comments/{}'.format(self.self_, random_id()),
                "id": random_id._last_res,
                "text": "Comment text 2",
                "createdBy": {
                    "self": api_url('/users/1120000000003941'),
                    "id": "testuser",
                    "display": "Test User 2"
                },
                "updatedBy": {
                    "self": api_url('/users/1120000000003941'),
                    "id": "testuser",
                    "display": "Test User 2"
                },
                "createdAt": "2015-03-05T17:17:16.765+0000",
                "updatedAt": "2015-03-05T17:17:16.765+0000"
            }]

        return self._comments

    @property
    def links(self):
        if not hasattr(self, '_links'):
            self._links = [{
                "self": '{}/links/{}'.format(self.self_, random_id()),
                "id": random_id._last_res,
                "type": {
                    "self": "{}/linktypes/relates".format(self.self_),
                    "id": "relates",
                    "inward": "Relates",
                    "outward": "Relates"},
                "direction": "inward",
                "object": {
                    "self": api_url("/issues/DUMMY-123"),
                    "id": random_id(),
                    "key": "DUMMY-123",
                    "display": "Any dummy text"
                },
                "createdBy": {
                    "self": api_url("/users/1120000000000218"),
                    "id": "testuser",
                    "display": "Test User"
                },
                "updatedBy": {
                    "self": api_url("/users/1120000000000218"),
                    "id": "testuser",
                    "display": "Test User"},
                "createdAt": "2015-04-14T17:04:44.025+0000",
                "updatedAt": "2015-04-14T17:04:44.025+0000"
            }, {
                "self": '{}/links/{}'.format(self.self_, random_id()),
                "id": random_id._last_res,
                "type": {
                    "self": "{}/linktypes/relates".format(self.self_),
                    "id": "relates",
                    "inward": "Relates",
                    "outward": "Relates"},
                "direction": "inward",
                "object": {
                    "self": api_url("/issues/DUMMY-124"),
                    "id": random_id(),
                    "key": "DUMMY-124",
                    "display": "Any dummy text 2"
                },
                "createdBy": {
                    "self": api_url("/users/1120000000000219"),
                    "id": "testuser2",
                    "display": "Test User2"
                },
                "updatedBy": {
                    "self": api_url("/users/1120000000000219"),
                    "id": "testuser2",
                    "display": "Test User2"},
                "createdAt": "2015-04-14T17:04:44.026+0000",
                "updatedAt": "2015-04-14T17:04:44.026+0000"}]

        return self._links

    @property
    def events(self):
        if not hasattr(self, '_events'):
            self._events = {
                "events": [
                    {
                        "id": random_id._last_res,
                        "author": "Tester",
                        "date": "2024-12-11T08:09:03.206+0000",
                        "transport": "v2",
                        "display": "Задача создана",
                        "changes": [
                            {
                                "diff": "<added>Test Project</added>",
                                "field": {
                                    "id": "summary",
                                    "display": "Название"
                                }
                            }
                        ]
                    }
                ],
                "hasNext": True
            }
        return self._events

    def __init__(self, entity_type, idx=None):
        self.entity_type = entity_type
        self.idx = 123

        self._json = {
            "self": api_url('/entities/{entity}/{idx}'.format(entity=self.entity_type, idx=self.idx)),
            "id": self.idx,
            "version": int(time.time()),
            "shortId": random_id(),
            "entityType": self.entity_type,
            "summary": "Simple title",
            "description": "Empty description",
            "status": {
                "self": api_url('/statuses/1'),
                "id": "1",
                "key": "new",
                "display": "Новый"
            },
            "createdAt": "2015-04-05T12:20:04.022+0000",
            "updatedAt": "2015-04-05T12:20:04.022+0000",
            "createdBy": {
                "self": api_url('/users/1120000000006155'),
                "id": "testuser",
                "display": "Test User"
            },
            "updatedBy": {
                "self": api_url('/users/1120000000006155'),
                "id": "testuser",
                "display": "Test User"
            },
        }


class FakeEntitiesCollection(FakeObject):
    @property
    def json(self):
        return [it.json for it in self._json]

    def __getitem__(self, item):
        return self._json[item]

    def __init__(self, entity_type, count=None):
        self.count = count or random.randint(1, 50)
        self._json = [FakeEntity(entity_type) for _ in range(self.count)]
