#!/usr/bin/env python
# -*- coding: utf-8 -*-
import setuptools
import os

ver_file = os.path.join('hw2vec', '_version.py')
with open(ver_file) as f:
    exec(f.read())

DISTNAME = 'hw2vec'

INSTALL_REQUIRES = [i.strip() for i in open("requirements.txt").readlines()]

with open("README.md", "r") as fh:
    long_description = fh.read()

VERSION = __version__

setuptools.setup(
    name='hw2vec',
    version=VERSION,
    author="Shih-Yuan Yu, Rozhin Yasaei, Qingrong Zhou, Tommy Nguyen, Mohammad Abdullah Al Faruque",
    author_email="sujitchhetri@gmail.com",
    description="HW2Vec: A Python-based Hardware Designs Embedding Tool for Hardware Security",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/louisccc/hw2vec.git",
    packages=setuptools.find_packages(exclude=['data', 'py-env', 'build', 'dist', 'hw2vec.egg-info']),
    package_dir={DISTNAME: 'hw2vec'},
    package_data={'hw2vec': ['examples/*.py','examples/*.yaml']},
    setup_requires=['sphinx>=2.1.2'],
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)