#!/usr/bin/env python3
"""Read-only verification of the seminar paper's saved headline results.

The verifier recomputes a small, fixed set of results from the supplied raw
Stata files and compares them with the saved analysis artifacts.  It never
calls an analysis script's ``main`` function and writes only
``seminar_paper_drafts/source/verification.json``.

Run from the repository root with::

    MPLCONFIGDIR=/private/tmp/yoetz-seminar-verifier-mpl \
        python3 seminar_paper_drafts/verify_results.py

The bootstrap check reads the saved 9,999 t statistics.  It does not rerun the
bootstrap or write any original analysis output.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats


# No figure is produced, but setting this before any optional plotting import
# keeps this verifier safe in the documented system environment.
os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/yoetz-seminar-verifier-mpl")

ROOT = Path(__file__).resolve().parents[1]
SOURCE_OUT = ROOT / "seminar_paper_drafts" / "source" / "verification.json"

ATTENDANCE_RAW = ROOT / "data" / "Incentives_FINAL" / "Raw-Data" / "RandomCheck" / "Teacher-Attendance" / "randomcheck.dta"
ATTENDANCE_REFERENCE = ROOT / "seminar_paper_drafts" / "source" / "attendance_recheck.json"
TABLE2_CSV = ROOT / "data" / "Incentives_FINAL" / "Output" / "table2.csv"

ROSTER_RAW = ROOT / "data" / "Incentives_FINAL" / "Raw-Data" / "RandomCheck" / "Roster"
TABLE10_CSV = ROOT / "data" / "Incentives_FINAL" / "Output" / "Table10.csv"
SHIPPED_DROP = ROSTER_RAW / "Temp" / "drop.dta"
TABLE10_REPRO_CSV = ROOT / "outputs" / "research_direction_audit" / "transition_table10_reproduction.csv"
TRANSITION_INTERACTION_CSV = ROOT / "outputs" / "research_direction_audit" / "transition_interaction.csv"
TRANSITION_GROUP_MEANS_CSV = ROOT / "outputs" / "research_direction_audit" / "transition_group_means.csv"

SCOPE_OUT = ROOT / "outputs" / "scope_search_2026_09_22" / "transition"
SCOPE_GROUPS_CSV = SCOPE_OUT / "transition_scope_group_effects.csv"
SCOPE_MODELS_CSV = SCOPE_OUT / "transition_scope_model_results.csv"

DROP_BOOTSTRAP_SUMMARY = SCOPE_OUT / "drop_wildbootstrap_summary.json"
DROP_BOOTSTRAP_T = SCOPE_OUT / "drop_wildbootstrap_t_statistics.csv"
DROP2_BOOTSTRAP_SUMMARY = SCOPE_OUT / "drop2_wildbootstrap_summary.json"
DROP2_BOOTSTRAP_T = SCOPE_OUT / "drop2_wildbootstrap_t_statistics.csv"

CHILD_KEYS = ["schid", "childno"]
DROP_CLOSED_SCHOOLS = [1111, 1211, 2493, 5221, 5231, 5332, 5711]
TOLERANCE = 1e-10


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def as_json(value: Any) -> Any:
    """Convert NumPy and pandas scalars to ordinary JSON values."""

    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    if isinstance(value, Path):
        return relative(value)
    if isinstance(value, dict):
        return {str(key): as_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [as_json(item) for item in value]
    return value


def close_enough(left: float, right: float, tolerance: float = TOLERANCE) -> bool:
    return bool(np.isclose(float(left), float(right), rtol=tolerance, atol=tolerance))


def add_table2_time(frame: pd.DataFrame) -> pd.DataFrame:
    """Reproduce the time coding in Programs/Table-2.do."""

    out = frame.copy()
    out["time"] = np.nan
    time = 1
    for year, months in [
        (2003, range(8, 13)),
        (2004, range(1, 13)),
        (2005, range(1, 13)),
        (2006, range(1, 3)),
    ]:
        for month in months:
            out.loc[(out["year"] == year) & (out["month"] == month), "time"] = time
            time += 1
    out.loc[(out["month"] == 8) & (out["day"] > 24), "time"] = 2
    return out


def cluster_ols(
    frame: pd.DataFrame,
    outcome: str,
    regressors: list[str],
    cluster: str,
) -> dict[str, Any]:
    """OLS with the finite-sample school-cluster correction used in the audits."""

    columns = [outcome, cluster] + regressors
    work = frame[columns].dropna().reset_index(drop=True)
    y = work[outcome].to_numpy(dtype=float)
    x = np.column_stack(
        [np.ones(len(work), dtype=float)]
        + [work[name].to_numpy(dtype=float) for name in regressors]
    )
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    residual = y - x @ beta
    xtx_inv = np.linalg.inv(x.T @ x)
    meat = np.zeros((x.shape[1], x.shape[1]), dtype=float)
    for _, indices in work.groupby(cluster, sort=False).groups.items():
        positions = np.asarray(indices, dtype=int)
        score = x[positions].T @ residual[positions]
        meat += np.outer(score, score)

    n = len(work)
    k = x.shape[1]
    groups = int(work[cluster].nunique())
    correction = (groups / (groups - 1)) * ((n - 1) / (n - k))
    covariance = correction * xtx_inv @ meat @ xtx_inv
    standard_error = np.sqrt(np.maximum(np.diag(covariance), 0.0))
    names = ["const"] + regressors
    t_stat = beta / standard_error
    p_value = 2 * stats.t.sf(np.abs(t_stat), groups - 1)
    return {
        "work": work,
        "names": names,
        "beta": pd.Series(beta, index=names),
        "se": pd.Series(standard_error, index=names),
        "covariance": pd.DataFrame(covariance, index=names, columns=names),
        "t": pd.Series(t_stat, index=names),
        "p": pd.Series(p_value, index=names),
        "n": int(n),
        "schools": groups,
        "cluster_df": groups - 1,
        "correction": correction,
    }


def interaction_result(frame: pd.DataFrame, outcome: str) -> dict[str, Any]:
    fit = cluster_ols(frame, outcome, ["treat", "pre_writ", "treat_x_pre_writ"], "schid")
    term = "treat_x_pre_writ"
    index = fit["names"].index(term)
    estimate = float(fit["beta"][term])
    se = float(fit["se"][term])
    critical = float(stats.t.ppf(0.975, fit["cluster_df"]))
    return {
        "estimate": estimate,
        "se_clustered": se,
        "t_stat": float(fit["t"][term]),
        "p_value": float(fit["p"][term]),
        "ci_low": estimate - critical * se,
        "ci_high": estimate + critical * se,
        "n": fit["n"],
        "schools": fit["schools"],
        "cluster_df": fit["cluster_df"],
    }


def record_check(
    checks: list[dict[str, Any]],
    check_id: str,
    passed: bool,
    details: str,
    observed: Any = None,
    expected: Any = None,
) -> None:
    row: dict[str, Any] = {
        "id": check_id,
        "status": "pass" if passed else "fail",
        "details": details,
    }
    if observed is not None:
        row["observed"] = observed
    if expected is not None:
        row["expected"] = expected
    checks.append(as_json(row))


def compare_numeric_fields(
    checks: list[dict[str, Any]],
    check_id: str,
    observed: dict[str, Any],
    expected: dict[str, Any],
    details: str,
    tolerance: float = TOLERANCE,
) -> None:
    failures = []
    for field, target in expected.items():
        value = observed.get(field)
        if isinstance(target, (int, float)) and isinstance(value, (int, float)):
            matches = close_enough(value, target, tolerance)
        else:
            matches = value == target
        if not matches:
            failures.append(field)
    record_check(
        checks,
        check_id,
        not failures,
        details if not failures else f"{details}; mismatched fields: {', '.join(failures)}",
        observed,
        expected,
    )


def load_transition_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Import only pure constructors from the audited raw-data script."""

    # The imported module defines paths and functions but does not call main or
    # write outputs.  Its existing constructor is the audited Table 10 rule.
    sys.path.insert(0, str(ROOT))
    from scripts import audit_transition_extension as raw  # noqa: PLC0415

    coded, pre_writ = raw.load_coded_roster()
    outcomes, open_counts = raw.build_table10_outcomes(coded)
    outcomes = outcomes.copy()
    outcomes["drop2"] = ((outcomes["drop"] == 1) & (outcomes["gov"] == 0)).astype(int)
    return outcomes, pre_writ, open_counts


