from distutils.core import setup
from setuptools import find_packages
from version import version

setup(
    name='bomberman',
    version=version,
    packages=find_packages(),
    install_requires=[
          'PySDL2'
    ]
)