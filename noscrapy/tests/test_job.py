import pytest
from mock import patch

from noscrapy import Job, Sitemap

URL_JOINS = {
    '0': ('http://example.com/', '/test/', 'http://example.com/test/'),
    '1': ('http://example.com/', 'test/', 'http://example.com/test/'),
    '2': ('http://example.com/asdasdad', 'http://tvnet.lv', 'http://tvnet.lv'),
    '3': ('http://example.com/asdasdad', '?test', 'http://example.com/asdasdad?test'),
    '4': ('http://example.com/1/', '2/', 'http://example.com/1/2/'),
    '5': ('http://127.0.0.1/1/', '2/', 'http://127.0.0.1/1/2/'),
    '6': ('http://xn--80aaxitdbjk.xn--p1ai/', '2/', 'http://xn--80aaxitdbjk.xn--p1ai/2/'),
    'with_slash_after_question_mark': ('http://a/b?y=5/9', 'c?x=4/9', 'http://a/c?x=4/9'),
    'port_0': ('http://a:81/http:/b/c', 'http://a:81/http:/b/d', 'http://a:81/http:/b/d'),
    'port_0': ('http://a:81/http:/b/c', 'd', 'http://a:81/http:/b/d'),
}
@pytest.mark.parametrize('parent_url,fragment,url', list(URL_JOINS.values()), ids=list(URL_JOINS))
def test_urljoins(parent_url, fragment, url):
    # should be able to create correct url from parent job
    parent = Job(parent_url)
    child = Job(fragment, parent_job=parent)
    assert url == child.url


@patch('requests.get')
def test_get_results(get_mock):
    # should not override data with base data if it already exists
    get_mock.content.return_value = ''
    class ScraperMock:
        def __init__(self):
            self.sitemap = Sitemap()

    job = Job(url=None,
              scraper=ScraperMock(),
              base_data={'a': 'do not override', 'c': 3})
    try:
        original_get_data = Sitemap.get_data
        Sitemap.get_data = lambda self: iter([{'a': 1, 'b': 2}])
        job.execute()
    finally:
        Sitemap.get_data = original_get_data

    results = job.get_results()
    assert [{'a': 'do not override', 'b': 2, 'c': 3}] == results
