# DMFO — A Modular Alignment Architecture for Situationally Interpretable State Representations

> **Reproduction package** for the paper *"DMFO: A Modular Alignment
> Architecture for Situationally Interpretable State Representations"*.
>
> **Version:** 1.0.0 (May 2026)
> **License:** [CC BY 4.0](LICENSE.txt)
> **OWL profile:** OWL 2 DL / SROIQ(D)

---

## What is DMFO?

DMFO is an **OWL 2 DL Ontology Design Pattern Network** in which a
*situation* decomposes into six dimensional slots — **Identity, State,
Location, Activity, Context, Evidence** — connected by typed bridge
relations. Each slot has an **anchor class**; domain ontologies bind to
those anchors via subclassing. Six **alignment axioms (A1)–(A6)** act
as conformance constraints that bind domain classes to imported W3C /
OGC vocabularies (PROV-O, SOSA/SSN, DUL/DnS, GeoSPARQL, OWL-Time) into
a cross-dimensional whole.

**Key claim** (Paper §1, §3): co-importing established vocabularies is
*necessary but not sufficient* for situational answerability. The
typed inter-dimensional bridges (A1)–(A6) are the *alignment layer* a
candidate ontology must explicitly commit to in order to expose
cross-dimensional query paths from a state assertion to its activity,
evidence, normative context, or institutional location.

DMFO contributes only **four classes** and **five object properties**;
all other slot anchors come from the imported vocabularies. The
contribution is the alignment layer, not new vocabulary.

| Class | Purpose |
|---|---|
| `dmfo:TimeVaryingEntity` | Identity anchor (TVE) |
| `dmfo:Manifestation` | State anchor — A1: jointly typed `prov:Entity ⊓ dul:Event ⊓ sosa:FeatureOfInterest` |
| `dmfo:SplitSourceIdentity` | Identity-derivation marker (split) |
| `dmfo:MergeSourceIdentity` | Identity-derivation marker (merge) |

| Property | Bridge | Axiom |
|---|---|---|
| `dmfo:manifestationOf` | Identity ↔ State | A2 |
| `dmfo:evidencedBy` | State ↔ Evidence | A3 (⊑ inverse `sosa:hasFeatureOfInterest`) |
| `dmfo:governedBy` | Context-internal | A4 (`dul:Situation` × `dul:Description`) |
| `dmfo:stateWasGeneratedBy` | State ↔ Activity | A5 (⊑ `prov:wasGeneratedBy`) |
| `dmfo:situatedAt` | Context ↔ Location | A6 (⊑ `geo:sfWithin`) |

---

## Repository structure

