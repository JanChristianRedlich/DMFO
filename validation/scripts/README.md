# Validation scripts

All validation, conformance, performance, scaling and B2-CCO-baseline
scripts live under this single directory. They are meant to be invoked
from the **repository root** (not from this folder), e.g.

```bash
bash validation/scripts/run_queries.sh
python validation/scripts/run_all_acqs.py
bash validation/scripts/b2cco-run-acqs.sh
```

## Layout

| Group | File | Purpose |
| --- | --- | --- |
| Core | `validate_kb.py` | TBox/ABox parse + OWL-2-DL profile check. |
| Core | `conformance_validator.py` | Verifies (A1)–(A6) anchor signature + binding for a profile. |
| Core | `locality_check.py` | Top-locality classification per Cuenca Grau et al. (JAIR 2008). |
| Core | `run_hermit_reasoner.py` | HermiT classification + ABox consistency. |
| Core | `run_all_acqs.py` | Runs the 20-ACQ catalogue against DMFO+profile, plus B1 ablation. |
| Core | `run_queries.sh` | End-to-end pipeline orchestrator (calls every step in order). |
| Core | `fetch_imports.sh` | Pull local copies of PROV-O / SOSA / DUL / GeoSPARQL / OWL-Time into `ontology/imports/`. |
| Core | `build_runtime_tbox.py` | Stripped runtime TBox (no doc triples, no `owl:Ontology` headers). |
| Performance | `perf-owlrl-baseline.py` | Reference run, full OWL-RL, no strips. |
| Performance | `perf-rdfs-vs-owlrl.py` | Closure-strategy A/B for DMFO. |
| Performance | `perf-fair-comparison.py` | Symmetric DMFO ↔ B2-CCO comparison under matched closure. |
| Performance | `perf-runtime-stripped.py` | Runtime-strip (annotations, ontology headers) effect on closure ms. |
| Performance | `perf-aggressive-strip.py` | Adds remap of `dmfo:*` predicates to imported-vocabulary terms. |
| Performance | `perf-rdfs-symmetric.py` | Final symmetric RDFS+strip table for paper §5. |
| Performance | `perf-final-table2.py` | Renders Table 2 (perf summary) from intermediate JSONs. |
| Performance | `benchmark_closure_strategies.py` | Sweep over `OWLRL_Semantics` / `RDFS_Semantics` / `RDFS_OWLRL_Semantics` / `none`. |
| Scale | `generate_scaled_abox.py` | Synthesises `validation/scale-test/{dmfo,b2cco}-maritime-N{N}.ttl` for N ∈ {1…500}. |
| Scale | `scale-benchmark.py` | rdflib + owlrl scaling sweep N ∈ {1, 10, 25, 50, 100}. |
| Scale | `scale-benchmark-large.py` | Same sweep extended to N = 200, 500. |
| Jena (Docker) | `jena-bench/Dockerfile` | Apache Jena 5.5.0 image (Eclipse Temurin 21). |
| Jena (Docker) | `jena-bench/JenaBenchmark.java` | Closure (RDFSReasoner / OWLMicroReasoner) + ARQ ACQ timing. |
| Jena (Docker) | `jena-bench/run-jena-scale.sh` | Driver: iterates N × reasoner × framework into the container. |
| Jena (Docker) | `jena-bench/queries-native-merged/` | Strict-CCO-native overrides for the 4 SOSA-dependent ACQs. |
| B2-CCO baseline | `b2cco-consistency-check.sh` | HermiT (or OWL-RL fallback) on the B2-CCO TBox+ABox. |
| B2-CCO baseline | `b2cco-oops-check.sh` | OOPS! pitfall scan against the merged B2-CCO TBox. |
| B2-CCO baseline | `b2cco-run-acqs.sh` | Runs the 20 CCO-SPARQL queries in both `sosa` and `native` variants. |
| B2-CCO baseline | `b2cco-perf-benchmark.py` | High-rep timing benchmark across DMFO / B2-CCO-sosa / B2-CCO-native. |

`b2cco-tests-README.md` keeps the original B2-CCO-tests preamble for
historical context (HermiT optional-install notes etc.).

## Reproducibility flow

```bash
# 1. Build local imports
bash validation/scripts/fetch_imports.sh

# 2. Validate + run baseline
bash validation/scripts/run_queries.sh

# 3. Run B2-CCO baseline (sosa + native)
bash validation/scripts/b2cco-run-acqs.sh

# 4. Generate scaled ABoxes + run scaling sweeps
python validation/scripts/generate_scaled_abox.py
python validation/scripts/scale-benchmark.py
python validation/scripts/scale-benchmark-large.py

# 5. (Optional) Replicate scaling under Apache Jena via Docker
docker build -t dmfo-jena-bench:latest validation/scripts/jena-bench
bash validation/scripts/jena-bench/run-jena-scale.sh
```

All JSON outputs are written to `validation/results/`. B2-CCO outputs
that compare against DMFO write to `validation/b2-cco/results/` (kept inside the
baseline package so the comparison artefacts ship with that folder).
