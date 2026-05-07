#!/usr/bin/env bash
# Run B2-CCO ACQs against maritime + food KBs in two variants:
#   sosa-coimport  (default; ADR-003a — uses SOSA Observation properties)
#   strict-native  (ADR-003b — no SOSA; only cco:Measurement ICE +
#                   cco:is_about; ACQ-II-06 + ACQ-III-03 become (d))
#
# Usage:
#   bash validation/scripts/b2cco-run-acqs.sh                       # both profiles, both variants
#   bash validation/scripts/b2cco-run-acqs.sh maritime              # one profile, both variants
#   bash validation/scripts/b2cco-run-acqs.sh food                  # one profile, both variants
#   VARIANT=sosa  bash validation/scripts/b2cco-run-acqs.sh         # only the SOSA variant
#   VARIANT=native bash validation/scripts/b2cco-run-acqs.sh        # only the strict-native variant
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ROOT="$REPO_ROOT/validation/b2-cco"
cd "$ROOT"
mkdir -p results

TARGET="${1:-all}"
VARIANT="${VARIANT:-both}"
export TARGET VARIANT REPO_ROOT

python3 <<'PY'
import json, time, statistics, sys, os
from pathlib import Path
from rdflib import Graph
import owlrl

ROOT = Path('.')
REPO_ROOT = Path(os.environ.get('REPO_ROOT', '.')).resolve()
TARGET = os.environ.get('TARGET', 'all')
VARIANT = os.environ.get('VARIANT', 'both')

QUERIES_DIR        = REPO_ROOT / 'acqs' / 'queries' / 'b2-cco-sosa'
QUERIES_NATIVE_DIR = REPO_ROOT / 'acqs' / 'queries' / 'b2-cco-native'

# Per-ACQ metadata, parameterised by variant. The variant flips
# classification + diagnosis for the four SOSA-dependent ACQs:
#   sosa:    II-03=a, II-06=a, III-03=a, IV-01=a
#   native:  II-03=b, II-06=d, III-03=d, IV-01=b
META_BASE = {
    'acq-01': ('ACQ-I-01',   'I',   'b',   'ADR-001'),
    'acq-02': ('ACQ-I-02',   'I',   'b',   'ADR-001+003a'),
    'acq-03': ('ACQ-II-01',  'II',  'b',   'ADR-001'),
    'acq-04': ('ACQ-II-02',  'II',  'a',   'ADR-002'),
    'acq-05': ('ACQ-II-03',  'II',  None,  None),    # variant-dependent
    'acq-06': ('ACQ-II-04',  'II',  'b',   'ADR-005'),
    'acq-07': ('ACQ-II-05',  'II',  'b',   'ADR-004'),
    'acq-08': ('ACQ-II-06',  'II',  None,  None),    # variant-dependent
    'acq-09': ('ACQ-III-01', 'III', 'b',   'ADR-001+002'),
    'acq-10': ('ACQ-III-02', 'III', 'b/c', 'ADR-004'),
    'acq-11': ('ACQ-III-03', 'III', None,  None),    # variant-dependent
    'acq-12': ('ACQ-III-04', 'III', 'd',   'ADR-002 (no PROV-O qualified usage / hadRole in CCO)'),
    'acq-13': ('ACQ-III-05', 'III', 'b',   'ADR-006 (act-mediated)'),
    'acq-14': ('ACQ-III-06', 'III', 'b',   'ADR-004+005'),
    'acq-15': ('ACQ-III-07', 'III', 'b',   'ADR-002+005'),
    'acq-16': ('ACQ-III-08', 'III', 'b',   'ADR-006 (transitive Act-chain)'),
    'acq-17': ('ACQ-IV-01',  'IV',  None,  None),    # variant-dependent
    'acq-18': ('ACQ-IV-02',  'IV',  'a',   'ADR-002'),
    'acq-19': ('ACQ-IV-03',  'IV',  'c',   'ADR-001 (scheme shift)'),
    'acq-20': ('ACQ-IV-04',  'IV',  'b',   'ADR-004'),
}
VARIANT_OVERRIDES = {
    'sosa': {
        'acq-05': ('a',   'ADR-003a (SOSA co-import)'),
        'acq-08': ('a',   'ADR-003a (SOSA bitemporal annotations)'),
        'acq-11': ('a',   'ADR-003a (SOSA sensor link)'),
        'acq-17': ('a',   'ADR-003a'),
    },
    'native': {
        'acq-05': ('b',   'ADR-003b (cco:is_about)'),
        'acq-08': ('d',   'ADR-003b (no bitemporal phenomenon/result-time in CCO Measurement ICE)'),
        'acq-11': ('d',   'ADR-003b (no sensor concept in CCO)'),
        'acq-17': ('b',   'ADR-003b (NOT EXISTS cco:is_about)'),
    },
}

