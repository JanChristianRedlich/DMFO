# B1 Ablation: DMFO − (A1)–(A6)

Per Paper §4.2, B1 is the **non-conformant baseline**: it imports the
same anchor vocabularies (PROV-O, SOSA/SSN, DUL/DnS, GeoSPARQL) and the
same ABox population as the DMFO-conformant profile, but **omits the six
alignment axioms (A1)–(A6)**.

## How to construct B1

The B1 KB is built by stripping (A1)–(A6) from the DMFO TBox closure.
This is automated by `validation/scripts/build_b1.py`, which:

1. Loads `ontology/dmfo-full.ttl` + the chosen profile (maritime / food).
2. Removes triples matching each of the (A1)–(A6) axiom shapes
   (the same patterns as `../../conformance/A?.ask.rq`).
3. Writes the resulting graph to `validation/results/b1_<profile>.ttl`.

## Re-using the ACQ catalog

B1 uses **the same 20 ACQ files** as the conformant case
(`../../ACQ-*.sparql`). The runner `run_all_acqs.py --b1` evaluates them
against the stripped KB and records which ACQs produce non-empty
bindings. Per Paper Table 3, the expected B1 score is 4/20: only the
identity–state subset (Class I + the single Class-II ACQ that traverses
A2 alone) survives the ablation; the other 16 ACQs are structurally
underdetermined without (A1)–(A6).

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
