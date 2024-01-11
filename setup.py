#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8"),
    ) as fh:
        return fh.read()


long_description = "%s" % (
    re.compile("^.. start-badges.*^.. end-badges", re.M | re.S).sub(
        "", read("README.rst")
    )
)


setup(
    name="oemof.network",
    version="0.5.0a6",
    license="MIT",
    description="The network/graph submodules of oemof.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="oemof developer group",
    author_email="contact@oemof.org",
    url="https://github.com/oemof/oemof.network",
    packages=["oemof"] + ["oemof." + p for p in find_packages("src/oemof")],
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list:
        #   http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        # uncomment if you test on these interpreters:
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: Stackless',
        "Topic :: Utilities",
    ],
    project_urls={
        "Documentation": "https://oemofnetwork.readthedocs.io/",
        "Changelog": (
            "https://oemofnetwork.readthedocs.io/en/latest/changelog.html"
        ),
        "Issue Tracker": "https://github.com/oemof/oemof.network/issues",
    },
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    python_requires=">=3.7",
    install_requires=["pandas", "blinker", "dill", "networkx", "oemof.tools"],
    extras_require={
        "dev": ["pytest"],
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
)
