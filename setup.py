#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name='flask http api',
      version='1.0',
      description='',
      long_description='',
      classifiers=[],
      keywords='',
      author='',
      author_email='',
      url='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
            'flask',
            'peewee',
            'PyYAML',
            'gprof2dot',
            'pycrypto',
            'watchdog',
            'pytest',
      ]
      )

# ./setup.py egg_info
# pip3 install -r *.egg-info/requires.txt
