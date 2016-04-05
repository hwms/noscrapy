import pytest

from noscrapy import json, Selector, Sitemap

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
        dict(id='d', type='ItemSelector', parents=['_root']),
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
        dict(id='d', type='ItemSelector', parents=['_root']),
    ]
    actual_selectors = list(Sitemap(dicts).get_direct_childs('a'))
    assert actual_selectors == expected_dicts

def test_will_return_many():
    sitemap = Sitemap([
        dict(id='a', type='ItemSelector', parents=['_root'], many=False),
        dict(id='b', type='ItemSelector', parents=['a'], many=True),
        dict(id='c', type='ItemSelector', parents=['b'], many=True),
    ])
    assert sitemap.will_return_many('a')

    sitemap = Sitemap([
        dict(id='a', type='ItemSelector', parents=['_root'], many=True),
        dict(id='b', type='ItemSelector', parents=['a'], many=False),
        dict(id='c', type='ItemSelector', parents=['b'], many=False),
    ])
    assert sitemap.will_return_many('a')

    sitemap = Sitemap([
        dict(id='a', type='ItemSelector', parents=['_root'], many=False),
        dict(id='b', type='ItemSelector', parents=['a'], many=False),
        dict(id='c', type='ItemSelector', parents=['b'], many=False),
    ])
    assert not sitemap.will_return_many('a')

def test_json():
    dicts = [dict(id='a', type='ItemSelector', parents=['_root'], many=False)]
    sitemap = Sitemap('l', dicts)

    js_dicts = json.loads(json.dumps(sitemap))
    assert js_dicts == {'id': 'l', 'selectors': dicts}

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
        dict(id='parent2', type='ItemSelector', parents=['_root'], many=True),
        dict(id='ignore1', type='TextSelector', parents=['link'], many=False),
        dict(id='ignore2', type='TextSelector', parents=['link'], many=False),
        dict(id='ignore_root', type='TextSelector', parents=['_root'], many=False),
        dict(id='ignore_parent1', type='TextSelector', parents=['parent1'], many=False),
    ])
    page_child_selectors = list(sitemap.get_one_page_childs('parent2'))
    assert page_child_selectors == expected_dicts

def test_get_one_page_selectors():
    expected_dicts = [
        dict(id='parent1', type='ItemSelector', parents=['_root'], many=True),
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
        dict(id='ignore_root', type='TextSelector', parents=['_root'], many=False),
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
        dict(id='parent1', type='ItemSelector', css='div.parent', parents=['_root']),
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
        dict(id='parent', type='ItemSelector', parents=['_root']),
        dict(id='a', type='TextSelector', parents=['parent']),
    ]
    sitemap = Sitemap(selectors=dicts)
    expected = Selector('b', type='TextSelector', parents=['parent'])
    sitemap[1] = expected
    assert sitemap[1] == expected

    # with childs
    dicts = [
        dict(id='child', type='TextSelector', parents=['a']),
        dict(id='a', type='ItemSelector', parents=['_root']),
    ]
    sitemap = Sitemap(selectors=dicts)
    expected = Selector('b', type='ItemSelector', parents=['_root'])
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
        dict(id='a', type='TextSelector', parents=['_root']),
        dict(id='b', type='LinkSelector', parents=['_root']),
    ]
    sitemap = Sitemap(selectors=dicts)
    del sitemap[0]
    assert len(sitemap) == 1

    dicts = [
        dict(id='a', type='TextSelector', parents=['_root']),
        dict(id='b', type='LinkSelector', parents=['a']),
    ]
    sitemap = Sitemap(selectors=dicts)
    del sitemap[0]
    assert len(sitemap) == 0

    dicts = [
        dict(id='a', type='TextSelector', parents=['_root']),
        dict(id='b', type='LinkSelector', parents=['a']),
        dict(id='c', type='LinkSelector', parents=['b', '_root']),
    ]
    sitemap = Sitemap(selectors=dicts)
    del sitemap[0]
    expected = Selector('c', type='LinkSelector', parents=['_root'])
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
