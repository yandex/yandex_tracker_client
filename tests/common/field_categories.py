# coding: utf-8

from __future__ import unicode_literals

import random

from .url import api_url
from .tracker import FakeObject, random_id


class FakeFieldCategory(FakeObject):

    def __init__(self):
        self.id = random_id()

        self._json = {
            "self": api_url('/fields/categories/' + self.id),
            "id": self.id,
            "version": 1412180164560,
            "name": "Test Field Category",
        }


class FakeFieldCategoriesCollection(FakeObject):
    @property
    def json(self):
        return [it.json for it in self._json]

    def __getitem__(self, item):
        return self._json[item]

    def __init__(self, count=None):
        self.count = count or random.randint(1, 50)
        self._json = [FakeFieldCategory() for _ in range(self.count)]