PROFILES_SOSA = {
    'maritime': [
        'ontology/b2-cco-base.ttl',
        'ontology/b2-cco-base-sosa.ttl',
        'ontology/b2-cco-maritime.ttl',
        'abox/maritime-abox.ttl',
    ],
    'food': [
        'ontology/b2-cco-base.ttl',
        'ontology/b2-cco-base-sosa.ttl',
        'ontology/b2-cco-food.ttl',
        'abox/food-abox.ttl',
    ],
}
PROFILES_NATIVE = {
    'maritime': [
        'ontology/b2-cco-base.ttl',
        'ontology/b2-cco-maritime.ttl',
        'abox/maritime-abox.ttl',
    ],
    'food': [
        'ontology/b2-cco-base.ttl',
        'ontology/b2-cco-food.ttl',
        'abox/food-abox.ttl',
    ],
}

def load_kb(profile, variant):
    g = Graph()
    files = PROFILES_NATIVE[profile] if variant == 'native' else PROFILES_SOSA[profile]
    for f in files:
        g.parse(f, format='turtle')
    # Symmetric runtime metadata-strip (parity with DMFO runner —
    # rdfs:label/comment, dcterms:*, owl:Ontology headers etc. are
    # not load-bearing for any ACQ).
    if os.environ.get('B2_RUNTIME_STRIP', '1') != '0':
        from rdflib import RDF, RDFS, OWL, URIRef
        DOC = {RDFS.label, RDFS.comment, RDFS.isDefinedBy, RDFS.seeAlso,
               URIRef('http://www.w3.org/2004/02/skos/core#scopeNote'),
               URIRef('http://www.w3.org/2004/02/skos/core#closeMatch'),
               URIRef('http://www.w3.org/2004/02/skos/core#exactMatch')}
        DOC_PFX = ('http://purl.org/dc/terms/', 'http://purl.org/vocab/vann/')
        TBOX_TYPES = {OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty,
                      OWL.AnnotationProperty, OWL.FunctionalProperty,
                      OWL.InverseFunctionalProperty, OWL.SymmetricProperty,
                      OWL.TransitiveProperty, OWL.IrreflexiveProperty, RDFS.Class}
        # Strip owl:Ontology headers
        for s in list(g.subjects(RDF.type, OWL.Ontology)):
            for s2, p, o in list(g.triples((s, None, None))):
                g.remove((s2, p, o))
        # Strip doc triples on TBox subjects only (preserve ABox labels —
        # ICE-pattern carries semantic content on rdfs:label of instances).
        tbox_subjs = set()
        for t in TBOX_TYPES:
            tbox_subjs.update(g.subjects(RDF.type, t))
        for s in tbox_subjs:
            for s2, p, o in list(g.triples((s, None, None))):
                if p in DOC or any(str(p).startswith(pfx) for pfx in DOC_PFX):
                    g.remove((s2, p, o))
        # Strip dcterms/vann everywhere (pure metadata)
        for s, p, o in list(g):
            if any(str(p).startswith(pfx) for pfx in DOC_PFX):
                g.remove((s, p, o))
    # Closure strategy — parity with DMFO runner. B2_CLOSURE env var:
    #   owl-rl (default) | rdfs | rdfs+rl | none
    _closure = os.environ.get('B2_CLOSURE', 'owl-rl').lower()
    t0 = time.perf_counter()
    if _closure == 'rdfs':
        owlrl.DeductiveClosure(owlrl.RDFS_Semantics).expand(g)
    elif _closure == 'rdfs+rl':
        owlrl.DeductiveClosure(owlrl.RDFS_OWLRL_Semantics).expand(g)
    elif _closure == 'none':
        pass
    else:
        owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
    return g, time.perf_counter() - t0

