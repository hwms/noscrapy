import re

DOCUMENT_RE = re.compile(r'.*?\.(doc|docx|pdf|ppt|pptx|odt)$', 2)

class Queue(object):
    def __init__(self):
        self.jobs = []
        self.scraped_urls = {}

    def add(self, job):
        """Returns false if page is already scraped."""
        if self.can_be_added(job):
            self.jobs.append(job)
            self._set_url_scraped(job.url)
            return True
        return False

    def can_be_added(self, job):
        if self.is_scraped(job.url):
            return False
        # reject documents
        if DOCUMENT_RE.match(job.url):
            return False
        return True

    def get_queue_size(self):
        return len(self.jobs)

    def is_scraped(self, url):
        return url in self.scraped_urls

    def _set_url_scraped(self, url):
        self.scraped_urls[url] = True

    def get_next_job(self):
        # TODO: test this
        if self.jobs:
            return self.jobs.pop(0)
        else:
            return False
