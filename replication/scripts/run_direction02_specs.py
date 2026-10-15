#!/usr/bin/env python3
"""Fixed Direction 0.2 significance checks for this follow-up.

This script uses the raw-data reconstruction functions in
``scripts/audit_learning_extension.py``.  It does not alter that audit or use
the shipped intermediate student files.  The post-test primary sample is
fixed once (complete cases for the post total, treatment, teacher score and
the three original child baseline controls); every post-test specification
below is estimated on that same 1,646-row/103-school sample.

The estimand is treatment-effect variation by the continuous, baseline
teacher-test score.  All standard errors are school-clustered and use the
same finite-sample correction as the audit.  The optional equal-school-weight
fit is explicitly a different estimand: it gives each school equal total
weight rather than each observed child equal weight.

Run from the repository root:

    python3 scripts/run_direction02_specs.py

Only ``specifications_*`` files are written to
``outputs/direction02_significance``.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
AUDIT_SOURCE = ROOT / "scripts" / "audit_learning_extension.py"
OUT = ROOT / "outputs" / "direction02_significance"
RAW = ROOT / "data" / "Incentives_FINAL" / "Raw-Data"
PROGRAMS = ROOT / "data" / "Incentives_FINAL" / "Programs"
SHIPPED = ROOT / "data" / "Incentives_FINAL" / "Output"

PRIMARY_TERMS = [
    "treat",
    "teacher_score_z",
    "treat_score_z",
    "pre_total_v",
    "pre_total_w",
    "pre_writ",
]
CHILD_BASELINE_TERMS = [
    "treat_pre_total_v",
    "treat_pre_total_w",
    "treat_pre_writ",
]
BLOCK_TERMS = ["block_2", "block_3", "block_4", "block_5"]
EXPECTED_MAIN = {"coefficient": 0.128862, "se_clustered": 0.071129}


def load_audit_module():
    spec = importlib.util.spec_from_file_location("audit_learning_extension", AUDIT_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {AUDIT_SOURCE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def add_score_variables(
    frame: pd.DataFrame, score_mean: float, score_sd: float
) -> pd.DataFrame:
    out = frame.copy()
    out["teacher_score_z"] = (out["teacher_score"] - score_mean) / score_sd
    out["treat_score_z"] = out["treat"] * out["teacher_score_z"]
    out["treat_pre_total_v"] = out["treat"] * out["pre_total_v"]
    out["treat_pre_total_w"] = out["treat"] * out["pre_total_w"]
    out["treat_pre_writ"] = out["treat"] * out["pre_writ"]
    return out


def add_geographic_block_dummies(frame: pd.DataFrame) -> pd.DataFrame:
    """Add geographic block indicators, using the first observed block as base."""
    out = frame.copy()
    observed = sorted(int(v) for v in out["block"].dropna().unique())
    expected = [1, 2, 3, 4, 5]
    if observed != expected:
        raise ValueError(f"Expected geographic blocks {expected}; observed {observed}")
    for block in expected[1:]:
        out[f"block_{block}"] = (out["block"] == block).astype(float)
    return out


def _check_numeric_design(x: np.ndarray, names: list[str]) -> tuple[int, float]:
    if not np.isfinite(x).all():
        raise ValueError("Design matrix contains non-finite values")
    rank = int(np.linalg.matrix_rank(x))
    if rank != x.shape[1]:
        dependent = ", ".join(names)
        raise ValueError(
            f"Rank-deficient design ({rank}/{x.shape[1]}): {dependent}"
        )
    condition = float(np.linalg.cond(x))
    if not np.isfinite(condition):
        raise ValueError("Design matrix has non-finite condition number")
    return rank, condition


def fit_cluster_ols(
    frame: pd.DataFrame,
    outcome: str,
    xvars: list[str],
    *,
    weights: pd.Series | None = None,
    sample_label: str,
) -> dict[str, Any]:
    """Fit OLS/WLS with school-clustered CR1 covariance.

    If weights are supplied, the fit minimizes sum_i w_i*u_i^2 and the
    cluster score is sum_i w_i*x_i*u_i.  Equal-school weights therefore sum
    to one within each school.  The finite-sample factor is the same
    G/(G-1)*(N-1)/(N-K) factor used by the audited unweighted regressions.
    """
    cols = [outcome, "schid"] + xvars
    work = frame[cols].copy()
    if weights is not None:
        work["_analysis_weight"] = weights.reindex(work.index)
        cols.append("_analysis_weight")
    work = work.dropna().copy()
    if work.empty:
        raise ValueError(f"Empty sample for {sample_label}")

    y = work[outcome].to_numpy(dtype=float)
    x = np.column_stack(
        [np.ones(len(work), dtype=float)]
        + [work[col].to_numpy(dtype=float) for col in xvars]
    )
    names = ["const"] + xvars
    rank, condition = _check_numeric_design(x, names)

    if weights is None:
        w = np.ones(len(work), dtype=float)
        weighting = "child_equal_weight"
    else:
        w = work["_analysis_weight"].to_numpy(dtype=float)
        if not np.isfinite(w).all() or (w <= 0).any():
            raise ValueError(f"Invalid analysis weights for {sample_label}")
        weighting = "equal_school_total_weight"

    x_weighted = x * np.sqrt(w)[:, None]
    y_weighted = y * np.sqrt(w)
    beta, _, weighted_rank, _ = np.linalg.lstsq(
        x_weighted, y_weighted, rcond=None
    )
    if int(weighted_rank) != x.shape[1]:
        raise ValueError(f"Weighted design is rank deficient for {sample_label}")
    residual = y - x @ beta
    xtwx = x.T @ (w[:, None] * x)
    bread = np.linalg.inv(xtwx)
    meat = np.zeros((x.shape[1], x.shape[1]), dtype=float)
    cluster_ids = work["schid"].to_numpy()
    for school in pd.unique(cluster_ids):
        mask = cluster_ids == school
        score = x[mask].T @ (w[mask] * residual[mask])
        meat += np.outer(score, score)

    n = len(work)
    k = x.shape[1]
    clusters = int(work["schid"].nunique())
    if clusters <= 1 or n <= k:
        raise ValueError(f"Insufficient degrees of freedom for {sample_label}")
    correction = (clusters / (clusters - 1)) * ((n - 1) / (n - k))
    covariance = correction * bread @ meat @ bread
    se = np.sqrt(np.maximum(np.diag(covariance), 0.0))
    if not np.isfinite(se).all() or (se <= 0).any():
        raise ValueError(f"Invalid clustered standard errors for {sample_label}")
    df = clusters - 1
    t_stat = beta / se
    p_value = 2 * stats.t.sf(np.abs(t_stat), df=df)
    critical = float(stats.t.ppf(0.975, df=df))
    y_centered = y - np.average(y, weights=w)
    weighted_sse = float(np.sum(w * residual**2))
    weighted_tss = float(np.sum(w * y_centered**2))
    r_squared = 1.0 - weighted_sse / weighted_tss if weighted_tss else np.nan
    return {
        "names": names,
        "beta": beta,
        "se": se,
        "p_value": p_value,
        "t_stat": t_stat,
        "covariance": covariance,
        "data": work,
        "n": int(n),
        "clusters": clusters,
        "df": int(df),
        "rank": rank,
        "n_parameters": int(k),
        "condition_number": condition,
        "critical": critical,
        "r_squared": float(r_squared),
        "weighting": weighting,
        "sample_label": sample_label,
    }


def coefficient_rows(
    fit: dict[str, Any], *, stage: str, model: str, estimand_note: str
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, term in enumerate(fit["names"]):
        coef = float(fit["beta"][index])
        se = float(fit["se"][index])
        rows.append(
            {
                "stage": stage,
                "model": model,
                "term": term,
                "coefficient": coef,
                "se_clustered": se,
                "t_stat": float(fit["t_stat"][index]),
                "p_value_two_sided_t": float(fit["p_value"][index]),
                "ci_low_95": coef - fit["critical"] * se,
                "ci_high_95": coef + fit["critical"] * se,
                "n_observations": fit["n"],
                "n_schools": fit["clusters"],
                "df_t": fit["df"],
                "rank": fit["rank"],
                "n_parameters": fit["n_parameters"],
                "condition_number": fit["condition_number"],
                "r_squared": fit["r_squared"],
                "weighting": fit["weighting"],
                "estimand_note": estimand_note,
            }
        )
    return rows


def contrast_row(
    fit: dict[str, Any],
    *,
    stage: str,
    model: str,
    label: str,
    score_raw: float,
    score_z: float,
    interaction_p: float,
) -> dict[str, Any]:
    """Formal treatment contrast beta[treat] + z*beta[treat_score_z]."""
    names = fit["names"]
    vector = np.zeros(len(names), dtype=float)
    vector[names.index("treat")] = 1.0
    vector[names.index("treat_score_z")] = score_z
    estimate = float(vector @ fit["beta"])
    variance = float(vector @ fit["covariance"] @ vector)
    if variance < -1e-12:
        raise ValueError(f"Negative contrast variance for {label}: {variance}")
    se = float(np.sqrt(max(variance, 0.0)))
    t_stat = estimate / se
    p_value = float(2 * stats.t.sf(abs(t_stat), df=fit["df"]))
    critical = fit["critical"]
    return {
        "stage": stage,
        "model": model,
        "term": f"marginal_treatment_effect_{label}",
        "teacher_score_raw": score_raw,
        "teacher_score_z": score_z,
        "coefficient": estimate,
        "se_clustered": se,
        "t_stat": t_stat,
        "p_value_two_sided_t": p_value,
        "ci_low_95": estimate - critical * se,
        "ci_high_95": estimate + critical * se,
        "interaction_p_value_two_sided_t": interaction_p,
        "interaction_significant_at_05": bool(interaction_p < 0.05),
        "n_observations": fit["n"],
        "n_schools": fit["clusters"],
        "df_t": fit["df"],
        "weighting": fit["weighting"],
        "estimand_note": "Formal linear contrast from the single primary fit; fixed school-score percentile.",
    }


def high_minus_low_row(
    fit: dict[str, Any],
    *,
    stage: str,
    model: str,
    low_raw: float,
    low_z: float,
    high_raw: float,
    high_z: float,
    interaction_p: float,
) -> dict[str, Any]:
    """Formal p75-minus-p25 contrast from the same primary fit.

    The treatment coefficient cancels algebraically, leaving the score
    interaction multiplied by the fixed difference in score z values.  No
    additional regression is estimated.
    """
    names = fit["names"]
    vector = np.zeros(len(names), dtype=float)
    vector[names.index("treat_score_z")] = high_z - low_z
    estimate = float(vector @ fit["beta"])
    variance = float(vector @ fit["covariance"] @ vector)
    if variance < -1e-12:
        raise ValueError(f"Negative high-minus-low variance: {variance}")
    se = float(np.sqrt(max(variance, 0.0)))
    t_stat = estimate / se
    p_value = float(2 * stats.t.sf(abs(t_stat), df=fit["df"]))
    if not np.isclose(p_value, interaction_p, rtol=0.0, atol=1e-12):
        raise AssertionError(
            f"High-minus-low p-value {p_value} does not match interaction p-value {interaction_p}"
        )
    critical = fit["critical"]
    return {
        "stage": stage,
        "model": model,
        "term": "marginal_treatment_effect_p75_minus_p25",
        "teacher_score_raw": np.nan,
        "teacher_score_z": np.nan,
        "teacher_score_raw_low": low_raw,
        "teacher_score_z_low": low_z,
        "teacher_score_raw_high": high_raw,
        "teacher_score_z_high": high_z,
        "coefficient": estimate,
        "se_clustered": se,
        "t_stat": t_stat,
        "p_value_two_sided_t": interaction_p,
        "ci_low_95": estimate - critical * se,
        "ci_high_95": estimate + critical * se,
        "interaction_p_value_two_sided_t": interaction_p,
        "interaction_significant_at_05": bool(interaction_p < 0.05),
        "n_observations": fit["n"],
        "n_schools": fit["clusters"],
        "df_t": fit["df"],
        "weighting": fit["weighting"],
        "estimand_note": "Formal p75-minus-p25 linear contrast from the single primary fit; no new fit estimated.",
    }


def input_hash_rows() -> pd.DataFrame:
    paths = [
        RAW / "Tests" / "Baseline" / "pre_verbal.dta",
        RAW / "Tests" / "Baseline" / "pre_written.dta",
        RAW / "Tests" / "Endline" / "post_verbal.dta",
        RAW / "Tests" / "Endline" / "post_written.dta",
        RAW / "Tests" / "Endline" / "normalization.dta",
        RAW / "Tests" / "treatschool.dta",
        RAW / "RandomCheck" / "Teacher-Attendance" / "teacher_test.dta",
        RAW / "Tests" / "BaselineChar.dta",
        PROGRAMS / "Table-9-Post.do",
        SHIPPED / "Table9A_post.csv",
        AUDIT_SOURCE,
    ]
    rows = []
    for path in paths:
        rows.append(
            {
                "kind": (
                    "raw_input"
                    if path.is_relative_to(RAW)
                    else "source_or_reference"
                ),
                "path": str(path.relative_to(ROOT)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    return pd.DataFrame(rows)


def format_p(value: float) -> str:
    return "<0.001" if value < 0.001 else f"{value:.3f}"


def write_methods_results(
    coefficients: pd.DataFrame,
    marginal: pd.DataFrame,
    loo: pd.DataFrame,
    metadata: dict[str, Any],
) -> None:
    primary_int = coefficients[
        (coefficients["model"] == "primary")
        & (coefficients["term"] == "treat_score_z")
    ].iloc[0]
    sensitivity_models = [
        "child_baseline_interactions",
        "geographic_block_fixed_effects",
        "child_baseline_interactions_plus_geographic_block_fixed_effects",
        "equal_school_weight_primary",
        "no_baseline_controls_same_sample",
        "data_quality_duplicate_key_exclusion",
    ]
    lines = [
        "# Direction 0.2 specification results",
        "",
        "## Question and fixed analysis sample",
        "",
        "The analysis asks whether the treatment effect on the post-test total learning score varies with the continuous baseline teacher-test score. The score is a pre-treatment school-level measure, standardized using the mean and sample standard deviation across the 107 score-observed schools used by the audited reconstruction. The primary post-test complete-case sample was fixed before fitting any specification: 1,646 observation rows in 103 schools, representing 1,631 unique `(schid, childno)` keys. Fifteen keys are repeated (30 rows). Every ordinary primary and post-test sensitivity model uses exactly those observations and schools; the separate duplicate-key data-quality sensitivity is explicitly reported on a reduced sample.",
        "",
        "The primary regression is post-test total score on treatment, standardized teacher score, their interaction, and the original child baseline controls (`pre_total_v`, `pre_total_w`, and `pre_writ`). The outcome and construction follow the raw-data audit; no subject-specific outcomes, score cutoffs, or outcome re-selection are used. The specification set was fixed for this follow-up after prior exploratory review; it was not preregistered.",
        "",
        "## Inference",
        "",
        "All fits use school-clustered CR1 standard errors with the audit's finite-sample factor G/(G-1) x (N-1)/(N-K). P-values and 95% intervals use a two-sided t distribution with G-1 school degrees of freedom. The coefficient table reports every estimated coefficient, including controls and geographic block indicators. Rank and condition checks are recorded for every fit.",
        "",
        f"The primary interaction is **{primary_int['coefficient']:.6f}** SD of learning per teacher-score SD (SE {primary_int['se_clustered']:.6f}, p={format_p(primary_int['p_value_two_sided_t'])}, 95% CI {primary_int['ci_low_95']:.6f} to {primary_int['ci_high_95']:.6f}; N={int(primary_int['n_observations'])}, G={int(primary_int['n_schools'])}). It reproduces the prior audited estimate 0.128862 (SE 0.071129) to rounding precision.",
        "",
        "## Fixed score-level treatment contrasts",
        "",
        "The marginal effects are formal linear contrasts from the same primary fit: treatment coefficient plus the interaction coefficient multiplied by the standardized teacher score. The school-score 25th percentile is a raw score of 27 (z = -0.6940); the 75th percentile is 41.75 (z = 0.7157).",
        "",
    ]
    percentile_rows = marginal[
        marginal["term"].isin(
            [
                "marginal_treatment_effect_p25_school_score",
                "marginal_treatment_effect_p75_school_score",
            ]
        )
    ]
    for _, row in percentile_rows.iterrows():
        lines.append(
            f"At the school-score **{row['term'].replace('marginal_treatment_effect_', '')}** (raw {row['teacher_score_raw']:.2f}, z {row['teacher_score_z']:.4f}), the treatment effect is **{row['coefficient']:.6f}** SD (SE {row['se_clustered']:.6f}, p={format_p(row['p_value_two_sided_t'])}, 95% CI {row['ci_low_95']:.6f} to {row['ci_high_95']:.6f})."
        )
    high_minus_low = marginal[
        marginal["term"] == "marginal_treatment_effect_p75_minus_p25"
    ].iloc[0]
    lines += [
        "",
        f"The formal high-minus-low contrast (p75 minus p25) is **{high_minus_low['coefficient']:.6f}** SD (SE {high_minus_low['se_clustered']:.6f}, p={format_p(high_minus_low['p_value_two_sided_t'])}, 95% CI {high_minus_low['ci_low_95']:.6f} to {high_minus_low['ci_high_95']:.6f}). Its p-value is exactly the interaction p-value because the treatment main effect cancels; no new fit is estimated. The interaction p-value is {format_p(float(primary_int['p_value_two_sided_t']))}. A significant marginal treatment effect at one fixed score percentile would therefore not by itself establish statistically significant heterogeneity; the heterogeneity claim is tested by the interaction coefficient and its confidence interval.",
        "",
        "## Sensitivities",
        "",
        "The child-composition sensitivity adds treatment interactions with all three original child baseline controls. The geographic-block specifications add indicators for blocks 2–5, with block 1 as the base; these are geographic block fixed effects and are not relabeled as randomized strata. The equal-school-weight fit gives each school total weight one, changing the estimand from the observation-weighted average treatment effect to an equal-school average. The no-baseline-controls model is a diagnostic on the same primary complete-case sample.",
        "",
    ]
    for model in sensitivity_models:
        row = coefficients[
            (coefficients["model"] == model)
            & (coefficients["term"] == "treat_score_z")
        ].iloc[0]
        lines.append(
            f"- `{model}`: interaction {row['coefficient']:.6f}, SE {row['se_clustered']:.6f}, p={format_p(row['p_value_two_sided_t'])}, 95% CI {row['ci_low_95']:.6f} to {row['ci_high_95']:.6f}; N={int(row['n_observations'])}, G={int(row['n_schools'])}."
        )
    lines += [
        "",
        "The data-quality sensitivity drops every row belonging to a repeated `(schid, childno)` key in the fixed post sample (15 keys, 30 rows), producing N=1,616 observations. This is a rule based on the full duplicate-key audit rather than a hand-picked exclusion. The IDs alone cannot establish whether these records are repeated measurements or identifier collisions, so the primary result retains the original audit-aligned rows and this result is reported as a sensitivity.",
        "",
        "The midline total-score model is secondary and uses its own audited midline complete-case sample (N=1,767 observations, G=107), with the same original baseline controls and score interaction. It is not pooled with the post-test specification.",
        "",
    ]
    secondary = coefficients[
        (coefficients["model"] == "secondary_midline_total")
        & (coefficients["term"] == "treat_score_z")
    ].iloc[0]
    lines.append(
        f"Secondary midline interaction: {secondary['coefficient']:.6f}, SE {secondary['se_clustered']:.6f}, p={format_p(secondary['p_value_two_sided_t'])}, 95% CI {secondary['ci_low_95']:.6f} to {secondary['ci_high_95']:.6f}; N={int(secondary['n_observations'])}, G={int(secondary['n_schools'])}."
    )
    lines += [
        "",
        "## Leave-one-school-out check",
        "",
        f"The primary specification was refit after omitting each of the {len(loo)} schools in turn. No school was selected for exclusion. Across all omissions, the interaction estimate ranges from {loo['coefficient'].min():.6f} to {loo['coefficient'].max():.6f}; the two-sided p-values range from {loo['p_value_two_sided_t'].min():.6f} to {loo['p_value_two_sided_t'].max():.6f}, with {int((loo['p_value_two_sided_t'] < 0.05).sum())} of {len(loo)} omissions yielding p<.05. The full per-school estimates, omitted-school identifiers, standard errors, p-values, intervals, sample sizes and rank checks are in `specifications_leave_one_school_out.csv`; no omission was used to select the reported result.",
        "",
        "## Limits",
        "",
        "Teacher score is observed before treatment but is not randomized, so the interaction is descriptive treatment-effect heterogeneity by an observed baseline measure. Teacher-score missingness and test attrition reduce the complete-case sample. The post-test high-score marginal effect is evidence that the treatment effect is positive at that fixed score level; it does not prove that the high-score effect differs from the low-score effect at the 5% level unless the interaction itself is significant.",
        "",
        "## Reproduction and provenance",
        "",
        f"Run `python3 scripts/run_direction02_specs.py` from `{ROOT}`. The raw input and source hashes, software versions, source audit hash, commit, sample definition, and specification list are recorded in `specifications_metadata.json` and `specifications_input_hashes.csv`. The article's Table 9B post panel reports N=1,760, while the released package/code Table9B_post reference reports N=1,624; this package/article discrepancy does not affect the primary Table 9A post reconstruction used here. Generated at {metadata['timestamp_utc']}.",
    ]
    (OUT / "specifications_methods_results.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    audit = load_audit_module()

    # Construct exactly the audited raw-data samples first.
    _, mid = audit.prepare_midline()
    _, post = audit.prepare_postline()
    mid, _ = audit.add_teacher_score(mid)
    post, _ = audit.add_teacher_score(post)
    scores = audit.score_reference(mid, post)
    score_mean = float(scores["teacher_score"].mean())
    score_sd = float(scores["teacher_score"].std(ddof=1))
    mid = add_score_variables(mid, score_mean, score_sd)
    post = add_score_variables(post, score_mean, score_sd)
    mid = add_geographic_block_dummies(mid)
    post = add_geographic_block_dummies(post)

    # Freeze the post complete-case sample once and reuse it for every primary
    # and sensitivity specification.
    post_required = (
        ["z_add_post_total", "schid", "childno"]
        + PRIMARY_TERMS
        + CHILD_BASELINE_TERMS
        + ["block"]
    )
    primary_sample = post[post_required].dropna().copy()
    if len(primary_sample) != 1646 or primary_sample["schid"].nunique() != 103:
        raise AssertionError(
            f"Unexpected fixed post sample: N={len(primary_sample)}, G={primary_sample['schid'].nunique()}"
        )
    primary_sample = add_geographic_block_dummies(primary_sample)
    primary_sample["school_child_key_count"] = primary_sample.groupby(
        ["schid", "childno"]
    )["schid"].transform("size")
    duplicate_free_sample = primary_sample[
        primary_sample["school_child_key_count"] == 1
    ].copy()
    duplicate_key_rows = int(len(primary_sample) - len(duplicate_free_sample))
    duplicate_keys = int(
        primary_sample.loc[primary_sample["school_child_key_count"] > 1, ["schid", "childno"]]
        .drop_duplicates()
        .shape[0]
    )
    if (len(duplicate_free_sample), duplicate_key_rows, duplicate_keys) != (1616, 30, 15):
        raise AssertionError(
            "Unexpected duplicate-key audit: "
            f"N={len(duplicate_free_sample)}, rows={duplicate_key_rows}, keys={duplicate_keys}"
        )
    for term in CHILD_BASELINE_TERMS:
        if term not in primary_sample:
            raise AssertionError(f"Missing child-composition term {term}")

    # All specifications below use the same fixed post sample.
    specs: list[tuple[str, list[str], pd.Series | None, str]] = [
        (
            "primary",
            PRIMARY_TERMS,
            None,
            "Observation-weighted post-test primary estimand; fixed complete-case sample.",
        ),
        (
            "child_baseline_interactions",
            PRIMARY_TERMS + CHILD_BASELINE_TERMS,
            None,
            "Observation-weighted post-test estimand with treatment interactions for all three original child baseline controls.",
        ),
        (
            "geographic_block_fixed_effects",
            PRIMARY_TERMS + BLOCK_TERMS,
            None,
            "Observation-weighted post-test estimand with geographic block fixed effects; block 1 is the base.",
        ),
        (
            "child_baseline_interactions_plus_geographic_block_fixed_effects",
            PRIMARY_TERMS + CHILD_BASELINE_TERMS + BLOCK_TERMS,
            None,
            "Observation-weighted post-test estimand with child baseline interactions and geographic block fixed effects.",
        ),
        (
            "equal_school_weight_primary",
            PRIMARY_TERMS,
            1.0 / primary_sample.groupby("schid")["schid"].transform("size"),
            "Equal-school-weight post-test estimand; each school's student weights sum to one, so this is a changed estimand.",
        ),
        (
            "no_baseline_controls_same_sample",
            ["treat", "teacher_score_z", "treat_score_z"],
            None,
            "Diagnostic observation-weighted post-test fit with no baseline controls, still restricted to the fixed primary complete-case sample.",
        ),
    ]

    coefficient_rows_all: list[dict[str, Any]] = []
    fits: dict[str, dict[str, Any]] = {}
    for model, terms, weights, note in specs:
        fit = fit_cluster_ols(
            primary_sample,
            "z_add_post_total",
            terms,
            weights=weights,
            sample_label=model,
        )
        fits[model] = fit
        coefficient_rows_all.extend(
            coefficient_rows(fit, stage="post", model=model, estimand_note=note)
        )

    # Data-quality sensitivity: remove all duplicated school-child keys as a
    # single rule.  No individual school or child key is chosen by outcome.
    duplicate_fit = fit_cluster_ols(
        duplicate_free_sample,
        "z_add_post_total",
        PRIMARY_TERMS,
        sample_label="data_quality_duplicate_key_exclusion",
    )
    fits["data_quality_duplicate_key_exclusion"] = duplicate_fit
    coefficient_rows_all.extend(
        coefficient_rows(
            duplicate_fit,
            stage="post_sensitivity",
            model="data_quality_duplicate_key_exclusion",
            estimand_note=(
                "Data-quality sensitivity: all rows belonging to any repeated "
                "(schid, childno) key dropped; no hand-picked exclusions."
            ),
        )
    )

    primary_interaction = coefficient_rows_all[
        next(
            i
            for i, row in enumerate(coefficient_rows_all)
            if row["model"] == "primary" and row["term"] == "treat_score_z"
        )
    ]
    if abs(primary_interaction["coefficient"] - EXPECTED_MAIN["coefficient"]) > 1e-6:
        raise AssertionError(
            f"Primary coefficient changed: {primary_interaction['coefficient']}"
        )
    if abs(primary_interaction["se_clustered"] - EXPECTED_MAIN["se_clustered"]) > 1e-6:
        raise AssertionError(f"Primary SE changed: {primary_interaction['se_clustered']}")

    # Fixed school-score percentiles are calculated from the school-level score
    # reference, then evaluated as formal contrasts from the one primary fit.
    p25_raw = float(scores["teacher_score"].quantile(0.25))
    p75_raw = float(scores["teacher_score"].quantile(0.75))
    p25_z = (p25_raw - score_mean) / score_sd
    p75_z = (p75_raw - score_mean) / score_sd
    marginal = pd.DataFrame(
        [
            contrast_row(
                fits["primary"],
                stage="post",
                model="primary",
                label="p25_school_score",
                score_raw=p25_raw,
                score_z=p25_z,
                interaction_p=primary_interaction["p_value_two_sided_t"],
            ),
            contrast_row(
                fits["primary"],
                stage="post",
                model="primary",
                label="p75_school_score",
                score_raw=p75_raw,
                score_z=p75_z,
                interaction_p=primary_interaction["p_value_two_sided_t"],
            ),
            high_minus_low_row(
                fits["primary"],
                stage="post",
                model="primary",
                low_raw=p25_raw,
                low_z=p25_z,
                high_raw=p75_raw,
                high_z=p75_z,
                interaction_p=primary_interaction["p_value_two_sided_t"],
            ),
        ]
    )

    # Secondary midline total model: its own complete cases, same original
    # baseline controls, explicitly labeled secondary.
    mid_required = ["z_add_mid_total", "schid"] + PRIMARY_TERMS
    mid_sample = mid[mid_required].dropna().copy()
    mid_fit = fit_cluster_ols(
        mid_sample,
        "z_add_mid_total",
        PRIMARY_TERMS,
        sample_label="secondary_midline_total",
    )
    coefficient_rows_all.extend(
        coefficient_rows(
            mid_fit,
            stage="midline_secondary",
            model="secondary_midline_total",
            estimand_note="Secondary midline total-score model with original child baseline controls; own complete-case sample.",
        )
    )

    # Every school is omitted once in the primary fit. No omission is used to
    # choose the reported result.
    loo_rows: list[dict[str, Any]] = []
    for omitted_school in sorted(primary_sample["schid"].unique()):
        loo_sample = primary_sample[primary_sample["schid"] != omitted_school].copy()
        fit = fit_cluster_ols(
            loo_sample,
            "z_add_post_total",
            PRIMARY_TERMS,
            sample_label=f"leave_one_school_out_{int(omitted_school)}",
        )
        idx = fit["names"].index("treat_score_z")
        coef = float(fit["beta"][idx])
        se = float(fit["se"][idx])
        loo_rows.append(
            {
                "omitted_school": int(omitted_school),
                "coefficient": coef,
                "se_clustered": se,
                "t_stat": float(fit["t_stat"][idx]),
                "p_value_two_sided_t": float(fit["p_value"][idx]),
                "ci_low_95": coef - fit["critical"] * se,
                "ci_high_95": coef + fit["critical"] * se,
                "n_observations": fit["n"],
                "n_schools": fit["clusters"],
                "df_t": fit["df"],
                "rank": fit["rank"],
                "n_parameters": fit["n_parameters"],
                "condition_number": fit["condition_number"],
                "weighting": fit["weighting"],
            }
        )
    loo = pd.DataFrame(loo_rows)

    coefficients = pd.DataFrame(coefficient_rows_all)
    hashes = input_hash_rows()
    timestamp = datetime.now(timezone.utc).isoformat()
    metadata = {
        "command": "python3 scripts/run_direction02_specs.py",
        "working_directory": str(ROOT),
        "timestamp_utc": timestamp,
        "python": sys.version,
        "platform": platform.platform(),
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "script_sha256": sha256(Path(__file__).resolve()),
        "audit_source_sha256": sha256(AUDIT_SOURCE),
        "git_commit": git_commit(),
        "primary_sample_rows": int(len(primary_sample)),
        "primary_unique_school_child_keys": int(
            primary_sample[["schid", "childno"]].drop_duplicates().shape[0]
        ),
        "primary_sample_schools": int(primary_sample["schid"].nunique()),
        "primary_treatment_rows": int(primary_sample["treat"].sum()),
        "primary_control_rows": int((1 - primary_sample["treat"]).sum()),
        "secondary_midline_rows": int(len(mid_sample)),
        "secondary_midline_schools": int(mid_sample["schid"].nunique()),
        "teacher_score_reference_schools": int(scores["schid"].nunique()),
        "teacher_score_mean": score_mean,
        "teacher_score_sd": score_sd,
        "teacher_score_p25_raw": p25_raw,
        "teacher_score_p25_z": p25_z,
        "teacher_score_p75_raw": p75_raw,
        "teacher_score_p75_z": p75_z,
        "duplicate_key_count_in_primary_sample": duplicate_keys,
        "duplicate_key_rows_dropped_in_sensitivity": duplicate_key_rows,
        "duplicate_free_sensitivity_rows": int(len(duplicate_free_sample)),
        "duplicate_free_sensitivity_schools": int(duplicate_free_sample["schid"].nunique()),
        "primary_interaction_expected": EXPECTED_MAIN,
        "primary_interaction_reproduced": {
            "coefficient": primary_interaction["coefficient"],
            "se_clustered": primary_interaction["se_clustered"],
        },
        "specifications": [model for model, _, _, _ in specs]
        + ["data_quality_duplicate_key_exclusion"]
        + ["secondary_midline_total"],
        "post_comparison_sample_frozen": True,
        "leave_one_school_out_count": int(len(loo)),
        "leave_one_school_out_p_min": float(loo["p_value_two_sided_t"].min()),
        "leave_one_school_out_p_max": float(loo["p_value_two_sided_t"].max()),
        "leave_one_school_out_p_lt_05_count": int(
            (loo["p_value_two_sided_t"] < 0.05).sum()
        ),
        "no_school_exclusion_selected": True,
        "analysis_status": "Fixed for this follow-up after prior exploratory review; not preregistered.",
        "article_table9b_post_n": 1760,
        "package_code_table9b_post_n": 1624,
        "table9a_post_primary_affected_by_table9b_discrepancy": False,
    }

    coefficients.to_csv(OUT / "specifications_coefficients.csv", index=False)
    marginal.to_csv(OUT / "specifications_marginal_effects.csv", index=False)
    loo.to_csv(OUT / "specifications_leave_one_school_out.csv", index=False)
    hashes.to_csv(OUT / "specifications_input_hashes.csv", index=False)
    (OUT / "specifications_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    write_methods_results(coefficients, marginal, loo, metadata)

    print(
        json.dumps(
            {
                "primary_interaction": primary_interaction,
                "marginal_effects": marginal.to_dict(orient="records"),
                "sensitivity_interactions": coefficients[
                    coefficients["term"] == "treat_score_z"
                ][
                    [
                        "model",
                        "coefficient",
                        "se_clustered",
                        "p_value_two_sided_t",
                        "n_observations",
                        "n_schools",
                    ]
                ].to_dict(orient="records"),
                "loo_range": [float(loo["coefficient"].min()), float(loo["coefficient"].max())],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