def verify_headline(checks: list[dict[str, Any]]) -> dict[str, Any]:
    raw = pd.read_stata(ATTENDANCE_RAW, convert_categoricals=False)
    coded = add_table2_time(raw)
    coded = coded.loc[~coded["schid"].isin(DROP_CLOSED_SCHOOLS)].copy()
    coded = coded.loc[coded["time"] != 1].copy()
    fit = cluster_ols(coded, "open", ["treat"], "schid")
    critical = float(stats.t.ppf(0.975, fit["cluster_df"]))
    result = {
        "estimate": float(fit["beta"]["treat"]),
        "se_clustered": float(fit["se"]["treat"]),
        "t_stat": float(fit["t"]["treat"]),
        "p_value": float(fit["p"]["treat"]),
        "ci_low": float(fit["beta"]["treat"] - critical * fit["se"]["treat"]),
        "ci_high": float(fit["beta"]["treat"] + critical * fit["se"]["treat"]),
        "control_mean": float(coded.loc[coded["treat"] == 0, "open"].mean()),
        "treatment_mean": float(coded.loc[coded["treat"] == 1, "open"].mean()),
        "n": fit["n"],
        "schools": fit["schools"],
        "cluster_df": fit["cluster_df"],
        "raw_rows_before_filters": int(len(raw)),
        "rows_after_closed_school_and_first_period_filters": int(len(coded)),
        "closed_school_ids": DROP_CLOSED_SCHOOLS,
    }
    saved = json.loads(ATTENDANCE_REFERENCE.read_text(encoding="utf-8"))
    compare_numeric_fields(
        checks,
        "headline.attendance.raw_vs_saved_recheck",
        result,
        {
            "estimate": saved["estimate"],
            "se_clustered": saved["se"],
            "n": saved["n"],
            "schools": saved["schools"],
            "control_mean": saved["control_mean"],
            "treatment_mean": saved["treatment_mean"],
        },
        "Raw random-check reconstruction agrees with the saved attendance recheck.",
    )
    table2 = pd.read_csv(TABLE2_CSV, header=None, dtype=str)
    table2_effect = table2.iloc[2, 1]
    table2_se = table2.iloc[3, 1]
    record_check(
        checks,
        "headline.attendance.rounded_published_table2",
        table2_effect == "0.21" and table2_se.startswith("[0.03]"),
        "Published Table 2 first post-baseline column rounds to 0.21 with SE 0.03.",
        {"coefficient_cell": table2_effect, "se_cell": table2_se},
        {"coefficient_cell": "0.21", "se_prefix": "[0.03]"},
    )
    return result


