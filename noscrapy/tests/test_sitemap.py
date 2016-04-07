import pytest

from noscrapy import ItemSelector, LinkSelector, Selector, Sitemap, TextSelector, json


def test_init():
    dicts = [dict(id='a', type='TextSelector')]
    sitemap = Sitemap('m', dicts)
    assert list(sitemap)
    assert isinstance(sitemap[0], Selector)
    assert sitemap.ids == ('_root', 'a')
    # create selector instances from dicts
    assert sitemap[0] == Selector(dicts[0])
    # ignore repeating selectors
    assert sitemap == Sitemap(dicts + dicts)
    # create selectors list from one selector
    assert Sitemap(Selector(dicts[0]))[0] == Selector(dicts[0])
    # create sitemap from other sitemap
    assert Sitemap(sitemap) == sitemap

def test_setitem():
    sitemap = Sitemap([dict(id='a', type='TextSelector'), dict(id='b', type='TextSelector')])
    sitemap[0] = dict(id='c', type='TextSelector')
    assert sitemap == [dict(id='c', type='TextSelector'), dict(id='b', type='TextSelector')]

    with pytest.raises(ValueError):
        sitemap[0] = dict(id='b', type='TextSelector')

def test_eq():
    dicts = [dict(id='a', type='TextSelector'), dict(id='b', type='TextSelector')]
    sitemap = Sitemap(dicts)
    assert sitemap == Sitemap(dicts)
    assert sitemap != Sitemap(reversed(dicts))
    assert sitemap != Sitemap(dicts[:1])

def test_repr():
    dicts = [dict(id='a', type='TextSelector'), dict(id='b', type='TextSelector')]
    sitemap = Sitemap('l', dicts)
    assert repr(sitemap) == \
        "Sitemap('l', [TextSelector('a'), TextSelector('b')])"

def test_copy():
    sitemap = Sitemap([dict(id='a', type='TextSelector')])
    result_list = sitemap.copy()
    assert sitemap == result_list
    assert sitemap is not result_list
    assert sitemap[0] == result_list[0]
    assert sitemap[0] is not result_list[0]
    sitemap.pop()
    assert len(sitemap) == 0
    assert len(result_list) == 1

def test_concat():
    sitemapa = Sitemap([dict(id='a', type='TextSelector')])
    sitemapb = Sitemap([dict(id='b', type='TextSelector')])
    sitemapc = Sitemap([dict(id='c', type='TextSelector')])
    result_list = sitemapa.concat(sitemapb, sitemapc)
    assert result_list == [sitemapa[0], sitemapb[0], sitemapc[0]]

def test_possible_parent_ids():
    dicts = [dict(id='a', type='ItemSelector'),
             dict(id='b', type='GroupSelector'),
             dict(id='c', type='HtmlSelector'),
             dict(id='d', type='ImageSelector'),
             dict(id='e', type='LinkSelector'),
             dict(id='f', type='TextSelector'),
             ]
    sitemap = Sitemap(selectors=dicts)
    assert sitemap.possible_parent_ids == ('_root', 'a', 'e')

def test_get_all():
    child_dicts = [
        dict(id='a', type='ItemSelector', parents=['_root', 'c']),
        dict(id='b', type='ItemSelector', parents=['a']),
        dict(id='c', type='ItemSelector', parents=['b']),
    ]
    all_dicts = child_dicts + [
        dict(id='d', type='ItemSelector'),
    ]
    sitemap = Sitemap(all_dicts)
    # return all selectors
    assert list(sitemap.get_all()) == all_dicts
    # return all childs of a parent
    assert list(sitemap.get_all('a')) == child_dicts

def test_get_direct_childs():
    expected_dicts = [
        dict(id='b', type='ItemSelector', parents=['a']),
        dict(id='c', type='ItemSelector', parents=['a']),
    ]
    dicts = expected_dicts + [
        dict(id='a', type='ItemSelector', parents=['_root', 'c']),
        dict(id='d', type='ItemSelector'),
    ]
    actual_selectors = list(Sitemap(dicts).get_direct_childs('a'))
    assert actual_selectors == expected_dicts

