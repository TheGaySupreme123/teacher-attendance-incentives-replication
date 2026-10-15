"""Focused robustness audit for the baseline-writing transition extension.

This is a bounded follow-up to ``audit_transition_extension.py``.  The fixed
primary family is the three Table 10 child outcomes (drop, government-school
transition, and drop excluding transfers), each with the same treatment x
baseline-writing interaction.  It reports Holm-adjusted clustered p-values,
an independent null-imposed school wild-bootstrap-t for the drop2 lead, a
randomization-block fixed-effect check, the pre-specified unique-ID exclusion,
and one measurement-driven calendar-endpoint check.

No reason values or child outcomes are filled or imputed.  The calendar
endpoint is fixed at 2005-12-31 because the appended rosterfin source has a
numeric reason field that becomes blank in the distributed Stata coded roster;
this check asks whether the lead is driven by the endpoint rows.  It is a
measurement sensitivity, not a search over windows.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "scope_search_2026_09_22" / "transition"
OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT))
from scripts import audit_transition_extension as raw  # noqa: E402
from scripts import run_direction02_wildbootstrap as wild  # noqa: E402


SEED = 20260922
BOOTSTRAPS = 9_999
BATCH_SIZE = 500
CALENDAR_CUTOFF = pd.Timestamp("2005-12-31")


def cluster_fit(df: pd.DataFrame, outcome: str, regressors: list[str]) -> dict:
    """Return OLS with the same finite-sample school cluster correction."""

    work = df[[outcome, "schid"] + regressors].dropna().reset_index(drop=True)
    y = work[outcome].to_numpy(float)
    x = np.column_stack([np.ones(len(work))] + [work[name].to_numpy(float) for name in regressors])
    fit = wild.cluster_fit(y, x, work["schid"].to_numpy())
    fit["names"] = ["const"] + regressors
    fit["data"] = work
    return fit


def add_block(df: pd.DataFrame) -> pd.DataFrame:
    rc = pd.read_stata(
        raw.ROOT / "data" / "Incentives_FINAL" / "Raw-Data" / "RandomCheck" / "Teacher-Attendance" / "randomcheck.dta",
        convert_categoricals=False,
    )
    school_block = rc[["schid", "block"]].drop_duplicates()
    assert school_block["schid"].duplicated().sum() == 0
    out = df.merge(school_block, on="schid", how="left", validate="many_to_one")
    assert out["block"].notna().all()
    return out


def consensus_status(pre_writ: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    status = (
        pre_writ.groupby(raw.CHILD_KEYS)["pre_writ"]
        .agg(pre_rows="size", pre_unique="nunique", pre_mean="mean")
        .reset_index()
    )
    status["pre_consensus"] = status["pre_mean"].where(status["pre_unique"] == 1)
    return status, status.loc[status["pre_unique"] != 1].copy()


def open_rows(coded: pd.DataFrame, cutoff: pd.Timestamp | None = None) -> pd.DataFrame:
    rows = coded.loc[coded["open"] == 1].copy()
    rows["date"] = pd.to_datetime(
        {
            "year": rows["year"].astype(int),
            "month": rows["month"].astype(int),
            "day": rows["day"].astype(int),
        },
        errors="coerce",
    )
    if cutoff is not None:
        rows = rows.loc[rows["date"] <= cutoff].copy()
    rows = rows.sort_values(
        ["schid", "childno", "date"],
        ascending=[True, True, False],
        kind="mergesort",
    )
    rows["last"] = rows.groupby(raw.CHILD_KEYS, sort=False).cumcount()
    rows = rows.loc[rows["last"] < 5].copy()
    rows["reason_blank"] = rows["reason"].eq("")
    rows["reason_2"] = rows["reason"].eq("2")
    return rows


def collapse_outcomes(rows: pd.DataFrame) -> pd.DataFrame:
    rows = rows.copy()
    rows["tempgov"] = rows["reason_2"].astype(int)
    outcomes = (
        rows.groupby(["schid", "childno", "treat"], as_index=False)
        .agg(attendance=("attendance", "sum"), tempgov=("tempgov", "sum"))
    )
    outcomes["drop"] = (outcomes["attendance"] == 0).astype(int)
    outcomes["gov"] = ((outcomes["tempgov"] != 0) & (outcomes["drop"] == 1)).astype(int)
    outcomes["drop2"] = ((outcomes["drop"] == 1) & (outcomes["gov"] == 0)).astype(int)
    return outcomes


def analysis_frame(coded: pd.DataFrame, status: pd.DataFrame, cutoff: pd.Timestamp | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = open_rows(coded, cutoff=cutoff)
    outcomes = collapse_outcomes(rows)
    data = outcomes.merge(status[["schid", "childno", "pre_consensus"]], on=raw.CHILD_KEYS, how="left")
    data = data.dropna(subset=["pre_consensus"]).rename(columns={"pre_consensus": "pre_writ"}).copy()
    data["treat_x_pre_writ"] = data["treat"] * data["pre_writ"]
    data = add_block(data)
    return data, rows


def model_rows(data: pd.DataFrame, specification: str, outcomes: list[str]) -> pd.DataFrame:
    rows = []
    regressors = ["treat", "pre_writ", "treat_x_pre_writ"]
    if specification == "same_sample_randomization_block_fe":
        blocks = sorted(data["block"].unique())
        for block in blocks[1:]:
            data[f"block_fe_{int(block)}"] = (data["block"] == block).astype(float)
        regressors += [f"block_fe_{int(block)}" for block in blocks[1:]]
    for outcome in outcomes:
        fit = cluster_fit(data, outcome, regressors)
        interaction = fit["names"].index("treat_x_pre_writ")
        df = fit["clusters"] - 1
        estimate = float(fit["beta"][interaction])
        se = float(fit["se"][interaction])
        crit = float(stats.t.ppf(0.975, df))
        rows.append(
            {
                "specification": specification,
                "outcome": outcome,
                "estimate": estimate,
                "se_clustered": se,
                "t_stat": float(fit["t"][interaction]),
                "p_value": float(2 * stats.t.sf(abs(fit["t"][interaction]), df)),
                "ci_low": estimate - crit * se,
                "ci_high": estimate + crit * se,
                "n": fit["n"],
                "schools": fit["clusters"],
                "cluster_df": df,
                "regressors": ";".join(regressors),
            }
        )
    return pd.DataFrame(rows)


def group_effect_rows(data: pd.DataFrame, outcomes: list[str]) -> pd.DataFrame:
    """Report fixed pre_writ-group treatment effects and counts."""

    rows = []
    regressors = ["treat", "pre_writ", "treat_x_pre_writ"]
    for outcome in outcomes:
        fit = cluster_fit(data, outcome, regressors)
        names = fit["names"]
        df = fit["clusters"] - 1
        critical = float(stats.t.ppf(0.975, df))
        for group in [0, 1]:
            vector = np.zeros(len(names), dtype=float)
            vector[names.index("treat")] = 1.0
            if group == 1:
                vector[names.index("treat_x_pre_writ")] = 1.0
            estimate = float(vector @ fit["beta"])
            se = float(np.sqrt(vector @ fit["covariance"] @ vector))
            treated = data[(data["treat"] == 1) & (data["pre_writ"] == group)]
            control = data[(data["treat"] == 0) & (data["pre_writ"] == group)]
            rows.append(
                {
                    "outcome": outcome,
                    "pre_writ": group,
                    "treatment_effect": estimate,
                    "se_clustered": se,
                    "ci_low": estimate - critical * se,
                    "ci_high": estimate + critical * se,
                    "p_value": float(2 * stats.t.sf(abs(estimate / se), df)),
                    "n_treated": len(treated),
                    "n_control": len(control),
                    "schools_treated": treated["schid"].nunique(),
                    "schools_control": control["schid"].nunique(),
                    "treated_mean": float(treated[outcome].mean()),
                    "control_mean": float(control[outcome].mean()),
                    "n_total": len(treated) + len(control),
                    "schools_total": data["schid"].nunique(),
                }
            )
    return pd.DataFrame(rows)


def holm_adjust(p_values: pd.Series) -> pd.Series:
    order = np.argsort(p_values.to_numpy())
    adjusted = np.empty(len(p_values), dtype=float)
    running = 0.0
    for rank, index in enumerate(order):
        value = min(1.0, (len(p_values) - rank) * float(p_values.iloc[index]))
        running = max(running, value)
        adjusted[index] = running
    return pd.Series(adjusted, index=p_values.index)


def wild_bootstrap(data: pd.DataFrame, outcome: str) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    """Null-imposed school wild-bootstrap-t for one primary interaction."""

    regressors = ["treat", "pre_writ", "treat_x_pre_writ"]
    work = data[[outcome, "schid"] + regressors].dropna().reset_index(drop=True)
    y = work[outcome].to_numpy(float)
    x_full = np.column_stack([np.ones(len(work))] + [work[name].to_numpy(float) for name in regressors])
    names = ["const"] + regressors
    interaction_index = names.index("treat_x_pre_writ")
    restricted_indices = [i for i, name in enumerate(names) if name != "treat_x_pre_writ"]
    x_restricted = x_full[:, restricted_indices]
    clusters = work["schid"].to_numpy()
    full_fit = wild.cluster_fit(y, x_full, clusters)
    restricted_fit = wild.cluster_fit(y, x_restricted, clusters)
    observed_t = float(full_fit["t"][interaction_index])
    observed_coef = float(full_fit["beta"][interaction_index])
    observed_se = float(full_fit["se"][interaction_index])

    rng = np.random.default_rng(SEED)
    bootstrap_t, bootstrap_coef = wild.bootstrap_t_statistics(
        y=y,
        x_full=x_full,
        x_restricted=x_restricted,
        clusters=clusters,
        beta_restricted=restricted_fit["beta"],
        interaction_index=interaction_index,
        rng=rng,
        repetitions=BOOTSTRAPS,
        batch_size=BATCH_SIZE,
    )
    extreme = np.abs(bootstrap_t) >= abs(observed_t)
    p_value = float((1 + int(extreme.sum())) / (BOOTSTRAPS + 1))
    mc_se = float(np.sqrt(p_value * (1 - p_value) / (BOOTSTRAPS + 1)))

    validation_rng = np.random.default_rng(SEED)
    _, cluster_codes = np.unique(clusters, return_inverse=True)
    first_weights = validation_rng.choice(np.array([-1.0, 1.0]), size=(5, full_fit["clusters"]))
    validation_rows = []
    for draw in range(5):
        weights_by_row = first_weights[draw, cluster_codes]
        direct_coef, direct_se, direct_t = wild.direct_bootstrap_refit(
            y,
            x_full,
            x_restricted,
            clusters,
            restricted_fit["beta"],
            weights_by_row,
            interaction_index,
        )
        validation_rows.append(
            {
                "draw": draw + 1,
                "vectorized_t": float(bootstrap_t[draw]),
                "direct_t": direct_t,
                "abs_t_difference": abs(float(bootstrap_t[draw]) - direct_t),
                "vectorized_coefficient": float(bootstrap_coef[draw]),
                "direct_coefficient": direct_coef,
                "abs_coefficient_difference": abs(float(bootstrap_coef[draw]) - direct_coef),
                "direct_se": direct_se,
            }
        )
    validation = pd.DataFrame(validation_rows)
    summary = {
        "outcome": outcome,
        "null": "treat_x_pre_writ = 0; treatment main effect and pre_writ main effect remain unrestricted",
        "inference": "null-imposed school-level Rademacher wild bootstrap-t",
        "estimate": observed_coef,
        "se_clustered": observed_se,
        "observed_t": observed_t,
        "classical_p_value": float(2 * stats.t.sf(abs(observed_t), full_fit["clusters"] - 1)),
        "wild_bootstrap_p_value": p_value,
        "wild_bootstrap_extreme_count": int(extreme.sum()),
        "wild_bootstrap_monte_carlo_se": mc_se,
        "bootstrap_repetitions": BOOTSTRAPS,
        "bootstrap_seed": SEED,
        "n": int(full_fit["n"]),
        "schools": int(full_fit["clusters"]),
        "cluster_df": int(full_fit["clusters"] - 1),
        "validation_pass": bool(
            (validation["abs_t_difference"] < 1e-10).all()
            and (validation["abs_coefficient_difference"] < 1e-10).all()
        ),
    }
    t_stats = pd.DataFrame(
        {
            "draw": np.arange(1, BOOTSTRAPS + 1),
            "wild_t": bootstrap_t,
            "coefficient": bootstrap_coef,
            "as_extreme": extreme,
        }
    )
    return summary, t_stats, validation


def coverage_outputs(rows: pd.DataFrame, status: pd.DataFrame, label: str) -> pd.DataFrame:
    frame = rows.merge(status[["schid", "childno", "pre_consensus"]], on=raw.CHILD_KEYS, how="inner")
    if "pre_writ" in frame.columns:
        frame = frame.drop(columns=["pre_writ"])
    frame = frame.dropna(subset=["pre_consensus"]).copy()
    frame = frame.rename(columns={"pre_consensus": "pre_writ"})
    counts = frame.groupby(["treat", "pre_writ"], as_index=False).agg(
        selected_open_rows=("reason", "size"),
        blank_reason_rows=("reason_blank", "sum"),
        reason_2_rows=("reason_2", "sum"),
    )
    child_counts = (
        frame[["schid", "childno", "treat", "pre_writ"]]
        .drop_duplicates()
        .groupby(["treat", "pre_writ"], as_index=False)
        .size()
        .rename(columns={"size": "child_ids"})
    )
    counts = child_counts.merge(counts, on=["treat", "pre_writ"], how="left")
    all_open = (
        frame.groupby(["schid", "childno", "treat", "pre_writ"], as_index=False)
        .size()
        .rename(columns={"size": "selected_rows"})
    )
    # The selected frame contains at most five rows; count coverage is reported
    # from the coded roster separately in main().
    counts["blank_reason_share"] = counts["blank_reason_rows"] / counts["selected_open_rows"]
    counts["reason_2_row_share"] = counts["reason_2_rows"] / counts["selected_open_rows"]
    counts.insert(0, "window", label)
    return counts


def main() -> None:
    coded, pre_writ = raw.load_coded_roster()
    status, conflicting = consensus_status(pre_writ)
    primary, primary_rows = analysis_frame(coded, status)
    cutoff, cutoff_rows = analysis_frame(coded, status, cutoff=CALENDAR_CUTOFF)
    outcomes = ["drop", "gov", "drop2"]

    primary_models = model_rows(primary, "primary_consensus_no_fe", outcomes)
    primary_models["holm_p_value"] = holm_adjust(primary_models["p_value"])
    # The Holm family is the three primary Table 10 outcome interactions only.
    primary_models["family"] = "drop/gov/drop2 primary interaction family"

    block_models = model_rows(primary, "same_sample_randomization_block_fe", outcomes)
    block_models["holm_p_value"] = np.nan
    block_models["family"] = "fixed-effect robustness"

    cutoff_models = model_rows(cutoff, "fixed_2005_12_31_endpoint", outcomes)
    cutoff_models["holm_p_value"] = np.nan
    cutoff_models["family"] = "measurement-driven endpoint sensitivity"

    models = pd.concat([primary_models, block_models, cutoff_models], ignore_index=True)
    models.to_csv(OUT / "transition_scope_model_results.csv", index=False)
    group_effects = group_effect_rows(primary, outcomes)
    group_effects.to_csv(OUT / "transition_scope_group_effects.csv", index=False)

    bootstrap_summaries = {}
    for bootstrap_outcome in ["drop", "drop2"]:
        bootstrap_summary, t_stats, validation = wild_bootstrap(primary, bootstrap_outcome)
        bootstrap_summaries[bootstrap_outcome] = bootstrap_summary
        (OUT / f"{bootstrap_outcome}_wildbootstrap_t_statistics.csv").write_text(
            t_stats.to_csv(index=False), encoding="utf-8"
        )
        validation.to_csv(OUT / f"{bootstrap_outcome}_wildbootstrap_validation.csv", index=False)
        (OUT / f"{bootstrap_outcome}_wildbootstrap_summary.json").write_text(
            json.dumps(bootstrap_summary, indent=2) + "\n", encoding="utf-8"
        )

    primary_rows_with_status = primary_rows.merge(
        primary[["schid", "childno"]].drop_duplicates(),
        on=raw.CHILD_KEYS,
        how="inner",
    )
    all_open = coded.loc[coded["open"] == 1].copy()
    all_open_counts = (
        all_open.groupby(["schid", "childno", "treat"], as_index=False)
        .size()
        .rename(columns={"size": "all_open_checks"})
        .merge(status[["schid", "childno", "pre_consensus"]], on=raw.CHILD_KEYS, how="inner")
        .dropna(subset=["pre_consensus"])
        .rename(columns={"pre_consensus": "pre_writ"})
    )
    bound_data = primary.merge(
        all_open_counts[["schid", "childno", "all_open_checks"]],
        on=raw.CHILD_KEYS,
        how="left",
        validate="one_to_one",
    )
    bound_data["incomplete_last_five"] = bound_data["all_open_checks"] < 5
    bound_rows = []
    cells = {}
    for (treat, pre_group), group in bound_data.groupby(["treat", "pre_writ"]):
        n = len(group)
        incomplete = int(group["incomplete_last_five"].sum())
        observed_complete_sum = int(group.loc[~group["incomplete_last_five"], "drop"].sum())
        lower = observed_complete_sum / n
        upper = (observed_complete_sum + incomplete) / n
        cells[(int(treat), int(pre_group))] = (lower, upper)
        bound_rows.append(
            {
                "quantity": "drop_cell_mean",
                "treat": int(treat),
                "pre_writ": int(pre_group),
                "n": n,
                "incomplete_last_five": incomplete,
                "observed_complete_drop_sum": observed_complete_sum,
                "lower_bound": lower,
                "upper_bound": upper,
                "inference": "algebraic binary-outcome bounds; no standard error",
            }
        )
    te_bounds = {}
    for pre_group in [0, 1]:
        lower = cells[(1, pre_group)][0] - cells[(0, pre_group)][1]
        upper = cells[(1, pre_group)][1] - cells[(0, pre_group)][0]
        te_bounds[pre_group] = (lower, upper)
        bound_rows.append(
            {
                "quantity": "drop_treatment_effect",
                "treat": np.nan,
                "pre_writ": pre_group,
                "n": np.nan,
                "incomplete_last_five": np.nan,
                "observed_complete_drop_sum": np.nan,
                "lower_bound": lower,
                "upper_bound": upper,
                "inference": "algebraic binary-outcome bounds; no standard error",
            }
        )
    bound_rows.append(
        {
            "quantity": "drop_interaction_writer_minus_nonwriter",
            "treat": np.nan,
            "pre_writ": np.nan,
            "n": len(bound_data),
            "incomplete_last_five": int(bound_data["incomplete_last_five"].sum()),
            "observed_complete_drop_sum": np.nan,
            "lower_bound": te_bounds[1][0] - te_bounds[0][1],
            "upper_bound": te_bounds[1][1] - te_bounds[0][0],
            "inference": "algebraic binary-outcome bounds; no standard error",
        }
    )
    pd.DataFrame(bound_rows).to_csv(OUT / "transition_incomplete_last5_bounds.csv", index=False)
    coverage = (
        all_open_counts.groupby(["treat", "pre_writ"], as_index=False)
        .agg(
            child_ids=("childno", "size"),
            mean_all_open_checks=("all_open_checks", "mean"),
            share_at_least_five=("all_open_checks", lambda s: float(np.mean(s >= 5))),
            min_all_open_checks=("all_open_checks", "min"),
            max_all_open_checks=("all_open_checks", "max"),
        )
    )
    coverage.insert(0, "audit", "all_open_check_coverage")
    coverage.to_csv(OUT / "transition_open_check_coverage.csv", index=False)

    selected_coverage = pd.concat(
        [coverage_outputs(primary_rows, status, "full_last_five_open_checks"), coverage_outputs(cutoff_rows, status, "through_2005_12_31_last_five_open_checks")],
        ignore_index=True,
    )
    selected_coverage.to_csv(OUT / "transition_reason_coverage.csv", index=False)

    period = primary_rows.merge(status[["schid", "childno", "pre_consensus"]], on=raw.CHILD_KEYS, how="inner")
    if "pre_writ" in period.columns:
        period = period.drop(columns=["pre_writ"])
    period = period.dropna(subset=["pre_consensus"]).copy()
    period = period.rename(columns={"pre_consensus": "pre_writ"})
    period_summary = (
        period.groupby(["year", "month", "treat", "pre_writ"], as_index=False)
        .agg(
            selected_open_rows=("reason", "size"),
            blank_reason_rows=("reason_blank", "sum"),
            reason_2_rows=("reason_2", "sum"),
        )
    )
    period_summary["blank_reason_share"] = period_summary["blank_reason_rows"] / period_summary["selected_open_rows"]
    period_summary.to_csv(OUT / "transition_reason_coverage_by_period.csv", index=False)

    missing = pd.DataFrame(
        [
            {"quantity": "table10_children", "value": int(len(raw.build_table10_outcomes(coded)[0]))},
            {"quantity": "consensus_analysis_children", "value": int(len(primary))},
            {"quantity": "pre_writ_duplicate_ids_total", "value": int((status["pre_rows"] > 1).sum())},
            {"quantity": "pre_writ_conflicting_ids_total", "value": int(len(conflicting))},
            {"quantity": "pre_writ_conflicting_ids_in_analysis", "value": int(len(conflicting.merge(primary, on=raw.CHILD_KEYS)))},
            {"quantity": "primary_selected_open_rows", "value": int(len(primary_rows_with_status))},
            {"quantity": "primary_blank_reason_rows", "value": int(primary_rows_with_status["reason_blank"].sum())},
            {"quantity": "primary_reason_2_rows", "value": int(primary_rows_with_status["reason_2"].sum())},
        ]
    )
    missing.to_csv(OUT / "transition_scope_measurement_summary.csv", index=False)

    primary_drop2 = primary_models.loc[primary_models["outcome"] == "drop2"].iloc[0]
    primary_gov = primary_models.loc[primary_models["outcome"] == "gov"].iloc[0]
    primary_drop = primary_models.loc[primary_models["outcome"] == "drop"].iloc[0]
    block_drop = block_models.loc[block_models["outcome"] == "drop"].iloc[0]
    block_drop2 = block_models.loc[block_models["outcome"] == "drop2"].iloc[0]
    cutoff_drop = cutoff_models.loc[cutoff_models["outcome"] == "drop"].iloc[0]
    cutoff_drop2 = cutoff_models.loc[cutoff_models["outcome"] == "drop2"].iloc[0]
    drop_bootstrap_summary = bootstrap_summaries["drop"]
    drop2_bootstrap_summary = bootstrap_summaries["drop2"]
    full_reason_coverage = selected_coverage.loc[
        selected_coverage["window"] == "full_last_five_open_checks"
    ]
    def coverage_value(frame: pd.DataFrame, treat: int, pre_group: int, column: str) -> float:
        row = frame.loc[(frame["treat"] == treat) & (frame["pre_writ"] == pre_group)].iloc[0]
        return float(row[column])

    nonwriter_control_open = coverage_value(coverage, 0, 0, "mean_all_open_checks")
    nonwriter_treated_open = coverage_value(coverage, 1, 0, "mean_all_open_checks")
    writer_control_open = coverage_value(coverage, 0, 1, "mean_all_open_checks")
    writer_treated_open = coverage_value(coverage, 1, 1, "mean_all_open_checks")
    nonwriter_control_blank = coverage_value(full_reason_coverage, 0, 0, "blank_reason_share")
    nonwriter_treated_blank = coverage_value(full_reason_coverage, 1, 0, "blank_reason_share")
    writer_control_blank = coverage_value(full_reason_coverage, 0, 1, "blank_reason_share")
    writer_treated_blank = coverage_value(full_reason_coverage, 1, 1, "blank_reason_share")
    drop_group0 = group_effects.loc[(group_effects["outcome"] == "drop") & (group_effects["pre_writ"] == 0)].iloc[0]
    drop_group1 = group_effects.loc[(group_effects["outcome"] == "drop") & (group_effects["pre_writ"] == 1)].iloc[0]
    bound_interaction = next(row for row in bound_rows if row["quantity"] == "drop_interaction_writer_minus_nonwriter")
    report = f"""# Transition scope and significance audit

