# Repository Timeline

This file documents the chronological order in which the artefacts of
this reproduction package were produced.

---

## Phase 1 — ACQ derivation and saturation (February 2026)

**Artefacts produced in this phase:**

* `acqs/catalogue.md` — the 20 ACQs with source,
  class, dimensional signature.
* `acqs/saturation-trace.md` — per-standard new-signature
  trace; saturation declared after three consecutive standards yielded
  zero new (dimension, class) signatures.
* `acqs/queries/dmfo/ACQ-I-*.sparql`, `ACQ-II-*.sparql`,
  `ACQ-III-*.sparql`, `ACQ-IV-*.sparql` — DMFO-side SPARQL bodies for
  the 20 ACQs.

**Ordering of standards:** UN/CEFACT BSP → GS1 EPCIS 2.0 → WCO Data
Model → IMO FAL.5/Circ.42 + ISPS → EU UCC + ICS2 + CER → IATA ONE
Record → PROV-O → FAIR Principles → ISO 8000-61 → FDA FSMA Rule 204 →
ISO 22005 → EU Regulation 178/2002 → (saturation reached after ISO
22005 and confirmed across the last three).

**Ordering of activity within Phase 1:** the 20 ACQ-IDs were assigned
first (catalogue file), then the SPARQL bodies were written *against
the DMFO anchor signature in `dmfo-state.ttl` + `dmfo-context.ttl` +
…* — i.e., the queries assume A1–A6 are present. A B1-friendly
non-bridged variant is **not** stored separately for each ACQ; the B1
score is obtained at evaluation time by stripping (A1)–(A6) from the
KB and re-running the same `ACQ-*.sparql` files (see
`validation/scripts/run_all_acqs.py --b1`).

---

## Phase 2 — DMFO-core implementation (March 2026)

**Artefacts:**

* `ontology/dmfo-base.ttl`, `dmfo-identity.ttl`, `dmfo-state.ttl`,
  `dmfo-evidence.ttl`, `dmfo-context.ttl`, `dmfo-activity.ttl`,
  `dmfo-location.ttl`, `dmfo-identity-deriv.ttl`, `dmfo-full.ttl`.
* `shapes/dmfo-core-shapes.ttl`, `shapes/identity-deriv-shapes.ttl`.
* `validation/scripts/validate_kb.py`, `conformance_validator.py`,
  `locality_check.py`.
* `acqs/queries/conformance/A1.ask.rq … A6.ask.rq`.

**Ordering within Phase 2:** modules in slot-order
(Identity → State → Evidence → Context → Activity → Location →
identity-deriv), with the bridge axioms (A1)–(A6) attached to the
*receiving* slot module per Theorem 2(b). The aggregated
`dmfo-full.ttl` is generated last and verified by `validate_kb.py`.

---

## Phase 3 — Profile implementation (March 2026)

**Maritime first**, food second.

* `profiles/maritime/{mar-tbox.ttl, mar-abox.ttl, mar-shapes.ttl}` —
  port-call sequence per IMO FAL.5/Circ.42; LCL deconsolidation
  pattern (`mar:CargoLot`, `mar:DeconsolidationActivity`) added to
  exercise ACQ-III-05/08.
* `profiles/food/{food-tbox.ttl, food-abox.ttl, food-shapes.ttl}` —
  FDA FSMA-204 KDE/CTE chain plus an explicit Split + Merge identity
  derivation.

Both ABoxes contain a *deliberate governance gap* (one
`mar:CustodyTransferSituation` / one `food:` lot without
`dmfo:governedBy`) so that ACQ-IV-04 returns a non-empty result on
both instantiations.

---

## Phase 4 — B1 ablation (April 2026)

B1 = DMFO − (A1)–(A6). Implemented at evaluation time by
`validation/scripts/run_all_acqs.py --b1`, which loads the same KB
and removes the six axiom triples before running the same 20 ACQs.
No separate B1 SPARQL files (intentional: this guarantees that any
score difference DMFO ↔ B1 is attributable to the axioms, not to
phrasing of the queries).

---

## Phase 5 — B2-CCO baseline (April 2026)

After DMFO + B1 were evaluated, the alternative-architecture baseline
B2-CCO was built per `evaluation.md`. ADRs 001–006 were written in slot
order:

1. ADR-001 (Identity + State via Quality-Inherence)
2. ADR-002 (Activity via cco:Act + cco:Agent)
3. ADR-003a / ADR-003b (Evidence — two variants: SOSA co-import vs.
   CCO-native Measurement ICE)
4. ADR-004 (Context via cco:Process Regulation)
5. ADR-005 (Location via bfo:Site + bfo:located in)
6. ADR-006 (Identity-derivation via Act-mediated input/output chains)
7. ADR-007 (Identifier-schema property — F3-forbidden, recorded as
   *not allowed* with citation)

For each ADR, both `acqs/queries/b2-cco-sosa/acq-NN-cco.rq` and
(where it diverges) `acqs/queries/b2-cco-native/acq-NN-cco-native.rq`
were written.
The two variant ABoxes are
`validation/b2-cco/abox/{maritime,food}-abox.ttl`.

---

## Phase 6 — Evaluation runs (April 2026)

Re-runnable in order from a clean checkout:

1. `bash validation/scripts/run_queries.sh` — full DMFO pipeline
   (validate_kb, conformance for both profiles, locality, SHACL,
   20 ACQs + B1 ablation, optional HermiT).
2. `bash validation/scripts/b2cco-run-acqs.sh` — B2-CCO baseline,
   sosa + native variants.
3. `python validation/scripts/perf-rdfs-symmetric.py` — Table 2
   (closure ms + per-class median).
4. `python validation/scripts/scale-benchmark.py` and
   `python validation/scripts/scale-benchmark-large.py` — rdflib
   scaling sweep N ∈ {1, 10, 25, 50, 100, 200, 500}.
5. `bash validation/scripts/jena-bench/run-jena-scale.sh` — Jena
   cross-engine replication of the scaling sweep.

Result JSONs land in `validation/results/`.

