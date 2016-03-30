import pytest

from noscrapy.selectors import GroupSelector

GET_DATA = {
    'text':
        (GroupSelector('a', css='p'), '<p>a</p><p>b</p>', [{'a': ({'a': 'a'}, {'a': 'b'})}]),
    'href':
        (GroupSelector('a', css='a', extract='href'),
        '<a href="http://aa/">a</a><a href="http://bb/">b</a>',
        [{'a': ({'a': 'a', 'a-href': 'http://aa/'}, {'a': 'b', 'a-href': 'http://bb/'})}]),
    'empty':
        (GroupSelector('a', css='p'), '', [{'a': ()}]),
}
@pytest.mark.parametrize('selector,html,expected', list(GET_DATA.values()), ids=list(GET_DATA))
def test_group_selector_get_data(selector, html, expected):
    assert list(selector.get_data(html)) == expected

def test_group_selector_columns():
    assert GroupSelector('id', css='div').columns == ('id',)
    assert GroupSelector('id', css='div', extract='href').columns == ('id',)
