# -*- coding: utf-8 *-*
import os

from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="noscrapy",
    version="0.0.1",
    author="Mathias Seidler",
    author_email="seishin@gmail.com",
    description=("Python port attempt of web-scraper-chrome-extension."),
    license="MIT",
    url="https://github.com/katakumpo/noscrapy",
    packages=find_packages(exclude=['noscrapy.tests*']),
    py_modules=['noscrapy'],
    entry_points={'console_scripts': 'noscrapy=noscrapy.cli:cli'},
    long_description=read('README.rst'),
    install_requires=['pyquery>=1.2.11', 'requests>=2.9.1', 'click==6.6', 'couchdb>=1.0.1'],
    tests_require=['mock>=1.3.0', 'pytest>=2.9.1', 'pytest-cov>=2.2.1', 'python-coveralls>=2.7.0'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Topic :: Utilities",
    ],
)
