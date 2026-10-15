const significanceResults = [
  {
    "label": "Main observed-test model",
    "model": "primary",
    "stage": "post_observed_only",
    "estimate": 0.13213278149563928,
    "low": -0.009228136581792584,
    "high": 0.2734936995730711,
    "p": 0.06662062087250628,
    "n": 1625
  },
  {
    "label": "Allow effects to vary with child preparation",
    "model": "child_baseline_interactions",
    "stage": "post_observed_only",
    "estimate": 0.12940336081849355,
    "low": -0.013248232296341977,
    "high": 0.27205495393332907,
    "p": 0.07492082503729076,
    "n": 1625
  },
  {
    "label": "Add geographic controls",
    "model": "geographic_block_fixed_effects",
    "stage": "post_observed_only",
    "estimate": 0.08720034998793379,
    "low": -0.04246525395337823,
    "high": 0.2168659539292458,
    "p": 0.18516074046363998,
    "n": 1625
  },
  {
    "label": "Child preparation + geography",
    "model": "child_baseline_interactions_plus_geographic_block_fixed_effects",
    "stage": "post_observed_only",
    "estimate": 0.08652077655382717,
    "low": -0.04639081986462504,
    "high": 0.21943237297227938,
    "p": 0.19950905774407646,
    "n": 1625
  },
  {
    "label": "Give each school equal total weight",
    "model": "equal_school_weight_primary",
    "stage": "post_observed_only",
    "estimate": 0.12422492734960718,
    "low": -0.01462701129144113,
    "high": 0.2630768659906555,
    "p": 0.07894470554546647,
    "n": 1625
  },
  {
    "label": "Remove child controls (diagnostic)",
    "model": "no_baseline_controls_same_sample",
    "stage": "post_observed_only",
    "estimate": 0.1533750260995136,
    "low": -0.04867942706885309,
    "high": 0.35542947926788027,
    "p": 0.13522247933033787,
    "n": 1625
  },
  {
    "label": "Exclude all repeated child-ID keys",
    "model": "data_quality_duplicate_key_exclusion",
    "stage": "post_observed_only",
    "estimate": 0.13011022835885583,
    "low": -0.00918942105879636,
    "high": 0.26940987777650804,
    "p": 0.06681785790240027,
    "n": 1595
  }
];
