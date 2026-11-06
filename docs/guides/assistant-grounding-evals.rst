Assistant Grounding Evaluations
===============================

The portal assistant has two evaluation layers: deterministic structural checks and opt-in live
grounding checks.

Structural checks
-----------------

The structural suite builds the current cheat sheet from real repository files and verifies that:

- every expected source/doc path exists and appears in the cheat sheet's required-reading list;
- the sheet contains the documentation digest and AST-generated source API index;
- known facts are present, including ``build_notebook_spec``, ``class ModelFacade``,
  ``TotalResultsWF``, the 2024 version difference, and the GitHub issue-filing protocol.

Run it from the repository root:

.. code-block:: bash

   python scripts/evaluate_assistant_grounding.py

This is fast and safe for CI because it does not invoke the assistant model.

Live grounding checks
---------------------

Use ``--live`` to run the installed ``opencode`` CLI for a fixed question set. Each case checks
that the answer or tool actions cite an expected file and contain expected terms, and that forbidden
claims are absent:

.. code-block:: bash

   python scripts/evaluate_assistant_grounding.py --live
   python scripts/evaluate_assistant_grounding.py --live --json
   python scripts/evaluate_assistant_grounding.py --live --case notebook_signature

The live suite is opt-in because it depends on local agent authentication, model availability, and
network timing. It uses the same new-session grounding prompt as the portal, including the compiled
cheat sheet. The current cases cover the notebook API signature, Modelwright's ``ModelFacade``, the
2024 missing water series, the portal's read-only boundary, and GitHub issue filing.

The corresponding pytest entry point is gated:

.. code-block:: bash

   FABLE_PYCULATOR_RUN_AGENT_EVALS=1 python -m pytest -q tests/web/test_grounding_evals.py

Browser smoke
-------------

``scripts/browser_smoke.py`` starts an isolated portal, drives the real SPA in Chromium, and checks:

- the **+ Ask** overlay opens;
- Shift+Enter inserts a newline and Enter submits;
- assistant markdown renders as HTML;
- a live assistant chat persists across a full page reload.

Run it with Playwright installed:

.. code-block:: bash

   python -m pip install -e '.[browser]'
   playwright install chromium
   python scripts/browser_smoke.py --root . --server-python .venv/bin/python --live-agent

The pytest wrapper is gated:

.. code-block:: bash

   FABLE_PYCULATOR_RUN_BROWSER_TESTS=1 python -m pytest -q tests/web/test_browser_e2e.py

CI should keep both live layers opt-in. The structural checks and all non-agent portal tests remain
the default blocking gates.
