from ..selector import Selector

class TextSelector(Selector):
    def _get_item_data(self, item):
        # remove script and style tag contents from text results
        item = item.clone()
        item.find('script, style').remove()
        # add newline placeholder after br tags
        item.find('br').after('\\n')
        text = item.text().replace('\\n ', '\n').replace('\\n', '\n')
        yield {self.id: text}
