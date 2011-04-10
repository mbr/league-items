#!/usr/bin/env python
# coding=utf8

from distutils.core import setup

setup(name = 'leagueoflegends',
      version = '0.1dev',
      description = 'Utilities for creating websites related to League of Legends.',
      author = 'Marc Brinkmann',
      url = 'https://github.com/mbr/league-items',
      packages = ['leagueoflegends'],
      install_requires = ['networkx>=1.2', 'BeautifulSoup', 'PyYAML'],
      scripts = ['download-items', 'item-build-printer'],
     )