def test_will_return_many():
    sitemap = Sitemap([
        dict(id='a', type='ItemSelector', many=False),
        dict(id='b', type='ItemSelector', parents=['a'], many=True),
        dict(id='c', type='ItemSelector', parents=['b'], many=True),
    ])
    assert sitemap.will_return_many('a')

    sitemap = Sitemap([
        dict(id='a', type='ItemSelector', many=True),
        dict(id='b', type='ItemSelector', parents=['a'], many=False),
        dict(id='c', type='ItemSelector', parents=['b'], many=False),
    ])
    assert sitemap.will_return_many('a')

    sitemap = Sitemap([
        dict(id='a', type='ItemSelector', many=False),
        dict(id='b', type='ItemSelector', parents=['a'], many=False),
        dict(id='c', type='ItemSelector', parents=['b'], many=False),
    ])
    assert not sitemap.will_return_many('a')

def test_json():
    dicts = [dict(id='a', type='ItemSelector', many=False)]
    sitemap = Sitemap('l', dicts)

    js_dicts = json.loads(json.dumps(sitemap))
    assert js_dicts == {'id': 'l', 'selectors': dicts, 'parent_id': '_root', 'parent_item': None}

    result_list = Sitemap(js_dicts)
    assert result_list == sitemap

def test_get_one_page_childs():
    expected_dicts = [
        dict(id='child1', type='TextSelector', parents=['parent2'], many=False),
        dict(id='child2', type='TextSelector', parents=['parent2'], many=False),
        dict(id='child3', type='ItemSelector', parents=['parent2'], many=False),
        dict(id='child4', type='ItemSelector', parents=['child3'], many=False),
        dict(id='child5', type='TextSelector', parents=['child4'], many=False),
        dict(id='link', type='LinkSelector', parents=['child3'], many=False),
    ]
    sitemap = Sitemap(expected_dicts + [
        dict(id='parent2', type='ItemSelector', many=True),
        dict(id='ignore1', type='TextSelector', parents=['link'], many=False),
        dict(id='ignore2', type='TextSelector', parents=['link'], many=False),
        dict(id='ignore_root', type='TextSelector', many=False),
        dict(id='ignore_parent1', type='TextSelector', parents=['parent1'], many=False),
    ])
    page_child_selectors = list(sitemap.get_one_page_childs('parent2'))
    assert page_child_selectors == expected_dicts

def test_get_one_page_selectors():
    expected_dicts = [
        dict(id='parent1', type='ItemSelector', many=True),
        dict(id='parent2', type='ItemSelector', parents=['parent1'], many=False),
        dict(id='child1', type='TextSelector', parents=['parent2'], many=False),
        dict(id='child2', type='TextSelector', parents=['parent2'], many=False),
        dict(id='child3', type='ItemSelector', parents=['parent2'], many=False),
        dict(id='child4', type='ItemSelector', parents=['child3'], many=False),
        dict(id='child5', type='TextSelector', parents=['child4'], many=False),
        dict(id='link', type='LinkSelector', parents=['parent2'], many=False),
    ]
    sitemap = Sitemap(expected_dicts + [
        dict(id='ignore1', type='TextSelector', parents=['link'], many=False),
        dict(id='ignore2', type='TextSelector', parents=['link'], many=False),
        dict(id='ignore_root', type='TextSelector', many=False),
        dict(id='ignore_parent1', type='TextSelector', parents=['parent1'], many=False),
    ])
    page_child_selectors = list(sitemap.get_one_page_selectors('parent2'))
    assert page_child_selectors == expected_dicts

