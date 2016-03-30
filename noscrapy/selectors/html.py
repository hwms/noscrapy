from ..selector import Selector

class HtmlSelector(Selector):
    def _get_item_data(self, item):
        yield {self.id: item.html()}
