from noscrapy.utils import json


def test_dumps():
    class Foo(object):
        def __getstate__(self):
            return {1: 2}

    foo = Foo()
    assert json.dumps(foo) == '{"1": 2}'
    assert json.dumps(Foo) == '"<class \'noscrapy.tests.test_utils_json.test_dumps.<locals>.Foo\'>"'
    assert json.dumps(1) == '1'