## Scope and prior exploration

The fixed primary family for this audit is the treatment x baseline-writing interaction for the three existing Table 10 child outcomes: `drop` (realized departure from the NFE at the last open checks), `gov` (an observed government-school transition marker), and `drop2` (departure without that observed transfer marker). The family was chosen for this audit after prior exploratory work and is not preregistered or independent confirmation. Holm adjustment is applied across these three primary interaction p-values. Broader prior exploration means even the adjusted values remain exploratory evidence.

The primary data rule is the existing raw reconstruction in `scripts/audit_transition_extension.py`, with the two conflicting eligible baseline-writing IDs excluded. It leaves {len(primary)} children in {primary.schid.nunique()} schools. No reason field, transition indicator, or dropout indicator is imputed.

## Primary family

| Outcome | Interaction | Clustered SE | t | Raw p | Holm p | 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| drop | {primary_drop.estimate:.3f} | {primary_drop.se_clustered:.3f} | {primary_drop.t_stat:.2f} | {primary_drop.p_value:.4f} | {primary_drop.holm_p_value:.4f} | [{primary_drop.ci_low:.3f}, {primary_drop.ci_high:.3f}] |
| gov | {primary_gov.estimate:.3f} | {primary_gov.se_clustered:.3f} | {primary_gov.t_stat:.2f} | {primary_gov.p_value:.4f} | {primary_gov.holm_p_value:.4f} | [{primary_gov.ci_low:.3f}, {primary_gov.ci_high:.3f}] |
| drop2 | {primary_drop2.estimate:.3f} | {primary_drop2.se_clustered:.3f} | {primary_drop2.t_stat:.2f} | {primary_drop2.p_value:.4f} | {primary_drop2.holm_p_value:.4f} | [{primary_drop2.ci_low:.3f}, {primary_drop2.ci_high:.3f}] |

