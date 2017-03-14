#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Packaging settings"""

import io
from zabbix2jira import __version__
from os.path import abspath, dirname, join

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

this_dir = abspath(dirname(__file__))
with io.open(join(this_dir, 'README.rst'), encoding='utf-8') as file:
    long_description = file.read()

config = {
    'name': 'zabbix2jira',
    'version': __version__,
    'description': 'Creates or updates a ticket on JIRA from Zabbix alarms',
    'long_description': long_description,
    'url': 'https://github.com/Movile/zabbix2jira',
    'author': 'Hugo Cisneiros',
    'author_email': 'hugo.cisneiros@movile.com',
    'license': 'GPL version 3',
    'classifiers': [
        'Intended Audience :: System Administrators',
        'Topic :: Utilities',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
    'keywords': [
        'zabbix',
        'jira',
        'tickets'
    ],
    'packages': find_packages(exclude=['docs', 'tests*']),
    'install_requires': ['docopt', 'jira', 'py-zabbix'],
    'extras_require': {
        'test': ['nose'],
    },
    'entry_points': {
        'console_scripts': [
            'zabbix2jira=zabbix2jira.cli:main',
        ],
    },
}

setup(**config)
