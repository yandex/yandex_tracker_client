# coding: utf-8

import logging
import requests
import json

try:
    from requests.utils import check_header_validity
except:
    # For compatibility with requests version < 2.11
    check_header_validity = lambda header: True

import six
from six.moves.urllib.parse import urlparse, urljoin
from six.moves import range

from . import exceptions
from .objects import Reference, Resource, PaginatedList, SeekablePaginatedList
from .settings import VERSION_V2

logger = logging.getLogger(__name__)


def bind_method(name):
    def method(self, *args, **kwargs):
        return self.request(name, *args, **kwargs)

    method.func_name = name.lower()
    return method


class Connection(object):

    def __init__(self,
                 token,
                 org_id,
                 base_url="https://api.tracker.yandex.net",
                 timeout=10,
                 retries=10,
                 headers=None,
                 api_version=VERSION_V2,
                 verify=True,
                 ):

        self.session = requests.Session()
        self.session.verify = verify

        if headers is not None:
            self.session.headers.update(headers)

        self.session.headers['Authorization'] = 'OAuth ' + (token or 'not provided')
        self.session.headers['X-Org-Id'] = org_id or 'not provided'
        self.session.headers['Content-Type'] = 'application/json'

        # Check validity headers for requests >= 2.11
        for header in self.session.headers.items():
            check_header_validity(header)

        self.base_url = base_url
        self.api_version = api_version
        self.timeout = timeout
        self.retries = retries

    get = bind_method('GET')
    put = bind_method('PUT')
    post = bind_method('POST')
    patch = bind_method('PATCH')
    delete = bind_method('DELETE')

    def stream(self, path, params=None):
        logger.info("Stream GET %s", path)
        url = self.build_url(path)
        return self._request('GET', url, stream=True, params=params).iter_content(8 * 1024)

    def link(self, path, resource, rel, params=None, version=None):
        return self._link('LINK', path, resource, rel, params, version)

    def unlink(self, path, resource, rel, params=None, version=None):
        return self._link('UNLINK', path, resource, rel, params, version)

    def _link(self, method, path, resource, rel, params=None, version=None):
        logger.info("Request %s %s", method, path)
        url = self.build_url(path)
        link = '<{resource}>; rel="{rel}"'.format(
            resource=resource,
            rel=rel
        )
        response = self._request(method, url, headers={'Link': link}, version=version, params=params)
        return decode_response(response, self)

    def request(self, method, path, params=None, data=None, files=None, version=None, **kwargs):
        logger.info("Request %s %s", method, path)
        url = self.build_url(path)
        response = self._request(
            method=method,
            url=url,
            data=data,
            files=files,
            version=version,
            params=params,
            **kwargs
        )
        return decode_response(response, self)

    def build_url(self, path):
        return urljoin(self.base_url, path)

    def _request(self, method, url, data=None, files=None, version=None, headers=None, stream=False, params=None):
        if headers is None:
            headers = {}
        # XXX: API does not always respect If-Match header :(
        if version is not None:
            headers['If-Match'] = '"{}"'.format(version)
        if data is not None:
            data = json.dumps(data, default=encode_resource)
        logger.debug("HTTP %s %s DATA=%s", method, url, data)

        if files:
            headers['Content-Type'] = None

        return self._try_request(
            method=method,
            url=url,
            data=data,
            files=files,
            timeout=self.timeout,
            headers=headers,
            stream=stream,
            params=params,
        )

    def _try_request(self, **kwargs):
        response = None
        exception = None
        iterations = max(self.retries + 1, 1)

        for retry in range(iterations):
            try:
                response = self.session.request(**kwargs)
            except Exception as e:
                exception = e
            else:
                exception = None
                if 500 <= response.status_code < 600:
                    logger.warning(
                        "Request failed with status %d, retrying (%d)...",
                        response.status_code, retry
                    )
                    self._log_error(logging.WARNING, response)
                else:
                    break
            # XXX: sleep?

        if exception is not None:
            raise exceptions.TrackerRequestError(exception)
        elif 500 <= response.status_code < 600:
            raise exceptions.OutOfRetries(response)
        elif 400 <= response.status_code < 500:
            self._log_error(logging.ERROR, response)
            exc_class = exceptions.STATUS_CODES.get(
                response.status_code,
                exceptions.TrackerServerError
            )
            raise exc_class(response)
        return response

    def _log_error(self, level, response):
        try:
            data = response.json()
            logger.log(level, 'Tracker errors: %s %s',
                       data.get('statusCode'), data.get('errors'))
            messages = data.get('errorMessages', ())
            logger.log(level, '%d messages follow:', len(messages))
            for msg in messages:
                logger.log(level, ' - %s', msg)
        except Exception:
            logger.log(level, 'Unexpected tracker error: %s',
                       response.text)


def decode_response(response, conn):
    if not response.content:
        return None

    def decode_object(obj):
        if 'self' in obj:
            url = obj['self'].encode('utf-8') if six.PY2 else obj['self']
            path = urlparse(url).path

            return Reference(conn, path, obj)
        return obj

    decoded = response.json(object_hook=decode_object)

    if isinstance(decoded, Reference):
        return Resource(conn, decoded._path, decoded._value)
    elif isinstance(decoded, list):
        items = []
        for item in decoded:
            if hasattr(item, '_path') and  hasattr(item, '_value'):
                r = Resource(conn, item._path, item._value)
            else:
                r = item
            items.append(r)
        if 'next' in response.links:
            params = {
                'connection': conn,
                'head': items,
                'response': response,
            }
            if 'seek' in response.links:
                return SeekablePaginatedList(**params)
            else:
                return PaginatedList(**params)
        else:
            return items
    else:
        # XXX: dunno what to do
        return decoded


def encode_resource(obj):
    if isinstance(obj, (Resource, Reference)):
        attribute = next((attribute for attribute
                          in ('key', 'uid', 'url', 'id')
                          if hasattr(obj, attribute)),
                         None)
        if attribute:
            return {attribute: getattr(obj, attribute)}
    raise exceptions.UnencodableValue(obj)
