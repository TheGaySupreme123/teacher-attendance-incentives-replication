# Raw attendance-sentinel audit

The main result remains the original Table7/Table10 operational `drop` endpoint. The source program recodes negative attendance values and code 22 to zero before defining `drop`; the data package provides no value-label codebook explaining whether those values are absences or unresolved/missing observations.

## Child-level audit

The audit rebuilds the raw roster pipeline and preserves raw attendance before the original recode. It audits the 2,195 children with consensus baseline-writing status. A child is classified as an ambiguous departure when the original operational `source_drop=1` and at least one of the selected open-check attendance values is a negative sentinel or 22. Children with a raw presence value of 1 are kept when they are not operationally classified as `drop=1`; no outcome is filled.

The ambiguous departure counts are: control nonwriters 28, control writers 11, treated nonwriters 71, and treated writers 3; total 113. The all-selected-code ambiguous subset has 21 children; these are concentrated in the short-history control school 2491 as shown in `sentinel_all_ambiguous_children.csv`.

## Fixed complete-observed-outcome sensitivity

The operational original interaction is 0.211 (SE 0.072, p=0.0040; 95% CI [0.069, 0.353]). Excluding all 113 ambiguous operational departure classifications, while retaining known nondeparture children, gives 0.266 (SE 0.074, p=0.0005; 95% CI [0.120, 0.412]) in 2082 children and 111 schools. The fixed complete-observed-outcome sensitivity wild-bootstrap p-value is 0.0011 (9999 draws, seed 20260922; validation=True).

This exclusion is a selection sensitivity, not the main estimate: sentinel meanings are undocumented and the ambiguous children are not missing at random by treatment (or necessarily by baseline writing). The seminar result should retain the original operational endpoint for comparability and display this sensitivity as a measurement limitation.

Re-run with:

```bash
python3 scripts/audit_transition_sentinels.py
```