The drop2 lead remains below .05 after Holm adjustment across the fixed three-outcome family ({primary_drop2.holm_p_value:.4f}), but this is an exploratory family result, not a clean confirmatory claim. It should be read as higher realized NFE departure without an observed government-school reason marker, not as a definitive educational-dropout or school-exit mechanism.

The cleaner primary `drop` outcome has a fixed-group treatment effect of {drop_group0.treatment_effect:.3f} (SE {drop_group0.se_clustered:.3f}, 95% CI [{drop_group0.ci_low:.3f}, {drop_group0.ci_high:.3f}]) for baseline nonwriters and {drop_group1.treatment_effect:.3f} (SE {drop_group1.se_clustered:.3f}, 95% CI [{drop_group1.ci_low:.3f}, {drop_group1.ci_high:.3f}]) for baseline writers. The group counts are {int(drop_group0.n_control)} control/{int(drop_group0.n_treated)} treated nonwriters and {int(drop_group1.n_control)} control/{int(drop_group1.n_treated)} treated writers. These effects describe realized departure from the NFE under the Table 10 operational definition.

## Wild-bootstrap inference for the two positive primary leads

The primary `drop` interaction is {drop_bootstrap_summary['estimate']:.3f} (clustered SE {drop_bootstrap_summary['se_clustered']:.3f}, classical p {drop_bootstrap_summary['classical_p_value']:.4f}); its null-imposed school-level Rademacher wild bootstrap-t gives p={drop_bootstrap_summary['wild_bootstrap_p_value']:.4f} (Monte Carlo SE {drop_bootstrap_summary['wild_bootstrap_monte_carlo_se']:.4f}). The primary `drop2` interaction is {drop2_bootstrap_summary['estimate']:.3f} (clustered SE {drop2_bootstrap_summary['se_clustered']:.3f}, classical p {drop2_bootstrap_summary['classical_p_value']:.4f}); its wild-bootstrap p is {drop2_bootstrap_summary['wild_bootstrap_p_value']:.4f} (Monte Carlo SE {drop2_bootstrap_summary['wild_bootstrap_monte_carlo_se']:.4f}). Both use {BOOTSTRAPS} draws with seed {SEED}; treatment and baseline-writing main effects remain unrestricted under the null. The first five vectorized draws match independent refits for both outcomes: {drop_bootstrap_summary['validation_pass']} and {drop2_bootstrap_summary['validation_pass']}.