def test_get_one_page_css():
    sitemap = Sitemap([
        dict(id='div', type='TextSelector', css='div'),
    ])
    css = sitemap.get_one_page_css('div', ['_root'])
    assert css == 'div'

    sitemap = Sitemap([
        dict(id='parent1', type='ItemSelector', css='div.parent'),
        dict(id='div', type='TextSelector', css='div'),
    ])
    css = sitemap.get_one_page_css('div', ['_root', 'parent1'])
    assert css == 'div.parent div'

    sitemap = Sitemap([
        dict(id='parent2', type='ItemSelector', css='div.parent2'),
        dict(id='parent1', type='ItemSelector', css='div.parent'),
        dict(id='div', type='TextSelector', css='div'),
    ])
    css = sitemap.get_one_page_css('div', ['_root', 'parent2', 'parent1'])
    assert css == 'div.parent2 div.parent div'

    sitemap = Sitemap([
        dict(id='parent2', type='LinkSelector', css='div.parent2'),
        dict(id='parent1', type='ItemSelector', css='div.parent'),
        dict(id='div', type='TextSelector', css='div'),
    ])
    css = sitemap.get_one_page_css('div', ['_root', 'parent2', 'parent1'])
    assert css == 'div.parent div'

def test_get_one_page_parent_css():
    sitemap = Sitemap([
        dict(id='parent2', type='ItemSelector', css='div.parent2'),
        dict(id='parent1', type='ItemSelector', css='div.parent'),
        dict(id='div', type='TextSelector', css='div'),
    ])
    css = sitemap.get_one_page_parent_css(['_root', 'parent2', 'parent1'])
    assert css == 'div.parent2 div.parent'

def test_has_recursive_selectors():
    sitemap = Sitemap([
        dict(id='parent1', type='ItemSelector', css='div.parent'),
        dict(id='parent2', type='ItemSelector', css='div.parent2', parents=['parent1']),
        dict(id='div', type='ItemSelector', css='div', parents=['parent2']),
    ])
    assert not sitemap.has_recursive_selectors

    sitemap = Sitemap([
        dict(id='parent1', type='ItemSelector', css='div.parent', parents=['div']),
        dict(id='parent2', type='ItemSelector', css='div.parent2', parents=['parent1']),
        dict(id='div', type='ItemSelector', css='div', parents=['parent2']),
    ])
    result = sitemap.has_recursive_selectors
    assert result

    sitemap = Sitemap([
        dict(id='link', type='LinkSelector', css='div.parent', parents=['link', '_root']),
        dict(id='parent', type='ItemSelector', css='div.parent2', parents=['link']),
        dict(id='div', type='ItemSelector', css='div', parents=['parent', 'link']),
    ])
    assert not sitemap.has_recursive_selectors

def test_update_selector():
    # with parent
    dicts = [
        dict(id='parent', type='ItemSelector'),
        dict(id='a', type='TextSelector', parents=['parent']),
    ]
    sitemap = Sitemap(selectors=dicts)
    expected = Selector('b', type='TextSelector', parents=['parent'])
    sitemap[1] = expected
    assert sitemap[1] == expected

    # with childs
    dicts = [
        dict(id='child', type='TextSelector', parents=['a']),
        dict(id='a', type='ItemSelector'),
    ]
    sitemap = Sitemap(selectors=dicts)
    expected = Selector('b', type='ItemSelector')
    expected_child = Selector('child', type='TextSelector', parents=['b'])
    sitemap[1] = expected
    assert sitemap[1] == expected
    assert sitemap[0] == expected_child

    # with itself as parent
    dicts = [
        dict(id='a', type='ItemSelector', parents=['a']),
    ]
    sitemap = Sitemap(selectors=dicts)
    update = Selector('b', type='ItemSelector', parents=['a'])
    expected = Selector('b', type='ItemSelector', parents=['b'])
    sitemap[0] = update
    assert sitemap[0] == expected

    # type change
    dicts = [
        dict(id='a', type='TextSelector', parents=['a']),
    ]
    sitemap = Sitemap(selectors=dicts)
    update = Selector('a', type='LinkSelector', parents=['a'])
    assert not sitemap.selectors[0].can_create_new_jobs
    sitemap[0] = update
    assert sitemap[0].__class__.__name__ == 'LinkSelector'

