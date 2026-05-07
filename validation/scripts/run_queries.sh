#!/usr/bin/env bash
# =============================================================
# DMFO Reproduction Pipeline
#
# Orchestrates the end-to-end validation chain reported in the
# paper (Sections 4.1–4.3). Designed to run inside the Docker
# image; use `python3 -m venv` outside Docker.
#
# Steps:
#   1. KB syntax & bridge-GCI check       (validate_kb.py)
#   2. Conformance per profile           (conformance_validator.py)
#   3. Top-locality classification        (locality_check.py)
#   4. SHACL validation per profile       (pyshacl)
#   5. ACQ catalogue + B1 ablation        (run_all_acqs.py)
#   6. HermiT reasoning (optional)         (run_hermit_reasoner.py)
#
# Outputs: validation/results/*.json + reasoning logs.
# =============================================================
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

mkdir -p validation/results

step() { echo; echo "==[ $1 ]==========================================" ; }

step "1/6  KB syntax + bridge-GCI check"
python3 validation/scripts/validate_kb.py

step "2/6  Conformance — maritime profile"
python3 validation/scripts/conformance_validator.py profiles/maritime || true

step "2/6  Conformance — food profile"
python3 validation/scripts/conformance_validator.py profiles/food || true

step "3/6  Top-locality classification"
python3 validation/scripts/locality_check.py

step "4/6  SHACL — maritime"
pyshacl -s shapes/dmfo-core-shapes.ttl \
        -s shapes/identity-deriv-shapes.ttl \
        -s profiles/maritime/mar-shapes.ttl \
        -e ontology/dmfo-full.ttl \
        -d profiles/maritime/mar-abox.ttl \
        -f human \
        > validation/results/shacl_maritime.txt 2>&1 || true

step "4/6  SHACL — food"
pyshacl -s shapes/dmfo-core-shapes.ttl \
        -s shapes/identity-deriv-shapes.ttl \
        -s profiles/food/food-shapes.ttl \
        -e ontology/dmfo-full.ttl \
        -d profiles/food/food-abox.ttl \
        -f human \
        > validation/results/shacl_food.txt 2>&1 || true

step "5/6  ACQ catalog + B1 ablation"
python3 validation/scripts/run_all_acqs.py --all

step "6/6  HermiT reasoning (optional)"
if command -v java >/dev/null 2>&1; then
    python3 validation/scripts/run_hermit_reasoner.py || true
else
    echo "  (skip — Java not available)"
fi

echo
echo "Pipeline finished. See validation/results/ for outputs."
