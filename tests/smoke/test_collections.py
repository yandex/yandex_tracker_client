# coding: utf-8

import inspect

from yandex_tracker_client.settings import VERSION_V2


def test_url_slots():
    from yandex_tracker_client import collections as colls
    for attr in dir(colls):
        obj = getattr(colls, attr)

        is_coll = (
            inspect.isclass(obj)
            and
            obj != colls.Collection
            and
            obj != colls.Unknown
            and
            issubclass(obj, colls.Collection)
        )

        if is_coll:
            url_params = dict.fromkeys(obj.url_slots, '')
            # тут проверяем, что слотов достаточно
            try:
                obj.path.format(**url_params)
            except Exception:
                print(attr)
                raise
            # тут, что нет лишних
            assert all('{%s}' % p in obj.path for p in obj.url_slots), obj.__name__


def test_extract_url_params():
    from yandex_tracker_client.collections import Collection

    class TestColl(Collection):
        path = '/{api_version}/{id}'
        url_slots = {'id'}
        fields = {}

    coll = TestColl('con', id=1)

    assert coll._extract_params({'foo': 2}) == ({'id': 1, 'api_version': VERSION_V2}, {}, {'foo': 2})
    assert coll._extract_params({'id': 3}) == ({'id': 3, 'api_version': VERSION_V2}, {}, {})
    assert coll._extract_params({'foo': 2, 'id': 3}) == ({'id': 3, 'api_version': VERSION_V2}, {}, {'foo': 2})
    assert coll._extract_params({'foo': 2, 'id': 3, 'x_org_id': 278}) == ({'id': 3, 'api_version': VERSION_V2}, {'X-ORG-ID': '278'}, {'foo': 2})

    coll = TestColl('con')

    assert coll._extract_params({'foo': 2}) == ({'id': '', 'api_version': VERSION_V2}, {}, {'foo': 2})
    assert coll._extract_params({'id': 3}) == ({'id': 3, 'api_version': VERSION_V2}, {}, {})
    assert coll._extract_params({'id': 3, 'x_org_id': 278}) == ({'id': 3, 'api_version': VERSION_V2}, {'X-ORG-ID': '278'}, {})
