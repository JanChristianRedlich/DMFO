# B1 Ablation: DMFO − (A1)–(A6)

Per Paper §4.2, B1 is the **non-conformant baseline**: it imports the
same anchor vocabularies (PROV-O, SOSA/SSN, DUL/DnS, GeoSPARQL) and the
same ABox population as the DMFO-conformant profile, but **omits the six
alignment axioms (A1)–(A6)**.

## How to construct B1

The B1 KB is built at evaluation time by stripping the (A1)–(A6)
axiom triples from the DMFO TBox closure. This is implemented inside
`validation/scripts/run_all_acqs.py --b1`, which:

1. Loads `ontology/dmfo-full.ttl` + the chosen profile (maritime / food).
2. Removes triples matching each of the (A1)–(A6) axiom shapes
   (the same patterns as `../../conformance/A?.ask.rq`).
3. Re-runs the same 20 ACQ files against the stripped graph.

## Re-using the ACQ catalog

B1 uses **the same 20 ACQ files** as the conformant case
(`../../dmfo/ACQ-*.sparql`). The score on the current package is **8/20**
on each profile (per-class: I=2/2, II=1/6, III=1/8, IV=4/4) — the
identity-only and absence-detection ACQs survive the ablation, while
the multi-bridge and single-bridge-with-typed-anchor ACQs collapse.

## Failure-pattern attribution

Each B1-failing ACQ maps to the specific missing axiom (Paper §4.2
"Failure pattern, not score"):

| ACQ class | Failing axiom |
|---|---|
| Class III multi-bridge accountability | A1 + A5 |
| Evidence-grounded queries | A3 |
| Normative-framing queries | A4 |
| Location-scoped obligation queries | A6 |
| Identity-derivation queries | A1 (Manifestation typing) + identity-deriv module |