def test_columns():
    dicts = [
        dict(id='a', type='TextSelector', parents=['div']),
        dict(id='b', type='LinkSelector', parents=['b']),
    ]
    sitemap = Sitemap(selectors=dicts)
    assert sitemap.columns == ('a', 'b', 'b-href')

def test_delete():
    dicts = [
        dict(id='a', type='TextSelector'),
        dict(id='b', type='LinkSelector'),
    ]
    sitemap = Sitemap(selectors=dicts)
    del sitemap[0]
    assert len(sitemap) == 1

    dicts = [
        dict(id='a', type='TextSelector'),
        dict(id='b', type='LinkSelector', parents=['a']),
    ]
    sitemap = Sitemap(selectors=dicts)
    del sitemap[0]
    assert len(sitemap) == 0

    dicts = [
        dict(id='a', type='TextSelector'),
        dict(id='b', type='LinkSelector', parents=['a']),
        dict(id='c', type='LinkSelector', parents=['b', '_root']),
    ]
    sitemap = Sitemap(selectors=dicts)
    del sitemap[0]
    expected = Selector('c', type='LinkSelector')
    assert len(sitemap) == 1
    assert sitemap[0] == expected

URLS = {
    'one':
        ('http://a.b/', ['http://a.b/']),
    'tuple':
        (('http://a.b/1.html', 'http://a.b/2.html'), ['http://a.b/1.html', 'http://a.b/2.html']),
    'list':
        (['http://a.b/1.html', 'http://a.b/2.html'], ['http://a.b/1.html', 'http://a.b/2.html']),
    'range':
        ('http://a.b/[1-3].html', ['http://a.b/1.html', 'http://a.b/2.html', 'http://a.b/3.html']),
    'range_in_get':
        ('http://a.b/?id=[1-3]', ['http://a.b/?id=1', 'http://a.b/?id=2', 'http://a.b/?id=3']),
    'range_step':
        ('http://a.b/?id=[0-4:2]', ['http://a.b/?id=0', 'http://a.b/?id=2', 'http://a.b/?id=4']),
    'range_with_lpad':
        ('http://a.b/[001-003]/', ['http://a.b/001/', 'http://a.b/002/', 'http://a.b/003/']),
}
@pytest.mark.parametrize('start_urls,expected', list(URLS.values()), ids=list(URLS))
def test_start_urls(start_urls, expected):
    sitemap = Sitemap(dict(start_urls=start_urls))
    assert list(sitemap.start_urls) == expected

def test_get_csv_rows():
    dicts = [
        dict(id='a', type='TextSelector', parents=['div']),
        dict(id='b', type='TextSelector', parents=['b']),
    ]
    sitemap = Sitemap(selectors=dicts)
    row_dicts = [dict(a='a', b=['b'], c='c')]
    csv_rows = list(sitemap.get_csv_rows(row_dicts))
    # can't access the data so I'm just checking whether this runs
    assert csv_rows == [('a', 'b'), ('a', '["b"]')]

IS_COMMON = {
    'one_single_is':
        [TextSelector('a', many=0)],
    'one_many_is_not':
        [TextSelector('a', many=1)],
    'link_is_not':
        [LinkSelector('a', many=0), TextSelector('b', parents=['a'], many=0)],
    'singles_tree_is':
        [ItemSelector('a', many=0), TextSelector('b', parents=['a'], many=0)],
    'singles_tree_with_many_is_not':
        [ItemSelector('a', many=0), TextSelector('b', parents=['a'], many=1)],
}
@pytest.mark.parametrize('title,selectors', list(IS_COMMON.items()), ids=list(IS_COMMON.keys()))
def test_selector_is_common_to_all_trees(title, selectors):
    """Should be able to tell whether a selector will be common to all selector tree groups."""
    expected = not title.endswith('not')
    result = Sitemap(selectors).selector_is_common_to_all_trees(selectors[0])
    assert result is expected


