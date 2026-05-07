# B2 Ablation: Engineered Baseline (naïve integration sketch)

Per Paper §4.2 "Engineered baseline (B2)", B2 is a deliberately
under-specified competing alternative on top of the same anchor
vocabularies. Following the camera-ready protocol it adds:

1. `prov:Entity ⊓ dul:Event ⊑ owl:Thing` — only generic typing of
   PROV-bearing event individuals (no joint `sosa:FeatureOfInterest`
   typing as in A1).
2. `owl:sameAs` between selected `dul:Situation` and `prov:Activity`
   instances for events with both provenance and contextual
   descriptions (instead of the typed bridges A4–A5).
3. SWRL-style domain inference rules connecting `sosa:Observation` to
   its target via `sosa:hasFeatureOfInterest` only (no inverse-typed A3
   bridge).
4. **No** typed `situatedAt` bridge between `dul:Situation` and
   `geo:Feature` (A6 absent).

The B2 construction protocol and ABox annotations will be supplied with
the camera-ready release. The repo provides a stub
(`validation/scripts/build_b2.py`) that the camera-ready release
populates with the published B2 axioms; until then the ACQ scores for
B2 are reported as TODO in `validation/results/ablation.json`, matching
Table 3 of the submitted version.
