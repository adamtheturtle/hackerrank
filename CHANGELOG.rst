Changelog
=========

.. towncrier release notes start

2026.07.19
----------

- SCIM v2 requests are now sent to ``https://services.hackerrank.com/scim/v2`` instead of the v3 API host, so ``client.scim`` works out of the box. A new ``scim_base_url`` argument on ``HackerRank`` and ``AsyncHackerRank`` allows overriding it.

- Bring the async ``AsyncHackerRank`` client to full parity with the synchronous ``HackerRank`` client, adding all missing operations and aligning method shapes (``ats.codepair``/``ats.codescreen``, ``teams.memberships`` and ``scim.users``/``scim.groups`` sub-namespaces).

2026.07.08
----------

No significant changes.

2026.05.12.2
------------


2026.05.12.1
------------


2026.05.12
----------


* Initial release.
