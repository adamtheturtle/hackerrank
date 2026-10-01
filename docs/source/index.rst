|project|
=========

Installation
------------

.. code-block:: console

   $ pip install hackerrank

This is tested on Python |minimum-python-version|\+.

Usage
-----

Generate an API token from the `HackerRank for Work tokens page`_ and pass it to :class:`hackerrank.client.HackerRank`:

.. code-block:: python

   """Example usage."""

   import sys

   from hackerrank.client import HackerRank

   client = HackerRank(api_key="your-api-key")
   for test in client.tests.list().data:
       _ = sys.stdout.write(test.name)
   interview = client.interviews.create(title="My Interview")
   _ = sys.stdout.write(interview.url)

Project directory uploads
-------------------------

Use ``client.questions.upload_project_directory(question_id=..., directory=Path(...))`` to upload a prepared directory for a fullstack question.
The client includes every file, including hidden files, with its relative path and original bytes.
It builds a ZIP in memory and delegates to ``upload_project_zip``, preserving the API response and retry behavior.
No temporary archive is created.
The asynchronous method performs file operations and compression in a worker thread.
Missing directories and regular files raise :class:`NotADirectoryError`.
Symbolic links within the directory raise :class:`ValueError`.
An empty directory produces an empty ZIP.

Filtering and transformations belong in the caller.
Use :func:`shutil.copytree` with an ``ignore`` callback and :class:`tempfile.TemporaryDirectory` to prepare and clean up a staging directory.
Already-prepared directories can be uploaded directly without copying.

.. code-block:: python

   """Filter a directory, then upload the staged files."""

   from pathlib import Path
   from shutil import copytree, ignore_patterns
   from tempfile import TemporaryDirectory

   from hackerrank.client import HackerRank

   with TemporaryDirectory() as temporary:
       source = Path(temporary) / "source"
       source.mkdir()
       _ = (source / "main.py").write_text(
           data="print('Hello')\n", encoding="utf-8"
       )
       directory = Path(
           copytree(
               src=source,
               dst=Path(temporary) / "upload",
               ignore=ignore_patterns("node_modules", "__pycache__", "*.pyc"),
           )
       )
       with HackerRank(api_key="your-api-key") as client:
           _response = client.questions.upload_project_directory(
               question_id="q1", directory=directory
           )

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
