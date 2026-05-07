# Manuscript Section 4.2 — B2-CCO Block (drop-in)

> Half-page block for Paper §4.2 *Engineered baseline (B2)*. Replaces
> the current "B2-LLM" / TODO placeholder text. Includes the
> Faithful-Translation-Rule, slot-mapping summary, and a forward
> reference to Tables 3 and 4 of this manuscript.

---

**Engineered baseline (B2-CCO).** B2-CCO is an alternative-architecture
baseline that re-implements the same anchor competence questions on
top of the **Common Core Ontologies (CCO 2.0)** [Jensen et al., FOIS
2024] — a BFO-based mid-level ontology suite that uses fundamentally
different modelling idioms from DMFO's typed-bridge architecture.
The point is not to win or lose against DMFO but to demonstrate, via
a faithful CCO-native implementation, *which* ACQ classes become
structurally hard when the architecture follows BFO's
continuant/occurrent split and CCO's quality-inherence + ICE-based
modelling.

We govern B2-CCO by a **Faithful-Translation-Rule (F1–F5)** with five
criteria: (F1) every slot is modelled with a CCO 2.0 pattern
documented in the FOIS 2024 paper or the *Modeling with CCO* guide;
(F2) all CCO references use the version-2.0 opaque IRIs; (F3) no
typed inter-dimensional bridges are introduced (no
"B2-CCO-evidencedBy" or similar); (F4) every modelling decision is
recorded in an Architecture Decision Record (ADR) citing the CCO
source; (F5) ACQ failures are diagnosed in the per-ACQ translation
log, never patched.

The slot mapping is summarised in the table below; full ADRs are in
the artefact package (Appendix B):

| DMFO slot | CCO/BFO pendant | Bridge property reused | ADR |
|---|---|---|---|
| Identity | `bfo:object` (BFO_0000030) + sortal subclass | — | ADR-001 |
| State | `bfo:Quality` + `cco:Stasis of Quality`; **no direct equivalent** | `bfo:inheres in` | ADR-001 |
| Activity | `cco:Act` (`ont00000005`) for intentional acts | `cco:has output`, `cco:has agent` | ADR-002 |
| Evidence | (a) co-import SOSA; (b) `cco:Measurement ICE` | (a) `sosa:hasFeatureOfInterest`; (b) `cco:is about` | ADR-003a / 003b |
| Context | `cco:Process Regulation` (`ont00001324`); **no Situation class** | `cco:prescribes` (reversed direction vs. DMFO) | ADR-004 |
| Location | `bfo:Site` + `cco:Geospatial Region`; **no GeoSPARQL spatial relations** | `bfo:located in` | ADR-005 |

Three slots are **documented absences**: State has no class
equivalent of `dmfo:Manifestation`, Context has no `Situation` class,
and Location has no GeoSPARQL spatial-relation algebra. We accept
the reduced expressivity these absences imply — patching them with
typed bridges would violate F3. A sixth ADR (ADR-006) commits to
**act-mediated identity-derivation chains** as the CCO-faithful
analogue of PROV-O `wasDerivedFrom`: a successor lot is one
`cco:has_input` / `cco:has_output` join away from its source through
an act token, and transitive chains are SPARQL property paths of the
form `(^cco:has_output / cco:has_input)+`. This is verbose but
faithful (Jensen et al. 2024, §4 *Event Ontology*).

**Two B2-CCO variants.** SOSA/SSN is not part of CCO 2.0; ADR-003a
co-imports it as a documented exception "for evaluation only" while
ADR-003b is the strict CCO-native alternative using `cco:Measurement
ICE` + `cco:is_about` only. We therefore report two B2-CCO scores:
**B2-CCO/sosa** treats SOSA as a temporary upstream borrow, and
**B2-CCO/native** is the F1-conformant baseline. The native column
is the empirical answer to the question "what does a strictly
CCO-native architecture cost?"; the sosa column is an upper bound
on what CCO achieves with one disciplined upstream import.

The two-instantiation evaluation yields:

| Framework | Maritime | Food | Combined |
|---|---|---|---|
| DMFO              | **20/20** | 20/20 | **20/20** |
| B1 (DMFO − A1–A6) | 8/20  | 8/20  | 8/20  |
| **B2-CCO/sosa**   | 17/20 | 17/20 | **17/20** |
| **B2-CCO/native** | 15/20 | 15/20 | **15/20** |

