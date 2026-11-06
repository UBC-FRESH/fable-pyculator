GitHub issue workflow
=====================

This project uses the UBC-FRESH phase/task issue workflow. GitHub issues are part of the project
specification, not an informal chat log. The issue body must let a new student, an external
collaborator, or a coding agent understand the task, do it, verify it, and close it without the
conversation that created it.

The portal assistant may draft and file an issue on the user's behalf, but it must use this page,
the tracked issue templates, and the repository state. It must not invent repository names, parent
issue numbers, task identifiers, labels, or verification evidence.

Choose the type and level first
-------------------------------

Ask the user enough questions to classify the request before drafting. A short set of questions is
usually enough:

- Is this a bug, a feature request, a documentation change, a maintenance task, or a question?
- What user-visible behaviour or file is affected?
- Which workbook version, portal page, command, notebook, or package area is involved?
- What is the impact and urgency: blocker, wrong result, confusing output, or a nice-to-have?
- Is this one task under the active phase, or a coherent multi-task deliverable that needs a new
  phase?
- What is in scope, and what is explicitly out of scope?
- How will we know it is done? What command, test, screenshot, or read-back proves it?
- For a bug: what are the exact steps, expected result, actual result, version, and relevant output?
- For a feature: what problem does it solve, who benefits, and what alternatives were considered?
- For documentation: which page is wrong or missing, and what should it say instead?
- Does the report contain secrets, private workbook data, personal paths, or other material that must
  not be published?

The issue level is one of:

``Phase`` (parent issue)
  A coherent deliverable made of multiple tasks. Use the ``phase`` template only after the
  maintainer agrees to a new roadmap phase. Title: ``P<n>: <phase name>``.
``Task`` (child issue)
  The default for a bug, feature request, documentation change, or maintenance item. Use the
  ``task`` template and link the issue as a sub-issue of the active phase. Title:
  ``P<n>.<m>: <task name>``.
``Subtask`` (checklist item)
  A step inside an existing task issue. Do not create a fourth issue level.

Issue type is metadata, not a fourth level. Prefer labels that already exist in the repository:

- ``bug`` for incorrect behaviour or an incorrect result;
- ``enhancement`` for a feature request;
- ``documentation`` for a docs-only change;
- ``question`` for a request for information that may not become code;
- ``help wanted`` or ``good first issue`` when the maintainer has decided that they apply.

The canonical workflow also uses ``phase`` and ``task`` labels to express the level. Check
``gh label list`` before posting. If a required label is missing, say so and ask the maintainer to
create it rather than silently inventing a different convention.

Before drafting
---------------

Audit the repository read-only first:

.. code-block:: bash

   gh issue list --state open
   gh issue view <n> --json number,title,state,body,labels
   gh pr list --state open
   sed -n '1,180p' ROADMAP.md

Find the active phase parent issue and the next task identifier in ``ROADMAP.md``. Do not guess them.
If the issue belongs to a different phase, confirm that with the maintainer. If no open parent issue
exists for the active phase, ask whether to create it from ``phase.md`` or attach the task to an
existing phase before creating the child issue.

Draft the body from the template
--------------------------------

Use the tracked template:

- ``.github/ISSUE_TEMPLATE/task.md`` for a task;
- ``.github/ISSUE_TEMPLATE/phase.md`` for a new phase.

The task body has these labelled sections, in this order:

.. code-block:: text

   Task identifier:
   Parent phase issue:
   Status:
   Branch:
   Related planning:
   Goal:
   Scope:
   Out of scope:
   Subtasks:
   Acceptance criteria:
   Verification:
   Artifacts:
   Risks:
   Completion metadata:

The phase body uses ``Phase identifier:``, ``Status:``, ``Branch:``, ``Roadmap:``, and
``Pull request:`` instead of the task header, and adds ``Architecture notes:`` and
``Child task checklist:``.

Formatting rules:

- Put each section label on its own line.
- Use real task-list syntax, one item per line: ``- [ ] First subtask.``.
- Wrap branch names, paths, commands, issue numbers, and commit hashes in backticks.
- Replace every placeholder such as ``<n>``, ``<m>``, ``<parent>``, or ``<task name>``.
- Do not build the body with escaped strings or inline pseudo-checklists.
- Do not include tokens, private workbook contents, personal home paths, or raw transcripts.

Validate and confirm before posting
-----------------------------------

Write the body to an ignored file, for example ``tmp/issue-<slug>.md``. Validate it with the local
checker before posting:

.. code-block:: bash

   python scripts/check_issue_body.py \
     --kind task \
     --title "P28.10: Add an example task" \
     --file tmp/issue-add-example-task.md

Then show the user the proposed title, labels, parent issue, and body. Ask for explicit confirmation
before creating the issue, unless the user already gave a complete, unambiguous request and asked
you to file it immediately. If required information is missing, ask only for the missing details and
say what is already known.

Post and verify
---------------

Create the issue from the body file:

.. code-block:: bash

   gh issue create \
     --repo UBC-FRESH/fable-pyculator \
     --title "P28.10: Add an example task" \
     --body-file tmp/issue-add-example-task.md \
     --label task \
     --label enhancement

Link a task to its parent when the web interface does not do it automatically:

.. code-block:: bash

   child_id=$(gh api repos/UBC-FRESH/fable-pyculator/issues/<child> --jq .id)
   gh api -X POST repos/UBC-FRESH/fable-pyculator/issues/<parent>/sub_issues \
     -F sub_issue_id="$child_id"

Read the result back before reporting success:

.. code-block:: bash

   gh issue view <child> --json number,title,state,body,labels,url

Report the issue number and URL. If GitHub is unavailable or unauthenticated, record the exact
command, exit status, and error text, keep a draft manifest under ``tmp/`` or ``notes/``, and say that
the issue was not filed. Never describe the GitHub side as complete when it is not.

Assistant behaviour
-------------------

When the user asks to "file an issue", "report a bug", or "request a feature", the portal assistant
must:

1. Read this page and the selected template before drafting.
2. Ask for the missing type, scope, scale, impact, reproduction or desired outcome, acceptance
   criteria, and verification details.
3. Inspect ``ROADMAP.md`` and the current GitHub issues to choose the parent phase and task ID.
4. Draft the canonical body, write it to a file, and run ``scripts/check_issue_body.py``.
5. Show the draft and get confirmation.
6. Post with ``gh issue create --body-file``, link the parent, read it back, and report the URL.
7. Stop and explain the exact blocker if filing cannot be completed.
