# Changelog

All notable changes to this project are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [1.0.0] – 2026-05-03 — Initial release

First public release of the DMFO reproduction package.

### Contents

- **Modular DMFO TBox** across eight files: `dmfo-base`,
  `dmfo-identity`, `dmfo-state`, `dmfo-evidence`, `dmfo-context`,
  `dmfo-activity`, `dmfo-location`, `dmfo-identity-deriv`, plus the
  aggregated `dmfo-full.ttl`.
- **Four classes / five object properties** under the single `dmfo:`
  namespace (`TimeVaryingEntity`, `Manifestation`,
  `SplitSourceIdentity`, `MergeSourceIdentity`; `manifestationOf`,
  `stateWasGeneratedBy`, `evidencedBy`, `governedBy`, `inZone`).
- **Two profiles**: `profiles/maritime/` (port-call sequence per IMO
  FAL.5/Circ.42) and `profiles/food/` (FDA FSMA-204 KDE/CTE
  traceability with split/merge identity derivation).
- **DMFO core SHACL shapes** (`shapes/dmfo-core-shapes.ttl`,
  `shapes/identity-deriv-shapes.ttl`).
- **20 Anchor Competence Questions** in `acqs/queries/dmfo/`,
  classified into Class I (identity-only), II (single-bridge),
  III (multi-bridge), IV (absence detection); ACQ catalogue at
  `acqs/catalogue.md`, saturation trace at `acqs/saturation-trace.md`,
  IRR plan at `acqs/irr/PLAN.md`.
- **B2-CCO baseline** (`validation/b2-cco/`): two-variant CCO 2.0
  implementation (`sosa-coimport`, `strict-native`) with 7 ADRs and
  the Faithful-Translation-Rule (F1–F5).
- **Validation scripts** consolidated in `validation/scripts/`:
  `validate_kb`, `conformance_validator`, `locality_check`,
  `run_all_acqs` (incl. B1 ablation), `run_hermit_reasoner`,
  `run_queries.sh`, plus the perf, scaling, and B2-CCO runners and
  the Apache Jena Docker replication under `jena-bench/`.
- **Reproduction pipeline**: `Dockerfile`, `environment.yml`,
  `.github/workflows/ci.yml`.
- **Documentation**: `README.md`, `TIMELINE.md`,
  `docs/architecture/`, `docs/specifications/`,
  `docs/appendix-{A,C,D}-*.md`, `docs/DEVELOPER_GUIDE.md`.
- **Visualization**: `visualization/visualize_abox.py` renders
  interactive vis.js graphs for both profiles.
