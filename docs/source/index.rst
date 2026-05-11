|project|
=========

Installation
------------

.. code-block:: console

   $ pip install hackerrank-py

This is tested on Python |minimum-python-version|\+.

Usage
-----

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

Reference
---------

.. toctree::
   :maxdepth: 3

   api-reference
   openapi-spec
   contributing
   release-process
   changelog
