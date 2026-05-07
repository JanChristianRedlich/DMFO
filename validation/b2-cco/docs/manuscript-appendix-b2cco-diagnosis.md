# Manuscript Appendix B — B2-CCO Per-ACQ Diagnosis

> Appendix material for the camera-ready submission. Each entry
> reports the DMFO query path, the B2-CCO translation under the
> Faithful-Translation-Rule, and the diagnostic explanation when the
> two diverge. ADR numbers refer to `validation/b2-cco/docs/adr/`.

## B.1 The Faithful-Translation-Rule (F1–F5)

Reproduced from `validation/b2-cco/docs/faithful-translation-rule.md`. Briefly:

* **(F1)** Every slot uses a CCO 2.0 pattern documented in
  Jensen et al. 2024, the *Modeling with CCO* guide, or a peer-
  reviewed CCO-conformant publication.
* **(F2)** All CCO references use the version-2.0 opaque IRIs.
* **(F3)** No typed inter-dimensional bridges are introduced.
* **(F4)** Each modelling decision is recorded in an ADR with CCO
  citation.
* **(F5)** ACQ failures are diagnosed, not patched.

## B.2 Slot mapping summary

(Compact version of Paper Section 4.2 table; full table in
`validation/b2-cco/docs/slot-mapping.md`.)

| Slot | CCO/BFO pendant | Documented absence |
|---|---|---|
| Identity | `bfo:object` + sortal | — |
| State | `bfo:Quality` + `bfo:inheres in` | no direct class for Manifestation |
| Activity | `cco:Act` + `cco:has agent` | — |
| Evidence | SOSA co-import (a) / `cco:Measurement ICE` (b) | no native observation event class |
| Context | `cco:Process Regulation` + `cco:prescribes` | no `Situation` class |
| Location | `bfo:Site` + `bfo:located in` | no GeoSPARQL spatial relations |

## B.3 Per-ACQ diagnostic appendix (only for ACQs where DMFO ≠ B2-CCO)

We report the diagnosis under both **B2-CCO/sosa** (ADR-003a active)
and **B2-CCO/native** (strict ADR-003b, no SOSA co-import).

### ACQ-II-06 (Class II, status DMFO ✓ → sosa ✓ → native ✗)

DMFO: `?observation sosa:phenomenonTime ?pt ; sosa:resultTime ?rt ;
sosa:madeBySensor ?sn .` Reports a 3-attribute completeness check
per ISO 8000-61 §5.2 — phenomenon-time vs. result-time vs. sensor.

B2-CCO/sosa: same query — answerable.
B2-CCO/native: structurally underdetermined.

**Diagnosis (ADR-003b).** The CCO Measurement Information Content
Entity has no native phenomenon/result-time distinction. Adding a
custom `b2cco:phenomenonTime` would violate Faithful-Translation-Rule
F3. Likewise, CCO has no native Sensor concept; the closest
substitute (the agent of a measurement act) is already exercised by
ACQ-III-01 and is not an evidential commitment. Reported as ✗.

### ACQ-III-03 (Class III, status DMFO ✓ → sosa ✓ → native ✗)

DMFO: `?observation sosa:hasFeatureOfInterest ?manifestation ;
sosa:madeBySensor ?sensor .` Resolves the evidential chain
manifestation → observation → sensor.

B2-CCO/sosa: same query — answerable.
B2-CCO/native: structurally underdetermined.

**Diagnosis (ADR-003b).** Sensor identity has no CCO-native
counterpart. Reported as ✗.

### ACQ-III-02 (Class III, status DMFO ✓ → B2-CCO ◑)

DMFO: `?manifestation dmfo:manifestationOf ?tve . ?situation
dul:includesObject ?manifestation ; dmfo:governedBy ?regime .`
Returns `(tve, manifestation, situation, regime)` rows.

B2-CCO: `?quality bfo:inheres_in ?tve . ?act cco:has_output
?quality . ?regime cco:prescribes ?act .` Empty on the maritime
ABox.

**Diagnosis (ADR-004).** The DMFO query reaches the regime via the
`dul:Situation` that `includesObject` the manifestation. CCO has no
`Situation` class; the analogue is the `cco:Act` token that the
regulation prescribes. The two acts in the maritime ABox
(`CustodyTransfer_HLXU`, `CustomsControl_HLXU`) are prescribed by
their respective regulations, but they are *not* outputs of the
state-generating discharge / crane / gate-movement acts — those
acts produce `Quality` outputs (the location states), not the
custody-control act tokens. So the join `?regime cco:prescribes
?act` fails to align with `?act cco:has_output ?quality
bfo:inheres_in ?tve`. Faithful CCO modelling cannot join the
state's generating activity to the regulating regime through a
single act token; the multi-state-inclusion abstraction of
`dul:Situation` has no CCO analogue.

### ACQ-III-04 (Class III, status DMFO ✓ → B2-CCO ✗ both variants)

DMFO (PROV-O Rec §5.7 strict reading):

```sparql
?activity   prov:qualifiedUsage ?usage .
?usage      prov:entity   ?carrier ;
            prov:hadRole  ?carrierRole .
?carrier    prov:wasGeneratedBy ?antecedent .
```

Requires bound values for ?activity, ?antecedent, ?carrier *and*
?carrierRole. The qualified-usage construct exposes the typed-role
qualification on the carrier-flow witness — what role the carrier
plays in the dependent activity's plan.

B2-CCO best-effort substitute (both variants):

```sparql
?activity   bfo:preceded_by ?antecedent .
?activity   cco:has_input ?carrier .
?antecedent cco:has_output ?carrier .
?carrier    <hasNoRoleAnalogue> ?carrierRole .   # cannot bind
```

