# coding: utf-8

import random
import string


def random_id():
    id_ = ''.join([random.choice(string.ascii_lowercase + string.digits)
                   for _ in range(24)])

    random_id._last_res = id_
    return id_


class FakeObject(object):
    @property
    def json(self):
        return self._json
