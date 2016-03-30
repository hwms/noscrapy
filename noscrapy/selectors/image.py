import base64

from ..selector import Selector
from ..utils import Field, requests


class ImageSelector(Selector):
    item_css_selector = 'img'

    download_image = Field(False)

    def _get_columns(self):
        return self.id + '-src',

    def _get_item_data(self, item):
        src = item.attr.src
        data = {self.id + '-src': src}
        if src and self.download_image:
            data['_image_base64'] = self.download_image_base64(src)
        yield data

    def _get_noitems_data(self):
        yield {self.id + '-src': None}

    def download_image_base64(self, url):
        response = requests.get(url)
        return base64.encodebytes(response.content)
