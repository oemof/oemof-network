========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |requires|
        | |coveralls|
        | |scrutinizer| |codacy| |codeclimate|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/oemofnetwork/badge/?style=flat
    :target: https://readthedocs.org/projects/oemofnetwork
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/oemof/oemof.network.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/oemof/oemof.network

.. |requires| image:: https://requires.io/github/oemof/oemof.network/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/oemof/oemof.network/requirements/?branch=master

.. |coveralls| image:: https://coveralls.io/repos/oemof/oemof.network/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/oemof/oemof.network

.. |codacy| image:: https://img.shields.io/codacy/grade/CODACY_PROJECT_ID.svg
    :target: https://www.codacy.com/app/oemof/oemof.network
    :alt: Codacy Code Quality Status

.. |codeclimate| image:: https://codeclimate.com/github/oemof/oemof.network/badges/gpa.svg
   :target: https://codeclimate.com/github/oemof/oemof.network
   :alt: CodeClimate Quality Status

.. |version| image:: https://img.shields.io/pypi/v/oemof.network.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/oemof

.. |wheel| image:: https://img.shields.io/pypi/wheel/oemof.network.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/oemof

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/oemof.network.svg
    :alt: Supported versions
    :target: https://pypi.org/project/oemof

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/oemof.network.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/oemof

.. |commits-since| image:: https://img.shields.io/github/commits-since/oemof/oemof.network/v0.4.0rc1/dev
    :alt: Commits since latest release
    :target: https://github.com/oemof/oemof.network/compare/master...dev

.. |scrutinizer| image:: https://img.shields.io/scrutinizer/quality/g/oemof/oemof.network/master.svg
    :alt: Scrutinizer Status
    :target: https://scrutinizer-ci.com/g/oemof/oemof.network/


.. end-badges

The network/graph submodules of oemof.

* Free software: MIT license

Installation
============

::

    pip install oemof.network

You can also install the in-development version with::

    pip install https://github.com/oemof/oemof.network/archive/master.zip


Documentation
=============


https://oemofnetwork.readthedocs.io/


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox

