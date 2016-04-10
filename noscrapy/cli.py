import click

from noscrapy import Queue, Scraper, Store


@click.group()
def cli():
    pass

@cli.command(name='show')
def show_sitemaps():
    store = Store()
    for sitemap in store.get_all_sitemaps():
        print(sitemap.id)

@cli.command(name='print')
@click.argument('name')
def print_sitemap(name):
    store = Store()
    sitemap = store.get_sitemap(name)
    print(sitemap)

@cli.command(name='data')
@click.argument('name')
def data_sitemap(name):
    store = Store()
    for row in store.get_sitemap_data(name):
        print(row)

@cli.command(name='rescrape')
@click.argument('name')
def rescrape_sitemap(name):
    queue = Queue()
    store = Store()
    store.reset_sitemap_data_db(name)
    sitemap = store.get_sitemap(name)
    scraper = Scraper(queue, sitemap, store)
    scraper.run()
