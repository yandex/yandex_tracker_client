# coding: utf-8
from setuptools import setup

setup(
    name='yandex_tracker_client',
    version='1.0',
    description='Client for Yandex.Tracker',
    author='Yandex Team',
    author_email='smosker@yandex-team.ru',
    url='https://github.com/yandex/yandex-tracker-client',
    packages=['yandex_tracker_client'],
    install_requires=[
        'requests[security]>=2.0',
        'setuptools',
        'six>=1.9',
    ]
)
