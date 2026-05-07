#!/usr/bin/env bash
# =============================================================
# Fetch the imported W3C / OGC vocabularies into ontology/imports/
# at the versions documented in Paper Appendix A. Idempotent.
# =============================================================
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../ontology/imports" && pwd)"
cd "$DIR"

fetch() {
    local url="$1"; local out="$2"
    if [ -f "$out" ]; then
        echo "  skip   $out (already present)"
    else
        echo "  fetch  $out"
        curl -fsSL -H "Accept: text/turtle, application/rdf+xml;q=0.9" "$url" -o "$out"
    fi
}

fetch "https://www.w3.org/ns/prov-o-20130430.ttl"          prov-o.ttl
fetch "https://www.w3.org/ns/sosa/"                         sosa.ttl
fetch "https://www.w3.org/ns/ssn/"                          ssn.ttl
fetch "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl" dul.owl
fetch "http://www.opengis.net/ont/geosparql"                geosparql.ttl
fetch "https://www.w3.org/2006/time"                        time.ttl

echo "All imports cached in $DIR"
