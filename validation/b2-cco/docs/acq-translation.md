# DMFO → B2-CCO ACQ Translation Log

Per Faithful-Translation-Rule F5, every ACQ that fails or shifts
semantics under B2-CCO carries a one-paragraph diagnosis here.

Classification legend:
- **(a)** directly translatable — same query shape, different IRIs
- **(b)** translatable with modelling rework — different SPARQL pattern
- **(c)** translatable but semantically shifted or partial — query runs
  but the result interpretation differs from DMFO
- **(d)** not meaningfully translatable — CCO has no analogue

| ACQ | DMFO class | Classification | B2-CCO file | Diagnosis ADR |
|---|---|---|---|---|
| ACQ-I-01   | I   | (b) | [acq-01-cco.rq](../queries/acq-01-cco.rq) | ADR-001 (identifier ICE) |
| ACQ-I-02   | I   | (b) | [acq-02-cco.rq](../queries/acq-02-cco.rq) | ADR-001 + ADR-003a (last-time via observation result) |
| ACQ-II-01  | II  | (b) | [acq-03-cco.rq](../queries/acq-03-cco.rq) | ADR-001 (Quality as state-class proxy) |
| ACQ-II-02  | II  | (a) | [acq-04-cco.rq](../queries/acq-04-cco.rq) | ADR-002 (cco:has output) |
| ACQ-II-03  | II  | (a) | [acq-05-cco.rq](../queries/acq-05-cco.rq) | ADR-003a (variant a, SOSA co-import) |
| ACQ-II-04  | II  | (b) | [acq-06-cco.rq](../queries/acq-06-cco.rq) | ADR-005 (bfo:located in, no GeoSPARQL) |
| ACQ-II-05  | II  | (b) | [acq-07-cco.rq](../queries/acq-07-cco.rq) | ADR-004 (cco:prescribes, reversed direction) |
| ACQ-II-06  | II  | (a) | [acq-08-cco.rq](../queries/acq-08-cco.rq) | ADR-003a (SOSA properties retained) |
| ACQ-III-01 | III | (b) | [acq-09-cco.rq](../queries/acq-09-cco.rq) | ADR-001 + ADR-002 (extra Quality hop) |
| ACQ-III-02 | III | (b/c) | [acq-10-cco.rq](../queries/acq-10-cco.rq) | ADR-004 (Situation reified as Act) |
| ACQ-III-03 | III | (a) | [acq-11-cco.rq](../queries/acq-11-cco.rq) | ADR-003a |
| ACQ-III-04 | III | (c) | [acq-12-cco.rq](../queries/acq-12-cco.rq) | ADR-002 (no PROV-O wasInformedBy; bfo:preceded by is temporal not causal) |
| ACQ-III-05 | III | (d) | [acq-13-cco.rq](../queries/acq-13-cco.rq) | ADR-001 + ADR-002 (no identity-derivation in CCO) |
| ACQ-III-06 | III | (b) | [acq-14-cco.rq](../queries/acq-14-cco.rq) | ADR-004 + ADR-005 |
| ACQ-III-07 | III | (b) | [acq-15-cco.rq](../queries/acq-15-cco.rq) | ADR-002 + ADR-005 |
| ACQ-III-08 | III | (d) | [acq-16-cco.rq](../queries/acq-16-cco.rq) | same as ACQ-III-05 |
| ACQ-IV-01  | IV  | (a) | [acq-17-cco.rq](../queries/acq-17-cco.rq) | ADR-003a |
| ACQ-IV-02  | IV  | (a) | [acq-18-cco.rq](../queries/acq-18-cco.rq) | ADR-002 |
| ACQ-IV-03  | IV  | (c) | [acq-19-cco.rq](../queries/acq-19-cco.rq) | ADR-001 (scheme shift: object-without-ICE rather than TVE-without-scheme) |
| ACQ-IV-04  | IV  | (b) | [acq-20-cco.rq](../queries/acq-20-cco.rq) | ADR-004 (reversed: act-not-prescribed) |

## Per-ACQ diagnoses (for (c)/(d) cases only)

### ACQ-III-04 — Causal antecedent (c)

**DMFO query** uses `prov:wasInformedBy` to retrieve causally-prior
activities. PROV-O is not co-imported by CCO 2.0; the closest CCO/BFO
relation is `bfo:preceded by` (BFO_0000062), which expresses temporal
precedence between processes. The B2-CCO query returns rows on the
maritime ABox because activities have explicit `bfo:preceded by`
annotations, but the **semantics differs**: temporal precedence does
not entail causal-information flow. ACQ-III-04 should therefore be
read as "temporal antecedent" under B2-CCO and is reported as (c) in
results JSON. **Governing decision: ADR-002.**

### ACQ-III-05 — Identity split chain (d)

DMFO uses `dmfo:SplitSourceIdentity` together with
`prov:wasDerivedFrom` to model splitting transformations. CCO 2.0
makes no commitment about identity preservation across processing
steps; BFO continuants are either identical or not. The query is
structurally underdetermined under B2-CCO and is documented as such.
**Governing decision: ADR-001 + ADR-002.**

### ACQ-III-08 — FSMA traceability (d)

Same root cause as ACQ-III-05. The DMFO query traverses
`prov:wasDerivedFrom+` to reach all source lots via the transitive
PROV-O derivation chain. With no PROV-O in the import closure and no
CCO derivation chain, the query has no faithful CCO counterpart.
**Governing decision: ADR-001 + ADR-002.**

### ACQ-IV-03 — Identifier scheme gap (c)

DMFO checks `?tve dmfo:hasIdentifier ?id` `FILTER NOT EXISTS { ?tve
dmfo:identifierScheme ?s }`. The "scheme" attribute identifies which
identifier system (ISO 6346, GS1, IMO) the identifier follows. In
B2-CCO, the scheme is implicit in the *class* of the identifier ICE
(`b2mar:BICCode` vs `b2mar:IMONumber`). The query is rewritten as
"objects not designated by any identifier ICE" — a different question
that B2-CCO can answer. The DMFO version's exact semantics
(identifier-without-scheme) is not preserved.
**Governing decision: ADR-001.**