```
DMFO/
├── ontology/                # 8 modular DMFO TBox files + aggregated dmfo-full.ttl
│   ├── dmfo-base.ttl              ← O_base
│   ├── dmfo-identity.ttl          ← O_Id (dmfo:TimeVaryingEntity)
│   ├── dmfo-state.ttl             ← O_St + b(Id,St)  (A1, A2)
│   ├── dmfo-evidence.ttl          ← O_Ev + b(St,Ev)  (A3)
│   ├── dmfo-context.ttl           ← O_Co + b(St,Co)  (A4)
│   ├── dmfo-activity.ttl          ← O_Act + b(St,Act)(A5)
│   ├── dmfo-location.ttl          ← O_Lo + b(Co,Lo)  (A6)
│   ├── dmfo-identity-deriv.ttl    ← O_identity-deriv (split/merge)
│   ├── dmfo-full.ttl              ← all-modules import
│   ├── catalog-v001.xml           ← Protégé catalog
│   └── imports/                   ← cached W3C / OGC vocabularies
│
├── profiles/                # the two paper instantiations
│   ├── maritime/                  ← Instantiation I  (port-call IMO FAL.5)
│   │   ├── mar-tbox.ttl
│   │   ├── mar-abox.ttl
│   │   └── mar-shapes.ttl
│   └── food/                      ← Instantiation II (FDA FSMA-204 KDE/CTE)
│       ├── food-tbox.ttl
│       ├── food-abox.ttl
│       └── food-shapes.ttl
│
├── shapes/                  # DMFO core SHACL shapes
│   ├── dmfo-core-shapes.ttl       ← (A1)–(A6) conformance
│   └── identity-deriv-shapes.ttl  ← acyclicity of prov:wasDerivedFrom
│
├── validation/
│   ├── scripts/                  ← single canonical script folder
│   │   ├── validate_kb.py               ← syntax + bridge-GCI check
│   │   ├── conformance_validator.py     ← A1–A6 + SHACL conformance
│   │   ├── locality_check.py            ← top-locality classification
│   │   ├── run_all_acqs.py              ← ACQ catalog + B1 ablation
│   │   ├── run_hermit_reasoner.py       ← HermiT TBox+ABox reasoning
│   │   ├── run_queries.sh               ← end-to-end orchestrator
│   │   ├── fetch_imports.sh             ← downloads imported vocabs
│   │   ├── perf-*.py                    ← closure / strip / RDFS-vs-OWL-RL benchmarks
│   │   ├── scale-benchmark*.py          ← rdflib scaling sweep (N ∈ {1…500})
│   │   ├── generate_scaled_abox.py      ← synthetic ABox generator
│   │   ├── b2cco-run-acqs.sh            ← B2-CCO baseline runner (sosa + native)
│   │   ├── b2cco-consistency-check.sh   ← HermiT/OWL-RL consistency on CCO
│   │   ├── b2cco-oops-check.sh          ← OOPS! pitfall scan
│   │   ├── b2cco-perf-benchmark.py      ← high-rep DMFO/CCO timing benchmark
│   │   └── jena-bench/                  ← Apache Jena Docker replication
│   │       ├── Dockerfile, JenaBenchmark.java, run-jena-scale.sh
│   │       └── queries-native-merged/   ← strict-CCO-native query overlay
│   ├── scale-test/               ← generated scaled ABoxes (N=1…500)
│   ├── results/                  ← reproduction-pipeline outputs
│   └── b2-cco/                   ← Common-Core-Ontologies baseline (B2 in paper §4)
│       ├── ontology/, abox/, vendor/cco-2.0/
│       ├── docs/                     ← ADRs, slot-mapping, manuscript inputs
│       └── results/                  ← B2-CCO ACQ + perf JSON + comparison CSVs
│
├── acqs/                       ← all 20 ACQs in one place (paper §4.2)
│   ├── catalogue.md                  ← ACQ catalog with source standard, class
│   ├── saturation-trace.md           ← per-standard new-signature trace
│   ├── queries/
│   │   ├── dmfo/                     ← ACQ-{I,II,III,IV}-*.sparql (20 files)
│   │   ├── b2-cco-sosa/              ← acq-NN-cco.rq (SOSA co-import variant)
│   │   ├── b2-cco-native/            ← strict-CCO-native overrides for 4 ACQs
│   │   ├── conformance/              ← A1.ask.rq … A6.ask.rq
│   │   └── ablation/B1, B2/          ← alignment-ablation specs
│   └── irr/                          ← IRR plan + delivery slot
│       ├── PLAN.md                   ← pre-registered protocol
│       └── README.md
│
├── docs/
│   ├── architecture/ARCHITECTURE.md     ← architectural deep dive
│   ├── architecture/MODULES.md          ← per-module reference
│   ├── specifications/ALIGNMENT_AXIOMS.md  ← A1–A6 formal spec (Manchester + Turtle + locality)
│   ├── specifications/PROFILE_AUTHORING.md ← 5-step profile-authoring guide
│   ├── appendix-A-formal.md            ← per-axiom Turtle, locality, imports
│   ├── appendix-C-acq-catalogue.md     ← per-framework ACQ result matrix
│   ├── appendix-C-scaling.md           ← N=1…500 scaling test
│   ├── appendix-D-examples.md          ← worked examples + necessity matrix
│   └── DEVELOPER_GUIDE.md
│
├── visualization/
│   ├── visualize_abox.py            ← interactive vis.js graph (maritime + food)
│   └── results/                     ← `abox_{maritime,food}_<date>.html`
├── Dockerfile
├── environment.yml
├── CITATION.cff
└── .github/workflows/ci.yml
```

---

## Quickstart

### One-shot reproduction

```bash
docker build -t dmfo:1.0.0 .
docker run --rm -v "$PWD/validation/results:/work/validation/results" dmfo:1.0.0
```

The container runs the full pipeline (validate, conformance, locality,
SHACL, 20 ACQs + B1 ablation, optional HermiT) and writes results into
`validation/results/`.

### Local Python install

```bash
conda env create -f environment.yml
conda activate dmfo

bash validation/scripts/fetch_imports.sh           # cache W3C/OGC vocabs
python validation/scripts/validate_kb.py           # KB syntax + bridge-GCI check
python validation/scripts/conformance_validator.py profiles/maritime
python validation/scripts/conformance_validator.py profiles/food
python validation/scripts/locality_check.py        # Theorem 2 reproduction
python validation/scripts/run_all_acqs.py --all    # 20 ACQs + B1 ablation
```

### Single SPARQL query

```bash
# rdflib (with OWL-RL closure already applied by the runner):
python validation/scripts/run_all_acqs.py --profile maritime

# or with Apache Jena ARQ (after running fetch_imports.sh):
arq --data ontology/dmfo-full.ttl \
    --data profiles/maritime/mar-tbox.ttl \
    --data profiles/maritime/mar-abox.ttl \
    --query acqs/queries/dmfo/ACQ-III-01_state_activity_agent.sparql
```

### Visualization

Render an interactive vis.js graph of the maritime **and** food ABoxes
(slot- and bridge-coloured, browser-side filters, presets per
alignment axiom):

