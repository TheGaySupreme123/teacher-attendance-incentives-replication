#!/usr/bin/env python3
"""Build compact replication exhibits from the supplied saved analysis files."""
from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/teacher-attendance-replication-mpl")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PACKAGE = Path(__file__).resolve().parents[1]
RESULTS = PACKAGE / "results"
RESULTS.mkdir(parents=True, exist_ok=True)


def load_json(rel: str):
    return json.loads((PACKAGE / rel).read_text(encoding="utf-8"))


def build_tables() -> None:
    attendance = load_json("results/attendance_recheck.json")
    table10 = pd.read_csv(PACKAGE / "outputs/research_direction_audit/transition_table10_reproduction.csv")
    models = pd.read_csv(PACKAGE / "outputs/scope_search_2026_09_22/transition/transition_scope_model_results.csv")
    groups = pd.read_csv(PACKAGE / "outputs/scope_search_2026_09_22/transition/transition_scope_group_effects.csv")

    table1_rows = [{
        "result": "teacher_attendance",
        "coefficient": attendance["estimate"],
        "se_clustered": attendance["se"],
        "ci_low": attendance["ci_low"],
        "ci_high": attendance["ci_high"],
        "p_value": attendance["p"],
        "n": attendance["n"],
        "schools": attendance["schools"],
    }]
    for _, row in table10.iterrows():
        table1_rows.append({
            "result": f"table10_{row['outcome']}",
            "coefficient": row["estimate"],
            "se_clustered": row["se_clustered"],
            "ci_low": np.nan,
            "ci_high": np.nan,
            "p_value": row["p_value"],
            "n": int(row["n"]),
            "schools": int(row["schools"]),
        })
    pd.DataFrame(table1_rows).to_csv(RESULTS / "table1_replication.csv", index=False, float_format="%.10g")

    group_rows = groups[groups["outcome"].eq("drop")].copy()
    group_rows["group"] = group_rows["pre_writ"].map({0: "non_writer", 1: "writer"})
    group_rows = group_rows.rename(columns={
        "treatment_effect": "coefficient",
        "p_value": "p_value",
        "n_treated": "n_treated",
        "n_control": "n_control",
    })
    group_cols = ["group", "coefficient", "se_clustered", "ci_low", "ci_high", "p_value", "n_treated", "n_control", "n_total", "schools_total"]
    group_rows[group_cols].to_csv(RESULTS / "table2_group_effects.csv", index=False, float_format="%.10g")

    boot_ps = {}
    for outcome in ("drop", "drop2"):
        rel = f"outputs/scope_search_2026_09_22/transition/{outcome}_wildbootstrap_summary.json"
        boot_ps[outcome] = load_json(rel)["wild_bootstrap_p_value"]
    primary = models[models["specification"].eq("primary_consensus_no_fe")].copy()
    primary["wild_bootstrap_p_value"] = primary["outcome"].map(boot_ps)
    primary = primary.rename(columns={"estimate": "coefficient"})
    cols = ["outcome", "coefficient", "se_clustered", "ci_low", "ci_high", "p_value", "holm_p_value", "wild_bootstrap_p_value", "n", "schools", "cluster_df", "regressors"]
    primary[cols].to_csv(RESULTS / "table3_interactions.csv", index=False, float_format="%.10g")

    # Appendix A1 is assembled from the same saved model rows used in the
    # manuscript.  Values are retained as fractions and percentage points so
    # that the table can be consumed without re-fitting any model.
    sentinel = pd.read_csv(PACKAGE / "outputs/scope_search_2026_09_22/transition/sentinel_drop_interaction.csv")
    sentinel_boot = load_json(
        "outputs/scope_search_2026_09_22/transition/sentinel_complete_wildbootstrap_summary.json"
    )
    a1_specs = [
        ("primary_consensus_no_fe", "Main interaction", "operational_original", None),
        ("same_sample_randomization_block_fe", "Geographic block controls", "operational_original", None),
        ("fixed_2005_12_31_endpoint", "December 2005 endpoint", "operational_original", None),
    ]
    a1_rows = []
    for specification, label, _, _ in a1_specs:
        row = models.loc[
            (models["specification"] == specification) & (models["outcome"] == "drop")
        ].iloc[0]
        a1_rows.append(
            {
                "check": label,
                "coefficient": row["estimate"],
                "coefficient_percentage_points": 100 * row["estimate"],
                "se_clustered": row["se_clustered"],
                "ci_low": row["ci_low"],
                "ci_high": row["ci_high"],
                "ci_low_percentage_points": 100 * row["ci_low"],
                "ci_high_percentage_points": 100 * row["ci_high"],
                "p_value": row["p_value"],
                "wild_bootstrap_p_value": (
                    boot_ps["drop"] if specification == "primary_consensus_no_fe" else np.nan
                ),
                "n": int(row["n"]),
                "schools": int(row["schools"]),
                "source": "outputs/scope_search_2026_09_22/transition/transition_scope_model_results.csv",
            }
        )
    excluded = sentinel.loc[sentinel["sample"] == "exclude_ambiguous_drop"].iloc[0]
    a1_rows.append(
        {
            "check": "Exclude ambiguous attendance-code classifications",
            "coefficient": excluded["estimate"],
            "coefficient_percentage_points": 100 * excluded["estimate"],
            "se_clustered": excluded["se_clustered"],
            "ci_low": excluded["ci_low"],
            "ci_high": excluded["ci_high"],
            "ci_low_percentage_points": 100 * excluded["ci_low"],
            "ci_high_percentage_points": 100 * excluded["ci_high"],
            "p_value": excluded["p_value"],
            "wild_bootstrap_p_value": sentinel_boot["wild_bootstrap_p_value"],
            "n": int(excluded["n"]),
            "schools": int(excluded["schools"]),
            "source": "outputs/scope_search_2026_09_22/transition/sentinel_drop_interaction.csv",
        }
    )
    pd.DataFrame(a1_rows).to_csv(RESULTS / "tableA1_sensitivity.csv", index=False, float_format="%.10g")

    # Appendix A2 reports algebraic ranges, not standard-error intervals.
    bounds = load_json("outputs/scope_search_2026_09_22/measurement/sentinel_interaction_bounds.json")
    incomplete = pd.read_csv(
        PACKAGE / "outputs/scope_search_2026_09_22/transition/transition_incomplete_last5_bounds.csv"
    )
    incomplete_row = incomplete.loc[
        incomplete["quantity"] == "drop_interaction_writer_minus_nonwriter"
    ].iloc[0]
    bound_rows = [
        {
            "sensitivity": "Attendance-code flags",
            "lower_bound": bounds["sentinel_bounds"]["beta_min"],
            "upper_bound": bounds["sentinel_bounds"]["beta_max"],
            "lower_bound_percentage_points": 100 * bounds["sentinel_bounds"]["beta_min"],
            "upper_bound_percentage_points": 100 * bounds["sentinel_bounds"]["beta_max"],
            "flagged_or_incomplete_children": bounds["sentinel_bounds"]["unknown_total"],
            "inference": "algebraic range; no standard error or p-value",
            "source": "outputs/scope_search_2026_09_22/measurement/sentinel_interaction_bounds.json",
        },
        {
            "sensitivity": "Fewer-than-five open checks",
            "lower_bound": incomplete_row["lower_bound"],
            "upper_bound": incomplete_row["upper_bound"],
            "lower_bound_percentage_points": 100 * incomplete_row["lower_bound"],
            "upper_bound_percentage_points": 100 * incomplete_row["upper_bound"],
            "flagged_or_incomplete_children": incomplete_row["incomplete_last_five"],
            "inference": "algebraic range; no standard error or p-value",
            "source": "outputs/scope_search_2026_09_22/transition/transition_incomplete_last5_bounds.csv",
        },
        {
            "sensitivity": "Union of flags",
            "lower_bound": bounds["union_all_bounds"]["beta_min"],
            "upper_bound": bounds["union_all_bounds"]["beta_max"],
            "lower_bound_percentage_points": 100 * bounds["union_all_bounds"]["beta_min"],
            "upper_bound_percentage_points": 100 * bounds["union_all_bounds"]["beta_max"],
            "flagged_or_incomplete_children": bounds["union_all_bounds"]["unknown_total"],
            "inference": "algebraic range; no standard error or p-value",
            "source": "outputs/scope_search_2026_09_22/measurement/sentinel_interaction_bounds.json",
        },
    ]
    pd.DataFrame(bound_rows).to_csv(RESULTS / "tableA2_measurement_bounds.csv", index=False, float_format="%.10g")


