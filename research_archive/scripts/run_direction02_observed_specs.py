#!/usr/bin/env python3
"""Observed-outcome follow-up for the fixed Direction 0.2 specifications.

The source-compatible Direction 0.2 estimates retain 21 rows whose post
verbal total is absent and later becomes zero through the source program's
fill operation.  This follow-up restricts the same post-test design to
``R == 1`` from ``run_direction02_attrition.prepare_data``: the outcome is
observed in the reconstructed raw source, with no synthetic zero outcome.

The seven post-test specifications are the fixed follow-up set: primary,
child-baseline interactions, geographic block fixed effects, both together,
equal-school weights, no-baseline-controls diagnostic, and the all-duplicate-
key data-quality sensitivity.  No new outcome, cutoff, or model is added.
The p25, p75, and p75-minus-p25 effects are formal contrasts from the same
observed-only primary fit.
"""

from __future__ import annotations

import importlib.util
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "direction02_significance"
ATTRITION_SOURCE = ROOT / "scripts" / "run_direction02_attrition.py"
SPECS_SOURCE = ROOT / "scripts" / "run_direction02_specs.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    attrition = load_module("direction02_attrition", ATTRITION_SOURCE)
    specs = load_module("direction02_specs", SPECS_SOURCE)

    all_scored, source_post, scores = attrition.prepare_data()
    observed = all_scored.loc[all_scored["R"].eq(1)].copy()
    # The attrition helper maps only the total outcome into all_scored.  Map
    # the two pre-defined component outcomes by source row_id so duplicate
    # school-child keys cannot multiply or misassign observations.
    source_by_row = source_post.set_index("row_id")
    for domain in ["math", "lang", "total"]:
        observed[f"z_add_post_{domain}"] = observed["row_id"].map(
            source_by_row[f"z_add_post_{domain}"]
        )
    observed["z_add_post_total"] = observed["z_add_post_total"].fillna(
        observed["outcome_z"]
    )
    observed["teacher_score_z"] = observed["score_z"]
    observed["treat_score_z"] = observed["treat"] * observed["teacher_score_z"]
    observed["treat_pre_total_v"] = observed["treat"] * observed["pre_total_v"]
    observed["treat_pre_total_w"] = observed["treat"] * observed["pre_total_w"]
    observed["treat_pre_writ"] = observed["treat"] * observed["pre_writ"]
    observed = specs.add_geographic_block_dummies(observed)

    if len(observed) != 1625 or observed["schid"].nunique() != 101:
        raise AssertionError(
            f"Unexpected observed-only sample: N={len(observed)}, G={observed['schid'].nunique()}"
        )

    primary_terms = [
        "treat",
        "teacher_score_z",
        "treat_score_z",
        "pre_total_v",
        "pre_total_w",
        "pre_writ",
    ]
    child_terms = ["treat_pre_total_v", "treat_pre_total_w", "treat_pre_writ"]
    block_terms = ["block_2", "block_3", "block_4", "block_5"]
    duplicate_count = observed.groupby(["schid", "childno"])["schid"].transform("size")
    observed["school_child_key_count"] = duplicate_count
    duplicate_free = observed.loc[duplicate_count.eq(1)].copy()
    duplicate_keys = int(
        observed.loc[duplicate_count.gt(1), ["schid", "childno"]]
        .drop_duplicates()
        .shape[0]
    )
    duplicate_rows = int(len(observed) - len(duplicate_free))

    specs_to_run = [
        (
            "primary",
            observed,
            primary_terms,
            None,
            "Observed-only post-test primary estimand; fixed R=1 sample.",
        ),
        (
            "child_baseline_interactions",
            observed,
            primary_terms + child_terms,
            None,
            "Observed-only post-test estimand with treatment interactions for the three original child baseline controls.",
        ),
        (
            "geographic_block_fixed_effects",
            observed,
            primary_terms + block_terms,
            None,
            "Observed-only post-test estimand with geographic block fixed effects; block 1 is the base.",
        ),
        (
            "child_baseline_interactions_plus_geographic_block_fixed_effects",
            observed,
            primary_terms + child_terms + block_terms,
            None,
            "Observed-only post-test estimand with child baseline interactions and geographic block fixed effects.",
        ),
        (
            "equal_school_weight_primary",
            observed,
            primary_terms,
            1.0 / observed.groupby("schid")["schid"].transform("size"),
            "Observed-only equal-school-weight estimand; each school's observation weights sum to one.",
        ),
        (
            "no_baseline_controls_same_sample",
            observed,
            ["treat", "teacher_score_z", "treat_score_z"],
            None,
            "Observed-only diagnostic with no baseline controls, on the fixed R=1 sample.",
        ),
        (
            "data_quality_duplicate_key_exclusion",
            duplicate_free,
            primary_terms,
            None,
            "Observed-only data-quality sensitivity: all repeated school-child keys dropped.",
        ),
    ]

    coefficient_rows: list[dict] = []
    fits: dict[str, dict] = {}
    for model, frame, terms, weights, note in specs_to_run:
        fit = specs.fit_cluster_ols(
            frame,
            "z_add_post_total",
            terms,
            weights=weights,
            sample_label=f"observed_{model}",
        )
        fits[model] = fit
        coefficient_rows.extend(
            specs.coefficient_rows(
                fit,
                stage="post_observed_only",
                model=model,
                estimand_note=note,
            )
        )

    primary_interaction = next(
        row
        for row in coefficient_rows
        if row["model"] == "primary" and row["term"] == "treat_score_z"
    )
    if abs(primary_interaction["coefficient"] - 0.13213278149564028) > 1e-8:
        raise AssertionError(primary_interaction)
    if abs(primary_interaction["se_clustered"] - 0.0712514855999031) > 1e-8:
        raise AssertionError(primary_interaction)

    score_mean = float(scores["teacher_score"].mean())
    score_sd = float(scores["teacher_score"].std(ddof=1))
    p25_raw = float(scores["teacher_score"].quantile(0.25))
    p75_raw = float(scores["teacher_score"].quantile(0.75))
    p25_z = (p25_raw - score_mean) / score_sd
    p75_z = (p75_raw - score_mean) / score_sd
    marginal = pd.DataFrame(
        [
            specs.contrast_row(
                fits["primary"],
                stage="post_observed_only",
                model="primary",
                label="p25_school_score",
                score_raw=p25_raw,
                score_z=p25_z,
                interaction_p=primary_interaction["p_value_two_sided_t"],
            ),
            specs.contrast_row(
                fits["primary"],
                stage="post_observed_only",
                model="primary",
                label="p75_school_score",
                score_raw=p75_raw,
                score_z=p75_z,
                interaction_p=primary_interaction["p_value_two_sided_t"],
            ),
            specs.high_minus_low_row(
                fits["primary"],
                stage="post_observed_only",
                model="primary",
                low_raw=p25_raw,
                low_z=p25_z,
                high_raw=p75_raw,
                high_z=p75_z,
                interaction_p=primary_interaction["p_value_two_sided_t"],
            ),
        ]
    )

    coefficients_df = pd.DataFrame(coefficient_rows)
    hashes = specs.input_hash_rows()
    attrition_hash = pd.DataFrame(
        [
            {
                "kind": "follow_up_source",
                "path": str(ATTRITION_SOURCE.relative_to(ROOT)),
                "bytes": ATTRITION_SOURCE.stat().st_size,
                "sha256": specs.sha256(ATTRITION_SOURCE),
            },
            {
                "kind": "follow_up_source",
                "path": str(SPECS_SOURCE.relative_to(ROOT)),
                "bytes": SPECS_SOURCE.stat().st_size,
                "sha256": specs.sha256(SPECS_SOURCE),
            },
        ]
    )
    hashes = pd.concat([hashes, attrition_hash], ignore_index=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    metadata = {
        "command": "python3 scripts/run_direction02_observed_specs.py",
        "working_directory": str(ROOT),
        "timestamp_utc": timestamp,
        "python": sys.version,
        "platform": platform.platform(),
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "script_sha256": specs.sha256(Path(__file__).resolve()),
        "attrition_source_sha256": specs.sha256(ATTRITION_SOURCE),
        "specs_source_sha256": specs.sha256(SPECS_SOURCE),
        "observed_source_indicator": "R == 1 from run_direction02_attrition.prepare_data",
        "observed_only_rows": int(len(observed)),
        "observed_only_schools": int(observed["schid"].nunique()),
        "observed_only_unique_school_child_keys": int(
            observed[["schid", "childno"]].drop_duplicates().shape[0]
        ),
        "duplicate_key_count": duplicate_keys,
        "duplicate_rows_dropped_sensitivity": duplicate_rows,
        "duplicate_free_rows": int(len(duplicate_free)),
        "duplicate_free_schools": int(duplicate_free["schid"].nunique()),
        "score_reference_schools": int(scores["schid"].nunique()),
        "score_mean": score_mean,
        "score_sd": score_sd,
        "p25_raw": p25_raw,
        "p25_z": p25_z,
        "p75_raw": p75_raw,
        "p75_z": p75_z,
        "primary_interaction": {
            "coefficient": primary_interaction["coefficient"],
            "se_clustered": primary_interaction["se_clustered"],
            "p_value_two_sided_t": primary_interaction["p_value_two_sided_t"],
        },
        "specifications": [model for model, *_ in specs_to_run],
        "analysis_status": "Observed-only substantive result for the fixed Direction 0.2 specification set; no new outcomes or models.",
        "amendment_note": "Observed-only constraint was a data-quality amendment discovered after the initial plan and documented in this follow-up.",
    }

    coefficients_df.to_csv(OUT / "specifications_observed_coefficients.csv", index=False)
    marginal.to_csv(OUT / "specifications_observed_marginal_effects.csv", index=False)
    hashes.to_csv(OUT / "specifications_observed_input_hashes.csv", index=False)
    (OUT / "specifications_observed_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    high_low = marginal.loc[
        marginal["term"] == "marginal_treatment_effect_p75_minus_p25"
    ].iloc[0]
    sensitivity = coefficients_df[coefficients_df["term"] == "treat_score_z"]
    methods = [
        "# Direction 0.2 observed-only follow-up",
        "",
        "This is a data-quality follow-up of the fixed Direction 0.2 specification set. It uses the same reconstructed post-test total outcome, teacher-score moderator, controls, seven post-test model specifications, and fixed p25/p75 contrasts. The specification set was fixed for this follow-up after prior exploratory review; it was not preregistered.",
        "",
        f"The observed-only indicator is `R == 1` from `run_direction02_attrition.prepare_data`: the reconstructed source post verbal total is observed and the normalized post total exists. This excludes the 21 source stayer rows that would otherwise receive a zero through the source missing-value fill. The observed-only sample has N={len(observed)} rows, G={observed['schid'].nunique()} schools, and {observed[['schid', 'childno']].drop_duplicates().shape[0]} unique school-child keys.",
        "",
        f"Primary interaction: **{primary_interaction['coefficient']:.8f}**, SE **{primary_interaction['se_clustered']:.8f}**, p={primary_interaction['p_value_two_sided_t']:.5f}, 95% CI {primary_interaction['ci_low_95']:.8f} to {primary_interaction['ci_high_95']:.8f}.",
        "",
        "The p25, p75, and p75-minus-p25 results are formal contrasts from this same primary fit; no new model or outcome is estimated.",
        f"At p25 (raw {p25_raw:.2f}, z {p25_z:.6f}), the treatment effect is {marginal.iloc[0]['coefficient']:.8f}, SE {marginal.iloc[0]['se_clustered']:.8f}, p={marginal.iloc[0]['p_value_two_sided_t']:.5f}.",
        f"At p75 (raw {p75_raw:.2f}, z {p75_z:.6f}), the treatment effect is {marginal.iloc[1]['coefficient']:.8f}, SE {marginal.iloc[1]['se_clustered']:.8f}, p={marginal.iloc[1]['p_value_two_sided_t']:.5f}.",
        f"The p75-minus-p25 contrast is {high_low['coefficient']:.8f}, SE {high_low['se_clustered']:.8f}, p={high_low['p_value_two_sided_t']:.5f}, 95% CI {high_low['ci_low_95']:.8f} to {high_low['ci_high_95']:.8f}; its p equals the interaction p because the treatment main effect cancels.",
        "",
        "Interaction results for all seven fixed post-test specifications:",
    ]
    for _, row in sensitivity.iterrows():
        methods.append(
            f"- `{row['model']}`: {row['coefficient']:.8f}, SE {row['se_clustered']:.8f}, p={row['p_value_two_sided_t']:.5f}, 95% CI {row['ci_low_95']:.8f} to {row['ci_high_95']:.8f}, N={int(row['n_observations'])}, G={int(row['n_schools'])}."
        )
    methods += [
        "",
        f"The duplicate-key sensitivity drops all {duplicate_rows} rows belonging to {duplicate_keys} repeated school-child keys, yielding N={len(duplicate_free)}; no individual key was selected.",
        "",
        "The source-compatible N=1,646 result is retained as the replication reference for alignment with the original source program. Under the observed-only constraint, the N=1,625 result is the substantive Direction 0.2 result emphasized here; it avoids treating source-filled zeros as observed outcomes. This observed-only constraint was a data-quality amendment discovered after the initial plan and is documented in this follow-up.",
        "",
        "Outputs: `specifications_observed_coefficients.csv`, `specifications_observed_marginal_effects.csv`, `specifications_observed_metadata.json`, and `specifications_observed_input_hashes.csv`.",
    ]
    (OUT / "specifications_observed_methods_results.md").write_text(
        "\n".join(methods) + "\n", encoding="utf-8"
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
