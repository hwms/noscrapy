from urllib.parse import urljoin

import requests

from .sitemap import Sitemap


class Job(object):
    def __init__(self, url, parent_id=None, scraper=None, parent_job=None, base_data=None):
        if parent_job:
            self.url = self.combine_urls(parent_job.url, url)
        else:
            self.url = url
        self.parent_id = parent_id
        self.scraper = scraper
        self.data_items = []
        self.base_data = base_data or {}

    def combine_urls(self, parent_url, child_url):
        return urljoin(parent_url, child_url)

    def execute(self):
        sitemap = Sitemap(self.scraper.sitemap, parent_id=self.parent_id)
        response = requests.get(self.url)
        sitemap.parent_item = response.content
        sitemap_data = list(sitemap.get_data())
        # merge data with data from initialization
        for result in sitemap_data:
            result.update(result, **self.base_data)
            self.data_items.append(result)

    def get_results(self):
        return self.data_items
