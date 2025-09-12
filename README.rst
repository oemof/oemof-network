========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |tox-pytest| |tox-checks|
        | |coveralls| |scrutinizer| |codacy|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since| |packaging|

.. |tox-pytest| image:: https://github.com/oemof/oemof-network/actions/workflows/tox_pytests.yml/badge.svg?branch=dev
     :target: https://github.com/oemof/oemof-network/actions?query=workflow%3A%22tox+checks%22

.. |tox-checks| image:: https://github.com/oemof/oemof-network/actions/workflows/tox_checks.yml/badge.svg?branch=dev
     :target: https://github.com/oemof/oemof-network/actions?query=workflow%3A%22tox+checks%22

.. |packaging| image:: https://github.com/oemof/oemof-network/actions/workflows/packaging.yml/badge.svg?branch=dev)
     :target: https://github.com/oemof/oemof-network/actions?query=workflow%3Apackaging

.. |docs| image:: https://readthedocs.org/projects/oemof-network/badge/?style=flat
    :target: https://readthedocs.org/projects/oemof-network
    :alt: Documentation Status

.. |coveralls| image:: https://coveralls.io/repos/oemof/oemof-network/badge.svg?branch=dev&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/oemof/oemof-network?branch=dev

.. |codacy| image:: https://api.codacy.com/project/badge/Grade/39b648d0de3340da912c3dc48688a7b5
    :target: https://app.codacy.com/gh/oemof/oemof-network
    :alt: Codacy Code Quality Status

.. |version| image:: https://img.shields.io/pypi/v/oemof.network.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/oemof.network

.. |wheel| image:: https://img.shields.io/pypi/wheel/oemof.network.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/oemof.network

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/oemof.network.svg
    :alt: Supported versions
    :target: https://pypi.org/project/oemof.network

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/oemof.network.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/oemof.network

.. |commits-since| image:: https://img.shields.io/github/commits-since/oemof/oemof-network/v0.5.0/dev
    :alt: Commits since latest release
    :target: https://github.com/oemof/oemof-network/compare/master...dev

.. |scrutinizer| image:: https://img.shields.io/scrutinizer/quality/g/oemof/oemof-network/dev.svg
    :alt: Scrutinizer Status
    :target: https://scrutinizer-ci.com/g/oemof/oemof-network/


.. end-badges

The network/graph submodules of oemof.

* Free software: MIT license

Installation
============

::

    pip install oemof.network

You can also install the in-development version with::

    pip install https://github.com/oemof/oemof-network/archive/dev.zip


Documentation
=============


https://oemof-network.readthedocs.io/


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

