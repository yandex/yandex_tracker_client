# coding: utf-8

from .config import config


def api_url(path):
    return '{}{}'.format(config.api_url, path)