def build_figure() -> None:
    groups = pd.read_csv(PACKAGE / "outputs/scope_search_2026_09_22/transition/transition_scope_group_effects.csv")
    groups = groups[groups["outcome"].eq("drop")].sort_values("pre_writ")
    model = pd.read_csv(PACKAGE / "outputs/scope_search_2026_09_22/transition/transition_scope_model_results.csv")
    main = model.loc[
        (model["specification"] == "primary_consensus_no_fe") & (model["outcome"] == "drop")
    ].iloc[0]
    labels = ["Baseline nonwriters", "Baseline writers", "Difference between effects"]
    effects = np.array([
        groups.iloc[0]["treatment_effect"],
        groups.iloc[1]["treatment_effect"],
        main["estimate"],
    ], dtype=float) * 100
    lows = np.array([
        groups.iloc[0]["ci_low"],
        groups.iloc[1]["ci_low"],
        main["ci_low"],
    ], dtype=float) * 100
    highs = np.array([
        groups.iloc[0]["ci_high"],
        groups.iloc[1]["ci_high"],
        main["ci_high"],
    ], dtype=float) * 100

    # The paper figure is deliberately a horizontal, black-and-serif exhibit:
    # two cell effects followed by their direct interaction estimate.
    fig, ax = plt.subplots(figsize=(10.0, 3.8), constrained_layout=False)
    y = np.array([2, 1, 0], dtype=float)
    ax.errorbar(
        effects,
        y,
        xerr=np.vstack([effects - lows, highs - effects]),
        fmt="o",
        color="black",
        ecolor="black",
        capsize=5,
        markersize=6,
        linewidth=1.5,
    )
    ax.axvline(0, color="#777777", linewidth=1.0)
    ax.set_xlim(-10, 47)
    ax.set_ylim(-0.75, 2.75)
    ax.set_yticks(y, labels)
    ax.set_xlabel("Effect on recorded departure (percentage points)", fontfamily="serif", color="black")
    ax.tick_params(axis="x", colors="black")
    ax.tick_params(axis="y", colors="black", length=0)
    for tick in ax.get_xticklabels() + ax.get_yticklabels():
        tick.set_fontfamily("serif")
        tick.set_color("black")
    ax.grid(False)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("black")
    for yi, hi, effect in zip(y, highs, effects):
        ax.text(
            hi + 0.8,
            yi,
            f"{effect:.1f}",
            ha="left",
            va="center",
            fontfamily="serif",
            color="black",
        )
    ax.text(
        0.5,
        -0.28,
        "Points are treatment effects; bars are 95% cluster-robust confidence intervals.",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=8.5,
        fontfamily="serif",
        color="black",
    )
    fig.savefig(RESULTS / "figure1.png", dpi=220, bbox_inches="tight", facecolor="white")
    fig.savefig(RESULTS / "figure1.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    build_tables()
    build_figure()
    print("Wrote results/table1_replication.csv, table2_group_effects.csv, table3_interactions.csv, tableA1_sensitivity.csv, tableA2_measurement_bounds.csv, figure1.png, figure1.svg")
