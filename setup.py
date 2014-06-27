#!/usr/bin/env python
from distutils.core import setup

setup(name='extras_mongoengine',
      version='0.1',
      description='MongoEngine Extras - Field Types and any other wizardry.',
      url='https://github.com/MongoEngine/extras-mongoengine/',
      install_requires=['mongoengine>=0.8.6'],
      packages=['extras_mongoengine'],
     )
