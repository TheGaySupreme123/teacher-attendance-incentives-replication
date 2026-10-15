# Raw-data learning-extension audit

This is a reproducibility audit, not paper prose. The script reconstructs the source Table 9 A/B midline and post-test models from raw `.dta` files before estimating the single proposed moderator candidate.

## Replication gate

Coefficient, clustered SE, and observation-count comparisons against the shipped Table 9 A/B CSVs: **PASS** (16/16 specifications match at the printed precision). All R-squared differences are within 0.01; the largest is 0.0050.

The shipped `Temp` files were not used to construct the estimates. They are intermediate artifacts only. The source transforms were followed: post-test sentinel/missing values are zeroed before totals, baseline/midline sentinels are set missing, the three source corrections are applied, written scores are divided by five where the source program does so, the source stayer rule is applied, and scores are normalized using the supplied `Endline/normalization.dta` reference and the control moments specified in the source programs.

If this gate fails, the interaction results below are not interpretable as a validated extension until the discrepancy is resolved.

## Primary exploratory candidate

Candidate: post-test total score interacted with continuous baseline teacher test score, standardized using the school-level teacher-score mean and standard deviation from the 107 active score-observed schools. Inference is clustered by school.

Post-test controlled interaction estimate: **0.129 SD per teacher-score SD** (SE 0.071, 95% CI -0.012 to 0.270, p=0.073, N=1646, schools=103). The approximate 80%-power MDE for this interaction is 0.201 SD per teacher-score SD.

The midline version is secondary: 0.051 (SE 0.060, 95% CI -0.068 to 0.171, p=0.395, N=1767, schools=107); its approximate 80%-power MDE is 0.171.

The unadjusted and Table 9 A-controlled specifications are both reported in `learning_model_results.csv`. The controlled model adds the original total-score baseline controls (`pre_total_v`, `pre_total_w`, and `pre_writ`) to the treatment, score, and treatment-by-score terms. No subject-specific interaction search was run.

## Sample and missing-score audit

Teacher-score item sums agree with `BaselineChar.dta` for 109 nonmissing crosswalk records; maximum absolute difference is 0.

The full Table 9 A/B samples and the teacher-score-complete samples are shown by treatment in `learning_sample_counts.csv`. The score-complete restriction changes both student counts and school counts; the post-test interaction therefore must be presented alongside the full-sample replication.

`learning_attrition_balance.csv` reports baseline rows retained in the midline/post analytic samples by treatment and teacher-score tercile. These are descriptive selection checks, not proof that attrition is ignorable.

## Interpretation limits

Teacher score is pre-treatment but not randomized, and it is measured at the school level in a one-teacher school. It may also proxy baseline pupil composition or other school characteristics. The interaction describes treatment-effect variation by an observed moderator; it does not identify a causal effect of teacher quality itself.

The candidate was selected after earlier exploratory work in this repository. It therefore cannot be described as preregistered. The reported p-values are exploratory evidence conditional on that selection history, not confirmatory strength claims. The small number of school clusters relative to the student observations, teacher-score missingness, and test attrition limit precision and external validity.

## Reproduction

Run `python3 scripts/audit_learning_extension.py` from the repository root. Raw-input and reference-file SHA-256 hashes, Python/package versions, the command, and the commit are recorded in `learning_raw_input_hashes.csv` and `learning_run_metadata.json`.
