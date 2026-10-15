# Focused validation

- Reused the independently audited original Table 10 raw reconstruction. Its 2,197 child outcome records match the shipped reference; two conflicting baseline-writing IDs are excluded from the extension (2,195 children/111 schools).
- Root independently recalculated the main interaction directly from raw reconstructed group counts: control nonwriters 290/858, treatment nonwriters 365/940, control writers 89/201, treatment writers 138/196. The resulting difference of treatment effects is 0.21099302865623243, matching the regression within 1e-10.
- School-level wild-bootstrap vectors for departure and residual departure each pass first-five-draw direct-refit validation. Every fixed-family result and unsuccessful alternative is retained.
- Independent paper/code reviewer confirmed no baseline-writing × Table 10 departure interaction in the article, appendix or original Table 10 program. See novelty.md.
- Independent raw measurement audit confirmed the numeric/string transfer-reason mismatch; semantic recoding changes 13 destinations but no total-departure labels in the 2,197-child reference cohort. See measurement_audit.md.
- No raw data files or the user's existing seminar deck were modified. No external data or fabricated observations were added. Original operational attendance coding maps undocumented negative codes to absence; this is disclosed and audited with unknown-status bounds and a separately reported observed-status sensitivity.
- Site uses aggregate results only. Desktop table and navigation rendering checked; download files correspond to the saved local aggregate output files. Statistical p-values are exploratory and school-clustered, not adjusted for the entire historical search.

- The two independent raw-attendance flag reconstructions agree for all 2,197 children. Exactly 113 ambiguous departures are excluded in the fixed sensitivity; its school wild-bootstrap direct-refit validation passes. Both original and sensitivity results are retained, with selection limitations stated.
- Updated site checked at 1440px and390px; no unintended horizontal document overflow at390px. Navigation between learning and departure results works through the same exposed page controls.
