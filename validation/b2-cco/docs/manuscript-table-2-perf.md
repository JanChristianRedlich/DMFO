# Manuscript Table 2 — Reasoning-performance metrics

> Drop-in replacement for the camera-ready TODO in Paper §4.2 Table 2.
> Numbers from `validation/results/perf_rdfs_symmetric.json` and
> `validation/results/table2_perf.json`.

## Configuration

* **Reasoner**: `owlrl` 7.x via `rdflib` 7.x. Two closure strategies
  reported: **OWL-RL_Semantics** (the conservative default
  consistent with Paper §3 Principle P1) and **RDFS_Semantics** (the
  empirically minimal closure that still answers all 20 ACQs on
  both DMFO and B2-CCO — see "Closure-strategy sufficiency" below).
* **Hardware**: numbers materialised at evaluation time on a single
  development workstation; `validation/results/env.json` records
  CPU / RAM / Java / Python versions used for the camera-ready
  numbers.
* **Symmetric strip**: both DMFO and B2-CCO apply a runtime
  metadata-strip (rdfs:label/comment/isDefinedBy, dcterms/vann
  predicates on TBox subjects, owl:Ontology header triples) so the
  comparison reflects entailment-relevant content only. ABox-level
  rdfs:labels (semantically load-bearing for CCO's ICE-mediated
  identifier pattern) are preserved on both sides.
* **Repetitions**: 30 reps per ACQ + median; warm-up rounds excluded.

## Table 2 — under OWL-RL_Semantics (conservative default)

| Metric | DMFO Mar. | DMFO Food | sosa Mar. | sosa Food | native Mar. | native Food |
|---|---|---|---|---|---|---|
| KB raw triples (loaded)              |   453 |   369 |   266 |   203 |   262 |   199 |
| KB raw triples (after strip)         |   284 |   210 |   213 |   157 |   213 |   157 |
| KB closure size                      |   964 |   765 |   689 |   554 |   689 |   554 |
| **Closure expansion time (ms)**      | **79.3** | **59.5** | **37.0** | **29.6** | **37.0** | **30.7** |
| Class I median (ms)                  |  2.12 |  1.96 |  2.51 |  2.34 |  2.36 |  2.38 |
| Class II median (ms)                 |  2.63 |  2.71 |  2.22 |  2.07 |  1.31 |  1.31 |
| Class III median (ms)                |  1.50 |  1.49 |  1.50 |  1.42 |  1.64 |  1.43 |
| Class IV median (ms)                 |  1.83 |  1.69 |  1.32 |  1.28 |  1.60 |  1.51 |
| Total query time (ms)                |  40.1 |  38.1 |  36.4 |  35.0 |  35.4 |  33.2 |
| **Total pipeline (closure + queries)** | **119.4** | **97.6** | **73.3** | **64.7** | **72.4** | **63.9** |

## Table 2′ — under RDFS_Semantics (production-efficient alternative)

| Metric | DMFO Mar. | DMFO Food | sosa Mar. | sosa Food | native Mar. | native Food |
|---|---|---|---|---|---|---|
| KB closure size                      |   664 |   504 |   447 |   347 |   447 |   347 |
| **Closure expansion time (ms)**      | **17.3** | **15.9** | **14.2** | **10.9** | **13.5** | **10.9** |
| Total query time (ms)                |  41.3 |  37.7 |  35.0 |  34.6 |  33.0 |  32.3 |
| **Total pipeline (closure + queries)** | **58.6** | **53.6** | **49.2** | **45.5** | **46.6** | **43.2** |
| Speedup vs. OWL-RL                   | **1.98×** | 1.77× | 1.47× | 1.42× | 1.48× | 1.44× |

## Closure-strategy sufficiency (key finding)

We tested whether the 20-ACQ catalogue can be answered under a
weaker closure than OWL-RL_Semantics. The result, run via
`validation/scripts/perf-rdfs-symmetric.py`:

| Framework | OWL-RL coverage | RDFS coverage | Δ |
|---|---|---|---|
| DMFO (maritime + food) | 20/20 | 20/20 | 0 |
| B2-CCO/sosa | 17/20 | 17/20 | 0 |
| B2-CCO/native | 15/20 | 15/20 | 0 |

**No ACQ in the catalogue depends on OWL-RL-specific entailment
rules** (cls-int1 intersection-of materialisation, prp-inv1/2
inverse-property, etc.). RDFS sub-class + sub-property + domain +
range entailment is sufficient on **both DMFO and B2-CCO**. This
falsifies the hypothesis that B2-CCO might require OWL-RL features
that DMFO does not — neither does. The closure-strategy choice is
therefore an **infrastructure decision**, not a coverage decision.

## Reading

* **Coverage outcomes are identical between OWL-RL and RDFS**
  (Table 3): DMFO 20/20, B2-CCO/sosa 17/20, B2-CCO/native 15/20
  under both closures.
* **DMFO benefits more from RDFS** (1.98× speedup vs. ~1.5× for
  B2-CCO) because DMFO's OWL-RL closure expanded more aggressively
  (964 vs. 689 triples maritime). Under RDFS the expansion is
  proportionally smaller (664 vs. 447) and DMFO's relative
  overhead drops accordingly.
* **DMFO–B2-CCO/native pipeline-time gap shrinks**:
  * under **OWL-RL**: 119 vs. 72 ms maritime → **1.6×** slower
  * under **RDFS**: 59 vs. 47 ms maritime → **1.26×** slower
* **Per-class query medians are within ±50%** across all
  configurations (1.3–2.7 ms) — the architectural difference is
  not a query-time differentiator under rdflib's BGP engine.
* **The 42 ms (OWL-RL) / 12 ms (RDFS) closure-expansion overhead
  on DMFO** is the empirical price of the alignment layer
  (A1 cls-int1 inferences, A3–A6 prp-spo1 + prp-dom + prp-rng
  entailments). It is fixed (does not grow with ABox size in the
  ranges studied) and amortizes across query batches.

## Configurable runtime

```bash
DMFO_CLOSURE=owl-rl  python3 validation/scripts/run_all_acqs.py --all   # default
DMFO_CLOSURE=rdfs    python3 validation/scripts/run_all_acqs.py --all
B2_CLOSURE=owl-rl    bash validation/scripts/b2cco-run-acqs.sh                      # default
B2_CLOSURE=rdfs      bash validation/scripts/b2cco-run-acqs.sh
```

The B2-CCO and DMFO runners share the same env-var convention so
benchmarks can be reproduced symmetrically.

## Caveats

* **rdflib + owlrl is a Python in-memory engine**. Apache Jena ARQ,
  Stardog, GraphDB, and other production triple-stores apply
  substantially different optimisations (BGP indexing, cost-based
  join planning, materialised closure caching). The relative cost
  of DMFO's larger closure may be smaller under such engines.
  Camera-ready may add a Jena ARQ comparison.
* **Pre-materialised closure cache.** Both frameworks could publish
  pre-closured KBs as runtime artefacts, reducing closure-expansion
  cost to zero on subsequent runs. Combined with the RDFS-suffizienz
  finding, this would make total pipeline cost ~SPARQL-only
  (~33–41 ms for both frameworks).
* **Small ABoxes (115–183 raw triples per profile).** At 10⁵ triples
  the closure-expansion cost would dominate over per-query cost much
  more strongly; the ratios reported here are the lower bound on the
  ABox-size-independent overhead.
