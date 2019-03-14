# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='PySatsearch',
    version='1.0.1',
    description='Python code for accessing the Satsearch API',
    long_description=readme,
    author='Joe Verbist for Satsearch',
    author_email='info@satsearch.co',
    url='https://github.com/satsearch/pysatsearch',
    license=license,
    packages=find_packages()
)

