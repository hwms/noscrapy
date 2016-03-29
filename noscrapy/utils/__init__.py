from .declarative import *
from .pyquery import *
import requests

# provide ide convenience for unprovided source equivalents of lxml.etree
class etree:
    def __getattr__(self, name):
        pass  # pragma: no cover
from lxml import etree  # noqa @UnresolvedImport
