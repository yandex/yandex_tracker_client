# coding: utf-8

import random

import pytest

from common.url import api_url


@pytest.fixture
def attachments(net_mock, mocked_fake_issue, fake_issue):
    net_mock.get(api_url('/issues/{}/attachments/'.format(fake_issue.key)),
                 json=fake_issue.attachments)

    return list(mocked_fake_issue.attachments)


@pytest.fixture
def random_attachment_num(fake_issue):
    return random.randint(0, len(fake_issue.attachments) - 1)
