# Developer Guide

How to extend DMFO, contribute changes, and prepare a release. The
paper artefact is frozen at version 1.0.0; later releases will
follow the conventions below.

---

## Local development environment

```bash
# 1. Clone
git clone https://github.com/JanChristianRedlich/DMFO.git
cd DMFO

# 2. Conda env (preferred)
conda env create -f environment.yml
conda activate dmfo

# 3. Cache imported vocabularies (one-off)
bash validation/scripts/fetch_imports.sh

# 4. Smoke-test
python validation/scripts/validate_kb.py
python validation/scripts/conformance_validator.py profiles/maritime --no-shacl
python validation/scripts/run_all_acqs.py --all
```

Without conda:

```bash
python -m venv .venv
source .venv/bin/activate
pip install rdflib pyshacl owlrl owlready2
```

---

## Adding a new alignment axiom

A1–A6 are deliberately ACQ-minimal: each axiom contributes one missing
cross-dimensional typing or bridge relation, and the ablation study
confirms that removing any one eliminates at least one ACQ class.
Adding a new axiom A7 should follow the same discipline:

1. Decide which dimension(s) the axiom couples and place the axiom in
   the corresponding `ontology/dmfo-<dim>.ttl` file.
2. Add an `ASK` query under
   `acqs/queries/conformance/A7.ask.rq`.
3. Update `ALIGNMENT_AXIOMS` in `validation/scripts/conformance_validator.py`.
4. Add a corresponding SHACL shape (severity = warning unless the axiom
   is mandatory for conformance).
5. Add at least one new ACQ that depends on A7 + at least one ACQ-IV
   absence-detection variant.
6. Re-run `python validation/scripts/locality_check.py` and update
   `docs/architecture/MODULES.md` with the new locality classification.
7. Add a paragraph to
   [`docs/specifications/ALIGNMENT_AXIOMS.md`](specifications/ALIGNMENT_AXIOMS.md).

---

## Adding a new profile

See [Profile authoring](specifications/PROFILE_AUTHORING.md). In short:

1. `mkdir profiles/<name>` with three files: `<name>-tbox.ttl`,
   `<name>-abox.ttl`, `<name>-shapes.ttl`.
2. Add `<name>` to `PROFILE_PATHS` in
   `validation/scripts/run_hermit_reasoner.py`.
3. Add `<name>` as a `--profile` choice in
   `validation/scripts/run_all_acqs.py`.
4. Add a job to `.github/workflows/ci.yml` that runs
   `conformance_validator.py profiles/<name>`.

---

## Coding conventions

* Python ≥ 3.10. Type hints encouraged on new code; not yet enforced.
* No dependencies beyond `rdflib`, `pyshacl`, `owlrl`, `owlready2`.
  Heavier libraries (Java-side reasoners) are optional and documented
  per script.
* RDF: prefer Turtle for hand-written files. Use `n3` only if a feature
  requires it (it doesn't, in this repo).
* SPARQL files: header comment line listing class, source standard,
  required bridges. Keep prefix declarations alphabetical within a
  file.
* Write new comments only for non-obvious *why* lines. If an identifier
  is well-named, the *what* is already clear.

---

## Testing

The CI gate in `.github/workflows/ci.yml` runs:

1. `validate_kb.py` (syntax + bridge GCI).
2. `conformance_validator.py` for each profile.
3. `locality_check.py` (must yield exactly 2 definitional axioms).
4. `pyshacl` for each profile.
5. `run_all_acqs.py --all` (ACQ catalog + B1 ablation).

A failing CI run fails the build. To reproduce locally:

```bash
bash validation/scripts/run_queries.sh
```

---

## Release checklist (semantic versioning)

Major / minor / patch — Semantic Versioning.

For each release:

1. Bump `owl:versionInfo` and `owl:versionIRI` across all
   `ontology/dmfo-*.ttl` headers.
2. Add a `[X.Y.Z] – YYYY-MM-DD` block to
   [`CHANGELOG.md`](../CHANGELOG.md).
3. Update `version` in [`CITATION.cff`](../CITATION.cff).
4. Re-run `bash validation/scripts/run_queries.sh` and commit the
   updated `validation/results/*.json`.
5. Tag the commit (`git tag -a vX.Y.Z`) and push.

---

## Asking for help

Open a GitHub issue with:

* The DMFO version (from `owl:versionInfo` in any module header).
* The Python + rdflib + pyshacl versions.
* A minimal failing input (TBox / ABox / ACQ).
* Expected vs. actual output of the relevant validation script.
