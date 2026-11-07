# Exact optimization frontiers

These artifacts back the portal **Optimization** page.

`fable_2024/frontier.json` is the browser-ready exact frontier assembled from the Phase 37-40 exact
runs. It contains 160 unique scenario points and 15 unique Pareto objective triples. Every point is a
real 2024 Pyculator run; the viewer never runs a surrogate or an optimizer.

Regenerate from the exact artifacts:

```bash
.venv/bin/python scripts/fable_exact_decision.py \
  --input tmp/fable-exact-optimization/domain.json \
  tmp/fable-exact-sensitivity/sensitivity.json \
  tmp/fable-exact-sensitivity/combined \
  tmp/fable-exact-neighborhood/sensitivity.json \
  tmp/fable-exact-decision/targeted \
  --output tmp/fable-exact-decision/decision.json \
  --artifact-output examples/optimization/fable_2024/frontier.json \
  --version 2024
```

Boundary: the frontier is exact but local to the evaluated scenario set. Caps and floors are policy
inputs, and the provisional scenario rules are not expert-approved.
