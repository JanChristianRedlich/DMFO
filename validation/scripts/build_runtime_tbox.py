#!/usr/bin/env python3
"""Build a runtime-optimised DMFO TBox: single file, metadata-
stripped, ready for fast closure expansion. Equivalent ABox-side
semantics to the modular sources; documentation triples (rdfs:label,
rdfs:comment, dcterms:*, vann:*, skos:*, owl:Ontology metadata) are
removed because they don't participate in any ACQ query path.

Output: ontology/dmfo-runtime.ttl
"""
from __future__ import annotations
from pathlib import Path
from rdflib import Graph, RDF, RDFS, OWL, URIRef, Namespace, Literal

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / 'ontology' / 'dmfo-runtime.ttl'

# Documentation predicates that are NOT load-bearing for any ACQ.
DOC_PREDICATES = {
    URIRef('http://www.w3.org/2000/01/rdf-schema#label'),
    URIRef('http://www.w3.org/2000/01/rdf-schema#comment'),
    URIRef('http://www.w3.org/2000/01/rdf-schema#isDefinedBy'),
    URIRef('http://www.w3.org/2000/01/rdf-schema#seeAlso'),
    URIRef('http://www.w3.org/2004/02/skos/core#scopeNote'),
    URIRef('http://www.w3.org/2004/02/skos/core#closeMatch'),
    URIRef('http://www.w3.org/2004/02/skos/core#exactMatch'),
}
# All dcterms:* and vann:* predicates are documentation.
DOC_PREFIXES = (
    'http://purl.org/dc/terms/',
    'http://purl.org/vocab/vann/',
)

def is_doc(p):
    if p in DOC_PREDICATES: return True
    return any(str(p).startswith(pfx) for pfx in DOC_PREFIXES)

g = Graph()
for f in sorted((REPO/'ontology').glob('dmfo-*.ttl')):
    if f.name in ('dmfo-full.ttl', 'dmfo-runtime.ttl'):
        continue
    g.parse(str(f), format='turtle')
print(f'  loaded {len(g)} triples from {len([f for f in (REPO/"ontology").glob("dmfo-*.ttl") if f.name not in ("dmfo-full.ttl","dmfo-runtime.ttl")])} module files')

# (1) Strip owl:Ontology metadata (header triples)
onto_iris = set(g.subjects(RDF.type, OWL.Ontology))
removed_header = 0
for s in onto_iris:
    for s2, p, o in list(g.triples((s, None, None))):
        g.remove((s2, p, o))
        removed_header += 1
print(f'  stripped {removed_header} owl:Ontology header triples '
      f'({len(onto_iris)} ontology declarations)')

# (2) Strip documentation predicates
removed_doc = 0
for s, p, o in list(g):
    if is_doc(p):
        g.remove((s, p, o))
        removed_doc += 1
print(f'  stripped {removed_doc} documentation triples (rdfs:label/comment/isDefinedBy, dcterms, vann, skos)')

# (3) Add a single minimal owl:Ontology header so reasoners recognise it
DMFO = URIRef('https://w3id.org/dmfo/runtime')
g.add((DMFO, RDF.type, OWL.Ontology))

# Bind clean prefixes for human-readable Turtle
for prefix, uri in [
    ('dmfo', 'https://w3id.org/dmfo#'),
    ('prov', 'http://www.w3.org/ns/prov#'),
    ('sosa', 'http://www.w3.org/ns/sosa/'),
    ('dul',  'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#'),
    ('geo',  'http://www.opengis.net/ont/geosparql#'),
    ('time', 'http://www.w3.org/2006/time#'),
]:
    g.namespace_manager.bind(prefix, uri, replace=True, override=True)

g.serialize(destination=str(OUT), format='turtle')
print(f'\n  → {OUT.relative_to(REPO)}: {len(g)} triples (compared to ~{167-1} in modular source)')
