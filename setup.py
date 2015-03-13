#!/usr/bin/env python
# encoding: utf-8

"""
FM Slack
========

Slack integration for FM player.
"""

import os
import sys

from setuptools import setup, find_packages

root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.join(root, 'fmslack'))

import fmslack

INSTALL_REQS = [
    'redis===2.10.3',
    'click===3.3',
    'requests===2.5.3']

TEST_REQS = [
    'nose==1.3.4',
    'coverage==3.7.1',
    'sure==1.2.8',
    'pinocchio==0.3',
    'mock==1.0.1']

DEVELOP_REQS = TEST_REQS + []

# Setup

setup(
    name='FM-Slack',
    version=fmslack.__version__,
    author=fmslack.__author__,
    author_email=fmslack.__author_email__,
    url='https://github.com/thisissoon/FM-Slack',
    description='This application posts currently playing track to Slack',
    packages=find_packages(
        exclude=[
            'tests'
        ]),
    include_package_data=True,
    zip_safe=False,
    # Dependencies
    install_requires=INSTALL_REQS,
    extras_require={
        'develop': DEVELOP_REQS
    },
    tests_require=TEST_REQS,
    entry_points={
        'console_scripts': [
            'fm-slack = fmslack.cli:run'
        ]
    })
