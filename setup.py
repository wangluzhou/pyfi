# encoding: utf-8
from setuptools import setup, find_packages
import sys, os

VERSION = '0.1.7'

setup(name='windHelper',
      version=VERSION,
      description='encapsulate the windPy API with pandas',
      url='https://github.com/wangluzhou/windHelper.git',
      author='wangluzhou',
      author_email='wangluzhou@aliyun.com',
      license='MIT',
      packages=['windHelper'],
      zip_safe=True)
