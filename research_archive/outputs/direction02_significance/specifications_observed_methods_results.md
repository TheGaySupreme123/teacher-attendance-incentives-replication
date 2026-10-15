# Direction 0.2 observed-only follow-up

This is a data-quality follow-up of the fixed Direction 0.2 specification set. It uses the same reconstructed post-test total outcome, teacher-score moderator, controls, seven post-test model specifications, and fixed p25/p75 contrasts. The specification set was fixed for this follow-up after prior exploratory review; it was not preregistered.

The observed-only indicator is `R == 1` from `run_direction02_attrition.prepare_data`: the reconstructed source post verbal total is observed and the normalized post total exists. This excludes the 21 source stayer rows that would otherwise receive a zero through the source missing-value fill. The observed-only sample has N=1625 rows, G=101 schools, and 1610 unique school-child keys.

Primary interaction: **0.13213278**, SE **0.07125149**, p=0.06662, 95% CI -0.00922814 to 0.27349370.

The p25, p75, and p75-minus-p25 results are formal contrasts from this same primary fit; no new model or outcome is estimated.
At p25 (raw 27.00, z -0.694023), the treatment effect is 0.01743044, SE 0.10631874, p=0.87011.
At p75 (raw 41.75, z 0.715683), the treatment effect is 0.20369879, SE 0.09933839, p=0.04293.
The p75-minus-p25 contrast is 0.18626835, SE 0.10044364, p=0.06662, 95% CI -0.01300896 to 0.38554567; its p equals the interaction p because the treatment main effect cancels.

Interaction results for all seven fixed post-test specifications:
- `primary`: 0.13213278, SE 0.07125149, p=0.06662, 95% CI -0.00922814 to 0.27349370, N=1625, G=101.
- `child_baseline_interactions`: 0.12940336, SE 0.07190204, p=0.07492, 95% CI -0.01324823 to 0.27205495, N=1625, G=101.
- `geographic_block_fixed_effects`: 0.08720035, SE 0.06535659, p=0.18516, 95% CI -0.04246525 to 0.21686595, N=1625, G=101.
- `child_baseline_interactions_plus_geographic_block_fixed_effects`: 0.08652078, SE 0.06699269, p=0.19951, 95% CI -0.04639082 to 0.21943237, N=1625, G=101.
- `equal_school_weight_primary`: 0.12422493, SE 0.06998686, p=0.07894, 95% CI -0.01462701 to 0.26307687, N=1625, G=101.
- `no_baseline_controls_same_sample`: 0.15337503, SE 0.10184342, p=0.13522, 95% CI -0.04867943 to 0.35542948, N=1625, G=101.
- `data_quality_duplicate_key_exclusion`: 0.13011023, SE 0.07021252, p=0.06682, 95% CI -0.00918942 to 0.26940988, N=1595, G=101.

The duplicate-key sensitivity drops all 30 rows belonging to 15 repeated school-child keys, yielding N=1595; no individual key was selected.

The source-compatible N=1,646 result is retained as the replication reference for alignment with the original source program. Under the observed-only constraint, the N=1,625 result is the substantive Direction 0.2 result emphasized here; it avoids treating source-filled zeros as observed outcomes. This observed-only constraint was a data-quality amendment discovered after the initial plan and is documented in this follow-up.

Outputs: `specifications_observed_coefficients.csv`, `specifications_observed_marginal_effects.csv`, `specifications_observed_metadata.json`, and `specifications_observed_input_hashes.csv`.
