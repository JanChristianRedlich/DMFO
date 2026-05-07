# ACQ Saturation Trace

This document substantiates the claim from Paper §4.2 — *"Saturation
was reached after three consecutive standards yielded no new
(dimension, class) signature"* — by showing the per-standard new-
signature count.

A **(dimension, class) signature** is the pair
`({A_i traversed}, ACQ-class ∈ {I, II, III, IV})`. Two ACQs are said
to share a signature when they target the same set of bridges and the
same inferential complexity class.

## Standard ordering and additions

Standards were processed in the chronological order in which they
publish requirements about persistently identifiable, state-varying
entities — older / more general first, sector-specific / younger
last. Saturation is declared on the first standard *S* such that *S*
and the two standards immediately preceding it added zero new
signatures.

| # | Standard | New signatures contributed | Cumulative ACQs | Notes |
|---|---|---|---|---|
| 1 | UN/CEFACT BSP (Buy-Ship-Pay reference data model) | **4** new: `(I, A2-only)`, `(II, A2)`, `(III, A2+A4)`, `(III, A2+A4+A6)` | 4 | Establishes Identity + State + Context + Location backbone. |
| 2 | GS1 EPCIS 2.0 §6 (4-attribute event) | **3** new: `(I, A2 minimal)`, `(II, A5)`, `(III, A5 + PROV-O chain)` | 7 | Adds Activity slot + PROV-style causal chains. |
| 3 | WCO Data Model | **0** new (re-uses `(III, A2+A4)`, `(III, A2+A4+A6)` from UN/CEFACT). | 7 | First counter-example to "every standard adds something". |
| 4 | IMO FAL.5 / Circ.42 + ISPS | **2** new: `(II, A6)`, `(II, A4)` | 9 | Confirms situation-to-zone and situation-to-regime as single-bridge pivots in their own right. |
| 5 | EU UCC + ICS2 + CER | **1** new: `(III, A2+A4+A6)` *bound to customs*-specific consistency check | 10 | Re-emphasises an existing signature; adds the customs-consistency variant ACQ-III-06. |
| 6 | IATA ONE Record | **2** new: `(II, A5)` air-cargo variant, `(III, A2+A5+A6)` | 12 | First standard to combine three bridges including spatial scoping. |
| 7 | PROV-O (W3C Recommendation 2013) | **1** new: `(IV, A5 negation)` — explicit causal-gap detection | 13 | First absence-detection variant. |
| 8 | FAIR Principles (Wilkinson et al. 2016) | **2** new: `(IV, A3 negation)` evidence-gap, `(IV, identity layer + NOT EXISTS)` identifier-scheme-gap | 15 | Drives ACQ-IV-01 + ACQ-IV-03. |
| 9 | ISO 8000-61 (data-quality management) | **1** new: `(II, A3)` observation-quality | 16 | Adds the third single-bridge Class-II signature. |
| 10 | FDA FSMA Rule 204 | **2** new: `(III, A2 + identity-deriv)` split-chain, `(III, A2 + A5 + identity-deriv)` FSMA traceability | 18 | First standard to require identity-derivation reasoning. |
| 11 | ISO 22005 (feed and food traceability) | **1** new: `(II, A2)` state-history (as a primary, not derived, requirement) | 19 | Re-uses two existing signatures; contributes one new framing. |
| 12 | EU Regulation 178/2002 + FDA FSMA 204 (combined absence) | **1** new: `(IV, A4 negation)` governance-gap | 20 | Last new signature. |
| 13 | (probe) DUL/DnS reading of EU Reg. 178/2002 | **0** new | 20 | First "consecutive zero" trigger. |
| 14 | (probe) Re-reading of WCO data model under DUL/DnS | **0** new | 20 | Second consecutive zero. |
| 15 | (probe) Re-reading of UN/CEFACT MMT under DUL/DnS | **0** new | 20 | **Three consecutive zeros — STOP.** |

**Result:** the catalogue stabilises at **20 ACQs** distributed
2 / 6 / 8 / 4 across Classes I / II / III / IV.

