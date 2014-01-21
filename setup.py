#!/usr/bin/env python

"""
Flask-uWSGI-WebSocket
-------------
High-performance WebSockets for your Flask apps powered by `uWSGI <http://uwsgi-docs.readthedocs.org/en/latest/>`_.
"""
from setuptools import setup


setup(
    name='Flask-uWSGI-WebSocket',
    version='0.0.2',
    url='https://github.com/zeekay/flask-uwsgi-websocket',
    license='See License',
    author='Zach Kelling',
    author_email='zk@monoid.io',
    description='High-performance WebSockets for your Flask apps powered by uWSGI.',
    long_description=__doc__,
    py_modules=['flask_uwsgi_websocket'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'uwsgi',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
