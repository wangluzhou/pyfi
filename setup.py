# encoding: utf-8
# python setup.py register sdist upload
from setuptools import setup, find_packages

VERSION = '0.1.5'

setup(name='pyfi_helper',
      version=VERSION,
      description='encapsulate the windPy API with pandas',
      url='https://github.com/wangluzhou/pyfi.git',
      author='wangluzhou',
      author_email='wangluzhou@aliyun.com',
      license='MIT',
      packages=find_packages(),
      zip_safe=True,
      install_requires=['pandas'])
