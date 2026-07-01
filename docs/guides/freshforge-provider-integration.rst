FreshForge Provider Integration
===============================

FABLE Pyculator exposes a plan-only FreshForge provider for FABLE notebook workflow stages. The
provider helps FreshForge validate and plan FABLE-specific steps such as notebook-spec discovery,
output-ref derivation, validation-scenario preparation, downstream Modelwright workflow construction,
and notebook-loop planning.

This provider is deliberately not an execution adapter. FABLE Pyculator owns FABLE workbook-surface
knowledge; Modelwright owns generated-model inference, generation, execution, and validation; and
FreshForge owns workflow validation, planning, and provider orchestration.

Installation Boundary
---------------------

FABLE Pyculator registers a ``freshforge.providers`` entry point, but it does not depend on
FreshForge directly. FreshForge can only discover that entry point after the current FABLE Pyculator
checkout has been installed into the active environment. From the repository root, refresh the local
editable install after pulling provider changes:

.. code-block:: bash

   scripts/bootstrap_dev_env.sh

or, when the virtual environment already exists:

.. code-block:: bash

   source .venv/bin/activate
   python -m pip install -e ".[dev,notebook,docs]"

Then install FreshForge separately in development environments that need provider discovery or
workflow planning:

.. code-block:: bash

   python -m pip install "freshforge @ git+https://github.com/UBC-FRESH/freshforge.git@v0.1.0a1"

Confirm that FreshForge can see the FABLE Pyculator provider before validating the example:

.. code-block:: bash

   freshforge providers

The provider list should include ``fable_pyculator``. If validation reports
``Provider 'fable_pyculator' is not registered``, reinstall FABLE Pyculator in the active
environment with ``python -m pip install -e ".[dev,notebook,docs]"``.

Normal imports remain FreshForge-free:

.. code-block:: python

   import fable_pyculator

Provider Nodes
--------------

The provider id is ``fable_pyculator``. Phase 9 exposes these plan-only node types:

``notebook_spec_discover``
   Declares FABLE workbook-surface discovery into a notebook-facing spec.

``output_refs_derive``
   Declares output-ref derivation from FABLE output-table flavour metadata such as ``OUTPUT-*``.

``validation_scenario_prepare``
   Declares cached-workbook validation-scenario preparation for selected output refs.

``modelwright_workflow_build``
   Declares construction of the downstream Modelwright FreshForge workflow document.

``notebook_loop_plan``
   Declares a notebook loop around a matching workbook spec and generated model.

The node vocabulary maps to the public workflow helper APIs documented in
:mod:`fable_pyculator.workflows`, including ``derive_output_refs``,
``derive_output_refs_for_strategy``, ``fable_freshforge_build_paths``,
``build_cached_workbook_validation_scenario``, ``prepare_freshforge_rebuild``, and
``build_modelwright_freshforge_workflow``. The 2021-specific helper names remain available as
compatibility shortcuts for existing notebooks and scripts.

Example
-------

The public-safe example workflow uses ignored ``tmp/`` paths and can be validated or planned when
FreshForge is installed:

.. code-block:: bash

   freshforge validate examples/freshforge/fable_2021_notebook_workflow.yaml
   freshforge inspect examples/freshforge/fable_2021_notebook_workflow.yaml
   freshforge plan examples/freshforge/fable_2021_notebook_workflow.yaml

Planning this graph does not derive real output refs, inspect source workbooks, execute Modelwright,
or materialize generated artifacts. It proves only that the FABLE-specific planning boundary is
structured and discoverable.

Boundary
--------

The FABLE Pyculator provider may describe FABLE-specific workflow planning metadata. It must not:

- execute FABLE notebook loops;
- generate or validate Modelwright Python models;
- choose generic workbook conversion semantics;
- claim additional country-calculator compatibility from planning metadata alone.
