#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from distutils.core import setup
from ptxconftools import __version__ as version

setup(name='ptxconf',
      version=version,
      packages=['ptxconftools', 'ptxconftools.gtk'],
      package_data={'': ['*.png']},
      scripts=['./ptxconf.py'])
