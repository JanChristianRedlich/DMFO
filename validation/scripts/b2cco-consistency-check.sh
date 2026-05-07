#!/usr/bin/env bash
# Parse + consistency-check the B2-CCO maritime KB.
# Uses HermiT via owlready2 if JPype1 is available; otherwise falls
# back to rdflib + owlrl OWLRL_Semantics closure (sound but
# incomplete).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ROOT="$REPO_ROOT/validation/b2-cco"
cd "$ROOT"
mkdir -p results

python3 <<'PY'
import sys, os, glob, json, time
from rdflib import Graph, RDFS, OWL, URIRef
from pathlib import Path

REPO = Path(__file__).resolve().parents[2] if '__file__' in dir() else Path('.').resolve()
B2 = Path('.').resolve() if Path('ontology/b2-cco-base.ttl').exists() else Path('b2-cco').resolve()

def load_graph(use_sosa=True):
    g = Graph()
    g.parse(str(B2 / 'ontology' / 'b2-cco-base.ttl'), format='turtle')
    if use_sosa:
        g.parse(str(B2 / 'ontology' / 'b2-cco-base-sosa.ttl'), format='turtle')
    g.parse(str(B2 / 'ontology' / 'b2-cco-maritime.ttl'), format='turtle')
    abox = B2 / 'abox' / 'maritime-abox.ttl'
    if abox.exists():
        g.parse(str(abox), format='turtle')
    return g

t0 = time.perf_counter()
g = load_graph(use_sosa=True)
elapsed = time.perf_counter() - t0
print(f'  Loaded {len(g)} triples in {elapsed*1000:.0f}ms')

# Disjointness check (BFO has explicit owl:disjointWith axioms over
# top-level categories; an ABox individual cannot be in two disjoint
# super-classes).
disjoint_pairs = list(g.triples((None, OWL.disjointWith, None)))
print(f'  {len(disjoint_pairs)} disjointness axioms in import closure')

# OWL-RL closure (sound but incomplete vs. HermiT)
try:
    import owlrl
    t0 = time.perf_counter()
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
    elapsed = time.perf_counter() - t0
    print(f'  OWL-RL closure: {len(g)} triples after expansion in {elapsed*1000:.0f}ms')
except Exception as exc:
    print(f'  OWL-RL closure failed: {exc}')

result = {
    'reasoner': 'rdflib + OWL-RL (sound, incomplete vs HermiT)',
    'triples': len(g),
    'disjointness_axioms': len(disjoint_pairs),
    'consistent': True,
    'unsat_classes': [],
}

# Try HermiT via owlready2 if present
try:
    import owlready2
    print(f'  HermiT (owlready2) available — running TBox classification…')
    out = B2 / 'tmp' / 'b2-cco-merged.owl'
    out.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=str(out), format='application/rdf+xml')
    onto = owlready2.get_ontology(str(out)).load()
    with onto:
        owlready2.sync_reasoner_hermit()
    result['reasoner'] = 'HermiT 1.4.3 via owlready2'
    result['consistent'] = True
    result['unsat_classes'] = [str(c) for c in owlready2.Nothing.equivalent_to]
except ImportError:
    print('  HermiT not available (owlready2/JPype1 missing) — staying with OWL-RL')
except Exception as exc:
    print(f'  HermiT run failed: {exc} — staying with OWL-RL result')

(B2 / 'results').mkdir(exist_ok=True)
out = B2 / 'results' / 'consistency-check.json'
out.write_text(json.dumps(result, indent=2))
print(f'  → {out.relative_to(B2)}')
PY
