# coding: utf-8
from __future__ import unicode_literals
import copy

from .tracker import FakeObject
from .tracker import random_id
from .url import api_url


class FakeBulkchange(FakeObject):
    def __init__(self, json=None):
        self.key = json['id'] if json else random_id()
        self._json = json or {
            'id': self.key,
            'self': api_url('/bulkchange/' + self.key),
            'createdBy': {
                'self': api_url('/users/1120000000006155'),
                'id': 'testuser',
                'display': 'Test User'
            },
            'createdAt': '2015-07-05T10:39:38.258+0000',
            'status': 'CREATED',
            'statusText': 'Создан',
            'executionChunkPercent': 0,
            'executionIssuePercent': 0,
        }

    def set_status(self, status):
        new_json = copy.deepcopy(self._json)
        new_json['status'] = status
        return self.__class__(new_json)
