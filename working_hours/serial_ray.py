"""A serial stand-in for the few ray calls the hours stage makes.

ray's raylet would not start on the build machine on 2026-11-06 (the object
store's CreateFileMapping failed with Windows error 1450, then a worker died
with an access violation once it did start with a smaller store). With
LABOR_NO_RAY=1 the hours modules import this instead of ray: `init` and
`shutdown` do nothing, `remote(f).remote(*args)` runs `f` at once on deep
copies of its arguments (a ray task works on its own deserialised copy, so a
function that modifies its input must not see another call's changes), and
`get` returns what it is given. Same functions, same order, so the same
result as the ray run.
"""
from __future__ import annotations

import copy


def init(*args, **kwargs):
    return None


def shutdown(*args, **kwargs):
    return None


class _Remote:
    def __init__(self, func):
        self._func = func

    def remote(self, *args, **kwargs):
        return self._func(*copy.deepcopy(args), **copy.deepcopy(kwargs))

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)


def remote(*args, **kwargs):
    if len(args) == 1 and callable(args[0]) and not kwargs:
        return _Remote(args[0])
    return lambda func: _Remote(func)


def get(refs, *args, **kwargs):
    return refs


def put(value, *args, **kwargs):
    return value
