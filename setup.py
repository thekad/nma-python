#!/usr/bin/env python
#
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8

import setuptools
from nma import NAME, VERSION


setuptools.setup(
    name = NAME,
    version = VERSION,
    author = 'Jorge Gallegos',
    author_email = 'kad@blegh.net',
    description = 'A library/cli tool for notifymyandroid (http://nma.usk.bz)',
    install_requires = [
        'argparse',
        'httplib2'
    ],
    packages = setuptools.find_packages('.'),
    zip_safe = False,
    url = 'https://github.com/thekad/nma-python',
    license = 'MIT',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Libraries',
    ],
    entry_points = {
        'console_scripts': [
            'nma_cli = nma.nma:main'
        ],
    },
)
