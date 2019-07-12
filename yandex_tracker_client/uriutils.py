# coding: utf-8

import re

VARIABLE = re.compile(r'{([\w\d\-_\.]+)}')


class Matcher(object):

    def __init__(self):
        self._patterns = []

    def add(self, uri, resource, priority=0):
        parts = uri.strip('/').split('/')

        pattern_parts = []
        for part in parts:
            is_variable = VARIABLE.search(part)
            if is_variable:
                pattern_part = r'(?P<{0}>[\w\d\-\_\.]+)'.format(
                    is_variable.group(1)
                )
                pattern_parts.append(pattern_part)
            else:
                pattern_parts.append(part)

        pattern = re.compile('/'.join(pattern_parts))
        self._patterns.append((
            priority,
            pattern,
            resource
        ))

        #sort by priority
        self._patterns.sort(key=lambda it: it[0], reverse=True)  # ok for our N < 20

    def match(self, uri):
        path = uri.strip('/')
        for _, pattern, value in self._patterns:
            match = pattern.match(path)
            if match:
                return value
        return None
