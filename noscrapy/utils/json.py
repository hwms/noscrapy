import json
from functools import partial

__all__ = 'dump', 'dumps', 'load', 'loads', 'JSONDecoder', 'JSONEncoder'

class JSONEncoder(json.JSONEncoder):

    def default(self, obj):
        try:
            return getattr(obj, '__getstate__')()
        except (AttributeError, TypeError):
            # type error for missing argument 'self' on classes
            pass
        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError:
            pass
        return repr(obj)

dump = partial(json.dump, cls=JSONEncoder)
dumps = partial(json.dumps, cls=JSONEncoder)
load = json.load
loads = json.loads
JSONDecoder = json.JSONDecoder
