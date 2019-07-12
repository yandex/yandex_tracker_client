# coding: utf-8

import os
import json
from codecs import open

import requests_mock

from .url import api_url


def backend_response(file):
    with open(
            os.path.join(os.path.dirname(__file__), 'backend_responses', file),
            encoding='utf-8') as f:
        return json.load(f)


def base_mock():
    m = requests_mock.mock()
    m.get(api_url('/fields/'), json=backend_response('fields.json'))
    return m
