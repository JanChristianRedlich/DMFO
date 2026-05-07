# B2-CCO Tests

* `consistency-check.sh` — TBox + ABox parsed under rdflib, checked for
  HermiT-class consistency if Java + JPype1 + owlready2 are available;
  falls back to OWL-RL closure + disjointness-violation grep otherwise.
* `oops-check.sh` — POSTs the merged TBox to oops.linkeddata.es,
  parses the result HTML, stores the per-pitfall report at
  `../results/oops-report.json`.
* `run-acqs.sh` — runs the 20 CCO-SPARQL queries against the maritime
  KB; emits `../results/b2-cco-results.json` + `../results/b2-cco-perf.json`.

## HermiT install (optional)

```bash
pip install JPype1 owlready2
# owlready2 ships HermiT.jar internally
```

If JPype1 is not available, the consistency check uses the rdflib +
owlrl OWLRL_Semantics closure as a sound-but-incomplete substitute.
This is documented in the per-test output.
