# Phase 10: Cross-Package FreshForge Workflow Example

## Summary

Phase 10 will add a plan-only FreshForge workflow example that composes FABLE
Pyculator workbook-surface discovery with Modelwright generated-model planning.

## Intent

The workflow should make the end-to-end FABLE workbook-version path explicit:
FABLE Pyculator identifies the FABLE notebook/output surfaces, Modelwright owns
generic generated-model materialization and validation stages, and FreshForge
owns graph validation, inspection, and planning.

## Planned Flow

1. Restore a version-specific FABLE workbook under ignored local paths.
2. Build the FABLE Pyculator notebook spec.
3. Derive explicit output refs from FABLE output tables or headline series.
4. Plan Modelwright contract inference, generation, execution, and validation.
5. Plan FABLE notebook rendering from the matching workbook and generated model.

## Boundaries

- No FreshForge execution unless a later FreshForge phase explicitly provides it.
- No source workbook, raw generated model, or raw validation report tracking.
- No claim of new FABLE country-calculator support from a plan-only graph.

## Issue Map

- Parent: #62
