import re
from collections import MutableSequence
from itertools import chain, zip_longest

from noscrapy.utils import Field, Type, json

from .selector import Selector

START_URLS_RE = re.compile(r'^(.*?)\[(\d+)\-(\d+)(:(\d+))?\](.*)$')

class Sitemap(MutableSequence, metaclass=Type):
    id = Field(None)
    ids = Field(fget='_ids', ro=True)
    possible_parent_ids = Field(fget='_possible_parent_ids', ro=True)
    columns = Field(fget='_columns', ro=True)
    has_recursive_selectors = Field(fget='_has_recursive_selectors', ro=True)
    start_urls = Field(fget='_get_start_urls', ro=True)

    parent_id = Field('_root')
    parent_item = Field(None)

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
        start_urls = features.pop('start_urls', ())
        start_urls = [start_urls] if isinstance(start_urls, str) else start_urls
        self._start_urls = list(start_urls)
        for value in features.pop('selectors', ()):
            try:
                self.append(value)
            except ValueError:
                pass
        for attr, value in features.items():
            setattr(self, attr, value.strip() if isinstance(value, str) else value)

    def __delitem__(self, value):
        unlinked_ids = []
        index = value if isinstance(value, (int, slice)) else self.selectors.index(value)
        selector_id = self.selectors[index].id
        for selector in self.selectors:
            selector.remove_parent(selector_id)
            if not selector.parents and selector_id != selector.id:
                unlinked_ids.append(selector.id)
        del self.selectors[index]
        for unlinked_id in unlinked_ids:
            del self[unlinked_id]

    def __getitem__(self, index):
        index = index if isinstance(index, (int, slice)) else self.selectors.index(index)
        return self.selectors[index]

    def get(self, index, default=None):
        try:
            return self[index]
        except ValueError:
            return default

    def __setitem__(self, index, value):
        index = index if isinstance(index, (int, slice)) else self.selectors.index(index)
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
        return {'id': self.id, 'selectors': self.selectors, 'parent_id': self.parent_id,
                'parent_item': self.parent_item}

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

    def get_data(self):
        for tree in self.trees:
            for results in self.get_selector_tree_data(tree, self.parent_id, self.parent_item):
                yield results

    @property
    def trees(self):
        """List of independent selector lists. follow=true splits selectors in trees.
        Two side by side type=multiple selectors split trees."""
        return self._find_trees(self.parent_id, [])

    def _find_trees(self, parent_id, common_selectors_from_parent):
        common_selectors = common_selectors_from_parent[:]
        common_selectors += self.get_selectors_common_to_all_trees(parent_id)

        # find selectors that will be making a selector tree
        trees = []
        childs = list(self.get_direct_childs(parent_id))
        for selector in childs:
            if self.selector_is_common_to_all_trees(selector):
                continue
            # this selector will be making a new selector tree.
            # But this selector might contain some child selectors that are making more trees,
            # so here should be a some kind of seperation for that
            tree = Sitemap(common_selectors + [selector])
            if selector.can_have_local_childs:
                # find selector tree within this selector
                trees.extend(self._find_trees(selector.id, tree))
            else:
                trees.append(tree)

        # it there were not any selectors that make a separate tree then all common selectors make up a single selector tree
        return trees or [Sitemap(common_selectors)]

    def get_selector_tree_data(self, tree, parent_id, parent_item, common_data=None):
        child_common_data = self.get_selector_tree_common_data(tree, parent_id, parent_item)
        common_data = dict(common_data or {}, **child_common_data)
        yielded = False
        for selector in tree.get_direct_childs(parent_id):
            if tree.will_return_many(selector.id):
                new_common_data = dict(common_data)
                for responses in self.get_many_selector_data(tree, selector, parent_item, new_common_data):
                    yield responses
                    yielded = True
        if not yielded and common_data:
            yield common_data

    def get_selectors_common_to_all_trees(self, parent_id):
        common_selectors = []
        for selector in self.get_direct_childs(parent_id):
            if self.selector_is_common_to_all_trees(selector):
                common_selectors.append(selector)
                # also add all childs which. Childs were also checked
                for child in self.get_all(selector.id):
                    if child not in common_selectors:
                        common_selectors.append(child)
        return common_selectors

    def selector_is_common_to_all_trees(self, selector):
        """The selector cannot return multiple records and it also cannot create new jobs.
        Also all of its child selectors must have the same features."""
        if selector.will_return_many:
            return False
        # Link selectors which will follow to a new page also cannot be common to all selectors
        if selector.can_create_new_jobs and self.get_direct_childs(selector.id):
            return False
        # also all child selectors must have the same features
        for child in self.get_all(selector.id):
            if not self.selector_is_common_to_all_trees(child):
                return False
        return True

    def get_selector_tree_common_data(self, tree, parent_id, parent_item):
        common_data = {}
        for child in tree.get_direct_childs(parent_id):
            if tree.will_return_many(child.id):
                continue
            for results in self.get_selector_common_data(tree, child, parent_item):
                common_data.update(results)
        return common_data

    def get_selector_common_data(self, tree, selector, parent_item):
        for data in selector.get_data(parent_item):
            if selector.will_return_items:
                yield self.get_selector_tree_common_data(tree, selector.id, data[0])
            else:
                yield data

    def get_many_selector_data(self, tree, selector, parent_item, common_data):
        """Returns all data records for a selector that can return multiple records."""
        # if the selector is not an Item selector then its fetched data is the result.
        if selector.will_return_items:
            # handle situation when this selector is an Item Selector
            for item in selector.get_data(parent_item):
                new_common_data = dict(common_data)
                for responses in self.get_selector_tree_data(tree, selector.id, item, new_common_data):
                    yield responses
        else:
            new_common_data = dict(common_data)
            for record in selector.get_data(parent_item):
                record.update(new_common_data)
                yield record

    def get_single_selector_data(self, parent_ids, selector_id):  # pragma: no cover
        # to fetch only single selectors data we will create a sitemap that only contains this
        # selector, his parents and all child selectors
        sitemap = self.sitemap.copy()
        selector = sitemap[selector_id]
        childs = sitemap.get_all(selector_id)
        parents = [sitemap[i] for i in parent_ids]
        for parent_id in parent_ids[::-1]:
            if parent_id == '_root':
                break
            parents.append(sitemap[parent_id])

        # merge all needed selectors together
        sitemap.clear()
        sitemap.extend(parents + childs + [selector])

        # find the parent that leaded to the page where required selector is being used
        for parent_id in parent_ids[::-1]:
            if parent_id == '_root':
                break
            parent = self.sitemap[parent_id]
            if parent.will_return_items:
                break
        sitemap.parent_id = parent_id
        yield from sitemap.get_data()
