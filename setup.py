#!/usr/bin/env python

from distutils.core import setup
from version import __version__

setup(name='CCS SQS',
      version=__version__,
      license='MIT',
      description='Utilities to be used with AWS SQS',
      author='Caio Caçador da Silva',
      author_email='caiocacador.s@gmail.com',
      url='https://github.com/caio-cacador/ccs_sqs',
      packages=['sqs'])
