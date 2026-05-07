# DMFO Module Reference

Per-module breakdown of the DMFO 2.0 axiom set. Each module file in
`ontology/` corresponds to one entry below. The classification under
"Locality" is reproduced by `python validation/scripts/locality_check.py`.

| Module | File | Imports | Contributes | Locality |
|---|---|---|---|---|
| O_base | [`ontology/dmfo-base.ttl`](../../ontology/dmfo-base.ttl) | all DMFO modules | umbrella ontology header only | top-local |
| O_Id | [`ontology/dmfo-identity.ttl`](../../ontology/dmfo-identity.ttl) | — | `dmfo:TimeVaryingEntity`, `dmfo:hasIdentifier`, `dmfo:identifierScheme` | top-local |
| O_St + b(Id,St) | [`ontology/dmfo-state.ttl`](../../ontology/dmfo-state.ttl) | O_Id, PROV-O, SOSA, DUL, OWL-Time | `dmfo:Manifestation`, A1 (joint typing), A2 (`dmfo:manifestationOf`), `dmfo:hasManifestationTime` | **A1 + A2 definitional**, rest top-local |
| O_Ev + b(St,Ev) | [`ontology/dmfo-evidence.ttl`](../../ontology/dmfo-evidence.ttl) | O_St, SOSA | `dmfo:evidencedBy`, A3 | top-local |
| O_Co + b(St,Co) | [`ontology/dmfo-context.ttl`](../../ontology/dmfo-context.ttl) | O_St, DUL/DnS | `dmfo:governedBy`, A4 | top-local |
| O_Act + b(St,Act) | [`ontology/dmfo-activity.ttl`](../../ontology/dmfo-activity.ttl) | O_St, PROV-O | `dmfo:stateWasGeneratedBy`, A5 | top-local |
| O_Lo + b(Co,Lo) | [`ontology/dmfo-location.ttl`](../../ontology/dmfo-location.ttl) | O_Co, GeoSPARQL | `dmfo:inZone`, A6 | top-local |
| O_identity-deriv | [`ontology/dmfo-identity-deriv.ttl`](../../ontology/dmfo-identity-deriv.ttl) | O_Id, PROV-O | `dmfo:SplitSourceIdentity`, `dmfo:MergeSourceIdentity` | top-local |

---

## Naming convention

* All DMFO terms are under the single namespace `https://w3id.org/dmfo#`,
  prefix `dmfo:`. There are no per-dimension sub-prefixes (the
  CritSupPort working-paper layout used `id:`/`st:`/`loc:`/`act:`/
  `ctx:`/`ev:` — that pattern was retired in 2.0 because DMFO does not
  itself contribute the dimensional vocabulary; the dimensional anchors
  come from imported W3C / OGC vocabs).
* Imported vocabularies retain their canonical prefixes: `prov:`,
  `sosa:`, `dul:`, `geo:`, `time:`.

## Activation matrix

A profile `P = (D, B, S)` activates a subset `A ⊆ {Id, St, Lo, Act, Co, Ev}`
of the dimensional modules by importing them. The Identity and State
modules are mandatory (Paper §3.2 Definition 1). Optional modules are:

| Use case | Id | St | Lo | Act | Co | Ev |
|---|---|---|---|---|---|---|
| Maritime port-call (Inst. I) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Food traceability (Inst. II) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Identity-only registry | ✓ | — | — | — | — | — |
| State-only history | ✓ | ✓ | — | — | — | — |

Both paper instantiations activate all six modules. Lighter
profiles (Identity-only registry, State-only history) are valid DMFO
configurations covered by the locality + decidability theorems.

## Bridge GCI absence

A property is a *bridge* if it carries one of the alignment axioms A2,
A3, A4, A5, A6. By construction, none of these properties has an
existential GCI: there is no `_:X owl:onProperty dmfo:evidencedBy ;
owl:someValuesFrom ?Y` axiom in any DMFO module. The check is
mechanised by `validation/scripts/validate_kb.py` and is part of the CI
gate.
