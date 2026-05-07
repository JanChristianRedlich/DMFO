# B2-CCO: Common Core Ontologies Baseline for the DMFO Evaluation

**Purpose.** B2-CCO is the alternative-architecture baseline for the
DMFO paper. It implements the same 20 anchor competence questions
on top of the **Common Core Ontologies (CCO 2.0)**, a BFO-based
mid-level ontology, *without* re-introducing DMFO's typed bridge
architecture (Faithful-Translation-Rule, see
[`docs/faithful-translation-rule.md`](docs/faithful-translation-rule.md)).

The point is **not** to win or lose against DMFO. It is to demonstrate
which ACQ classes become structurally hard when the architecture follows
BFO's continuant/occurrent split + CCO's quality-inherence + ICE-based
modelling instead of DMFO's six typed bridges (A1–A6).

* Specification: [`../evaluation.md`](../evaluation.md)
* DMFO main repo: [`../README.md`](../README.md)
* Slot-mapping: [`docs/slot-mapping.md`](docs/slot-mapping.md)
* ADRs: [`docs/adr/`](docs/adr/)
* ACQ translation log: [`docs/acq-translation.md`](docs/acq-translation.md)

## Build / test

All baseline runners live in the consolidated
[`../validation/scripts/`](../validation/scripts/) folder (paper-strict
single-folder layout). Invoke them from the repository root:

```bash
# Run all 20 ACQs in both variants (sosa-coimport + strict-native)
bash validation/scripts/b2cco-run-acqs.sh

# Consistency check (rdflib + OWL-RL fallback if HermiT unavailable)
bash validation/scripts/b2cco-consistency-check.sh

# OOPS! pitfall scan against the public service
bash validation/scripts/b2cco-oops-check.sh

# High-rep DMFO/B2-CCO/sosa/B2-CCO/native side-by-side timing
python validation/scripts/b2cco-perf-benchmark.py
```

CCO 2.0 source is vendored read-only at
[`vendor/cco-2.0/`](vendor/cco-2.0/). The opaque IRI mapping is at
[`vendor/cco-2.0-mapping.csv`](vendor/cco-2.0-mapping.csv).

## Hard rules

1. No DMFO typed bridges in CCO clothing. No `b2cco:evidencedBy`.
2. CCO 2.0 opaque IRIs everywhere; `rdfs:label` for human readability.
3. Maritime first end-to-end. Food is future work.
4. Every modelling choice goes into an ADR.
5. DMFO files at the repo root are read-only references.
6. No hidden tuning. ACQ failures are documented, not patched.

## CCO version pinned

* CCO 2.0 commit: `9a8b27c87c6188cb0a469f1ead18fd602e42cc8a`
  (cloned 2026-05-03 from
  [`CommonCoreOntology/CommonCoreOntologies`](https://github.com/CommonCoreOntology/CommonCoreOntologies))
* BFO 2020 (transitively imported by CCO).
