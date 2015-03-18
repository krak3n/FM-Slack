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


def read_requirements(filename):
    """ Read requirements file and process them into a list
    for usage in the setup function.
    Arguments
    ---------
    filename : str
        Path to the file to read line by line
    Returns
    --------
    list
        list of requirements::
            ['package==1.0', 'thing>=9.0']
    """

    requirements = []
    with open(filename) as f:
        for line in f.readlines():
            line = line.strip()
            if not line or line.startswith('#') or line == '':
                continue
            requirements.append(line)
    requirements.reverse()
    return requirements


# Requirements

INSTALL_REQS = read_requirements('install.reqs')
TESTING_REQS = read_requirements('test.reqs')
DEVELOP_REQS = TESTING_REQS + read_requirements('develop.reqs')

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
    tests_require=TESTING_REQS,
    entry_points={
        'console_scripts': [
            'fm-slack = fmslack.cli:run'
        ]
    })
