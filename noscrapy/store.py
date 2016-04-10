import re

import couchdb

from noscrapy.sitemap import Sitemap

DB_NAME_RE = re.compile(r'[^a-z0-9_\$\(\)\+\-/]', re.I)

class Store(object):
    def __init__(self, server_url=None, db_name='scraper-sitemaps'):
        self.server_url = server_url
        self.server = couchdb.Server(server_url) if server_url else couchdb.Server()
        self.db_name = db_name
        self.db = self.server[db_name]

    def get_sitemap_data(self, sitemap_id):
        db = self.get_sitemap_data_db(sitemap_id)
        return StoreScrapeResult(db)

    def get_sitemap_data_db(self, sitemap_id):
        db_location = self.sanitize_sitemap_data_db_name(sitemap_id)
        try:
            return self.server[db_location]
        except couchdb.http.ResourceNotFound:
            return self.server.create(db_location)

    def reset_sitemap_data_db(self, sitemap_id):
        try:
            db_location = self.sanitize_sitemap_data_db_name(sitemap_id)
            del self.server[db_location]
        except couchdb.http.ResourceNotFound:
            pass

    @staticmethod
    def sanitize_sitemap_data_db_name(sitemap_id):
        return 'sitemap-data-' + DB_NAME_RE.sub('_', sitemap_id)

    def update_sitemap(self, sitemap):
        if not sitemap.id:
            raise ValueError('cannot save sitemap without an id')
        self.db.update_doc(sitemap.id, **sitemap.__getstate__())

    def remove_sitemap(self, sitemap_id):
        del self.db[sitemap_id]

    def get_all_sitemaps(self):
        for sitemap_id in self.db:
            yield self.get_sitemap(sitemap_id)

    def get_sitemap(self, sitemap_id):
        # convert chrome webscraper extension sitemap dict in noscrapy dict
        webscraper_doc = self.db[sitemap_id]
        python_dct = webscraper_to_python(webscraper_doc)
        return Sitemap(python_dct)

    def sitemap_exists(self, sitemap_id):
        return sitemap_id in self.db


class StoreScrapeResult(object):
    def __init__(self, db):
        self.db = db

    def save(self, record):
        if record:
            if '_id' in record:
                self.db.update([record])
            else:
                self.db.save({k: v for k, v in record.items() if (not k.startswith('_') or k == '_id')})

    def __iter__(self):
        for doc_id in self.db:
            yield dict(self.db[doc_id])

    def filter(self, **kwds):
        if not kwds:
            return list(self)
        keys = ','.join('doc["%s"]' % k for k in kwds)
        vals = list(kwds.values())
        map_fun = 'function(doc) {emit([%s], doc);}' % keys
        return list(self.db.query(map_fun)[vals])

DIRECT_NAME_MAP = [
    ('startUrl', 'start_urls'),
    ('parentSelectors', 'parents'),
    ('selector', 'css'),
    ('multiple', 'many'),
    ('_id', 'id'),
]

def webscraper_to_python(webscraper_dict):
    dct = {}
    for key, value in webscraper_dict.items():
        for f, t in DIRECT_NAME_MAP:
            if key == f:
                key = t
        if value:
            if key == 'selectors':
                python_value = []
                for webscraper_selector_dict in value:
                    python_value.append(webscraper_to_python(webscraper_selector_dict))
                value = python_value
            elif key == 'type':
                value = value.replace('Selector', '') + 'Selector'
        dct[key] = value
    return dct