def select_query(qkey, variant):
    """Return path to the right query file for the variant.
    Native variant uses queries-native/{qkey}-cco-native.rq when present,
    else falls back to queries/{qkey}-cco.rq."""
    if variant == 'native':
        native = QUERIES_NATIVE_DIR / f'{qkey}-cco-native.rq'
        if native.exists():
            return native
    return QUERIES_DIR / f'{qkey}-cco.rq'

def status_for(rows, classification):
    """Strict rubric, consistent with Paper §4.2 definition:
    'a CQ is fully answerable (✓) when a SPARQL query returns a
    non-empty, semantically complete result'. A semantically shifted
    answer (classification 'c' or 'b/c') violates the
    'semantically complete' clause, so it does not count as
    answerable — regardless of whether the SPARQL engine produces
    rows."""
    if classification == 'd':
        return ('✗', False)
    if rows == 0:
        return ('◑', False)
    if classification in ('c', 'b/c'):
        return ('◑', False)   # strict rubric: semantic shift = not fully answerable
    return ('✓', True)

def run_profile(profile, variant):
    print(f'\n=== Profile: {profile} | Variant: {variant} ===')
    g, closure_s = load_kb(profile, variant)
    print(f'  loaded + closure: {len(g)} triples ({closure_s*1000:.0f}ms)')

    qkeys = sorted(META_BASE.keys())
    overrides = VARIANT_OVERRIDES.get(variant, {})
    results = []
    class_times = {'I': [], 'II': [], 'III': [], 'IV': []}

    for qkey in qkeys:
        acq_id, cls, base_classification, base_diag = META_BASE[qkey]
        if base_classification is None:
            classification, diag_adr = overrides.get(qkey, ('?', '?'))
        else:
            classification, diag_adr = base_classification, base_diag

        q_path = select_query(qkey, variant)
        text = q_path.read_text()

        try:
            list(g.query(text))
            durs = []
            for _ in range(5):
                t0 = time.perf_counter()
                rows = list(g.query(text))
                durs.append(time.perf_counter() - t0)
            n = len(rows)
            median_ms = statistics.median(durs) * 1000
            class_times[cls].append(median_ms)
            status, answerable = status_for(n, classification)
            results.append({
                'id': acq_id, 'class': cls,
                'cco_query': str(q_path.relative_to(REPO_ROOT)) if str(q_path).startswith(str(REPO_ROOT)) else str(q_path),
                'classification': classification, 'diagnosis_adr': diag_adr,
                'result_rows': n, 'status': status, 'answerable': answerable,
                'median_ms': round(median_ms, 3),
            })
            print(f'  {acq_id:11s} cls={cls} {status} rows={n:3d}  median={median_ms:6.2f}ms  ({classification})')
        except Exception as exc:
            print(f'  {acq_id:11s} ERROR: {exc}')
            results.append({
                'id': acq_id, 'class': cls,
                'classification': classification, 'diagnosis_adr': diag_adr,
                'result_rows': 0, 'status': '✗', 'answerable': False,
                'error': str(exc),
            })

    cls_perf = {c: {'n': len(ts), 'median_ms': round(statistics.median(ts), 3)}
                for c, ts in class_times.items() if ts}
    score = {c: {'total': 0, 'answerable': 0} for c in 'I II III IV'.split()}
    for r in results:
        score[r['class']]['total'] += 1
        if r['answerable']:
            score[r['class']]['answerable'] += 1
    total = sum(c['total'] for c in score.values())
    ans   = sum(c['answerable'] for c in score.values())

    summary = {
        'profile': profile, 'variant': variant, 'kb_triples': len(g),
        'closure_seconds': round(closure_s, 3),
        'score': f'{ans}/{total}', 'by_class': score,
        'classification_breakdown': {
            c: sum(1 for r in results if r['classification'].startswith(c))
            for c in 'a b c d b/c'.split()
        },
        'per_class_perf': cls_perf,
    }
    return {'summary': summary, 'acqs': results}

profiles = ['maritime', 'food'] if TARGET == 'all' else [TARGET]
variants = ['sosa', 'native'] if VARIANT == 'both' else [VARIANT]