## Fixed-effect and endpoint checks

Adding the existing school block field as geography/block fixed effects on the same consensus sample gives a `drop` interaction of {block_drop.estimate:.3f} (SE {block_drop.se_clustered:.3f}, p={block_drop.p_value:.4f}; 95% CI [{block_drop.ci_low:.3f}, {block_drop.ci_high:.3f}]) and a `drop2` interaction of {block_drop2.estimate:.3f} (SE {block_drop2.se_clustered:.3f}, p={block_drop2.p_value:.4f}; 95% CI [{block_drop2.ci_low:.3f}, {block_drop2.ci_high:.3f}]). This check does not add a new outcome or change the child sample.

The raw source has a structural measurement issue: `reason` is string in `roster_rema2012.dta` but numeric in `rosterfin.dta`; the distributed Stata append leaves the latter values blank in the coded roster. Across the primary selected rows, {primary_rows_with_status['reason_blank'].mean():.1%} of reason fields are blank ({int(primary_rows_with_status['reason_blank'].sum())} of {len(primary_rows_with_status)}); blanks are {primary_rows_with_status.loc[primary_rows_with_status['treat']==0, 'reason_blank'].mean():.1%} in control and {primary_rows_with_status.loc[primary_rows_with_status['treat']==1, 'reason_blank'].mean():.1%} in treatment. No blanks are filled.

