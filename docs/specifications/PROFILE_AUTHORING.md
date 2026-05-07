# Authoring a DMFO-Conformant Profile

Five-step procedure for a new domain author, following Paper §4.4.
The maritime and food profiles in [`profiles/`](../../profiles/) are
worked examples.

---

## Step 1 — Identify domain classes per slot

For each of the six slots, decide which domain-vocabulary classes will
populate it. Mandatory: at least one class binds to the Identity slot
and at least one to the State slot. Optional slots can be left empty.

| Slot | Anchor | Maritime example | Food example |
|---|---|---|---|
| Identity   | `dmfo:TimeVaryingEntity`              | `mar:Container`           | `food:Batch` |
| State      | `dmfo:Manifestation`                  | `mar:InYard`, `mar:OnVessel` | `food:InColdStorage` |
| Activity   | `prov:Activity`                       | `mar:CraneTransfer`       | `food:SplittingActivity` |
| Evidence   | `sosa:Observation`                    | `mar:Observation_AIS`     | `food:HACCPRecord` |
| Context    | `dul:Situation` / `dul:Description`   | `mar:CustodyTransferSituation`, `mar:RegulatoryRegime` | `food:RegulatorySituation`, `food:FoodLawRegime` |
| Location   | `geo:Feature`                         | `mar:ISPSZone`            | `food:FoodFacility` |

---

## Step 2 — Write binding axioms (B)

Bind each domain class to its anchor by `rdfs:subClassOf`:

```turtle
mar:Container         rdfs:subClassOf dmfo:TimeVaryingEntity .
mar:InYard            rdfs:subClassOf dmfo:Manifestation .
mar:CraneTransfer     rdfs:subClassOf prov:Activity .
mar:Observation_AIS   rdfs:subClassOf sosa:Observation .
mar:CustodyTransferSituation rdfs:subClassOf dul:Situation .
mar:RegulatoryRegime  rdfs:subClassOf dul:Description .
mar:ISPSZone          rdfs:subClassOf geo:Feature .
```

Profile-specific datatype properties (e.g. `mar:bicCode`) should be
declared `rdfs:subPropertyOf dmfo:hasIdentifier` so that the generic
ACQs over identifiers reach them under RDFS / OWL-RL closure.

---

## Step 3 — Author profile-level SHACL shapes (S)

Profile shapes encode closed-world deployment-time rules that go
beyond the framework's optional bridges. For example
([`mar-shapes.ttl`](../../profiles/maritime/mar-shapes.ttl)):

```turtle
mar:CustodyTransferSituationShape
    a sh:NodeShape ;
    sh:targetClass mar:CustodyTransferSituation ;
    sh:property [
        sh:path dul:includesObject ;
        sh:minCount 2 ;
        sh:message "M-02: must include at least a prior and a successor manifestation."@en ;
    ] .
```

Profile shapes should:

* Use `sh:Violation` for hard requirements (e.g. ID format).
* Use `sh:Warning` for "should-have" rules whose absence is an
  epistemic gap rather than malformation.
* Never duplicate the DMFO core shapes (`shapes/dmfo-core-shapes.ttl`),
  which are loaded together with profile shapes.

---

## Step 4 — Run the conformance validator

```bash
python validation/scripts/conformance_validator.py profiles/<your-profile>
```

The validator runs:

1. Import-closure check (does the profile import `https://w3id.org/dmfo`?).
2. (A1)–(A6) ASK queries against the merged TBox.
3. Anchor-binding check (do declared subclasses point to one of the six
   DMFO anchors?).
4. SHACL validation of the candidate profile's ABox against
   `dmfo-core-shapes.ttl` + `identity-deriv-shapes.ttl` +
   `<your-profile>-shapes.ttl`.

Failures are written to `validation/results/conformance_<profile>.json`
with diagnostic messages. The validator returns exit-code 0 iff the
profile is conformant.

---

## Step 5 — Instantiate the ACQ catalog

The 20 ACQs in [`acqs/queries/dmfo/`](../../acqs/queries/dmfo/) are
written against the DMFO bridges (`dmfo:manifestationOf`,
`dmfo:stateWasGeneratedBy`, `dmfo:evidencedBy`, `dmfo:governedBy`,
`dmfo:inZone`) and the imported vocabularies. They run unmodified
against any conformant profile.

```bash
python validation/scripts/run_all_acqs.py --profile <your-profile>
```

Domain-specific extensions (additional ACQs that use the profile's own
vocabulary) can be added under
`acqs/queries/dmfo/profile_extensions/<your-profile>/` without affecting
the core 20-ACQ score.

---

## What a conformance report flags vs. accepts

| Result | Meaning |
|---|---|
| All A1–A6 ASKs pass + SHACL `conforms = True` | Profile is DMFO-conformant. |
| A1 ASK fails | Profile redefined or shadowed `dmfo:Manifestation` without re-asserting the joint typing. Repair by adding A1 explicitly to the profile TBox. |
| Domain-class binding missing for a populated slot | Profile populates a slot via instances but no `rdfs:subClassOf` axiom binds the class to the anchor. Repair by adding the binding. |
| SHACL violation on `dmfo:ManifestationShape` (`dmfo:manifestationOf` minCount = 1) | Manifestation without TVE projection — A2 is missing data, not absent. Repair by adding the missing triple. |
| SHACL warning on `dmfo:evidencedBy` / `dmfo:stateWasGeneratedBy` | Optional bridge missing — *not* a violation; the absence is queryable as a Class IV ACQ. |

The "not a violation" pattern is the core data-of-opportunity
constraint: partial situational coverage stays consistent.
