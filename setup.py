#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(name='flask-http-api',
      version='0.1',
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
            'docutils',
            'flask',
            'peewee',
            'PyYAML',
            'gprof2dot',
            'Crypto',
            'watchdog',
            'pytest',
            'mock',
      ]
      )

# TODO The web test case's automation (in unit test)
