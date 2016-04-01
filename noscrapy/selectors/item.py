from ..selector import Selector

class ItemSelector(Selector):
    can_have_childs = True
    can_have_local_childs = True
    will_return_items = True

    def _get_data(self, parent_item):
        yield from self.get_items(parent_item)

    def _get_columns(self):
        return ()
