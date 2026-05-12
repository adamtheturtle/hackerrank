|Build Status| |PyPI|

hackerrank-py
=============

Python library for the `HackerRank for Work API`_.

.. _HackerRank for Work API: https://www.hackerrank.com/work/apidocs

Installation
------------

.. code-block:: shell

   pip install hackerrank-py

This is tested on Python |minimum-python-version|\+.

Getting Started
---------------

Generate an API token from the `HackerRank for Work tokens page`_ and
pass it as ``api_key``:

.. code-block:: python

   """Example usage."""

   import sys

   from hackerrank.client import HackerRank

   client = HackerRank(api_key="your-api-key")
   for test in client.tests.list().data:
       sys.stdout.write(test.name)
   interview = client.interviews.create(title="My Interview")
   sys.stdout.write(interview.url or "")

.. _HackerRank for Work tokens page: https://www.hackerrank.com/work/settings/token

Full Documentation
------------------

See the `full documentation <https://adamtheturtle.github.io/hackerrank/>`__.

.. |Build Status| image:: https://github.com/adamtheturtle/hackerrank/actions/workflows/ci.yml/badge.svg?branch=main
   :target: https://github.com/adamtheturtle/hackerrank/actions
.. |PyPI| image:: https://badge.fury.io/py/hackerrank-py.svg
   :target: https://badge.fury.io/py/hackerrank-py
.. |minimum-python-version| replace:: 3.13