def test_get_selectors_common_to_all_trees():
    """Should be able to find selectors common to all selector trees."""
    selectors = [
        ItemSelector('a', many=0),
        TextSelector('b', many=0, parents=['a']),
        TextSelector('c', many=0),
        TextSelector('d', many=1),
        ItemSelector('e', many=0),
        TextSelector('f', many=1, parents=['e']),
    ]
    result = Sitemap(selectors).get_selectors_common_to_all_trees('_root')
    assert result == selectors[:3]

TREES = {
    'single_item':
        ([TextSelector('a')], [['a']]),
    'link_tree':
        ([LinkSelector('a', many=1), TextSelector('b', many=0, parents=['a'])], [['a']]),
    'tree_with_many':
        ([ItemSelector('a', many=0), LinkSelector('b', many=1, parents=['a'])], [['a', 'b']]),
    'tree_without_many':
        ([ItemSelector('a', many=0),
          ItemSelector('b', many=0),
          TextSelector('c', many=0, parents=['a'])],
         [['a', 'c', 'b']]),
    # TODO: jasmine result: [['a', 'b', 'c']]
    'many_link_trees':
        ([ItemSelector('common  ', many=0),
          ItemSelector('parent1 ', many=0),
          ItemSelector('parent2 ', many=0),
          LinkSelector('follow1 ', many=1, parents=['parent1']),
          LinkSelector('follow11', many=1, parents=['parent1']),
          LinkSelector('follow2 ', many=1, parents=['parent2']),
          LinkSelector('follow3 ', many=1)],
         [['common', 'parent1', 'follow1'],
          ['common', 'parent1', 'follow11'],
          ['common', 'parent2', 'follow2'],
          ['common', 'follow3']]),
    'many_results_in_many_trees':
        ([ItemSelector('common ', many=0),
          ItemSelector('parent1', many=0),
          ItemSelector('parent2', many=0),
          TextSelector('common1', many=0, parents=['parent1']),
          TextSelector('many1  ', many=1, parents=['parent1']),
          TextSelector('many11 ', many=1, parents=['parent1']),
          TextSelector('many2  ', many=1, parents=['parent2']),
          TextSelector('many3  ', many=1)],
         [['common', 'parent1', 'common1', 'many1'],
          ['common', 'parent1', 'common1', 'many11'],
          ['common', 'parent2', 'many2'],
          ['common', 'many3']]),
    # TODO: jasmine result: [
    #     ['common', 'common1', 'parent1', 'many1'],
    #     ['common', 'common1', 'parent1', 'many11'],
    #     ['common', 'parent2', 'many2'],
    #     ['common', 'many3']
    # ]
    'chained_many':
        ([ItemSelector('div  ', many=0, css='div'),
          ItemSelector('table', many=1, css='table', parents=['div']),
          ItemSelector('tr   ', many=1, css='tr', parents=['table']),
          TextSelector('td   ', many=0, css='td', parents=['tr'])],
         [['div', 'table', 'tr', 'td']]),
    'return_one_for_this_map':
        # for url: http://www.centos.org/modules/tinycontent/index.php?id=30
        ([ItemSelector('mirror-row  ', many=1, parents=['_root', 'mirror-page'],
                       css='table#cter tr:nth-of-type(n+3)'),
          TextSelector('region      ', many=0, parents=['mirror-row'],
                       css='td:nth-of-type(1)'),
          TextSelector('state       ', many=0, parents=['mirror-row'],
                       css='td:nth-of-type(2)'),
          LinkSelector('url-http    ', many=0, parents=['mirror-row'],
                       css='td:nth-of-type(7) a')],
         [['mirror-row', 'region', 'state', 'url-http']]),
}
@pytest.mark.parametrize('selectors,expected', list(TREES.values()), ids=list(TREES))
def test_trees(selectors, expected):
    result = [[s.id for s in t] for t in Sitemap(selectors).trees]
    assert result == expected