def verify_table10_and_consensus(checks: list[dict[str, Any]]) -> tuple[dict[str, Any], pd.DataFrame]:
    outcomes, pre_writ, _ = load_transition_data()
    shipped = pd.read_stata(SHIPPED_DROP, convert_categoricals=False)
    raw_keys = outcomes[CHILD_KEYS].drop_duplicates()
    shipped_keys = shipped[CHILD_KEYS].drop_duplicates()
    merged = outcomes.merge(
        shipped,
        on=["schid", "childno", "treat"],
        how="outer",
        suffixes=("_raw", "_shipped"),
        indicator=True,
    )
    exact_key_match = len(merged) == len(outcomes) == len(shipped) and (merged["_merge"] == "both").all()
    value_mismatch_counts = {}
    for outcome in ["drop", "gov"]:
        value_mismatch_counts[outcome] = int(
            (~np.isclose(merged[f"{outcome}_raw"], merged[f"{outcome}_shipped"], equal_nan=True)).sum()
        )
    shipped_drop2 = ((shipped["drop"] == 1) & (shipped["gov"] == 0)).astype(int)
    raw_drop2 = outcomes["drop2"].astype(int)
    drop2_mismatch = int(
        (~np.isclose(
            outcomes.set_index(CHILD_KEYS)["drop2"].sort_index().to_numpy(),
            pd.Series(shipped_drop2.to_numpy(), index=shipped.set_index(CHILD_KEYS).index)
            .sort_index()
            .to_numpy(),
            equal_nan=True,
        )).sum()
    )
    table10 = {
        "raw_child_rows": int(len(outcomes)),
        "shipped_child_rows": int(len(shipped)),
        "raw_schools": int(outcomes["schid"].nunique()),
        "shipped_schools": int(shipped["schid"].nunique()),
        "raw_control_children": int((outcomes["treat"] == 0).sum()),
        "raw_treatment_children": int((outcomes["treat"] == 1).sum()),
        "shipped_control_children": int((shipped["treat"] == 0).sum()),
        "shipped_treatment_children": int((shipped["treat"] == 1).sum()),
        "exact_child_key_match": bool(exact_key_match),
        "drop_value_mismatches": value_mismatch_counts["drop"],
        "gov_value_mismatches": value_mismatch_counts["gov"],
        "drop2_value_mismatches": drop2_mismatch,
        "raw_drop2_definition_matches": bool(
            (outcomes["drop2"] == ((outcomes["drop"] == 1) & (outcomes["gov"] == 0)).astype(int)).all()
        ),
    }
    table10_pass = bool(
        table10["raw_child_rows"] == table10["shipped_child_rows"] == 2197
        and table10["raw_schools"] == table10["shipped_schools"] == 111
        and table10["raw_control_children"] == table10["shipped_control_children"] == 1061
        and table10["raw_treatment_children"] == table10["shipped_treatment_children"] == 1136
        and table10["exact_child_key_match"]
        and table10["drop_value_mismatches"] == 0
        and table10["gov_value_mismatches"] == 0
        and table10["drop2_value_mismatches"] == 0
        and table10["raw_drop2_definition_matches"]
    )
    record_check(
        checks,
        "table10.raw_reconstruction_matches_shipped_child_outcomes",
        table10_pass,
        "Raw Table 10 construction matches shipped child-level drop and government-marker outcomes and the derived drop2 outcome.",
        table10,
        {
            "raw_child_rows": 2197,
            "shipped_child_rows": 2197,
            "raw_schools": 111,
            "shipped_schools": 111,
            "raw_control_children": 1061,
            "shipped_control_children": 1061,
            "raw_treatment_children": 1136,
            "shipped_treatment_children": 1136,
            "exact_child_key_match": True,
            "drop_value_mismatches": 0,
            "gov_value_mismatches": 0,
            "drop2_value_mismatches": 0,
            "raw_drop2_definition_matches": True,
        },
    )

    status = (
        pre_writ.groupby(CHILD_KEYS)["pre_writ"]
        .agg(pre_rows="size", pre_unique="nunique", pre_mean="mean")
        .reset_index()
    )
    status["pre_consensus"] = status["pre_mean"].where(status["pre_unique"] == 1)
    analysis = outcomes.merge(status, on=CHILD_KEYS, how="left")
    conflict_ids = status.loc[status["pre_unique"] > 1, CHILD_KEYS]
    in_sample_conflicts = int(len(conflict_ids.merge(outcomes[CHILD_KEYS], on=CHILD_KEYS, how="inner")))
    analysis = analysis.dropna(subset=["pre_consensus"]).rename(columns={"pre_consensus": "pre_writ"}).copy()
    analysis["treat_x_pre_writ"] = analysis["treat"] * analysis["pre_writ"]
    group_counts = {
        f"treat_{int(treat)}_W_{int(pre)}": int(len(group))
        for (treat, pre), group in analysis.groupby(["treat", "pre_writ"], sort=True)
    }
    consensus = {
        "pre_writ_rows": int(len(pre_writ)),
        "pre_writ_unique_child_ids": int(len(status)),
        "pre_writ_conflicting_ids": int(len(conflict_ids)),
        "in_sample_conflicting_ids": in_sample_conflicts,
        "consensus_children": int(len(analysis)),
        "consensus_schools": int(analysis["schid"].nunique()),
        "W_0_children": int((analysis["pre_writ"] == 0).sum()),
        "W_1_children": int((analysis["pre_writ"] == 1).sum()),
        "control_children": int((analysis["treat"] == 0).sum()),
        "treatment_children": int((analysis["treat"] == 1).sum()),
        "group_counts": group_counts,
    }
    expected_groups = {
        "treat_0_W_0": 858,
        "treat_0_W_1": 201,
        "treat_1_W_0": 940,
        "treat_1_W_1": 196,
    }
    consensus_pass = (
        consensus["consensus_children"] == 2195
        and consensus["consensus_schools"] == 111
        and consensus["in_sample_conflicting_ids"] == 2
        and consensus["group_counts"] == expected_groups
        and consensus["W_0_children"] == 1798
        and consensus["W_1_children"] == 397
    )
    record_check(
        checks,
        "interaction.consensus_W_sample_and_cell_counts",
        consensus_pass,
        "Consensus baseline-writing status leaves N=2,195 children and reproduces all four treatment-by-W cells.",
        consensus,
        {
            "consensus_children": 2195,
            "consensus_schools": 111,
            "in_sample_conflicting_ids": 2,
            "W_0_children": 1798,
            "W_1_children": 397,
            "group_counts": expected_groups,
        },
    )
    return {"table10": table10, "consensus": consensus}, analysis


