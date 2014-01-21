#!/usr/bin/env python
from setuptools import setup
from flask_uwsgi_websocket import __version__


setup(
    name='Flask-uWSGI-WebSocket',
    version=__version__,
    url='https://github.com/zeekay/flask-uwsgi-websocket',
    license=open('LICENSE').read(),
    author='Zach Kelling',
    author_email='zk@monoid.io',
    description='High-performance WebSockets for your Flask apps powered by uWSGI.',
    long_description=open('README.rst').read(),
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
    ],
    keywords='uwsgi flask websockets'
)
