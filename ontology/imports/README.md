# Imported Vocabularies

DMFO imports five W3C / OGC vocabularies (Paper §2):

| Vocabulary | Canonical IRI | Local file | Version |
|---|---|---|---|
| PROV-O | `http://www.w3.org/ns/prov-o` | `prov-o.ttl` | 2013-04-30 |
| SOSA | `http://www.w3.org/ns/sosa/` | `sosa.ttl` | 2017-10 |
| SSN | `http://www.w3.org/ns/ssn/` | `ssn.ttl` | 2017-10 |
| DUL/DnS | `http://www.ontologydesignpatterns.org/ont/dul/DUL.owl` | `dul.owl` | 3.36 |
| GeoSPARQL | `http://www.opengis.net/ont/geosparql` | `geosparql.ttl` | 1.1 |
| OWL-Time | `http://www.w3.org/2006/time` | `time.ttl` | 2022-11-15 |

The local cache is populated by `validation/scripts/fetch_imports.sh`. The
Protégé catalog (`../catalog-v001.xml`) maps the canonical IRIs to these
local files so that ontology editors and reasoners do not need network
access.

The DMFO repository does not redistribute these vocabularies; the fetch
script downloads them from their canonical sources at the versions
documented in Paper Appendix A. The conservativity claims in Paper
Theorem 2 are bounded to the specific versions listed above; replacing an
import with a different version may introduce additional axioms that
re-trigger the locality check (run `validation/scripts/locality_check.py`
after any version change).
