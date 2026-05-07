# Strict CCO-Native Query Overrides

Per Faithful-Translation-Rule **F1** ("every slot uses a CCO 2.0
pattern documented in Jensen et al. 2024 or the *Modeling with CCO*
guide"), SOSA/SSN is **not** part of CCO 2.0. ADR-003a co-imported
SOSA as a documented exception "for evaluation only". This directory
holds the **strict CCO-native variant** of the four ACQs that depend
on SOSA properties: it uses only `cco:Measurement Information Content
Entity` + `cco:is about` (ADR-003b).

## Files

| Original | Strict native | What changes |
|---|---|---|
| `../queries/acq-05-cco.rq` (ACQ-II-03 state→evidence) | `acq-05-cco-native.rq` | substitute `sosa:hasFeatureOfInterest` → `cco:is about`; lose phenomenon/result-time + sensor annotations |
| `../queries/acq-08-cco.rq` (ACQ-II-06 observation completeness) | `acq-08-cco-native.rq` | structurally underdetermined — Measurement ICE has no bitemporal phenomenon/result-time split |
| `../queries/acq-11-cco.rq` (ACQ-III-03 state→evidence→sensor) | `acq-11-cco-native.rq` | structurally underdetermined — Measurement ICE has no sensor link |
| `../queries/acq-17-cco.rq` (ACQ-IV-01 evidence gap) | `acq-17-cco-native.rq` | substitute `sosa:hasFeatureOfInterest` → `cco:is about` |

The other 16 ACQ queries are unchanged — they don't use SOSA.

## How variant selection works

`bash validation/scripts/b2cco-run-acqs.sh` (`VARIANT=native`) picks query files from this
directory when present and falls back to `../queries/` otherwise.
`--variant sosa` (default) always uses `../queries/`.
`--variant both` runs both and emits `b2-cco-results-{profile}.json`
plus `b2-cco-results-{profile}-native.json` so the manuscript can
report both columns.
