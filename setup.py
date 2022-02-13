#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# Meta information
version = open('VERSION').read().strip()

setup(
    name='ptxconf',
    version=version,
    packages=['src/ptxconf', 'src/ptxconf/icon'],
    package_data={'': ['*.png']},
    scripts=['./src/ptxconf/ptxconf.py']
)
