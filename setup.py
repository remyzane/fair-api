#!/usr/bin/env python3
import os
from setuptools import setup, find_packages


def get_packages(package):
    """ Return root package and all sub-packages. """

    return [dir_path
            for dir_path, dir_names, file_names in os.walk(package)
            if os.path.exists(os.path.join(dir_path, '__init__.py'))]


def get_package_data(package):
    """ Return all files under the root package, that are not in a package themselves."""

    walk = [(dir_path.replace(package + os.sep, '', 1), file_names)
            for dir_path, dir_names, file_names in os.walk(package)
            if not os.path.exists(os.path.join(dir_path, '__init__.py'))]
    file_paths = []
    for base, file_names in walk:
        file_paths.extend([os.path.join(base, file_name)
                          for file_name in file_names])
    return {package: file_paths}


setup(name='flask-http-api',
      version='0.1',
      description='',
      long_description='',
      classifiers=[],
      keywords='',
      author='',
      author_email='',
      url='',
      packages=get_packages('fair'),
      package_data=get_package_data('fair'),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
            'docutils',
            'sphinx',
            'flask',
            'peewee',
            'PyYAML',
            'gprof2dot',
            'Crypto',
            'pytest',
            'mock',
            'pycrypto',
      ]
      )

# TODO The web test case's automation (in unit test)
