from abc import ABCMeta
from collections import OrderedDict
from itertools import chain
from types import FunctionType

__all__ = 'Object', 'Field', 'Type'

NOTSET = object()

class Field(object):
    """Class descriptor which enables declarative configuration.

        default: Value to be returned if attr isn't in instance dict.
                 Can also be a callable without parameters, eg. list.
        name: Name/Title for display of the field, same as attr if not set.
        desc: Description for display of the field, same as name if not set.
        attr: Gets set by metaclass to the attribute name on the class.
        ro: Readonly flag prohibiting setting the resulting value to the instance dict.
        fget/fset/fdel: Function or name of a function defined on the class.
                        Same behaviour like a property, but as Field replicated per class
    """
    __slots__ = 'default', 'name', 'desc', 'attr', 'ro', 'fget', 'fset', 'fdel', 'cls'

    def __init__(self, default=NOTSET, name=NOTSET, desc=NOTSET, attr=NOTSET, ro=False,
                 fget=None, fset=None, fdel=None):
        self.default = default
        self.name = name
        self.desc = desc
        self.attr = attr
        self.ro = ro
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.cls = None

    def _setup(self, cls, attr=NOTSET, default=NOTSET, base=NOTSET):
        self.cls = cls
        def setfattr(fattr, *values):
            for value in (v for v in values if v is not NOTSET):
                setattr(self, fattr, value)
                break

        setfattr('attr', attr, self.attr, getattr(base, 'attr', NOTSET))
        setfattr('default', default, self.default, getattr(base, 'default', NOTSET))
        setfattr('name', self.name, getattr(base, 'name', NOTSET), self.attr)
        setfattr('desc', self.desc, getattr(base, 'desc', NOTSET), self.name)
        return self

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.attr, self.default)
        if value is NOTSET:
            if not self.fget:
                raise ValueError('No default value given for Field %s' % self.attr)
            else:
                value = self.fget(obj)
        elif callable(value):
            value = value()
        if not self.ro:
            setattr(obj, self.attr, value)
        return value

    def __set__(self, obj, value):
        if self.ro:
            raise AttributeError('can not set readonly attribute %s' % self.attr)
        if self.fset:
            self.fset(obj, value)
        else:
            obj.__dict__[self.attr] = value

    def __delete__(self, obj):
        if self.ro:
            raise AttributeError('can not delete readonly attribute %s' % self.attr)
        if self.fdel:
            self.fdel(obj)
        else:
            obj.__dict__.pop(self.attr, None)

    def clone(self, cls, attr=NOTSET, default=NOTSET, base=NOTSET):
        return type(self)(self.default, self.name, self.desc, self.attr, self.ro, self.fget,
                          self.fset, self.fdel)._setup(cls, attr, default, base)

    def __repr__(self):
        return '<%s %s.%s>' % (self.__class__.__name__, self.cls.__name__, self.attr)

class Type(ABCMeta):
    """Type to add __attrs__ and __fields__ attributes."""
    @classmethod
    def __prepare__(cls, name, bases):
        return OrderedDict()

    def __new__(cls, name, bases, classdict):
        self = super().__new__(cls, name, bases, dict(classdict))

        attrs_lists = [getattr(b, '__attrs__', ()) for b in bases]
        attrs_lists += [[a for a in classdict if not a.startswith('__')]]
        # use ordered dict like an ordered set
        self.__attrs__ = tuple(OrderedDict.fromkeys(chain.from_iterable(attrs_lists)))

        base_fields = {}
        for base in bases:
            for attr in getattr(base, '__fields__', ()):
                if attr not in base_fields:
                    base_fields[attr] = getattr(base, attr).clone(self)
        fields = {}
        for attr, value in list(classdict.items()):
            if attr.startswith('__'):
                continue
            if isinstance(value, Field):
                fields[attr] = value._setup(self, attr, base=base_fields.get(attr, NOTSET))
            elif attr in base_fields:
                fields[attr] = base_fields[attr].clone(self, default=value)

        for attr, base_field in base_fields.items():
            if attr not in fields:
                fields[attr] = base_field.clone(self)

        for attr, field in fields.items():
            for prop_name in ('fget', 'fset', 'fdel'):
                prop_value = getattr(field, prop_name)
                if isinstance(prop_value, FunctionType):
                    prop_value = prop_value.__name__
                if isinstance(prop_value, str):
                    prop_value = getattr(self, prop_value)
                    setattr(field, prop_name, prop_value)
            setattr(self, attr, field)

        self.__fields__ = tuple(a for a in self.__attrs__ if a in fields)
        return self

class Object(metaclass=Type):
    """Class with extra attributes:

        __attrs__ contains all attribute names in order of assignment.
        __fields__ contains only the names of Field descriptor instances.
    """
    pass