HTML1 = '<a href="http://x.y/a/">A</a><a href="http://x.y/b/">B</a><span class="c">C</span>'
HTML2 = '<div><a href="http://x.y/a/">A</a></div><div><a href="http://x.y/b/">B</a></div>'
HTML3 = ('<div><table><tr><td>result1</td></tr><tr><td>result2</td></tr></table>'
         '<table><tr><td>result3</td></tr><tr><td>result4</td></tr></table></div>')

GET_DATA = {
    'text_from_single': (HTML1,
        [TextSelector('a', many=0, css='a')],
        [{'a': 'A'}]),
    'text_from_parent': (HTML1,
        [TextSelector('span', many=0, css='span')],
        [{'span': 'C'}]),
    'multiple_texts': (HTML1,
        [TextSelector('a', many=1, css='a')],
        [{'a': 'A'}, {'a': 'B'}]),
    'multiple_texts_with_common_data': (HTML1,
        [TextSelector('a', many=1, css='a'), TextSelector('c', many=0, css='.c')],
        [{'a': 'A', 'c': 'C'}, {'a': 'B', 'c': 'C'}]),
    'text_within_element': (HTML2,
        [ItemSelector('e', css='div', many=0), TextSelector('a', css='a', parents=['e'], many=0)],
        [{'a': 'A'}]),
    'texts_within_elements': (HTML2,
        [ItemSelector('e', css='div', many=1), TextSelector('a', css='a', parents=['e'], many=0)],
        [{'a': 'A'}, {'a': 'B'}]),
    'texts_within_element': (HTML2,
        [ItemSelector('e', css='div', many=0), TextSelector('a', css='a', parents=['e'], many=1)],
        [{'a': 'A'}]),
    'many_from_chained': (HTML3,
        [ItemSelector('div', css='div', many=0),
         ItemSelector('table', css='table', parents=['div'], many=1),
         ItemSelector('tr', css='tr', parents=['table'], many=1),
         TextSelector('td', css='td', parents=['tr'], many=0)],
        [{'td': 'result1'}, {'td': 'result2'}, {'td': 'result3'}, {'td': 'result4'}]),
    'empty_from_single': (HTML3,
        [ItemSelector('span', css='span.non', many=0)],
        []),  # TODO: jasmine result: [{'span': None}]
    'empty_from_many': (HTML3,
        [ItemSelector('span', css='span.non', many=1)],
        []),
}
@pytest.mark.parametrize('html,selectors,expected', list(GET_DATA.values()), ids=list(GET_DATA))
def test_get_data(html, selectors, expected):
    sitemap = Sitemap(selectors, parent_id='_root', parent_item=html)
    assert list(sitemap.get_data()) == expected

def test_get_selector_common_data():
    # with one selector
    selectors = [Selector('a', 'TextSelector', css='a', many=0)]
    sitemap = Sitemap(selectors)
    result = list(sitemap.get_selector_common_data(sitemap, selectors[0], HTML1))
    assert result == [{'a': 'A'}]

def test_get_selector_tree_common_data():
    # with one selector
    selectors = [Selector('a', 'TextSelector', css='a', many=0)]
    sitemap = Sitemap(selectors, parent_item=HTML1)
    assert sitemap.get_selector_tree_common_data(sitemap, '_root', HTML1) == {'a': 'A'}

    # with multiple selectors
    parent_item = """<div><div><a href="http://test.lv/a/">A</a></div></div>"""
    selectors = [
        Selector('parent1', 'ItemSelector', css='div', many=0),
        Selector('parent2', 'ItemSelector', css='div', parents=['parent1'], many=0),
        Selector('a', 'TextSelector', css='a', parents=['parent2'], many=0),
    ]
    sitemap = Sitemap(selectors, parent_item=parent_item)
    assert sitemap.get_selector_tree_common_data(sitemap, '_root', parent_item) == {'a': 'A'}
