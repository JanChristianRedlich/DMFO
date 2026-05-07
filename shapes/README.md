# DMFO SHACL Shapes

Three logical groups of shapes:

| File | Purpose | Severity |
|---|---|---|
| `dmfo-core-shapes.ttl` | A1–A6 conformance + Manifestation completeness | Violation / Warning |
| `identity-deriv-shapes.ttl` | Acyclicity of `prov:wasDerivedFrom`, split-successor multiplicity | Violation / Warning |
| `../profiles/<profile>/<profile>-shapes.ttl` | Profile-specific closed-world rules (e.g. M-01, F-01) | Violation |

## Design principles

* **No SHACL substitution for OWL inference (Principle P3).**
  The shapes never relax OWL claims; they only refine deployment-time
  constraints under closed-world semantics. The conservativity and
  locality results of Paper §4.1 apply to OWL axioms only.
* **Optional bridges stay optional.** Manifestations without
  `dmfo:evidencedBy` or `dmfo:stateWasGeneratedBy` are queryable
  epistemic gaps (Corollary of Theorem 2 / Paper §4.3 Negative Cases),
  not violations. Only `dmfo:manifestationOf` is mandatory at the
  Manifestation shape level.
* **Profile shapes layer on top.** The conformance validator
  (`validation/scripts/conformance_validator.py`) runs core shapes,
  identity-deriv shapes, and profile shapes together against the
  candidate profile's ABox.

## Running

```bash
pyshacl -s shapes/dmfo-core-shapes.ttl \
        -e ontology/dmfo-full.ttl \
        -d profiles/maritime/mar-abox.ttl \
        -f human
```

For the identity-derivation acyclicity check, include both shape files
via `-s shapes/dmfo-core-shapes.ttl -s shapes/identity-deriv-shapes.ttl`.
