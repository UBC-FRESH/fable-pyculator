Release And Deployment
======================

FABLE Pyculator releases follow the same maintainer-controlled pattern as Modelwright. A release is
ready only when package artifacts, documentation, alpha-boundary claims, and publication gates have
all been checked.

Current Release Candidate
-------------------------

The current alpha target is ``0.1.0a6``, published with Git tag ``v0.1.0a6``. The previous alpha
was ``0.1.0a5``. Publication and deployment remain maintainer-controlled actions.

This alpha may claim an early FABLE-C notebook wrapper that can discover the public 2020/2021
``SCENARIOS selection`` controls, inspect ``SCENARIOS definition`` tables, render canonical output
tables with output-column flavour filtering, render curated FOOD/LAND/GHG/WATER headline frames, run
a locally restored Modelwright-generated 2020 model from ignored ``tmp/`` artifacts, restore
validated compressed 2021 and 2024 generated models, plan and assemble FreshForge/Modelwright
rebuild workflows, run selection-control scenario bundles against an existing matching generated
model, compare output-ref strategy boundaries, orchestrate strategy-boundary and scenario-bundle
matrices through FreshForge, package opt-in benchmark evidence from restored local artifacts, and
serve the optional FastAPI portal with approved-artifact checksum verification, authenticated
staging, persistent assistant chats, and the GitHub issue-filing workflow.

The 2024 artifact is reproducible from the repaired workbook with Modelwright ``0.1.0a9`` or newer;
the tracked archive and a fresh regeneration are byte-identical.

It must not claim stable public API compatibility, full editable scenario-definition widgets,
production readiness, arbitrary country-calculator support, or generated-model equivalence beyond
the recorded public 2020/2021 FABLE-C benchmark evidence.

Local Release Checks
--------------------

Start from a clean checkout and bootstrap the repo-local development environment:

.. code-block:: bash

   scripts/bootstrap_dev_env.sh

Run the normal local checks:

.. code-block:: bash

   .venv/bin/python -m ruff check .
   .venv/bin/python -m pytest -vv
   .venv/bin/sphinx-build -b html docs _build/html -W -v
   .venv/bin/python scripts/verify_docs_theme.py _build/html

Build and inspect package artifacts:

.. code-block:: bash

   scripts/check_release_artifacts.sh

The artifact checker writes outputs under ignored ``tmp/release-checks/``. It builds an sdist and
wheel, runs ``twine check``, inspects artifact contents for source workbooks, raw generated models,
or unapproved generated artifacts, installs the wheel into a clean virtual environment, imports FABLE
Pyculator, and verifies the published package version.

Documentation Deployment Gate
-----------------------------

The docs workflow builds Sphinx documentation and uploads the built HTML artifact to GitHub Pages.
The build must pass ``scripts/verify_docs_theme.py`` so the uploaded artifact uses the Sphinx Read the
Docs theme rather than a fallback site.

After a release PR merges to ``main``, verify the published GitHub Pages site from the workflow
deployment result. The deployed page should show the Read the Docs side navigation and should not look
like a plain project page.

TestPyPI Rehearsal
------------------

Use the ``Release`` GitHub Actions workflow with ``publish_target`` set to ``testpypi``.

Requirements:

- the ``testpypi`` environment must be configured by the maintainer;
- trusted publishing is preferred;
- no API tokens should be committed to the repository;
- the workflow must build artifacts before publishing them.

After TestPyPI publication, install the package from TestPyPI in a clean environment and run at
least:

.. code-block:: bash

   python -m pip download --no-deps --index-url https://test.pypi.org/simple/ \
     --dest /tmp/fable-a6 fable-pyculator==0.1.0a6
   python -m pip install --no-deps /tmp/fable-a6/fable_pyculator-0.1.0a6-py3-none-any.whl
   python -m pip install --index-url https://pypi.org/simple/ \
     'modelwright[notebook]>=0.1.0a9' 'openpyxl>=3.1' 'pandas>=2' 'PyYAML>=6' \
     'fastapi>=0.110' 'uvicorn>=0.29'
   python -c "import fable_pyculator; print(fable_pyculator.__version__)"

Do not use TestPyPI as the primary dependency index. It can expose broken dependency artifacts
that are unrelated to this package; use PyPI for dependencies and TestPyPI only for the exact
release wheel/sdist.

Real PyPI Publication
---------------------

Real PyPI publication requires maintainer approval and the protected ``pypi`` environment.

Expected sequence:

1. Confirm ``CHANGE_LOG.md`` and release notes describe the actual alpha boundary.
2. Confirm local and CI release artifact checks pass.
3. Confirm TestPyPI rehearsal passes or document the exact blocker.
4. Create the annotated tag, for example ``v0.1.0a6``.
5. Run the ``Release`` workflow or push the tag, then approve the protected PyPI environment.
6. Verify the package page, wheel install, import, docs deployment, and GitHub release notes.

Verify the public prerelease explicitly:

.. code-block:: bash

   python -m pip install --pre 'fable-pyculator[web]==0.1.0a6'
   python -c "import fable_pyculator; print(fable_pyculator.__version__)"
   fable-pyculator --version

Pip needs ``--pre`` when resolving a prerelease by version, even when the version is pinned.

Rollback And Yanking
--------------------

If a broken alpha reaches PyPI, do not reuse the same version. PyPI artifacts are immutable.

Use one of these responses:

- yank the broken release on PyPI if installation should be discouraged but historical availability is
  still useful;
- publish a new alpha such as ``0.1.0a6`` after fixing the issue;
- update release notes and roadmap entries with the failure mode and mitigation.

Private Data Rules
------------------

Release artifacts must not include source workbooks, decompressed generated Python clones, raw
validation reports, local logs, credentials, or ignored ``tmp/`` material.

The approved generated-model exceptions in the public repository are the compressed 2021 and 2024
artifacts and their uncompressed checksum sidecars:

.. code-block:: text

   examples/fable_2021/generated_fable_2021_model.py.xz
   examples/fable_2021/generated_fable_2021_model.py.sha256
   examples/fable_2024/generated_fable_2024_model.py.xz
   examples/fable_2024/generated_fable_2024_model.py.sha256
