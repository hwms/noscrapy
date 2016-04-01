import pytest

from noscrapy.selectors import ItemSelector

GET_DATA = {
    'single':
        (ItemSelector('a', css='p', many=False), '<p>a</p><p>b</p>', ['<p>a</p>']),
    'many':
        (ItemSelector('a', css='p'), '<p>a</p><p>b</p>', ['<p>a</p>', '<p>b</p>']),
    'none':
        (ItemSelector('a', css='p'), None, []),
    'no_elements':
        (ItemSelector('a', css='p'), '', []),
    'just_space':
        (ItemSelector('a', css='p'), ' ', []),
}
@pytest.mark.parametrize('selector,html,expected', list(GET_DATA.values()), ids=list(GET_DATA))
def test_item_selector_get_data(selector, html, expected):
    assert list(selector.get_data(html)) == expected

def test_item_selector_columns():
    assert ItemSelector('id').columns == ()
