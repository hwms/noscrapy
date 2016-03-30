import pytest

from noscrapy.selectors import HtmlSelector

GET_DATA = {
    'single':
        (HtmlSelector('a', css='p', many=False), '<p>a<b>b</b>c</p><p>d<b>e</b>f</div>',
         [{'a': 'a<b>b</b>c'}]),
    'many':
        (HtmlSelector('a', css='p'), '<p>a<b>b</b>c</p><p>d<b>e</b>f</div>',
         [{'a': 'a<b>b</b>c'}, {'a': 'd<b>e</b>f'}]),
    'none':
        (HtmlSelector('a', css='p'), None, [{'a': None}]),
    'no_elements':
        (HtmlSelector('a', css='p'), '', [{'a': None}]),
    'just_space':
        (HtmlSelector('a', css='p'), ' ', [{'a': None}]),
    'regex_no_match':
        (HtmlSelector('a', css='p', regex='wontmatch'), '<p>a<b>b</b>c</p><p>d<b>e</b>f</div>',
         [{'a': None}, {'a': None}]),
    'regex_match':
        (HtmlSelector('a', css='p', regex='<b>\\w+'), '<p>a<b>bb</b>c</p><p>d<b>e</b>f</div>',
         [{'a': '<b>bb'}, {'a': '<b>e'}]),
}
@pytest.mark.parametrize('selector,html,expected', list(GET_DATA.values()), ids=list(GET_DATA))
def test_html_selector_get_data(selector, html, expected):
    assert list(selector.get_data(html)) == expected

def test_html_selector_get_columns():
    assert HtmlSelector('id').columns == ('id',)