The two instantiations now score identically because the maritime
ABox includes an LCL deconsolidation scenario (UN/CEFACT MMT, IMO
FAL.5/Circ.42 §3.5) that exercises the same identity-derivation
pattern that food's splitting / merging scenario does. The
combined scores are therefore identical to the per-instantiation
scores.

The decisive Δ between DMFO and B2-CCO/native (**5 ACQs combined**)
is concentrated in five ACQs, each attributable to a specific ADR:

* **ACQ-II-06** (observation completeness, ADR-003b): ISO 8000-61's
  bitemporal phenomenon-time / result-time distinction has no native
  Measurement-ICE counterpart in CCO. **Only B2-CCO/native loses
  this**; B2-CCO/sosa retains it via the SOSA borrow.
* **ACQ-III-02** (state→situation→regime, ADR-004): the
  `dul:Situation includesObject` pattern reifies the contextual
  frame as an information-bearing entity that includes multiple
  state manifestations. CCO's act-as-situation reification
  (`cco:prescribes`) loses this multi-state inclusion and the join
  vacuously empties on realistic ABoxes. Both variants ◑.
* **ACQ-III-03** (state→evidence→sensor, ADR-003b): SOSA's
  `madeBySensor` has no CCO analogue (no Sensor concept in CCO 2.0).
  **Only B2-CCO/native loses this**; B2-CCO/sosa retains it.
* **ACQ-III-04** (qualified causal-information antecedent, ADR-002):
  the strict reading of PROV-O Rec §5.7 (`prov:qualifiedUsage` +
  `prov:hadRole`) requires a typed-role qualification on the
  carrier-flow witness. CCO has no `prov:Role` analogue and no
  qualifying construct over `cco:has_input`. **Both variants lose
  this** — structurally underdetermined under
  Faithful-Translation-Rule F3.
* **ACQ-IV-03** (identifier-scheme gap, ADR-001): in CCO, the
  identifier scheme is encoded in the *class* of the identifier
  ICE (`b2mar:BICCode` vs. `b2mar:IMONumber`), not as a separate
  attribute. The DMFO question "identifier without scheme" shifts
  to "object without designating ICE" — a related but distinct
  correctness check.

DMFO's advantage on identity-derivation (ACQ-III-05, ACQ-III-08) is
**ergonomic, not categorical**: under ADR-006, both B2-CCO variants
answer both ACQs, but the SPARQL is 2× longer and the property-path
chain alternates inverse-output / input hops through act tokens.

**The 5-ACQ gap between DMFO and B2-CCO/native is exactly the cost
of refusing the four upstream borrows (PROV-O, SOSA, DnS, GeoSPARQL)
that DMFO discharges via the typed alignment axioms (A1)–(A6) and
that a CCO-only foundation cannot natively replicate.**

**Reasoning-performance trade-off** (Table 2). We report two
closure strategies — OWL-RL_Semantics (the conservative default
consistent with §3 P1) and RDFS_Semantics (the production-efficient
alternative). A symmetric metadata-strip is applied to both
frameworks for parity. Under **OWL-RL** the total pipeline is
119 ms (DMFO maritime) vs. 72 ms (B2-CCO/native maritime) — DMFO
is ~1.6 × slower; under **RDFS** the gap shrinks to 1.26× (59 vs.
47 ms maritime). Per-ACQ query medians are within ±50 % across all
configurations.

**Closure-strategy sufficiency.** We empirically verified that
**no ACQ in the catalogue depends on OWL-RL-specific entailment
rules** beyond RDFS sub-class / sub-property / domain / range. Both
DMFO (20/20) and B2-CCO (17/20 sosa, 15/20 native) preserve their
exact answer sets under RDFS_Semantics. The hypothesis that
B2-CCO might require OWL-RL features that DMFO does not is
therefore **falsified**: neither does. The closure-strategy choice
is an infrastructure decision rather than a coverage one. The
closure-expansion overhead of DMFO's alignment layer (12 ms under
RDFS, 42 ms under OWL-RL, maritime) is fixed (independent of ABox
size in the ranges studied) and the empirical price of the 5-ACQ
coverage gain.
