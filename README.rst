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

Updating private notes
----------------------

Use ``client.questions.update_internal_notes(question_id=..., internal_notes=...)`` to change private interviewer notes.
The same operation is available on ``AsyncHackerRank``.
It reads current fields, skips equivalent notes, resends required fields unchanged, and reads back the saved question.
It raises ``ValueError`` if required fields are absent or verification finds changes to other modeled fields.
Pass ``notes_equal`` to supply a comparison callback for server serialization differences.
The default compares exact text and treats absent notes as empty.
HTML comparison policies and question-type restrictions remain with the caller.

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
Existing HTTPX users can keep their current configuration, but HTTPX2 transports require timeout objects from HTTPX2 when passing them across the package boundary.
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
