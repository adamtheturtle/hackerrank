|project|
=========

Installation
------------

.. code-block:: console

   $ pip install hackerrank

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

HTTPX2 transports
-----------------

HTTPX remains the default client family. To opt in to HTTPX2, construct the
HTTPX2 transport explicitly and pass it to the client. The standard
``hackerrank`` installation includes both client families.

.. code-block:: python

   """Configure HackerRank to use HTTPX2."""

   import httpx2

   from hackerrank.client import HackerRank
   from hackerrank.transports import HTTPX2Transport

   transport = HTTPX2Transport(timeout=httpx2.Timeout(timeout=10))
   with HackerRank(api_key="your-api-key", transport=transport) as client:
       tests = client.tests.list()

Use ``AsyncHTTPX2Transport`` with ``AsyncHackerRank`` for asynchronous calls.
The ``timeout`` argument accepts an HTTPX2 timeout object or a number of
seconds; do not pass an equivalent ``httpx`` object across the package
boundary. Existing HTTPX users do not need to change anything. Migrating to
HTTPX2 only requires selecting the new transport; HackerRank client methods
and returned models are unchanged.

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
   unreleased
   changelog
