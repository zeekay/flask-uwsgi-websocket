'''
Flask-uWSGI-WebSocket
---------------------
High-performance WebSockets for your Flask apps powered by `uWSGI <http://uwsgi-docs.readthedocs.org/en/latest/>`_.
'''

__docformat__ = 'restructuredtext'
__version__ = '0.2.5'
__license__ = 'MIT'
__author__  = 'Zach Kelling'

import os
import sys
import uuid

from ._uwsgi import uwsgi
from .websocket import *
from .async import *

try:
    from ._gevent import *
except ImportError:
    pass
