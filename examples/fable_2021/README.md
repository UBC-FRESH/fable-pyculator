# FABLE 2021 Generated Model Artifact

This directory contains the approved compressed 2021 FABLE-C generated Python model used by the
FABLE Pyculator 2021 notebook.

Tracked artifact:

```text
examples/fable_2021/generated_fable_2021_model.py.xz
```

The source workbook is not tracked. Restore it locally under:

```text
tmp/private-workbooks/2021_Open_FABLECalculator.xlsx
```

The 2021 notebook materializes the compressed model into ignored working space:

```text
tmp/generated-models/fable-2021/generated_fable_2021_model.py
```

The tracked archive is authoritative. If the working model already exists but differs, force
materialization from the archive or remove the working file before preparing; the portal otherwise
uses the existing working model. A stale working model can silently change results even when the
tracked archive is correct.

## Validation Evidence

Phase 8 generated this model from the public 2021 FABLE Calculator workbook using Modelwright, after
the upstream Modelwright `VLOOKUP` `#N/A` generated-runtime fix in PR #204.

Validation summary:

- source workbook checksum:
  `aa5f2a768ae3670e93178a8f9f15fd10c4879101def52e987d374447098957e9`;
- extracted sheets: 62;
- extracted cells: 413,776;
- formula cells: 297,002;
- translated formula cells: 297,002;
- comparable cached outputs: 281,922;
- numeric comparable outputs: 240,124;
- text comparable outputs: 41,798;
- matches: 281,922;
- mismatches: 0;
- non-comparable cached blank formula outputs: 15,080.

The generated model source is about 117 MiB uncompressed and about 2.1 MiB as the tracked `.xz`
archive. The compressed archive checksum is:

```text
c9ab8dd1fba273cdd53386af1b65fae216086b4a05df78467681fdddbf5186d9
```

## Artifact Boundary

Only the compressed generated Python model is tracked here. Do not commit the 2021 source workbook,
decompressed generated source, `contract.json`, `expressions.json`, `constants.json`, raw validation
reports, logs, or scratch outputs. Those belong under ignored `tmp/` paths.
