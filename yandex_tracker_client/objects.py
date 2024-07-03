# coding: utf-8
from __future__ import absolute_import

import functools
import json
import logging
import textwrap

try:
    from collections import MutableMapping
except ImportError:
    from collections.abc import MutableMapping

import six
from six.moves.urllib.parse import urlsplit, urlunsplit

from .collections import match_collection

__all__ = [
    'Object',
    'Resource', 'Reference',
    'PaginatedList'
]

logger = logging.getLogger(__name__)


class FieldLoggingDict(MutableMapping, dict):
    def __init__(self, delegate, obj):
        super(FieldLoggingDict, self).__init__(delegate)
        self._obj = obj

    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        self._obj.log_local_key_usage(key)
        return value

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)

    def __iter__(self):
        return dict.__iter__(self)

    def __len__(self):
        return dict.__len__(self)

    def __contains__(self, x):
        return dict.__contains__(self, x)


class Object(object):
    def __init__(self, connection, path, value, local_fields_map=None):
        self._collection = connection._client._get_collection(match_collection(path))
        logger.debug('%s -> %s', path, self._collection)
        self._connection = connection
        self._path = path
        self._has_local_fields = self._collection.has_local_fields
        self._local_fields_map = {} if local_fields_map is None else local_fields_map
        self._value = self._process_value(value)
        self._version = value.get('version')

    def _local_fields_map_type(self):
        return dict

    def copy_into(self, conn, cons):
        return cons(conn, self._path, self._value, self._local_fields_map)

    def _process_value(self, value):
        if self._has_local_fields:
            local_fields_to_add = {}
            for field, field_value in six.iteritems(value):
                if '--' in field:
                    local_field_key = field.split('--')[-1]
                    if local_field_key in value:
                        local_field_key = 'local_{}'.format(local_field_key)
                    local_fields_to_add[local_field_key] = field_value
                    self._local_fields_map[local_field_key] = field
            value.update(local_fields_to_add)
            if type(value) == self._local_fields_map_type():
                return value
            return self._local_fields_map_type()(value, self)

        return value

    def process_kwargs(self, kwargs):
        if self._has_local_fields:
            for field_key, local_field_key in six.iteritems(self._local_fields_map):
                if field_key in kwargs:
                    kwargs[local_field_key] = kwargs.pop(field_key)
                    Object._log_local_key_usage_warning(field_key, local_field_key, 'update')
                    self._collection._updated_local_field = local_field_key
        return kwargs

    def log_local_key_usage(self, key):
        if self._has_local_fields and key in self._local_fields_map:
            local_field_key = self._local_fields_map[key]
            Object._log_local_key_usage_warning(key, local_field_key, 'access')
            self._collection._read_local_field = local_field_key

    @staticmethod
    def _log_local_key_usage_warning(field_key, local_field_key, action):
        logger.warning("{} for field value by key '{}' has been resolved to '{}'. "
                       "This functionality is unstable and will be removed soon. "
                       "Please, use full api key to {} the value of a local field "
                       "(e.g. '6063181a59590578909db920--localField'). "
                       "If you are attempting to {} the custom field '{}', you have encountered a bug. "
                       "Please, reach out to Tracker support team for details."
                       .format(action.title(), field_key, local_field_key,
                               action.lower(), action.lower(), field_key))

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

    def _local_fields_map_type(self):
        return FieldLoggingDict

    def __repr__(self):
        return '<Resource {path}>'.format(
            path=self._path
        )

    def __dir__(self):
        return sorted(
            set(self._collection.local_fields.keys())
            | set(self._collection.fields.keys())
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
