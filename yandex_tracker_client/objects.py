# coding: utf-8
from __future__ import absolute_import

import json
import functools
import logging
import textwrap

import six
from six.moves.urllib.parse import urlsplit, urlunsplit

from .collections import match_collection


__all__ = [
    'Object',
    'Resource', 'Reference',
    'PaginatedList'
]

logger = logging.getLogger(__name__)


class Object(object):
    def __init__(self, connection, path, value):
        self._collection = connection._client._get_collection(match_collection(path))
        logger.debug('%s -> %s', path, self._collection)
        self._connection = connection
        self._path = path
        self._value = self._collection._parse_value(value)
        self._version = value.get('version')

    def as_dict(self):
        def to_simple(value):
            if isinstance(value, dict):
                return dict((k, to_simple(v)) for k, v in six.iteritems(value))

            elif isinstance(value, Object):
                return value.as_dict()

            elif isinstance(value, (list, set, tuple)):
                return [to_simple(v) for v in value]

            else:
                return value

        return to_simple(self._value)

    def __reduce__(self):
        return (self.__class__, (self._connection, self._path, self._value))


class Resource(Object):
    def __repr__(self):
        return '<Resource {path}>'.format(
            path=self._path
        )

    def __dir__(self):
        return sorted(
            set(self._collection.fields.keys())
            | set(self._collection._injected_properties)
            | set(self._collection._injected_methods)
        )

    def __getattr__(self, key):
        collection = self._collection
        if key in collection._injected_methods:
            method = collection._injected_methods[key]

            @functools.wraps(method)
            def injected_method(*args, **kwargs):
                return method(collection, self, *args, **kwargs)

            return injected_method

        if key in collection._injected_properties:
            method = collection._injected_properties[key]
            return method(collection, self)

        if key in collection.fields:
            return self._value.get(key, collection.fields[key])
        elif key in self._value:
            return self._value.get(key)
        else:
            raise AttributeError(key)

    def __getitem__(self, key):
        try:
            return self.__getattr__(key)
        except AttributeError as e:
            raise KeyError(str(e))

    def _repr_pretty_(self, p, cycle):
        if cycle:
            p.text(self._path + ' {...}')
            return

        p.text(self._path)
        with p.group(4, ':'):
            for key in sorted(self._value):
                p.break_()
                p.text(key)
                p.text(': ')
                value = self._value[key]
                if isinstance(value, six.string_types):
                    lines = []
                    for line in value.splitlines():
                        lines.extend(textwrap.wrap(line))
                    if len(lines) <= 1:
                        p.text(value)
                    else:
                        with p.group(4):
                            for line in lines:
                                p.break_()
                                p.text(line)
                elif isinstance(value, list):
                    with p.group(2):
                        for item in value:
                            p.break_()
                            p.text('- ')
                            p.pretty(item)

                else:
                    p.pretty(self._value[key])
        p.break_()


class Reference(Object):
    _target = None

    def __repr__(self):
        display = self._value.get('display', '')
        if isinstance(display, dict):
            display = display['ru']

        _id = self._value.get('id')
        if isinstance(_id, int):
            _id = str(_id)

        return '<Reference to {collection}/{id} ({display})>'.format(
            collection=self._collection.__class__.__name__,
            id=_id.encode('utf-8'),
            display=display.encode('utf-8'),
        )

    def __dir__(self):
        return dir(self._dereference())

    def __getattr__(self, key):
        if key in self._value:
            return self._value[key]
        return getattr(self._dereference(), key)

    def _dereference(self):
        if self._target is None:
            self._target = self._connection.get(path=self._path)
        return self._target

    def _repr_pretty_(self, p, cycle):
        if cycle:
            p.text('[...]')
            return

        with p.group(1, '[', ']'):
            p.text(self._collection.__class__.__name__)
            p.text('/')
            if 'key' in self._value:
                p.text(self._value['key'])
            elif 'id' in self._value:
                p.text(self._value['id'])
            else:
                p.text('???')
            if 'display' in self._value:
                p.breakable(': ')
                if isinstance(self._value['display'], dict):
                    p.text(self._value['display']['ru'])
                else:
                    p.text(self._value['display'])


class PaginatedList(object):
    def __init__(self, connection, head, response):
        self._data = head
        self._connection = connection
        self._next_page = self._strip_host(response.links['next']['url'])
        self._original_request = response.request

        self._one_page = False  # итерироваться только по этой странице?

    def _strip_host(self, url):
        u = urlsplit(url)
        return urlunsplit(('', '', u.path, u.query, u.fragment))

    def __iter__(self):
        for item in self._data:
            yield item

        if not self._one_page:
            next_page = self._next_page

            while next_page is not None:
                page = self._get_page_data(next_page)
                if isinstance(page, list):
                    next_page = None
                    data = page
                else:
                    next_page = page._next_page
                    data = page._data

                for item in data:
                    yield item

    def _get_page_data(self, path):
        req = self._original_request
        method = req.method
        data = req.body
        if data and isinstance(data, six.string_types):
            data = json.loads(data)
        headers = req.headers
        return self._connection.request(method, path, data=data, headers=headers)


class SeekablePaginatedList(PaginatedList):

    def __init__(self, connection, head, response):
        super(SeekablePaginatedList, self).__init__(connection, head, response)
        self._seek_page = self._strip_host(response.links['seek']['url'])

        self._items_count = int(response.headers['X-Total-Count'])
        self.pages_count = int(response.headers['X-Total-Pages'])

    def __len__(self):
        if self._one_page:
            return len(self._data)
        else:
            return self._items_count

    def get_page(self, number):
        path = self._seek_page.replace('{&page}', '&page={}'.format(number))
        plist = self._get_page_data(path)
        if isinstance(plist, SeekablePaginatedList):
            plist._one_page = True
        return plist
