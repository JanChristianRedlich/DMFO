# ACQ Catalog (20 Anchor Competence Questions)

The ACQ catalog is the empirical workload of Paper §4.2. Each ACQ was
derived from one of thirteen internationally standardised catalogs
through the four-step procedure of Paper §4.2:

1. **Identification** of requirements concerning persistently
   identifiable, state-varying entities.
2. **Reformulation** as framework-level questions.
3. **Dimensional assignment** (which slots / bridges does the question
   traverse?).
4. **Classification** by inferential complexity.

Saturation was reached after three consecutive standards yielded no new
(dimension, class) signature.

## Classification

| Class | Description | Bridges required | Count |
|---|---|---|---|
| I   | Identity-only lookup    | none / A2 only | 2 |
| II  | Single-bridge traversal | one of A2–A6   | 6 |
| III | Multi-bridge traversal  | ≥ 2 of A1–A6   | 8 |
| IV  | Absence detection       | `FILTER NOT EXISTS` over a missing bridge | 4 |

Total: **20 ACQs**.

## Catalog

| ID | Class | Source standard | Bridges | File |
|---|---|---|---|---|
| ACQ-I-01   | I   | UN/CEFACT, GS1 EPCIS 2.0 | identity layer only | [identity_persistence](../../acqs/queries/dmfo/ACQ-I-01_identity_persistence.sparql) |
| ACQ-I-02   | I   | GS1 EPCIS 2.0 §6 (4-attribute) | A2 minimal | [epcis_4attribute](../../acqs/queries/dmfo/ACQ-I-02_epcis_4attribute.sparql) |
| ACQ-II-01  | II  | ISO 22005, GS1 EPCIS 2.0 | A2 | [state_history](../../acqs/queries/dmfo/ACQ-II-01_state_history.sparql) |
| ACQ-II-02  | II  | PROV-O, IATA ONE Record | A5 | [state_to_activity](../../acqs/queries/dmfo/ACQ-II-02_state_to_activity.sparql) |
| ACQ-II-03  | II  | SOSA/SSN, ISO 8000-61 | A3 | [state_to_evidence](../../acqs/queries/dmfo/ACQ-II-03_state_to_evidence.sparql) |
| ACQ-II-04  | II  | GeoSPARQL 1.1, IMO ISPS | A6 | [situation_to_zone](../../acqs/queries/dmfo/ACQ-II-04_situation_to_zone.sparql) |
| ACQ-II-05  | II  | DUL/DnS, EU Reg. 178/2002 | A4 | [situation_to_regime](../../acqs/queries/dmfo/ACQ-II-05_situation_to_regime.sparql) |
| ACQ-II-06  | II  | ISO 8000-61, SOSA/SSN | A3 | [observation_quality](../../acqs/queries/dmfo/ACQ-II-06_observation_quality.sparql) |
| ACQ-III-01 | III | PROV-O, IATA ONE Record | A2 + A5 | [state_activity_agent](../../acqs/queries/dmfo/ACQ-III-01_state_activity_agent.sparql) |
| ACQ-III-02 | III | WCO, EU UCC, IMO ISPS | A2 + A4 | [state_situation_regime](../../acqs/queries/dmfo/ACQ-III-02_state_situation_regime.sparql) |
| ACQ-III-03 | III | SOSA/SSN, ISO 8000-61, FAIR | A2 + A3 | [state_evidence_sensor](../../acqs/queries/dmfo/ACQ-III-03_state_evidence_sensor.sparql) |
| ACQ-III-04 | III | PROV-O, GS1 EPCIS BizSteps | A5 + PROV chain | [causal_antecedent](../../acqs/queries/dmfo/ACQ-III-04_causal_antecedent.sparql) |
| ACQ-III-05 | III | FDA FSMA Rule 204, ISO 22005 | A2 + identity-deriv | [identity_split_chain](../../acqs/queries/dmfo/ACQ-III-05_identity_split_chain.sparql) |
| ACQ-III-06 | III | WCO, EU UCC, EU ICS2 | A2 + A4 + A6 | [customs_consistency](../../acqs/queries/dmfo/ACQ-III-06_customs_consistency.sparql) |
| ACQ-III-07 | III | IATA ONE Record, UN/CEFACT MMT | A2 + A5 + A6 | [air_record_visibility](../../acqs/queries/dmfo/ACQ-III-07_air_record_visibility.sparql) |
| ACQ-III-08 | III | FDA FSMA Rule 204 | A2 + A5 + identity-deriv | [fsma_traceability](../../acqs/queries/dmfo/ACQ-III-08_fsma_traceability.sparql) |
| ACQ-IV-01  | IV  | ISO 8000-61, FAIR | A3 negation | [evidence_gap](../../acqs/queries/dmfo/ACQ-IV-01_evidence_gap.sparql) |
| ACQ-IV-02  | IV  | PROV-O, IATA ONE Record | A5 negation | [causal_gap](../../acqs/queries/dmfo/ACQ-IV-02_causal_gap.sparql) |
| ACQ-IV-03  | IV  | FAIR (F1) | identity layer + NOT EXISTS | [identifier_scheme_gap](../../acqs/queries/dmfo/ACQ-IV-03_identifier_scheme_gap.sparql) |
| ACQ-IV-04  | IV  | EU Reg. 178/2002, FDA FSMA 204 | A4 negation | [governance_gap](../../acqs/queries/dmfo/ACQ-IV-04_governance_gap.sparql) |

## Inter-rater reliability

The full pre-registered protocol (sample seed, annotator briefing,
adjudication procedure, κ / α thresholds) is in
[`irr/PLAN.md`](irr/PLAN.md) and will be executed before the
camera-ready release. The submitted version is single-annotator.

## Reproducing the ACQ run

```bash
python validation/scripts/run_all_acqs.py --all
```

Outputs:

* `validation/results/queries_maritime.json`  — per-ACQ row counts on
  the maritime instantiation.
* `validation/results/queries_food.json` — same for food.
* `validation/results/ablation_maritime.json` — DMFO vs. B1 ablation.
* `validation/results/ablation_food.json` — same for food.