As a fixed calendar-endpoint measurement sensitivity motivated by blank reason fields in the final Jan–Feb 2006 rosterfin rows, the same last-five-open-check rule is recomputed using observed roster dates through 2005-12-31. The `drop` interaction is {cutoff_drop.estimate:.3f} (SE {cutoff_drop.se_clustered:.3f}, p={cutoff_drop.p_value:.4f}; 95% CI [{cutoff_drop.ci_low:.3f}, {cutoff_drop.ci_high:.3f}]) and the `drop2` interaction is {cutoff_drop2.estimate:.3f} (SE {cutoff_drop2.se_clustered:.3f}, p={cutoff_drop2.p_value:.4f}; 95% CI [{cutoff_drop2.ci_low:.3f}, {cutoff_drop2.ci_high:.3f}]). This is not a p-selected window: the calendar date is fixed before looking at the estimates. It still uses blank reason fields as blank and does not impute outcomes. Both leads are smaller but remain positive; the endpoint check therefore does not show that the result is solely created by the final Jan–Feb 2006 records.

## Coverage and interpretation

Treatment changes observation opportunities: children in treatment schools have more open-school checks, so the last-five-open-check rule is post-treatment. The coverage CSVs report child counts, all-open-check counts, selected row counts, blank reason shares, and reason-2 counts by treatment and baseline-writing status and by period. The outcome remains an operational Table 10 classification rather than a directly observed transition process independent of treatment-generated open checks. In particular, `drop2` is not independently observed educational dropout: it is no attendance in the selected open checks without a recorded `reason == "2"` marker.

