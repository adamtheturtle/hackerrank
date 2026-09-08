|Build Status| |PyPI|

hackerrank
==========

Python library for the `HackerRank for Work API`_.

.. _HackerRank for Work API: https://www.hackerrank.com/work/apidocs

Installation
------------

.. code-block:: shell

   pip install hackerrank

This is tested on Python |minimum-python-version|\+.

Getting Started
---------------

Generate an API token from the `HackerRank for Work tokens page`_ and pass it as ``api_key``:

.. code-block:: python

   """Example usage."""

   import sys

   from hackerrank.client import HackerRank

   client = HackerRank(api_key="your-api-key")
   for test in client.tests.list().data:
       _ = sys.stdout.write(test.name)
   interview = client.interviews.create(title="My Interview")
   _ = sys.stdout.write(interview.url)

.. _HackerRank for Work tokens page: https://www.hackerrank.com/work/settings/token

HTTPX2 transports
-----------------

HTTPX remains the default client family.
To opt in to HTTPX2, construct the HTTPX2 transport explicitly and pass it to the client.
The standard ``hackerrank`` installation includes both client families.

.. code-block:: python

   """Configure HackerRank to use HTTPX2."""

   import httpx2

   from hackerrank.client import HackerRank
   from hackerrank.transports import HTTPX2Transport

   transport = HTTPX2Transport(timeout=httpx2.Timeout(timeout=10))
   with HackerRank(api_key="your-api-key", transport=transport) as client:
       tests = client.tests.list()

Use ``AsyncHTTPX2Transport`` with ``AsyncHackerRank`` for asynchronous calls.
The ``timeout`` argument accepts an HTTPX2 timeout object or a number of seconds.
Pass only HTTPX2 timeout objects across the package boundary.
Existing HTTPX users do not need to change anything.
Migrating to HTTPX2 only requires selecting the new transport.
HackerRank client methods and returned models are unchanged.

Full Documentation
------------------

See the `full documentation <https://adamtheturtle.github.io/hackerrank/>`__.

.. |Build Status| image:: https://github.com/adamtheturtle/hackerrank/actions/workflows/ci.yml/badge.svg?branch=main
   :target: https://github.com/adamtheturtle/hackerrank/actions
.. |PyPI| image:: https://badge.fury.io/py/hackerrank.svg
   :target: https://badge.fury.io/py/hackerrank
.. |minimum-python-version| replace:: 3.13