```bash
python visualization/visualize_abox.py                 # both profiles → visualization/results/
python visualization/visualize_abox.py --profile food
python visualization/visualize_abox.py --profile maritime
```

### Protégé

1. `File → Open → ontology/dmfo-full.ttl` (the catalog points imports at
   the cached vocabs in `ontology/imports/`).
2. `Reasoner → HermiT 1.4 → Start Reasoner` — expected: consistent, 0
   unsatisfiable classes.
3. To inspect a profile: open `profiles/maritime/mar-tbox.ttl` (it
   imports `https://w3id.org/dmfo`).

---

## Reproduced results

Output of `python validation/scripts/run_all_acqs.py --all` with
`owlrl.OWLRL_Semantics` materialisation, against the synthetic ABoxes in
`profiles/`:

| Profile | DMFO | B1 | Δ |
|---|---|---|---|
| Maritime (Inst. I)  | 20 / 20 | 8 / 20 | 12 ACQs lost without (A1)–(A6) |
| Food (Inst. II)     | 20 / 20 | 8 / 20 | 12 ACQs lost without (A1)–(A6) |

Both instantiations score 20/20 because the maritime ABox includes
the LCL deconsolidation pattern (UN/CEFACT MMT, IMO FAL.5/Circ.42 §3.5)
that exercises the same identity-derivation chain (ACQ-III-05 +
ACQ-III-08) as food's split/merge scenario.

Locality: per `python validation/scripts/locality_check.py`, two axioms
in `O_St + b(Id,St)` are definitional (A1, A2 — Paper Theorem 2(b)); all
other axioms are top-local (Theorem 2(a)).

Conformance: both maritime and food profiles pass A1–A6 ASK-checks +
SHACL validation against the DMFO core shapes.

---

## Documentation

### Architecture & specification

- [Architecture deep dive](docs/architecture/ARCHITECTURE.md) — six
  slots, five bridges, alignment-layer claim, conservativity.
- [Module reference](docs/architecture/MODULES.md) — per-module signature,
  imports, axioms.
- [Alignment axioms (A1)–(A6)](docs/specifications/ALIGNMENT_AXIOMS.md)
  — Manchester syntax, Turtle, locality classification.
- [ACQ catalog](acqs/catalogue.md) — 20 ACQs with
  source standard, class, bridge dependency, expected outcome.
- [Profile authoring](docs/specifications/PROFILE_AUTHORING.md) —
  5-step procedure to author a new DMFO-conformant profile.
- [Developer guide](docs/DEVELOPER_GUIDE.md) — how to extend, contribute,
  release.

### Paper appendices (consolidated)

- [Appendix A — Formal Properties](docs/appendix-A-formal.md) —
  per-axiom Turtle, OWL 2 DL construct table, decidability check,
  per-module locality classification, imports manifest with hashes.
- [Appendix C.1 — ACQ result matrix](docs/appendix-C-acq-catalogue.md)
  — DMFO / B1 / B2-CCO/sosa / B2-CCO/native per-ACQ results, with
  ADR-keyed diagnosis.
- [Appendix C.2 — Scaling test (N=1…500)](docs/appendix-C-scaling.md)
  — rdflib + Jena cross-engine replication, crossover analysis.
- [Appendix D — Worked examples + component-necessity matrix](docs/appendix-D-examples.md)
  — abstract pattern, maritime + food bindings, split/merge,
  strictest-applicable-obligation, per-component × per-ACQ matrix.

### Methodology artefacts

- [TIMELINE.md](TIMELINE.md) — chronological development phases.
- [ACQ saturation trace](acqs/saturation-trace.md) —
  per-standard new-signature counts.
- [IRR plan](acqs/irr/PLAN.md) — pre-registered protocol.

### B2-CCO baseline

- [Faithful-Translation-Rule (F1–F5)](validation/b2-cco/docs/faithful-translation-rule.md)
- [SOSA × CCO integration](validation/b2-cco/docs/sosa-cco-integration.md)
- [ADRs 001–007](validation/b2-cco/docs/adr/) — one per slot,
  plus ADR-003a/b for the two evidence variants and ADR-007 for
  the F3-prohibited identifier-scheme property.

---

## Citation

```bibtex
@unpublished{redlich2026dmfo,
  author    = {Redlich, Jan Christian and Kloke, Peter and Bosse, Sebastian},
  title     = {{DMFO}: A Modular Alignment Architecture for
               Situationally Interpretable State Representations},
  year      = {2026},
  note      = {Manuscript},
}
```

---

## Contact

**Jan Christian Redlich** (corresponding) · jan.redlich@bonnsystems.com · Bonn Systems GmbH, Bonn, Germany
**Peter Kloke** · peter.kloke@bonnsystems.com · Bonn Systems GmbH, Bonn, Germany
**Sebastian Bosse** · sebastian.bosse@hhi.fraunhofer.de · Fraunhofer Heinrich-Hertz-Institut (HHI), Berlin, Germany
