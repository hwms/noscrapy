import pytest

from noscrapy.selectors import TextSelector

GET_DATA = {
    'single':
        (TextSelector('a', css='p', many=False), '<p>a</p><p>b</p>', [{'a': 'a'}]),
    'many':
        (TextSelector('a', css='p'), '<p>a</p><p>b</p>', [{'a': 'a'}, {'a': 'b'}]),
    'with_url':
        (TextSelector('a', css='a'),
        '<a href="http://aa/">a</a><a href="http://bb/">b</a>', [{'a': 'a'}, {'a': 'b'}],
        #  [{'a': 'a', 'a-href': 'http://aa/'}, {'a': 'b', 'a-href': 'http://aa/'}]
         ),
    'none':
        (TextSelector('a', css='p'), None, [{'a': None}]),
    'no_elements':
        (TextSelector('a', css='p'), '', [{'a': None}]),
    'just_space':
        (TextSelector('a', css='p'), ' ', [{'a': None}]),
    'regex_no_match':
        (TextSelector('a', css='p', regex='wontmatch'), '<p>aaaaaaa11113123aaaaa11111</p>',
         [{'a': None}]),
    'regex_match':
        (TextSelector('a', css='p', regex='\\d+'), '<p>aaaaaaa11113123aaaaa11111</p>',
         [{'a': '11113123'}]),
    'ignore_script_and_style_tags':
        (TextSelector('a', css='p'), '<p>a<script>b=1;</script><style>.*{}</style></p>',
         [{'a': 'a'}]),
    'replace_br_tags_with_newlines':
        (TextSelector('a', css='p'), '<p>a<br>b<br />c<BR>d<BR />e</p>',
         [{'a': 'a b\nc\nd\ne\n'}]  # [{'a': 'a\nb\nc\nd\ne\n'}]
         ),
}
@pytest.mark.parametrize('selector,html,expected', list(GET_DATA.values()), ids=list(GET_DATA))
def test_text_selector_get_data(selector, html, expected):
    assert list(selector.get_data(html)) == expected

def test_text_selector_columns():
    assert TextSelector('id').columns == ('id',)
