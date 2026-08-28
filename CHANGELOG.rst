Changelog
=========

.. towncrier release notes start

2026.08.28
----------

- Every method which changes state now documents whether it is safe to retry, and why. ``tests.archive`` is now treated as safe to repeat, so it is retried when ``retries`` is set.

2026.08.27
----------

- The built-in ``HTTPXTransport`` and ``AsyncHTTPXTransport`` now default to a 60 second timeout instead of inheriting ``httpx``'s 5 second default, and accept a ``timeout`` argument so callers can choose their own.

- ``HackerRank`` and ``AsyncHackerRank`` accept a ``retries`` argument, defaulting to ``0``, which retries transport errors and ``429``, ``500``, ``502``, ``503`` and ``504`` responses for the requests which are safe to repeat.

2026.08.22
----------

- Accept documented object-form interviewers and candidate_details, preserve
  interview schedule / live fields, and return invite and update response
  bodies from sync and async clients.

- Add ``client.candidates.search`` (sync and async) for the global
  candidate-search endpoint, with typed attempt and candidate results.

- Expose documented list filters and body fields for interviews,
  questions, templates, and candidate invites on sync and async
  clients.

- Reject bare ``str`` values for list-like API fields (``interviewers``,
  ``languages``, ``tags``, and related parameters) so they are no longer
  split into character arrays in request bodies.

- Refresh ``openapi.json`` from the live HackerRank schema and add a
  semantic drift check that ignores dynamic example timestamps.

- Add ``client.interview_templates.explicit_sharing_roles`` with
  ``update_access`` and ``remove_access`` for sharing an interview template with
  users, teams or the whole company.

  Remove the ``team_share`` argument from interview-template ``create`` and
  ``update``. HackerRank ignores the parameter and has removed it from the API
  documentation; use ``explicit_sharing_roles`` instead.

- SCIM user and group PATCH methods now parse the documented message acknowledgement instead of treating the response as a full resource.

- SCIM group PATCH methods now parse the documented message acknowledgement instead of treating the response as a full group.

- SCIM pagination preserves an explicit ``startIndex`` of ``0`` instead of rewriting it to ``1``.

- ``generate_codestubs`` now requires a request body, matching the API contract.

- Custom transports are only replaced by the default when ``transport`` is ``None``, so falsy callables are preserved.

- Unexpected HTTP 3xx redirect responses now raise ``RedirectError`` instead of being treated as successful API responses.

- Trailing slashes on custom ``base_url`` and ``scim_base_url`` values are stripped so request paths are not double-slashed.

2026.08.16
----------

No significant changes.

2026.07.30
----------

- Align interview-template create and update requests with the current API,
  return updated templates, and parse live string template IDs and integer
  question IDs.

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
