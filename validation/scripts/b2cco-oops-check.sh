#!/usr/bin/env bash
# OOPS! pitfall scan against the merged B2-CCO maritime TBox.
# Calls the public OOPS! service at http://oops.linkeddata.es/rest
# Network access required.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ROOT="$REPO_ROOT/validation/b2-cco"
cd "$ROOT"
mkdir -p results

# Build merged TBox (no ABox) for OOPS. Output as RDF/XML.
python3 <<'PY'
from rdflib import Graph
g = Graph()
for f in ['ontology/b2-cco-base.ttl', 'ontology/b2-cco-base-sosa.ttl',
          'ontology/b2-cco-maritime.ttl']:
    g.parse(f, format='turtle')
g.serialize(destination='results/b2-cco-merged-for-oops.owl', format='application/rdf+xml')
print(f'  merged TBox: {len(g)} triples → results/b2-cco-merged-for-oops.owl')
PY

# Build OOPS request envelope
TBOX_XML=$(cat results/b2-cco-merged-for-oops.owl | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')
PAYLOAD=$(cat <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<OOPSRequest>
  <OntologyURI></OntologyURI>
  <OntologyContent>${TBOX_XML}</OntologyContent>
  <Pitfalls></Pitfalls>
  <OutputFormat>RDF/XML</OutputFormat>
</OOPSRequest>
EOF
)

if curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://oops.linkeddata.es/rest 2>/dev/null | grep -qE '^(200|405)$'; then
    echo "  OOPS! service reachable, submitting…"
    echo "$PAYLOAD" | curl -sS -X POST -H 'Content-Type: application/xml' \
        --data-binary @- http://oops.linkeddata.es/rest \
        > results/oops-report.xml || {
            echo "  OOPS! request failed (network/server)"
            echo '{"status": "service-unreachable", "fallback": "skipped"}' > results/oops-report.json
            exit 0
        }
    echo "  → results/oops-report.xml"
    # Extract pitfall counts (best-effort XML parse)
    python3 - <<'PY'
import json, re
try:
    txt = open('results/oops-report.xml').read()
    pitfalls = re.findall(r'<oops:hasName[^>]*>([^<]+)</oops:hasName>', txt)
    importance = re.findall(r'<oops:hasImportanceLevel[^>]*>([^<]+)</oops:hasImportanceLevel>', txt)
    n_critical = sum(1 for x in importance if x.lower() == 'critical')
    n_important = sum(1 for x in importance if x.lower() == 'important')
    n_minor = sum(1 for x in importance if x.lower() == 'minor')
    out = {
        'pitfalls_total': len(pitfalls),
        'pitfalls_critical': n_critical,
        'pitfalls_important': n_important,
        'pitfalls_minor': n_minor,
        'pitfall_names': pitfalls[:30],
    }
    json.dump(out, open('results/oops-report.json', 'w'), indent=2)
    print(f'  pitfalls: total={len(pitfalls)} critical={n_critical} important={n_important} minor={n_minor}')
except Exception as exc:
    print(f'  parse failed: {exc}')
    json.dump({'status': 'parse-failed', 'error': str(exc)},
              open('results/oops-report.json', 'w'))
PY
else
    echo "  OOPS! service unreachable — recording stub"
    cat > results/oops-report.json <<EOF
{
  "status": "service-unreachable",
  "note": "Run again when http://oops.linkeddata.es/rest is reachable. The merged TBox is in results/b2-cco-merged-for-oops.owl."
}
EOF
fi
