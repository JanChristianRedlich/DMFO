# Appendix C.1 — ACQ Catalogue (per-framework results)

This appendix consolidates the ACQ catalogue with the per-framework
result that the paper §4.2 reports. The minimal table form is at
[`acqs/catalogue.md`](../acqs/catalogue.md);
this appendix adds **expected vs. obtained per framework**
(DMFO, B1, B2-CCO/sosa, B2-CCO/native).

The numbers below are the result of
`bash validation/scripts/run_queries.sh` +
`bash validation/scripts/b2cco-run-acqs.sh` on a clean checkout
(`commit <to be filled at camera-ready>`).

The full ACQ texts and source-clause pointers are in the
catalogue; this appendix focuses on the result matrix and
diagnosis.

---

## Result matrix

Legend:
* ✓ — answerable (semantically complete result)
* ◑ — semantically shifted answer (rows > 0 but classification
  `(c)` or `(b/c)` per Paper §4.2 strict rubric)
* ✗ — not answerable / no result
* `(d)` — *known* not expressible under the relevant translation rule

| ACQ | Class | DMFO | B1 | B2-CCO/sosa | B2-CCO/native | B2 diagnosis (ADR) |
|---|---|---|---|---|---|---|
| ACQ-I-01   | I   | ✓ | ✓ | ✓ | ✓ | ADR-001 |
| ACQ-I-02   | I   | ✓ | ✓ | ✓ | ✓ | ADR-001+003a |
| ACQ-II-01  | II  | ✓ | ✓ | ✓ | ✓ | ADR-001 |
| ACQ-II-02  | II  | ✓ | ✗ | ✓ | ✓ | ADR-002 |
| ACQ-II-03  | II  | ✓ | ✗ | ✓ | ✓ | ADR-003a / 003b |
| ACQ-II-04  | II  | ✓ | ✗ | ✓ | ✓ | ADR-005 |
| ACQ-II-05  | II  | ✓ | ✗ | ✓ | ✓ | ADR-004 |
| ACQ-II-06  | II  | ✓ | ✗ | ✓ | ✗ `(d)` | ADR-003b (no SOSA → no observed-property quality) |
| ACQ-III-01 | III | ✓ | ✗ | ✓ | ✓ | ADR-001+002 |
| ACQ-III-02 | III | ✓ | ✗ | ◑ `(b/c)` | ◑ `(b/c)` | ADR-004 |
| ACQ-III-03 | III | ✓ | ✗ | ✓ | ✗ `(d)` | ADR-003b (no sensor concept in CCO) |
| ACQ-III-04 | III | ✓ | ✗ | ✗ `(d)` | ✗ `(d)` | ADR-002 (no PROV-O qualified usage / hadRole) |
| ACQ-III-05 | III | ✓ | ✓ | ✓ | ✓ | ADR-006 (act-mediated derivation) |
| ACQ-III-06 | III | ✓ | ✗ | ✓ | ✓ | ADR-004+005 |
| ACQ-III-07 | III | ✓ | ✗ | ✓ | ✓ | ADR-002+005 |
| ACQ-III-08 | III | ✓ | ✗ | ✓ | ✓ | ADR-006 (transitive Act chain) |
| ACQ-IV-01  | IV  | ✓ | ✓ | ✓ | ✗ `(d)` | ADR-003b |
| ACQ-IV-02  | IV  | ✓ | ✓ | ✓ | ✓ | ADR-002 |
| ACQ-IV-03  | IV  | ✓ | ✓ | ◑ `(c)`   | ◑ `(c)`   | ADR-007 (F3-prohibited typed scheme) |
| ACQ-IV-04  | IV  | ✓ | ✓ | ✓ | ✓ | ADR-004 |

Score (any-profile-answers, strict rubric):

| Framework | Total | by class (I / II / III / IV) |
|---|---|---|
| DMFO              | **20 / 20** | 2 / 6 / 8 / 4 |
| B1 (DMFO − A1–A6) | **8 / 20**  | 2 / 1 / 1 / 4 |
| B2-CCO/sosa       | **17 / 20** | 2 / 6 / 6 / 3 |
| B2-CCO/native     | **15 / 20** | 2 / 5 / 5 / 3 |

Source JSONs:

* DMFO: `validation/results/queries_{maritime,food}.json`,
  `validation/results/ablation_{maritime,food}.json`
* B2-CCO: `validation/b2-cco/results/b2-cco-results-{maritime,food}{,-native}.json`,
  `validation/b2-cco/results/comparison-dmfo-vs-b2cco-*.csv`

---

## Per-ACQ saturation pointers

Each ACQ in the catalogue ([`acqs/catalogue.md`](../acqs/catalogue.md))
carries the standard that introduced its (dimension, class)
signature. The full saturation trace, including per-standard
new-signature counts and the sensitivity check, is in
[`acqs/saturation-trace.md`](../acqs/saturation-trace.md).

---

## Reproducing the matrix

```bash
# 1. DMFO + B1
bash validation/scripts/run_queries.sh

# 2. B2-CCO (sosa + native variants)
bash validation/scripts/b2cco-run-acqs.sh

# 3. Render the matrix
python validation/scripts/perf-final-table2.py        # writes JSON
# (matrix above is the human-readable view)
```

The strict-rubric scoring is implemented by `status_for(rows,
classification)` in `validation/scripts/b2cco-run-acqs.sh`, and the
diagnosis ADR pointer is propagated through `META_BASE` /
`VARIANT_OVERRIDES`.

The B1 ablation strips the six bridge axioms by triple shape (see
`strip_a1_a6` in `validation/scripts/run_all_acqs.py`); the same
20 ACQ files are re-evaluated on the stripped graph.

---

## Cross-reference

* Paper §4.2 Table 3 (extended) → `validation/b2-cco/docs/manuscript-table-3-extended.md`
* Paper §4.2 diagnosis paragraph → `validation/b2-cco/docs/manuscript-appendix-b2cco-diagnosis.md`
* The IRR plan that addresses single-annotator bias for this matrix →
  [`acqs/irr/PLAN.md`](../acqs/irr/PLAN.md).
