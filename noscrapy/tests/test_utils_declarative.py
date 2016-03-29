import pytest

from noscrapy.utils import Object, Field

def test_object_attrs_is_ordered():
    class A(Object):
        b = 1
        a = 2

    assert A.__attrs__ == ('b', 'a')
    assert (A.b, A.a) == (1, 2)

def test_object_attrs_in_subclass():
    class B(Object):
        b = 1
        a = 2

    class A(B):
        c = 4
        a = 3

    assert A.__attrs__ == ('b', 'a', 'c')
    assert (A.b, A.c, A.a) == (1, 4, 3)

def test_object_attrs_in_mixed_in():
    class B(Object):
        b = 1
        a = 2
        d = 5

    class C(B):
        b = 3
        d = 8

    class A(C, B):
        c = 7
        d = 4

    assert A.__attrs__ == ('b', 'a', 'd', 'c')
    assert (A.b, A.a, A.d, A.c) == (3, 2, 4, 7)

def test_fields():
    class A(Object):
        b = Field(1)
        a = Field(2, name='A')

    class B(A):
        c = Field(list)
        a = Field(4)
        d = Field(5, ro=True)
        e = Field()

    class C(B):
        a = 6
        f = Field(fget='getf', fset='setf', fdel='delf')
        def setf(self, value):
            self._f = value
        def getf(self):
            return self._f
        def delf(self):
            del self._f

    assert hasattr(A, '__fields__')
    assert hasattr(B, '__fields__')
    assert hasattr(C, '__fields__')

    assert ('b', 'a') == A.__fields__
    assert ('b', 'a', 'c', 'd', 'e') == B.__fields__
    assert ('b', 'a', 'c', 'd', 'e', 'f') == C.__fields__

    assert repr(A.b) == '<Field A.b>'
    assert A.b.attr == 'b'
    assert A.b.default == 1
    assert A.b.name == 'b'
    assert A.b.desc == 'b'
    assert A.b.cls == A

    assert A.a.attr == 'a'
    assert A.a.default == 2
    assert A.a.name == 'A'
    assert A.a.desc == 'A'
    assert A.a.cls == A

    assert B.b is not A.b
    assert B.b.attr == 'b'
    assert B.b.default == 1
    assert B.b.name == 'b'
    assert B.b.desc == 'b'
    assert B.b.cls == B

    assert B.a is not A.a
    assert B.a.attr == 'a'
    assert B.a.default == 4
    assert B.a.name == 'A'
    assert B.a.desc == 'A'
    assert B.a.cls == B

    assert C.a is not B.a
    assert C.a.attr == 'a'
    assert C.a.default == 6
    assert C.a.name == 'A'
    assert C.a.desc == 'A'
    assert C.a.cls == C

    instance = B()

    assert instance.c == []
    instance.c.append(1)
    assert instance.c == [1]
    instance.c = 6
    assert instance.c == 6
    del instance.c
    assert instance.c == []
    instance.c.append(1)
    assert instance.c == [1]
    del instance.c
    assert instance.c == []

    assert instance.d == 5
    with pytest.raises(AttributeError):
        instance.d = 6
    with pytest.raises(AttributeError):
        del instance.d

    with pytest.raises(ValueError):
        instance.e
    instance.e = 7
    assert instance.e == 7

    instance = C()
    with pytest.raises(AttributeError):
        instance.f
    instance.f = 1
    assert instance._f == 1
    assert instance.f == 1
    assert 'f' not in instance.__dict__
    del instance.f
    assert '_f' not in instance.__dict__
    with pytest.raises(AttributeError):
        instance.f
