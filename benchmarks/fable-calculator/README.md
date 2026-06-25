# FABLE Calculator Benchmarks

The public FABLE-C Excel workbooks are local benchmark inputs for wrapper development. They are not
tracked in Git; keep them under ignored `tmp/private-workbooks/`.

Download folder:

```text
https://www.dropbox.com/scl/fo/ndgldfnq81v794mm8yebe/ADusMz23xtmYKDXoEkiNtJM?rlkey=d87qhjf5zd0pcowd5pfl5qdu7&st=qijm4tta&e=2&dl=0
```

Current local roles:

- `2019_Open_FABLECalculator.xlsx`: older structure and broken-reference/fragility check.
- `2020_Open_FABLECalculator.xlsx`: primary wrapper benchmark.
- `2021_Open_FABLECalculator.xlsx`: later generalizability check.

Verify downloaded files from the repository root:

```bash
sha256sum -c benchmarks/fable-calculator/checksums.sha256
```

