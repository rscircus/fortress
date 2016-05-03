import codecs
import unittest
from setuptools import setup, Command
import sys

import fortress

#TODO: Tests

with codecs.open('README.md', 'r', 'utf-8') as fd:
  setup(name='fortress',
        version=fortress.__version__,
        description='A formatter for Fortran code.',
        long_description=fd.read(),
        maintainer='F&R',
        packages=['fortress', 'fortress.lib'],
        classifiers=[
            'Development Status :: 2 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Software Development :: Quality Assurance',
        ],
        entry_points={'console_scripts': ['fortress = fortress:run_main'],})