def verify_interaction(
    checks: list[dict[str, Any]],
    analysis: pd.DataFrame,
) -> dict[str, Any]:
    raw_result = interaction_result(analysis, "drop")
    saved_models = pd.read_csv(SCOPE_MODELS_CSV)
    saved_row = saved_models.loc[
        (saved_models["specification"] == "primary_consensus_no_fe")
        & (saved_models["outcome"] == "drop")
    ]
    fields = ["estimate", "se_clustered", "t_stat", "p_value", "ci_low", "ci_high", "n", "schools", "cluster_df"]
    saved_result = {field: saved_row.iloc[0][field] for field in fields}
    compare_numeric_fields(
        checks,
        "interaction.main_drop_raw_vs_saved_model",
        raw_result,
        saved_result,
        "Raw interaction fit agrees with the saved primary drop model estimate, clustered SE, interval, and p-value.",
    )
    groups = pd.read_csv(SCOPE_GROUPS_CSV)
    expected_cells = {
        0: {"n_control": 858, "n_treated": 940, "control_mean": float(analysis.loc[(analysis.treat == 0) & (analysis.pre_writ == 0), "drop"].mean()), "treated_mean": float(analysis.loc[(analysis.treat == 1) & (analysis.pre_writ == 0), "drop"].mean())},
        1: {"n_control": 201, "n_treated": 196, "control_mean": float(analysis.loc[(analysis.treat == 0) & (analysis.pre_writ == 1), "drop"].mean()), "treated_mean": float(analysis.loc[(analysis.treat == 1) & (analysis.pre_writ == 1), "drop"].mean())},
    }
    cell_failures = []
    for pre_writ, expected in expected_cells.items():
        row = groups.loc[(groups["outcome"] == "drop") & (groups["pre_writ"] == pre_writ)]
        if len(row) != 1:
            cell_failures.append(f"W={pre_writ}:missing_saved_row")
            continue
        saved = row.iloc[0]
        for field, target in expected.items():
            if not close_enough(saved[field], target):
                cell_failures.append(f"W={pre_writ}:{field}")
    record_check(
        checks,
        "interaction.main_drop_four_cell_rates",
        not cell_failures,
        "Saved group effects agree with the raw four-cell counts and rates used by the interaction.",
        {"mismatches": cell_failures, "raw_cells": expected_cells},
        {"mismatches": []},
    )
    return {"raw": raw_result, "saved": saved_result, "cell_rates": expected_cells}


