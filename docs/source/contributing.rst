Contributing to |project|
=========================

Contributions to this repository must pass tests and linting.

CI is the canonical source of truth.

Install contribution dependencies
---------------------------------

Install Python dependencies in a virtual environment.

.. code-block:: console

   $ pip install --editable '.[dev]'

Spell checking requires ``enchant``.
This can be installed on macOS, for example, with `Homebrew`_:

.. code-block:: console

   $ brew install enchant

and on Ubuntu with ``apt``:

.. code-block:: console

   $ apt-get install -y enchant

Install ``prek`` hooks:

.. code-block:: console

   $ prek install

Linting
-------

Run lint tools either by committing, or with:

.. code-block:: console

   $ prek run --all-files --hook-stage pre-commit --verbose
   $ prek run --all-files --hook-stage pre-push --verbose
   $ prek run --all-files --hook-stage manual --verbose

.. _Homebrew: https://brew.sh

Running tests
-------------

Run ``pytest``:

.. code-block:: console

   $ pytest

Changelog entries
-----------------

Add one news fragment per user-facing change, as
:file:`newsfragments/<issue-number>.change.rst`, containing a single
sentence in the past or present tense.

``towncrier`` collects fragments by that exact filename pattern at
release time and silently ignores anything else, including a fragment
filed in a subdirectory, so a misnamed fragment never reaches the
changelog. A test guards against this.

Documentation
-------------

Documentation is built on Read the Docs.

Run the following commands to build and view documentation locally:

.. code-block:: console

   $ uv run --extra=dev sphinx-build -M html docs/source docs/build -W
   $ python -c 'import os, webbrowser; webbrowser.open("file://" + os.path.abspath("docs/build/html/index.html"))'

Continuous integration
----------------------

Tests are run on GitHub Actions.
The configuration for this is in :file:`.github/workflows/`.

Performing a release
--------------------

See :doc:`release-process`.
