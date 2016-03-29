import keyword
from itertools import chain, zip_longest

from pyquery import pyquery
from pyquery.pyquery import no_default

__all__ = 'attribute_mapper', 'PyQuery'

class FlexibleElement(pyquery.FlexibleElement):
    """property to allow a flexible api"""
    def __init__(self, pget, pset=no_default, pdel=no_default,
                 pdir=no_default):
        super().__init__(pget, pset, pdel)
        self.pdir = pdir

    def __get__(self, instance, klass):
        class _element(object):
            """real element to support set/get/del attr and item and js call
            style"""
            def __call__(prop, *args, **kwargs):  # @NoSelf
                return self.pget(instance, *args, **kwargs)
            __getattr__ = __getitem__ = __setattr__ = __setitem__ = __call__

            def __delitem__(prop, name):  # @NoSelf
                if self.pdel is not no_default:
                    return self.pdel(instance, attribute_mapper.to_xml(name))
                else:
                    raise NotImplementedError()  # pragma: no cover
            __delattr__ = __delitem__

            def __repr__(prop):  # @NoSelf
                return '<flexible_element %s>' % self.pget.__name__

            def __dir__(prop):  # @NoSelf
                if self.pdir is not no_default:
                    return self.pdir(instance) + super().__dir__()
                return super().__dir__()  # pragma: no cover
        return _element()


class PyQuery(pyquery.PyQuery):
    #########################################
    # Extended methods from the pyquery API #
    #########################################
    def _attr(self, *args, **kwargs):
        """Attributes manipulation.

        Same code as in pyquery, just replaced mapping with attribute_mapper.
        This allows:
            - additional access for '-' containing attributes, like data-xy as data_xy
            - and access to all attributes named like python keywords by using suffix '_'.
        """
        mapping = attribute_mapper

        attr = value = no_default
        length = len(args)
        if length == 1:
            attr = args[0]
            attr = mapping.to_xml(attr)
        elif length == 2:
            attr, value = args
            attr = mapping.to_xml(attr)
        elif kwargs:
            attr = {}
            for k, v in kwargs.items():
                attr[mapping.to_xml(k)] = v
        else:
            raise ValueError('Invalid arguments %s %s' % (args, kwargs))

        if not self:
            return None  # pragma: no cover don't know when this could be the case
        elif isinstance(attr, dict):
            for tag in self:
                for key, value in attr.items():
                    tag.set(key, value)
        elif value is no_default:
            return self[0].get(attr)
        elif value is None or value == '':
            return self.remove_attr(attr)
        else:
            for tag in self:
                tag.set(attr, value)
        return self

    def _attrs(self):
        return sorted(set(a.replace('-', '_')
                          for a in chain.from_iterable(t.attrib.keys() for t in self)))

    attrs = property(_attrs)
    attr = FlexibleElement(pget=_attr, pdel=pyquery.PyQuery.remove_attr, pdir=_attrs)

    ######################################################
    # Additional methods that are not in the pyquery API #
    ######################################################
    def map_items(self, func, selector=None):
        results = []
        items = list(self.items(selector))
        count = len(items)
        argcount = pyquery.func_code(func).co_argcount
        for index, item in enumerate(items):
            args = item, index, count
            result = func(*args[:argcount])
            if result is None:
                continue
            if isinstance(result, list):
                results.extend(result)
                continue
            results.append(result)  # pragma: no cover , not testable for now
        return self.__class__(results, **dict(parent=self))

    def __eq__(self, other):
        if isinstance(other, str):
            other = type(self)(other)
        if isinstance(other, list):
            for e1, e2 in zip_longest(self, other):
                if e1 != e2 and (e1 is None or e2 is None or not elements_equal(e1, e2)):
                    return False
            return True
        return False

    def __ne__(self, other):
        return not self == other

class AttributeMapper(object):
    def to_xml(self, name):
        name = name.replace('_', '-')
        if name.endswith('-'):
            name = name[:-1]
        return name

    def to_python(self, name):
        name = name.replace('-', '_')
        if name.endswith('_'):
            name = name[:-1]
        if keyword.iskeyword(name):
            name += '_'
        return name

attribute_mapper = AttributeMapper()
del AttributeMapper

def elements_equal(e1, e2, compare_tail=True):
    """Compares to elements from lxml.
    http://stackoverflow.com/questions/7905380/testing-equivalence-of-xml-etree-elementtree.
    """
    if e1.tag != e2.tag:
        return False
    if e1.text != e2.text:
        return False
    if compare_tail and e1.tail != e2.tail:
        return False
    if e1.attrib != e2.attrib:
        return False
    if len(e1) != len(e2):
        return False
    return all(elements_equal(c1, c2) for c1, c2 in zip_longest(e1, e2))