def verify_bootstrap(
    checks: list[dict[str, Any]],
    interaction: dict[str, Any],
    analysis: pd.DataFrame,
) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for outcome, summary_path, t_path in [
        ("drop", DROP_BOOTSTRAP_SUMMARY, DROP_BOOTSTRAP_T),
        ("drop2", DROP2_BOOTSTRAP_SUMMARY, DROP2_BOOTSTRAP_T),
    ]:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        t_stats = pd.read_csv(t_path)
        repetitions = int(summary["bootstrap_repetitions"])
        observed_t = float(summary["observed_t"])
        derived_extreme = np.abs(t_stats["wild_t"].to_numpy(dtype=float)) >= abs(observed_t)
        stored_extreme = t_stats["as_extreme"].astype(bool).to_numpy()
        extreme_count = int(derived_extreme.sum())
        derived_p = float((1 + extreme_count) / (repetitions + 1))
        rows_are_sequential = (
            len(t_stats) == repetitions == 9999
            and t_stats["draw"].astype(int).tolist() == list(range(1, repetitions + 1))
        )
        flag_consistent = bool(np.array_equal(derived_extreme, stored_extreme))
        summary_pass = bool(
            rows_are_sequential
            and flag_consistent
            and int(summary["wild_bootstrap_extreme_count"]) == extreme_count
            and close_enough(summary["wild_bootstrap_p_value"], derived_p)
            and int(summary["bootstrap_repetitions"]) == 9999
            and bool(summary["validation_pass"])
        )
        record_check(
            checks,
            f"bootstrap.{outcome}.saved_p_value_from_9999_t_statistics",
            summary_pass,
            "Saved wild-bootstrap p-value equals (1 + saved |t| exceedances) / (9,999 + 1), with sequential draws and stored flags checked.",
            {
                "bootstrap_repetitions": repetitions,
                "t_statistics_rows": int(len(t_stats)),
                "observed_t": observed_t,
                "extreme_count_from_t_statistics": extreme_count,
                "summary_extreme_count": int(summary["wild_bootstrap_extreme_count"]),
                "derived_p_value": derived_p,
                "summary_p_value": float(summary["wild_bootstrap_p_value"]),
                "rows_are_sequential": rows_are_sequential,
                "stored_extreme_flags_match": flag_consistent,
                "saved_vectorized_validation_pass": bool(summary["validation_pass"]),
            },
            {
                "bootstrap_repetitions": 9999,
                "extreme_count_from_t_statistics": extreme_count,
                "derived_p_value": derived_p,
                "rows_are_sequential": True,
                "stored_extreme_flags_match": True,
                "saved_vectorized_validation_pass": True,
            },
        )
        raw_result = interaction_result(analysis, outcome)
        summary_vs_raw = {
            "estimate": float(summary["estimate"]),
            "se_clustered": float(summary["se_clustered"]),
            "t_stat": float(summary["observed_t"]),
        }
        compare_numeric_fields(
            checks,
            f"bootstrap.{outcome}.saved_observed_fit_matches_raw",
            summary_vs_raw,
            {
                "estimate": raw_result["estimate"],
                "se_clustered": raw_result["se_clustered"],
                "t_stat": raw_result["t_stat"],
            },
            "Saved bootstrap summary reports the same observed interaction fit as the raw reconstruction.",
        )
        results[outcome] = {
            "summary_path": relative(summary_path),
            "t_statistics_path": relative(t_path),
            "observed_t": observed_t,
            "bootstrap_repetitions": repetitions,
            "extreme_count": extreme_count,
            "p_value_from_saved_t_statistics": derived_p,
            "saved_p_value": float(summary["wild_bootstrap_p_value"]),
            "seed": int(summary["bootstrap_seed"]),
            "validation_pass": bool(summary["validation_pass"]),
        }
    return results


