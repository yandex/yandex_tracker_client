# coding: utf-8

from __future__ import unicode_literals

from common.url import api_url


def test_field_category_create(net_mock, client, fake_field_category, mocked_fake_field_categories):
    data = {
        "name": {
            "en": "Test Field Category",
            "ru": "Тестовая Категория",
        },
        "description": "Test Description",
    }

    net_mock.post(api_url('/fields/categories/'), json=fake_field_category.json)

    mocked_fake_field_categories.create(**data)
    real_request = net_mock.request_history[0].json()
    assert real_request == data
