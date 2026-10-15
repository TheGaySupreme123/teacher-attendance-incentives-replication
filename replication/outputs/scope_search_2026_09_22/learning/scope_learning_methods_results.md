# Frozen three-outcome learning-family results

The family was fixed in `scope_family_plan.md` before estimation. It broadens Direction 0.2 by asking whether continuous baseline teacher-score moderation differs across the existing math, language, and total learning outcomes. This is a scope analysis, not a novelty claim; paper overlap is assessed separately.

The strict observed-only sample is `R == 1` from `run_direction02_attrition.prepare_data`: N=1625 observation rows, G=101 schools, and 1610 unique school-child keys. All outcomes use the same treatment, teacher-score, interaction, and three baseline controls. School-clustered inference uses two-sided t(G-1) p-values and 95% intervals.

## Individual domain interactions

- `primary` / **math**: interaction 0.209190, SE 0.098809, raw p=0.0367, Holm p=0.1102, 95% CI 0.013156 to 0.405224.
- `primary` / **language**: interaction 0.084897, SE 0.071647, raw p=0.2388, Holm p=0.2388, 95% CI -0.057248 to 0.227042.
- `primary` / **total**: interaction 0.132133, SE 0.071251, raw p=0.0666, Holm p=0.1332, 95% CI -0.009228 to 0.273494.
- `geographic_block_fixed_effects` / **math**: interaction 0.135692, SE 0.095327, raw p=0.1577, Holm p=0.4732, 95% CI -0.053434 to 0.324819.
- `geographic_block_fixed_effects` / **language**: interaction 0.058633, SE 0.061483, raw p=0.3426, Holm p=0.4732, 95% CI -0.063348 to 0.180614.
- `geographic_block_fixed_effects` / **total**: interaction 0.087200, SE 0.065357, raw p=0.1852, Holm p=0.4732, 95% CI -0.042465 to 0.216866.

Holm adjustment is applied separately within the primary three-outcome family and within the corresponding geographic-block family. All three outcomes are shown regardless of significance.

## Joint math/language tests and domain difference

- `primary` joint math/language interaction test: Wald F=2.471624, F(2,100), p=0.0896; chi-square(2) p=0.0844. Same-school math-language residual covariance is 0.00542207 (correlation 0.7659).
- `primary` math-minus-language interaction: 0.124293, SE 0.063657, t(100)=1.952529, p=0.0537, 95% CI -0.002002 to 0.250587.
- `geographic_block_fixed_effects` joint math/language interaction test: Wald F=1.023341, F(2,100), p=0.3631; chi-square(2) p=0.3594. Same-school math-language residual covariance is 0.00432456 (correlation 0.7379).
- `geographic_block_fixed_effects` math-minus-language interaction: 0.077059, SE 0.064949, t(100)=1.186463, p=0.2383, 95% CI -0.051797 to 0.205915.

No score cutoff, school exclusion, subject-specific search beyond the fixed three-outcome family, outcome re-selection, or additional model was run. The geographic-block family is a corresponding pre-defined check with blocks 2--5 and block 1 as the base.

Outputs are `scope_learning_coefficients.csv`, `scope_learning_interactions.csv`, `scope_learning_joint_tests.csv`, `scope_learning_metadata.json`, and this report. Hashes and the frozen family plan are recorded in the metadata and plan file.
