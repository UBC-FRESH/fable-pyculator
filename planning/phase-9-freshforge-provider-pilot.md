# Phase 9: FreshForge Provider Pilot

## Summary

Phase 9 will add a plan-only FreshForge provider for FABLE Pyculator notebook
workflow stages after the Modelwright provider pilot exists.

## Intent

The provider should expose FABLE-specific workbook and notebook surfaces to
FreshForge without moving FABLE knowledge into Modelwright.

## Planned Node Vocabulary

- `fable_pyculator.build_notebook_spec`
- `fable_pyculator.derive_output_refs`
- `fable_pyculator.materialize_generated_model`
- `fable_pyculator.run_notebook_loop`
- `fable_pyculator.render_outputs`
- `fable_pyculator.record_validation_summary`

## Boundaries

- No FreshForge execution.
- No cache, checkpoint, or artifact materialization beyond existing notebook helper behavior.
- No generated-model inference or formula translation in FABLE Pyculator.
- Modelwright remains responsible for generic generated-model creation and validation.

## Issue Map

- Parent: #61