overall = {}
for v in variants:
    overall[v] = {}
    for p in profiles:
        overall[v][p] = run_profile(p, v)
        suffix = '' if v == 'sosa' else '-native'
        out = ROOT / 'results' / f'b2-cco-results-{p}{suffix}.json'
        out.write_text(json.dumps(overall[v][p], indent=2))
        print(f'  → {out.relative_to(ROOT)}')

# Combined per variant (any-profile-answers)
for v in variants:
    if len(profiles) > 1:
        combined = {c: {'total': 0, 'answerable': 0} for c in 'I II III IV'.split()}
        by_id = {}
        for p in profiles:
            for r in overall[v][p]['acqs']:
                by_id.setdefault(r['id'], {'class': r['class'], 'profiles': {}})
                by_id[r['id']]['profiles'][p] = r['answerable']
        for aid, info in by_id.items():
            combined[info['class']]['total'] += 1
            if any(info['profiles'].values()):
                combined[info['class']]['answerable'] += 1
        total = sum(c['total'] for c in combined.values())
        ans   = sum(c['answerable'] for c in combined.values())
        print(f'\n=== Combined (any profile answers) — variant: {v} ===')
        print(f'  Total: {ans}/{total}  ' + '  '.join(
            f'{c}={combined[c]["answerable"]}/{combined[c]["total"]}'
            for c in 'I II III IV'.split()))
        overall[v]['combined'] = {'by_class': combined, 'score': f'{ans}/{total}'}

# Aggregate across variants
agg_path = ROOT / 'results' / 'b2-cco-results.json'
agg_path.write_text(json.dumps(overall, indent=2))

# Comparison CSV per profile + variant, against DMFO baseline
import csv
for v in variants:
    for p in profiles:
        dmfo_path = Path('..') / 'validation' / 'results' / f'queries_{p}.json'
        if not dmfo_path.exists():
            continue
        dmfo = json.load(open(dmfo_path))
        dmfo_by_id = {r['id']: r for r in dmfo['acqs']}
        suffix = '' if v == 'sosa' else '-native'
        out = ROOT / 'results' / f'comparison-dmfo-vs-b2cco-{p}{suffix}.csv'
        with open(out, 'w') as f:
            w = csv.writer(f)
            w.writerow(['ACQ', 'class', 'DMFO_status', 'DMFO_rows',
                        'B2CCO_status', 'B2CCO_rows', 'classification', 'diagnosis_adr'])
            for r in overall[v][p]['acqs']:
                d = dmfo_by_id.get(r['id'], {})
                dmfo_status = '✓' if d.get('answerable') else ('◑' if d.get('result_rows', 0) > 0 else '✗')
                w.writerow([r['id'], r['class'], dmfo_status, d.get('result_rows', 0),
                            r['status'], r['result_rows'], r['classification'], r['diagnosis_adr']])
        print(f'  → {out.relative_to(ROOT)}')

# Compact perf JSON across all variants + profiles
perf = {}
for v in variants:
    perf[v] = {p: overall[v][p]['summary']['per_class_perf'] for p in profiles}
(ROOT / 'results' / 'b2-cco-perf.json').write_text(json.dumps({
    'per_variant_per_profile_per_class_median_ms': perf,
    'closure_seconds': {v: {p: overall[v][p]['summary']['closure_seconds']
                             for p in profiles} for v in variants},
    'kb_triples_after_closure': {v: {p: overall[v][p]['summary']['kb_triples']
                                       for p in profiles} for v in variants},
}, indent=2))

print()
for v in variants:
    print(f'=== Variant {v} ===')
    for p in profiles:
        s = overall[v][p]['summary']
        bc = s['by_class']
        print(f'  {p:9s} score: {s["score"]}  '
              f'I={bc["I"]["answerable"]}/{bc["I"]["total"]}  '
              f'II={bc["II"]["answerable"]}/{bc["II"]["total"]}  '
              f'III={bc["III"]["answerable"]}/{bc["III"]["total"]}  '
              f'IV={bc["IV"]["answerable"]}/{bc["IV"]["total"]}')
    if 'combined' in overall[v]:
        print(f'  combined: {overall[v]["combined"]["score"]}')
PY
