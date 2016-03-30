from ..selector import Selector
from ..utils import Field

class GroupSelector(Selector):
    inline_many = True
    can_return_many = False

    extract = Field(None)

    def _get_item_data(self, item):
        data = {self.id: item.text()}
        if self.extract:
            data['%s-%s' % (self.id, self.extract)] = item.attr[self.extract]
        yield data
