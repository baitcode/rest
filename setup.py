#!/usr/bin/env python

from distutils.core import setup

with open('requirements.txt') as f:
    requirements = f.readlines()

print requirements

setup(
    name='Django REST library',
    version='0.3',
    description='Classes, Functions, and decorators to help you build high quality REST API',
    author='Ilya Batiy',
    author_email='batiyiv@gamil.com',
    url='',
    package_dir={'rest': 'src/'},
    packages=['rest'],
    requires=requirements
)