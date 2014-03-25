#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='codeco',
    version='1.0',
    description=(
        'Universal code annotator using Pygments '
        'and reStructuredText or Markdown.'
    ),
    author='Carlos Jenkins',
    author_email='carlos@jenkins.co.cr',
    url='https://github.com/carlos-jenkins/codeco',
    packages=['codeco'],
    package_dir={'': 'lib'},
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
    ],
    test_suite='test',
    setup_requires=[
        'flake8'
    ],
    install_requires=[
        'pygments>=1.6',
        'markdown',
        'docutils',
        'beautifulsoup4'
    ],
)
