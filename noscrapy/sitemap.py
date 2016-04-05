import re
from collections import MutableSequence
from itertools import zip_longest, chain

from noscrapy.utils import Field, json, Type

from .selector import Selector

START_URLS_RE = re.compile(r'^(.*?)\[(\d+)\-(\d+)(:(\d+))?\](.*)$')

class Sitemap(MutableSequence, metaclass=Type):
    id = Field(None)
    ids = Field(fget='_ids', ro=True)
    possible_parent_ids = Field(fget='_possible_parent_ids', ro=True)
    columns = Field(fget='_columns', ro=True)
    has_recursive_selectors = Field(fget='_has_recursive_selectors', ro=True)
    start_urls = Field(fget='_get_start_urls', ro=True)

    def __init__(self, *args, **features):
        self.selectors = []
        for arg in args:
            if isinstance(arg, str):
                features['id'] = arg
            if isinstance(arg, Selector):
                features['selectors'] = [arg]
            elif isinstance(arg, Sitemap):
                features = dict(arg.__getstate__(), **features)
            elif isinstance(arg, dict):
                features = dict(arg, **features)
            else:
                features['selectors'] = list(arg)
        self.id = features.get('id', self.id)
        start_urls = features.get('start_urls', ())
        start_urls = [start_urls] if isinstance(start_urls, str) else start_urls
        self._start_urls = list(start_urls)
        for value in features.get('selectors', ()):
            try:
                self.append(value)
            except ValueError:
                pass

    def __delitem__(self, value):
        unlinked_ids = []
        index = value if isinstance(value, int) else self.selectors.index(value)
        selector_id = self.selectors[index].id
        for selector in self.selectors:
            selector.remove_parent(selector_id)
            if not selector.parents and selector_id != selector.id:
                unlinked_ids.append(selector.id)
        del self.selectors[index]
        for unlinked_id in unlinked_ids:
            del self[unlinked_id]

    def __getitem__(self, index):
        index = index if isinstance(index, int) else self.selectors.index(index)
        return self.selectors[index]

    def get(self, index, default=None):
        try:
            return self[index]
        except ValueError:
            return default

    def __setitem__(self, index, value):
        index = index if isinstance(index, int) else self.selectors.index(index)
        current = self.selectors[index]
        selector = Selector(value)
        if current.id != selector.id:
            if selector.id in self.selectors:
                raise ValueError('Id %r is already taken' % selector.id)
        self.selectors[index] = selector
        if current.id != selector.id:
            self._rename_parents(current.id, selector.id)

    def insert(self, index, value):
        selector = Selector(value)
        if selector.id in self.selectors:
            raise ValueError('Id %r is already taken' % selector.id)
        self.selectors.insert(index, selector)

    def __len__(self):
        return len(self.selectors)

    def __eq__(self, other):
        marker = object()
        for a, b in zip_longest(self, other, fillvalue=marker):
            if a != b:
                return False
        return True

    def __repr__(self):
        reprs = [repr(o) for o in self]
        return '%s(%r, [%s])' % (type(self).__name__, self.id, ', '.join(reprs))

    def __getstate__(self):
        return {'id': self.id, 'selectors': self.selectors}

    __setstate__ = __init__

    def copy(self):
        return self.__class__(self.__getstate__())

    def concat(self, *other_lists):
        result = self.copy()
        for other_list in other_lists:
            result.extend(other_list)
        return result

    def _ids(self):
        return ('_root',) + tuple(s.id for s in self)

    def _possible_parent_ids(self):
        return ('_root',) + tuple(s.id for s in self if s.can_have_childs)

    def _columns(self):
        return tuple(chain.from_iterable(s.columns for s in self))

    def get_all(self, parent_id=None):
        """Returns all or recursively all childs of a parent."""
        if not parent_id:
            yield from self.selectors
            return

        results = set()
        def get_childs(parent_id):
            for pos, selector in enumerate(self):
                if pos not in results and selector.has_parent(parent_id):
                    results.add(pos)
                    get_childs(selector.id)
        get_childs(parent_id)
        for pos in sorted(results):
            yield self[pos]

    def get_direct_childs(self, parent_id):
        """Returns only selectors that are directly under a parent."""
        for selector in self:
            if selector.has_parent(parent_id):
                yield selector

    def get_one_page_selectors(self, selector_id):
        selector = self.get(selector_id)
        results = [selector]
        # recursively find all parents that could lead to the page where selector_id is used.
        def find_parents(selector):
            for parent_id in selector.parents:
                if parent_id == '_root':
                    return
                parent = self.get(parent_id)
                if parent not in results and parent.will_return_items:
                    results.append(parent)
                    find_parents(parent)
        find_parents(selector)
        results += self.get_one_page_childs(selector.id)
        results = sorted(self.index(s) for s in results)
        for pos in sorted(results):
            yield self[pos]

    def get_one_page_childs(self, parent_id):
        """Returns all child selectors of a selector which can be used within one page."""
        results = []
        def add_childs(parent):
            if not parent.will_return_items:
                return
            for child in self.get_direct_childs(parent.id):
                results.append(child)
                add_childs(child)
        add_childs(self.get(parent_id))
        results = sorted(self.index(s) for s in results)
        for pos in sorted(results):
            yield self[pos]

    def will_return_many(self, selector_id):
        selector = self.get(selector_id)
        if selector.will_return_many:
            return True
        for child_selector in self.get_all(selector_id):
            if child_selector.will_return_many:
                return True
        return False

    def get_one_page_css(self, selector_id, parent_ids):
        """Return css selector for a given element which includes all parent element selectors.
        parent_ids: array of parent selector ids from devtools Breadcumb."""
        css = self.get(selector_id).css
        parent_css = self.get_one_page_parent_css(parent_ids)
        return ' '.join(s for s in (parent_css, css) if s)

    def get_one_page_parent_css(self, parent_ids):
        """Return css selector for parent selectors that are within one page.
        parent_ids: array of parent selector ids from devtools Breadcumb."""
        css_deque = []
        for parent_id in parent_ids:
            parent_selector = self.get(parent_id)
            if parent_selector and parent_selector.will_return_items:
                css_deque.append(parent_selector.css)
        return ' '.join(s for s in css_deque if s)

    def _has_recursive_selectors(self):
        recursion_found = [False]
        for top_selector in self:
            visited = []
            def check_recursion(parent_selector):
                if parent_selector in visited:
                    recursion_found[0] = True
                    return
                elif parent_selector.will_return_items:
                    visited.append(parent_selector)
                    for child in self.get_direct_childs(parent_selector.id):
                        check_recursion(child)
                    visited.remove(parent_selector)
            check_recursion(top_selector)
        return recursion_found[0]

    def _rename_parents(self, current_id, new_id):
        for selector in self:
            selector.rename_parent(current_id, new_id)

    def _get_start_urls(self):
        for url in self._start_urls:
            matches = START_URLS_RE.match(url)
            matches = matches.groups() if matches else None
            if matches:
                step = int(matches[4] or 1)
                start_str, stop_str = matches[1], matches[2]
                start, stop = int(start_str), int(stop_str) + step
                lpad = len(start_str) if len(start_str) == len(stop_str) else 1
                fmt = '%s%%0%dd%s' % (matches[0], lpad, matches[5])
                for i in range(start, stop, step):
                    yield fmt % i
            else:
                yield url

    def get_csv_rows(self, row_dicts):
        headers = self.columns
        yield headers
        for row_dict in row_dicts:
            csv_row = []
            for header in headers:
                cell = row_dict.get(header, '')
                if not isinstance(cell, str):
                    cell = json.dumps(cell)
                csv_row.append(cell)
            yield tuple(csv_row)
