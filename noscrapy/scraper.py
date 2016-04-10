from noscrapy import Job


class Scraper(object):
    request_interval = 2000
    _time_next_scrape_available = 0

    def __init__(self, queue, sitemap, store, request_interval=None, pageload_delay=None):
        self.queue = queue
        self.sitemap = sitemap
        self.store = store
        self.request_interval = int(request_interval or self.request_interval)
        self.pageload_delay = int(pageload_delay or 0)

    def run(self):
        self.init_first_jobs()
        while True:
            job = self.queue.get_next_job()
            if not job:
                break
            self._run_job(job)

    def init_first_jobs(self):
        for url in self.sitemap.start_urls:
            first_job = Job(url, '_root', self)
            self.queue.add(first_job)

    def _run_job(self, job):
        job.execute()
        scraped_records = self.store.get_sitemap_data(job.scraper.sitemap.id)
        for record in job.get_results():
            save = True
            if self.record_can_have_child_jobs(record):
                follow_id = record.pop('_follow_id', None)
                follow_url = record.pop('_follow', None)
                new_job = Job(follow_url, follow_id, self, job, record)
                if self.queue.can_be_added(new_job):
                    self.queue.add(new_job)
                    save = False
            if save:
                scraped_records.save(record)
            break

    def record_can_have_child_jobs(self, record):
        if '_follow' in record:
            return bool(list(self.sitemap.get_direct_childs(record['_follow_id'])))

    @staticmethod
    def get_file_name(url):
        parts = url.split('/')
        name = parts[-1]
        name = name.replace('?', '')
        return name[:130]
