from ..selector import Selector


class LinkSelector(Selector):
    item_css_selector = 'a'
    can_have_childs = True
    can_create_new_jobs = True

    def _get_columns(self):
        return self.id, self.id + '-href'

    def _get_item_data(self, item):
        yield {self.id: item.text(), '%s-href' % self.id: item.attr.href, '_follow_id': self.id,
               '_follow': item.attr.href}

    def _get_noitems_data(self):
        raise StopIteration
