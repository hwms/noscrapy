import re
from time import sleep

from noscrapy.utils import Field, PyQuery, Type, etree


class SelectorType(Type):
    def __new__(cls, name, bases, classdict):
        self = super().__new__(cls, name, bases, classdict)
        if not bases:
            self.__types__ = {name: self}
        elif name in Selector.__types__:
            raise TypeError('Only one selector type can be named %s' % name)
        else:
            Selector.__types__[name] = self
        return self

class Selector(metaclass=SelectorType):
    can_return_many = Field(True, ro=True)
    inline_many = Field(False, ro=True)
    can_have_childs = Field(False, ro=True)
    can_have_local_childs = Field(False, ro=True)
    can_create_new_jobs = Field(False, ro=True)
    will_return_items = Field(False, ro=True)
    columns = Field(fget='_get_columns', ro=True)
    will_return_many = Field(fget='_will_return_many', ro=True)

    id = Field()
    css = Field(None)
    parents = Field(default=lambda: ['_root'])
    many = Field(True)
    delay = Field(0)
    regex = Field(None)
    item_css = Field('*')

    def __new__(cls, *args, **features):
        for arg in (features,) + args[::-1]:
            if isinstance(arg, Selector):
                cls = type(arg)
            elif isinstance(arg, str) and arg in cls.__types__:
                cls = cls.__types__[arg]
            elif isinstance(arg, dict) and 'type' in arg:
                cls = cls.__types__[arg['type']]
        return super().__new__(cls)

    def __init__(self, *args, **features):
        for arg in args:
            if isinstance(arg, str):
                if arg not in self.__types__:
                    features['id'] = arg
            else:
                if isinstance(arg, Selector):
                    arg = arg.__getstate__()
                if isinstance(arg, dict):
                    features = dict(arg, **features)
        features.pop('type', None)
        for attr, value in features.items():
            setattr(self, attr, value.strip() if isinstance(value, str) else value)

    def __setattr__(self, attr, value):
        if attr.startswith('__') or attr in self.__fields__:
            return super().__setattr__(attr, value)
        raise AttributeError('field %s not known in %s' % (attr, type(self).__name__))

    def __eq__(self, other):
        if isinstance(other, str):
            return self.id == other
        if not isinstance(other, (dict, Selector)):
            return False
        cls = type(self)
        if isinstance(other, dict):
            other = cls(other)
        state = self.__getstate__()
        other_state = other.__getstate__()
        return state == other_state

    def __repr__(self):
        kws = [repr(self.id)]
        for k, v in sorted(self.__getstate__().items()):
            if k not in ('id', 'type'):
                kws.append('%s=%r' % (k, v))
        return '%s(%s)' % (type(self).__name__, ', '.join(kws))

    def __getstate__(self):
        cls = type(self)
        state = {'type': cls.__name__}
        for field in (getattr(cls, n) for n in cls.__fields__):
            if field.fget or field.ro:
                continue
            value = field.__get__(self)
            if field.attr == 'parents' and value == ['_root']:
                continue
            default = field.default
            if value == default or (callable(default) and default() == value):  # pragma: no cover
                continue
            state[field.attr] = value
        return state

    def copy(self):
        return Selector(self)

    def _will_return_many(self):
        return self.can_return_many and self.many

    def _get_columns(self):
        return self.id,

    def has_parent(self, parent_id):
        return parent_id in self.parents

    def remove_parent(self, parent_id):
        try:
            self.parents.remove(parent_id)
        except ValueError:
            pass

    def rename_parent(self, parent_id, new_id):
        try:
            index = self.parents.index(parent_id)
            self.parents[index] = new_id
        except ValueError:
            pass

    def get_items(self, parent_item):
        if not isinstance(parent_item, PyQuery):
            try:
                parent_item = PyQuery(parent_item)
            except (etree.ParserError, etree.XMLSyntaxError) as e:  # pragma: no cover
                if isinstance(parent_item, str) and (not parent_item.strip() or
                                                     'Document is empty' == str(e)):
                        parent_item = PyQuery(None)
                else:
                    raise
        if parent_item and isinstance(parent_item[0], str):
            return
        query = parent_item(self.css)
        for item in query.items():
            yield item
            if not self.many:
                break

    def get_data(self, parent_item):
        sleep(int(self.delay or 0))
        yield from self._get_data(parent_item)

    def _get_data(self, parent_item):
        if self.inline_many:
            results = []
        yielded = False
        for item in self.get_items(parent_item):
            for data in self._get_item_data(item):
                if self.regex:
                    matches = re.search(self.regex, data[self.id])
                    data[self.id] = matches.group() if matches else None
                if self.inline_many:
                    results.append(data)
                else:
                    yield data
                    yielded = True
            if yielded and not self.many:
                break
        if self.inline_many:
            yield {self.id: tuple(results)}
        elif not yielded:
            yield from self._get_noitems_data()

    def _get_item_data(self, item):
        raise NotImplementedError

    def _get_noitems_data(self):
        yield {self.id: None}
