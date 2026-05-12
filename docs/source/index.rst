|project|
=========

Installation
------------

.. code-block:: console

   $ pip install hackerrank-py

This is tested on Python |minimum-python-version|\+.

Usage
-----

Generate an API token from the `HackerRank for Work tokens page`_ and pass
it to :class:`hackerrank.client.HackerRank`:

.. code-block:: python

   """Example usage."""

   import sys

   from hackerrank.client import HackerRank

   client = HackerRank(api_key="your-api-key")
   for test in client.tests.list().data:
       sys.stdout.write(test.name)
   interview = client.interviews.create(title="My Interview")
   sys.stdout.write(interview.url or "")

See the :doc:`api-reference` for full usage details.

.. _HackerRank for Work tokens page: https://www.hackerrank.com/work/settings/token

Reference
---------

.. toctree::
   :maxdepth: 3

   api-reference
   openapi-spec
   contributing
   release-process
   changelog
