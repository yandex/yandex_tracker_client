# coding: utf-8
from __future__ import unicode_literals

import random
import string

from .url import api_url
from .tracker import FakeObject


class FakeQueue(FakeObject):
    @property
    def random_key(self):
        return ''.join(
            [random.choice(string.ascii_uppercase) for _ in range(5)])

    def __init__(self):
        self.key = self.random_key

        self._json = {
            "self": api_url('/queues/' + self.key),
            "id": 786,
            "key": "BARAUTO",
            "version": 1412180164560,
            "name": "Test Queue",
            "lead": {
                "self": api_url('/users/1120000000006155'),
                "id": "testuser",
                "display": "Test User"
            },
            "assignAuto": True,
            "allowExternals": False,
            "defaultType": {
                "self": api_url('/issuetypes/2'),
                "id": "2",
                "key": "task",
                "display": "Задача"
            },
            "defaultPriority": {
                "self": api_url('/priorities/2'),
                "id": "2",
                "key": "normal",
                "display": "Средний"
            },
            "department": {
                "self": api_url('/departments/1519'),
                "id": "1519",
                "key": "yandex_infra",
                "display": "Test Department"
            }
        }


class FakeQueuesCollection(FakeObject):
    @property
    def json(self):
        return [it.json for it in self._json]

    def __getitem__(self, item):
        return self._json[item]

    def __init__(self, count=None):
        self.count = count or random.randint(1, 50)
        self._json = [FakeQueue() for _ in range(self.count)]
