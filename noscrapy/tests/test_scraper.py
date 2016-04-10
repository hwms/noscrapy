import pytest

from noscrapy import LinkSelector, Queue, Scraper, Sitemap, TextSelector


class FakeStore(object):
    def __init__(self):
        self.data = []

    def get_sitemap_data(self, sitemap_id):
        class FakeStoreScrapeResult:
            def __init__(self, store):
                self.store = store
            def __iter__(self):
                return iter(self.store.data)
            def save(self, obj):
                self.store.data.append(obj)

        return FakeStoreScrapeResult(self)

# fake store does something different but live works, case for rewrite anyway
@pytest.mark.xfail
def test_scrape_one_page():
    selectors = [TextSelector('a', many=0, css='a')]
    sitemap = Sitemap('test', selectors, start_urls='http://test.lv/', parent_item='<a>a</a>')
    store, queue = FakeStore(), Queue(),
    scraper = Scraper(queue, sitemap, store)
    scraper.run()
    assert store.data == [{'a': 'a'}]

@pytest.mark.xfail
def test_scrape_child_page():
    selectors = [LinkSelector('link', many=1, css='a'),
                 TextSelector('b', many=0, css='b', parents=['_root', 'link'])]
    sitemap = Sitemap('test', selectors, start_urls='http://test.lv/',
                      parent_item='<a href="http://test.lv/1/">test</a><b>b</b>')
    store, queue = FakeStore(), Queue(),
    scraper = Scraper(queue, sitemap, store)
    scraper.run()
    assert store.data == [{'link': 'test', 'link-href': 'http://test.lv/1/', 'b': 'b'}]

def test_record_can_have_child_jobs():
    selectors = [LinkSelector('link_with_childs', many=1, css='a'),
                 LinkSelector('link_without_childs', many=1, css='a'),
                 TextSelector('b', many=0, css='b', parents=['link_with_childs'])]
    sitemap = Sitemap('test', selectors, start_urls='http://test.lv/',
                      parent_item='<a href="http://test.lv/1/">test</a><b>b</b>')
    store, queue = FakeStore(), Queue(),
    scraper = Scraper(queue, sitemap, store)
    follow = scraper.record_can_have_child_jobs({'_follow': 'http://example.com/',
                                                 '_follow_id': 'link_with_childs'})
    assert follow
    follow = scraper.record_can_have_child_jobs({'_follow': 'http://example.com/',
                                                 '_follow_id': 'link_without_childs'})
    assert not follow

def test_create_multiple_jobs():
    sitemap = Sitemap(start_urls='http://test.lv/[1-100].html')
    store, queue = FakeStore(), Queue(),
    scraper = Scraper(queue, sitemap, store)
    scraper.init_first_jobs()
    assert len(queue.jobs) == 100

def test_create_multiple_jobs_from_multiple_urls():
    sitemap = Sitemap(start_urls=['http://example.com/1', 'http://example.com/2',
                                  'http://example.com/3'])
    store, queue = FakeStore(), Queue(),
    scraper = Scraper(queue, sitemap, store)
    scraper.init_first_jobs()
    assert len(queue.jobs) == 3

def test_file_name_from_image_url():
    assert Scraper.get_file_name('http://example.com/image.jpg') == 'image.jpg'
    # with query
    assert Scraper.get_file_name('http://example.com/image.jpg?a=1&b=2') == 'image.jpga=1&b=2'
    # shorten to 143 chars; max: ext4: 254, ntfs: 256, ecryptfs: 143 -> we allow only 130
    assert Scraper.get_file_name('http://example.com/' + '0' * 300) == '0' * 130
    # image url without http://
    assert Scraper.get_file_name('image.jpg') == 'image.jpg'
