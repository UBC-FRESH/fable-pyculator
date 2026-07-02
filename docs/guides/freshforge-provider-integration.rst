FreshForge Provider Integration
===============================

FABLE Pyculator exposes a FreshForge provider for FABLE notebook workflow stages. The original Phase
9 node types remain plan-only: they help FreshForge validate and plan FABLE-specific steps such as
notebook-spec discovery, output-ref derivation, validation-scenario preparation, downstream
Modelwright workflow construction, and notebook-loop planning. Phase 19 adds executable
scenario-bundle nodes for repeated selection-control runs against an existing generated model.

FABLE Pyculator owns FABLE workbook-surface and scenario-bundle semantics; Modelwright owns
generated-model inference, generation, execution, and validation; and FreshForge owns workflow
validation, planning, namespaces, and provider orchestration.

Installation Boundary
---------------------

FABLE Pyculator registers a ``freshforge.providers`` entry point. The core
package stays FreshForge-free during normal imports, but the ``freshforge``
extra installs the PyPI alpha needed for provider discovery, planning, and
execution:

.. code-block:: bash

   python -m pip install "fable-pyculator[freshforge]"

FreshForge can only discover the provider entry point after the current FABLE
Pyculator checkout has been installed into the active environment. From the
repository root, refresh the local editable install after pulling provider
changes:

.. code-block:: bash

   scripts/bootstrap_dev_env.sh

or, when the virtual environment already exists:

.. code-block:: bash

   source .venv/bin/activate
   python -m pip install -e ".[dev,notebook,docs]"

The development extra includes FreshForge so provider and matrix tests exercise
the published FreshForge alpha line.

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

Phase 19 adds executable scenario-bundle node types:

``scenario_bundle_prepare``
   Validates a bundle against a workbook-derived spec and writes normalized bundle metadata.

``scenario_run``
   Runs one bundle scenario against an existing matching generated model and writes rendered
   scenario artifacts.

``scenario_bundle_manifest``
   Assembles a namespaced bundle manifest from completed scenario run nodes.

The node vocabulary maps to the public workflow helper APIs documented in
:mod:`fable_pyculator.workflows`, including ``derive_output_refs``,
``derive_output_refs_for_strategy``, ``fable_freshforge_build_paths``,
``build_cached_workbook_validation_scenario``, ``prepare_freshforge_rebuild``, and
``build_modelwright_freshforge_workflow``. The 2021-specific helper names remain available as
compatibility shortcuts for existing notebooks and scripts.

For real workbook-derived output-ref strategy comparisons, see
:doc:`output-ref-strategy-comparison`. That guide records per-strategy FreshForge namespaces and
optional workflow documents without turning the FABLE provider into an execution adapter.

For executable scenario-bundle workflows, see
:doc:`scenario-bundle-freshforge-orchestration`.

Example
-------

The public-safe notebook workflow example uses ignored ``tmp/`` paths and can be validated or
planned when FreshForge is installed:

.. code-block:: bash

   freshforge validate examples/freshforge/fable_2021_notebook_workflow.yaml
   freshforge inspect examples/freshforge/fable_2021_notebook_workflow.yaml
   freshforge plan examples/freshforge/fable_2021_notebook_workflow.yaml

Planning this graph does not derive real output refs, inspect source workbooks, execute Modelwright,
or materialize generated artifacts. It proves only that the FABLE-specific planning boundary is
structured and discoverable.

The scenario-bundle workflow example can also be validated and planned:

.. code-block:: bash

   freshforge validate examples/freshforge/fable_2021_scenario_bundle_workflow.yaml
   freshforge plan examples/freshforge/fable_2021_scenario_bundle_workflow.yaml

Boundary
--------

The FABLE Pyculator provider may describe FABLE-specific workflow planning metadata. It must not:

- generate or validate Modelwright Python models;
- choose generic workbook conversion semantics;
- claim additional country-calculator compatibility from planning metadata alone.