def build_hash_record() -> dict[str, Any]:
    paths_with_roles = [
        (ATTENDANCE_RAW, "raw_input"),
        (ATTENDANCE_REFERENCE, "saved_reference"),
        (TABLE2_CSV, "shipped_reference_csv"),
        (ROOT / "data" / "Incentives_FINAL" / "Programs" / "Table-2.do", "source_program"),
        (ROOT / "data" / "Incentives_FINAL" / "Programs" / "Table7_Table10.do", "source_program"),
        (ROSTER_RAW / "roster_rema2012.dta", "raw_input"),
        (ROSTER_RAW / "rosterfin.dta", "raw_input"),
        (ROSTER_RAW / "rc_for_roster.dta", "raw_input"),
        (ROSTER_RAW / "enroll1.dta", "raw_input"),
        (ROSTER_RAW / "pre_writ_attend.dta", "raw_input"),
        (SHIPPED_DROP, "shipped_reference"),
        (TABLE10_CSV, "shipped_reference_csv"),
        (TABLE10_REPRO_CSV, "saved_analysis_csv"),
        (TRANSITION_INTERACTION_CSV, "saved_analysis_csv"),
        (TRANSITION_GROUP_MEANS_CSV, "saved_analysis_csv"),
        (SCOPE_GROUPS_CSV, "saved_analysis_csv"),
        (SCOPE_MODELS_CSV, "saved_analysis_csv"),
        (DROP_BOOTSTRAP_SUMMARY, "saved_analysis_summary"),
        (DROP_BOOTSTRAP_T, "saved_analysis_csv"),
        (DROP2_BOOTSTRAP_SUMMARY, "saved_analysis_summary"),
        (DROP2_BOOTSTRAP_T, "saved_analysis_csv"),
        (ROOT / "outputs" / "scope_search_2026_09_22" / "INPUT_HASHES.json", "saved_hash_manifest"),
        (ROOT / "scripts" / "audit_transition_extension.py", "audit_script"),
        (ROOT / "scripts" / "audit_transition_scope.py", "audit_script"),
    ]
    current = []
    missing = []
    for path, role in paths_with_roles:
        if not path.exists():
            missing.append(relative(path))
            continue
        current.append(
            {
                "role": role,
                "path": relative(path),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )

    manifest_path = ROOT / "outputs" / "scope_search_2026_09_22" / "INPUT_HASHES.json"
    manifest_rows = []
    manifest_failures = []
    if manifest_path.exists():
        for row in json.loads(manifest_path.read_text(encoding="utf-8")):
            path = ROOT / row["path"]
            observed_hash = sha256(path) if path.exists() else None
            match = observed_hash == row["sha256"]
            manifest_rows.append(
                {
                    "path": row["path"],
                    "recorded_sha256": row["sha256"],
                    "observed_sha256": observed_hash,
                    "match": match,
                }
            )
            if not match:
                manifest_failures.append(row["path"])
    return {
        "current_files": current,
        "missing_files": missing,
        "existing_input_manifest": {
            "path": relative(manifest_path),
            "rows": manifest_rows,
            "all_match": not manifest_failures and bool(manifest_rows),
            "mismatches": manifest_failures,
        },
        "verifier_script_sha256": sha256(Path(__file__).resolve()),
    }


def main() -> int:
    checks: list[dict[str, Any]] = []
    headline = verify_headline(checks)
    transition, analysis = verify_table10_and_consensus(checks)
    interaction = verify_interaction(checks, analysis)
    bootstrap = verify_bootstrap(checks, interaction, analysis)
    hashes = build_hash_record()
    record_check(
        checks,
        "provenance.existing_input_hash_manifest",
        bool(hashes["existing_input_manifest"]["all_match"]),
        "All entries in the saved transition input-hash manifest match current bytes.",
        hashes["existing_input_manifest"],
        {"all_match": True},
    )
    record_check(
        checks,
        "provenance.required_source_files_present",
        not hashes["missing_files"],
        "All raw, source-program, shipped-reference, and saved CSV/summary files used by this verifier are present.",
        {"missing_files": hashes["missing_files"]},
        {"missing_files": []},
    )

    passed = sum(row["status"] == "pass" for row in checks)
    failed = len(checks) - passed
    report = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "MPLCONFIGDIR=/private/tmp/yoetz-seminar-verifier-mpl python3 seminar_paper_drafts/verify_results.py",
        "working_directory": str(ROOT),
        "scope": "Narrow read-only verification of headline attendance, raw Table 10 reconstruction, consensus-W interaction, saved CSV provenance, and saved 9,999-draw wild-bootstrap p-values.",
        "software": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": stats.__version__ if hasattr(stats, "__version__") else package_version("scipy"),
            "matplotlib": package_version("matplotlib"),
            "MPLCONFIGDIR": os.environ.get("MPLCONFIGDIR"),
        },
        "summary": {
            "status": "pass" if failed == 0 else "fail",
            "checks_total": len(checks),
            "checks_passed": passed,
            "checks_failed": failed,
        },
        "headline_attendance": headline,
        "table10_and_consensus": transition,
        "main_interaction": interaction,
        "saved_wild_bootstrap": bootstrap,
        "checks": checks,
        "hashes": hashes,
        "limitations": [
            "This verifier does not rerun the 9,999-draw bootstrap; it checks the saved t-statistics and p-value arithmetic.",
            "It does not certify every original paper table, the structural model, or alternative learning extensions.",
            "Agreement with the operational last-open-check outcome does not remove the treatment-dependent observation and destination-coding limitations described in the paper.",
        ],
    }
    SOURCE_OUT.write_text(json.dumps(as_json(report), indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
