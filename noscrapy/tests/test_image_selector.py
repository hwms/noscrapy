import pytest
from mock import call, patch

from noscrapy.selectors import ImageSelector

GET_DATA = {
    'single':
        (ImageSelector('a', css='img', many=False), '<img src="http://a"/><img src="http://b"/>',
         [{'a-src': 'http://a'}]),
    'many':
        (ImageSelector('a', css='img'), '<img src="http://a"/><img src="http://b"/>',
         [{'a-src': 'http://a'}, {'a-src': 'http://b'}]),
    'notexist':
        (ImageSelector('a', css='img.notexist'), '<img src="http://a"/>', [{'a-src': None}]),
}
@pytest.mark.parametrize('selector,html,expected', list(GET_DATA.values()), ids=list(GET_DATA))
def test_image_selector_get_data(selector, html, expected):
    assert list(selector.get_data(html)) == expected

def test_image_selector_columns():
    assert ImageSelector('id').columns == ('id-src',)

@patch('requests.get')
def test_image_selector_with_download(get_mock):
    class RequestMock:
        content = b'abc'
    get_mock.return_value = RequestMock()

    selector = ImageSelector('id', css='img', download_image=True)
    actual = selector.download_image_base64('http://someimage')

    assert get_mock.call_args_list == [call('http://someimage')]
    assert actual == b'YWJj\n'

    get_mock.reset_mock()
    actual = list(selector.get_data('<img src="http://someimage">'))
    assert get_mock.call_args_list == [call('http://someimage')]
    assert actual == [{'id-src': 'http://someimage', '_image_base64': b'YWJj\n'}]
