'''
Flask-uWSGI-WebSocket
---------------------
High-performance WebSockets for your Flask apps powered by `uWSGI <http://uwsgi-docs.readthedocs.org/en/latest/>`_.
'''

__docformat__ = 'restructuredtext'
__version__ = '0.4.4'
__license__ = 'MIT'
__author__  = 'Zach Kelling'

from ._uwsgi import uwsgi
from .websocket import *
from .async import *

class GeventNotInstalled(Exception):
    pass

try:
    from ._gevent import *
except ImportError:
    class GeventWebSocket(object):
        def __init__(self, *args, **kwargs):
            raise GeventNotInstalled("Gevent must be installed to use GeventWebSocket. Try: `pip install gevent`.")