Coverage differs across both treatment and baseline-writing groups: mean all-open-check counts are {nonwriter_control_open:.2f} for control nonwriters versus {nonwriter_treated_open:.2f} for treated nonwriters, and {writer_control_open:.2f} for control writers versus {writer_treated_open:.2f} for treated writers. In the selected last-five rows, blank-reason shares are {nonwriter_control_blank:.1%}, {nonwriter_treated_blank:.1%}, {writer_control_blank:.1%}, and {writer_treated_blank:.1%}, respectively. The period-by-group CSV makes the temporal pattern inspectable without changing the window after seeing estimates.

The primary `drop` classification also has incomplete five-check coverage. In the consensus sample, {int(bound_interaction['incomplete_last_five'])} of {int(bound_interaction['n'])} children have fewer than five observed open checks. Treating every such child's binary `drop` outcome as unknown, without imputing or selecting a sample, gives algebraic cell bounds and a writer-minus-nonwriter treatment-effect-difference bound of [{bound_interaction['lower_bound']:.3f}, {bound_interaction['upper_bound']:.3f}]. The lower bound remains positive, but this is a partial-identification interval with no standard error or p-value; it does not remove the post-treatment coverage concern.

## Decision

The drop2 x baseline-writing lead survives the fixed three-outcome Holm adjustment, same-sample block fixed effects, and a source-motivated calendar-endpoint check, and the primary wild-bootstrap result should be reported alongside the classical inference. The cleaner `drop` interaction is the stronger substantive anchor because it does not require a `reason` code, and its incomplete-check worst-case bound remains positive. This is a plausible, genuinely new substantive direction under the existing-number constraint. The evidence remains exploratory and measurement-limited: reason coverage is incomplete, open-check coverage is treatment-affected, and the family was selected after prior exploration. The paper should state the lead as evidence consistent with a difference in realized NFE departure without an observed government-school marker among baseline writers, not as definitive educational-dropout avoidance, a causal mechanism, or a confirmatory discovery.

Re-run with:

```bash
python3 scripts/audit_transition_scope.py
```
"""
    (OUT / "transition_scope_report.md").write_text(report, encoding="utf-8")

    print(json.dumps({"primary": primary_models.to_dict(orient="records"), "wild": bootstrap_summaries}, indent=2))


if __name__ == "__main__":
    main()
