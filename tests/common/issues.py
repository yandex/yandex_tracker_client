# coding: utf-8

from __future__ import unicode_literals

import random
import time
import string

from .url import api_url
from .tracker import FakeObject, random_id


class FakeIssue(FakeObject):
    @property
    def random_key(self):
        queue_name = ''.join(
            [random.choice(string.ascii_uppercase) for _ in range(5)])

        return '{}-{}'.format(queue_name, random.randint(1, 10000))

    @property
    def self_(self):
        return api_url('/issues/{}'.format(self.key))

    @property
    def queue(self):
        return self.key.split('-')[0]

    @property
    def transitions(self):
        return [{
            "self": "{}/transitions/reopen".format(self.self_),
            "id": "reopen",
            "display": "Reopen",
            "to": {
                "self": api_url("/statuses/1"),
                "id": "1",
                "key": "open",
                "display": "Open"},
            "screen": {
                "self": api_url("/screens/4"),
                "id": "4",
                "display": "4"}}]

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
                "updatedBy":{
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
                "updatedBy":{
                   "self": api_url("/users/1120000000000219"),
                   "id": "testuser2",
                   "display": "Test User2"},
                "createdAt": "2015-04-14T17:04:44.026+0000",
                "updatedAt": "2015-04-14T17:04:44.026+0000"}]

        return self._links

    def __init__(self, key=None):
        self.key = key or self.random_key

        self._json = {
            "self": api_url('/issues/{}'.format(self.key)),
            "id": random_id(),
            "unique": random_id(),
            "key": self.key,
            "version": int(time.time()),
            "summary": "Simple title",
            "description": "Empty description",
            "queue": {
                "self": api_url('/queues/{}'.format(self.queue)),
                "id": "138",
                "key": self.queue,
                "display": "Песочница"
            },
            "status": {
                "self": api_url('/statuses/1'),
                "id": "1",
                "key": "open",
                "display": "Открыт"
            },
            "type": {
                "self": api_url('/issuetypes/1'),
                "id": "1",
                "key": "bug",
                "display": "Ошибка"
            },
            "createdAt": "2015-04-05T12:20:04.022+0000",
            "updatedAt": "2015-04-05T12:20:04.022+0000",
            "6063181a59590573909db929--localTestField": "local_field_value",
            "6063181a59590573909db940--description": "local_description",
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
            "priority": {
                "self": api_url('/priorities/2'),
                "id": "2",
                "key": "normal",
                "display": "Средний"
            }
        }


class FakeIssuesCollection(FakeObject):
    @property
    def json(self):
        return [it.json for it in self._json]

    def __getitem__(self, item):
        return self._json[item]

    def __init__(self, count=None):
        self.count = count or random.randint(1, 50)
        self._json = [FakeIssue() for _ in range(self.count)]
