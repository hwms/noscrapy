import pytest

from noscrapy.selectors import LinkSelector

GET_DATA = {
    'single':
        (LinkSelector('a', css='a', many=False),
        '<a href="http://te.st/a">a</a><a href="http://te.st/b">b</a>',
        [{'a': 'a', 'a-href': 'http://te.st/a', '_follow': 'http://te.st/a', '_follow_id': 'a'}]),
    'many':
        (LinkSelector('a', css='a'),
        '<a href="http://te.st/a">a</a><a href="http://te.st/b">b</a>',
        [{'a': 'a', 'a-href': 'http://te.st/a', '_follow': 'http://te.st/a', '_follow_id': 'a'},
         {'a': 'b', 'a-href': 'http://te.st/b', '_follow': 'http://te.st/b', '_follow_id': 'a'}]),
    'empty':
        (LinkSelector('a', css='a'), '#not-exist', []),
}
@pytest.mark.parametrize('selector,html,expected', list(GET_DATA.values()), ids=list(GET_DATA))
def test_link_selector_get_data(selector, html, expected):
    assert list(selector.get_data(html)) == expected

def test_link_selector_columns():
    assert LinkSelector('id').columns == ('id', 'id-href')