**Diagnosis (ADR-002).** PROV-O is not co-imported by CCO 2.0
(no integration in Jensen et al. 2024). The entity-flow witness
piece can be reconstructed via `cco:has_input` / `cco:has_output`,
but CCO has no analogue of `prov:Role` and no qualifying construct
over `cco:has_input` to expose what role the carrier plays in the
dependent activity. The SELECT requires a binding for
?carrierRole that CCO cannot supply. Adding a typed-role property
would violate Faithful-Translation-Rule F3.

Status under both B2-CCO variants: **✗ structurally
underdetermined (d)**. The earlier non-strict version of this ACQ
(plain `wasInformedBy` traversal) classified as (c) — semantically
shifted. The strict reading consistent with PROV-O Rec §5.7
upgrades the diagnosis to (d): the role-qualification piece is
categorically absent in CCO.

### ACQ-III-05 + ACQ-III-08 (Class III, status DMFO ✓ both profiles → B2-CCO ✓ both profiles under ADR-006)

DMFO: identity-derivation chain via `prov:wasDerivedFrom+` and
`dmfo:SplitSourceIdentity` / `dmfo:MergeSourceIdentity`. Both
profiles now exercise the pattern: food's splitting / merging
scenario and maritime's LCL deconsolidation scenario (UN/CEFACT MMT,
IMO FAL.5/Circ.42 §3.5).

B2-CCO: under **ADR-006**, the canonical CCO pattern is
**act-mediated input/output** — a successor lot is one
`cco:has_input` / `cco:has_output` join away from its source
through an act token, and transitive chains are SPARQL property
paths of the form `(^cco:has_output / cco:has_input)+`. The class
`b2cco:SplittingActivity` is the cross-profile marker; food
specialises it via `b2food:SplittingActivity` and maritime via
`b2mar:DeconsolidationActivity`.

**Diagnosis (ADR-006).** Both ACQs are now answered by both
profiles under both DMFO and B2-CCO. The advantage of DMFO's typed
`prov:wasDerivedFrom` is **ergonomic**, not categorical: the SPARQL
is roughly 2× the length of the DMFO version (two-hop join vs.
single property path) and traversal time is ~12 % higher
(1.56 ms vs. 1.40 ms median on ACQ-III-08).

### ACQ-IV-03 (Class IV, status DMFO ✓ → B2-CCO ◑)

DMFO: `?tve dmfo:hasIdentifier ?id . FILTER NOT EXISTS { ?tve
dmfo:identifierScheme ?s . }` Detects TVEs with an identifier
literal but no scheme attribution.

B2-CCO: `?obj a ?cls . ?cls rdfs:subClassOf*/rdfs:subClassOf*
bfo:object . FILTER NOT EXISTS { ?ice cco:designates ?obj . }`
Detects bare objects not designated by any identifier ICE.

**Diagnosis (ADR-001).** In CCO, an identifier *is* an
Information Content Entity that designates the object. The
identifier "scheme" is implicit in the ICE class
(`b2mar:BICCode`, `b2mar:IMONumber`). There is no separate
"scheme" datatype property to be present-or-absent. The B2-CCO
question shifts to "objects with no designating ICE at all",
which is a different but related correctness check (FAIR F1). The
shift is reported as ◑ (semantically shifted).

## B.4 ABox triple-count comparison

| KB | Triples | Closure size (OWL-RL) |
|---|---|---|
| DMFO maritime    | 115 | 1 026 |
| B2-CCO maritime  | 108 | 638 |
| DMFO food        | 102 | 975 |
| B2-CCO food      | 105 | 620 |

The B2-CCO ABoxes are within 5 % of the DMFO equivalents. The
BFO quality-inherence pattern (ADR-001) and the act-mediated
derivation chain (ADR-006) do not blow up the triple count: the
extra Quality / Act tokens are offset by the absence of explicit
OWL-Time `time:Instant` individuals and DMFO-specific marker
classes (`dmfo:SplitSourceIdentity` etc.).

## B.5 The two B2-CCO variants

| Variant | Active ADRs | Maritime | Food | Combined | Δ vs DMFO |
|---|---|---|---|---|---|
| B2-CCO/sosa   | 001, 002, **003a**, 004, 005, 006 | 17/20 | 17/20 | 17/20 | −3 |
| B2-CCO/native | 001, 002, **003b**, 004, 005, 006 | 15/20 | 15/20 | 15/20 | −5 |

**Reading.** Faithful-Translation-Rule F1 requires every slot to use
a CCO 2.0 pattern documented in Jensen et al. 2024 or the *Modeling
with CCO* guide. SOSA/SSN is not part of CCO 2.0; ADR-003a treats it
as a documented exception ("isolated co-import for evaluation only").
The strict-native variant (ADR-003b) drops the SOSA borrow and
reports the empirical answer to *"what does CCO 2.0 alone, without
upstream borrows, achieve on the ACQ catalogue?"* The 5-ACQ gap
between DMFO and B2-CCO/native is the cost of refusing the four
upstream vocabularies that DMFO discharges via the typed alignment
axioms (A1)–(A6).

The recommended manuscript reading reports both variants:

* B2-CCO/sosa as the **upper bound** on what a CCO-based
  architecture achieves with one disciplined borrow.
* B2-CCO/native as the **strict baseline** that a CCO-only camera-
  ready conformance check would actually pass.

## B.5 Reproducibility

```bash
git clone https://github.com/CommonCoreOntology/CommonCoreOntologies.git \
    b2-cco/vendor/cco-2.0
bash validation/scripts/b2cco-consistency-check.sh
bash validation/scripts/b2cco-run-acqs.sh
bash validation/scripts/b2cco-oops-check.sh
```

CCO 2.0 commit pinned to `9a8b27c87c6188cb0a469f1ead18fd602e42cc8a`.
