#!/usr/bin/env python3
"""Missing-outcome sensitivity for the Direction 0.2 learning extension.

This script uses the raw-data reconstruction in ``audit_learning_extension``.
It keeps the source reconstruction's row units (including repeated student
keys), reports those repeated keys explicitly, and does not impute a post-test
outcome.  The primary sensitivity starts with children whose original
baseline achievement and writing-status fields are observed and whose
pre-treatment teacher score is observed.  Post-test outcome observation is
then modeled from baseline variables, and one stabilized inverse-probability
weighting contrast is estimated for the same treatment-by-score regression.

Run from the repository root:

    python3 scripts/run_direction02_attrition.py

Only files beginning with ``attrition_`` are written to
``outputs/direction02_significance``.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import optimize, special, stats


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "direction02_significance"
sys.path.insert(0, str(ROOT / "scripts"))
import audit_learning_extension as audit  # noqa: E402


SEED = 20260922
BOOTSTRAPS = 999
BASELINE_VARS = [
    "treat",
    "score_z",
    "treat_score_z",
    "pre_total_v",
    "pre_total_w",
    "pre_writ",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_row_id(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["row_id"] = out.index.to_numpy()
    return out


def prepare_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build all-post rows, the source analytic rows, and score reference."""
    all_post, source_post = audit.prepare_postline()
    _, source_mid = audit.prepare_midline()

    # Carry the reconstruction's row identity through the score merge.  A
    # key-based merge would multiply the known repeated keys and misassign the
    # missingness state, so outcome values are mapped by this source row id.
    all_post = add_row_id(all_post)
    source_post = add_row_id(source_post)
    all_post["baseline_observed"] = (
        all_post["pre_total_v"].notna() | all_post["pre_total_w"].notna()
    )
    all_post["writing_observed"] = all_post["pre_writ"].notna()
    all_post["outcome_observed"] = all_post["post_total_v"].notna()

    all_scored, _ = audit.add_teacher_score(all_post.copy())
    post_scored, _ = audit.add_teacher_score(source_post.copy())
    post_outcome = post_scored.set_index("row_id")["z_add_post_total"]
    all_scored["outcome_z"] = all_scored["row_id"].map(post_outcome)

    # Match the existing extension's score reference: 107 score-observed
    # active schools pooled across the midline and post-test frames.
    scores = audit.score_reference(source_mid, source_post)
    score_mean = float(scores["teacher_score"].mean())
    score_sd = float(scores["teacher_score"].std(ddof=1))
    all_scored["score_z"] = (all_scored["teacher_score"] - score_mean) / score_sd
    all_scored["treat_score_z"] = all_scored["treat"] * all_scored["score_z"]

    # Match the source's baseline written-score scale and modality coding.  A
    # missing modality is a zero component by the source construction; no
    # post-test outcome is created here.
    all_scored["pre_total_w"] = all_scored["pre_total_w"] / 5
    for column in ["pre_total_v", "pre_total_w"]:
        all_scored[column] = all_scored[column].fillna(0)

    all_scored["eligible"] = (
        all_scored["baseline_observed"]
        & all_scored["writing_observed"]
        & all_scored["teacher_score"].notna()
    )
    # The eligible baseline cohort has no source-defined entry rows. Requiring
    # the actual post verbal total to be present keeps the outcome observed and
    # removes source rows that would otherwise acquire a zero by fillna(0).
    all_scored["R"] = (
        all_scored["eligible"]
        & all_scored["outcome_observed"]
        & all_scored["outcome_z"].notna()
    ).astype(float)
    all_scored.attrs["score_mean"] = score_mean
    all_scored.attrs["score_sd"] = score_sd
    all_scored.attrs["score_schools"] = int(scores["schid"].nunique())
    return all_scored, source_post, scores


def cluster_ols(
    frame: pd.DataFrame,
    outcome: str,
    xvars: list[str],
    weight_column: str | None = None,
    cluster_column: str = "schid",
) -> dict[str, Any]:
    """Weighted OLS with small-sample school-cluster sandwich covariance."""
    columns = [outcome, cluster_column] + xvars
    if weight_column is not None:
        columns.append(weight_column)
    data = frame[columns].dropna().copy()
    y = data[outcome].to_numpy(dtype=float)
    x = np.column_stack([np.ones(len(data))] + [data[col].to_numpy(dtype=float) for col in xvars])
    weights = (
        np.ones(len(data), dtype=float)
        if weight_column is None
        else data[weight_column].to_numpy(dtype=float)
    )
    xtwx = x.T @ (weights[:, None] * x)
    beta = np.linalg.solve(xtwx, x.T @ (weights * y))
    residual = y - x @ beta
    xtwx_inv = np.linalg.inv(xtwx)
    meat = np.zeros((x.shape[1], x.shape[1]))
    for _, group in data.groupby(cluster_column, sort=False):
        positions = data.index.get_indexer(group.index)
        score = x[positions].T @ (weights[positions] * residual[positions])
        meat += np.outer(score, score)
    n = len(data)
    k = x.shape[1]
    clusters = int(data[cluster_column].nunique())
    correction = (clusters / (clusters - 1)) * ((n - 1) / (n - k))
    covariance = correction * xtwx_inv @ meat @ xtwx_inv
    se = np.sqrt(np.maximum(np.diag(covariance), 0))
    df = clusters - 1
    t_stat = beta / se
    p_value = 2 * stats.t.sf(np.abs(t_stat), df=df)
    ci_crit = stats.t.ppf(0.975, df=df)
    return {
        "names": ["const"] + xvars,
        "beta": beta,
        "se": se,
        "p_value": p_value,
        "covariance": covariance,
        "n": int(n),
        "clusters": clusters,
        "df": int(df),
        "ci_crit": float(ci_crit),
        "data": data,
    }


def estimate_row(fit: dict[str, Any], term: str, model: str) -> dict[str, Any]:
    index = fit["names"].index(term)
    coefficient = float(fit["beta"][index])
    se = float(fit["se"][index])
    return {
        "model": model,
        "term": term,
        "coefficient": coefficient,
        "se_clustered": se,
        "p_value": float(fit["p_value"][index]),
        "ci_low": coefficient - fit["ci_crit"] * se,
        "ci_high": coefficient + fit["ci_crit"] * se,
        "n": fit["n"],
        "clusters": fit["clusters"],
    }


def logit_fit(x: np.ndarray, y: np.ndarray, start: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Fit an unpenalized logistic model with a deterministic fallback."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    def objective(beta: np.ndarray) -> float:
        eta = x @ beta
        return float(np.logaddexp(0, eta).sum() - y @ eta)

    def gradient(beta: np.ndarray) -> np.ndarray:
        return x.T @ (special.expit(x @ beta) - y)

    initial = np.zeros(x.shape[1], dtype=float) if start is None else np.asarray(start, dtype=float)
    result = optimize.minimize(
        objective,
        initial,
        jac=gradient,
        method="BFGS",
        options={"gtol": 1e-8, "maxiter": 300},
    )
    beta = np.asarray(result.x, dtype=float)
    grad_norm = float(np.max(np.abs(gradient(beta))))
    # BFGS can report precision loss after reaching a well-converged point.
    # The gradient criterion is the relevant check for the fitted probabilities.
    ok = bool(np.all(np.isfinite(beta)) and np.isfinite(grad_norm) and grad_norm < 1e-4)
    if not ok:
        # A bounded quasi-Newton retry is useful in bootstrap draws where a
        # school's duplicated rows create a poorly scaled Hessian.
        retry = optimize.minimize(
            objective,
            beta if np.all(np.isfinite(beta)) else initial,
            jac=gradient,
            method="L-BFGS-B",
            options={"ftol": 1e-13, "gtol": 1e-8, "maxiter": 500},
        )
        retry_beta = np.asarray(retry.x, dtype=float)
        retry_grad = float(np.max(np.abs(gradient(retry_beta))))
        if np.all(np.isfinite(retry_beta)) and retry_grad < grad_norm:
            beta, grad_norm = retry_beta, retry_grad
            ok = bool(np.isfinite(grad_norm) and grad_norm < 1e-4)
    probabilities = special.expit(x @ beta)
    return beta, probabilities, {
        "success": ok,
        "optimizer_success": bool(result.success),
        "message": str(result.message),
        "gradient_max_abs": grad_norm,
    }


def design_propensity(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
    """Add fixed geographic-block indicators to the pre-treatment design."""
    out = frame.copy()
    blocks = sorted(float(value) for value in out["block"].dropna().unique())
    block_columns: list[str] = []
    for block in blocks[1:]:
        column = f"block_{int(block)}"
        out[column] = (out["block"] == block).astype(float)
        block_columns.append(column)
    propensity_vars = BASELINE_VARS + block_columns
    return out, propensity_vars, block_columns


def weighted_interaction_arrays(
    x: np.ndarray, y: np.ndarray, weights: np.ndarray
) -> float:
    """Return the interaction coefficient for one bootstrap draw."""
    xtwx = x.T @ (weights[:, None] * x)
    beta = np.linalg.solve(xtwx, x.T @ (weights * y))
    return float(beta[3])  # const, treatment, score, treatment-by-score


def bootstrap_ipw(
    cohort: pd.DataFrame,
    propensity_vars: list[str],
    outcome_vars: list[str],
    seed: int,
    draws: int,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Whole-school bootstrap, refitting observation probabilities each draw."""
    cohort = cohort.reset_index(drop=True)
    rng = np.random.default_rng(seed)
    school_ids = cohort["schid"].drop_duplicates().to_numpy()
    school_rows = {
        school: group.index.to_numpy(dtype=int)
        for school, group in cohort.groupby("schid", sort=False)
    }
    propensity_x = np.column_stack(
        [np.ones(len(cohort))] + [cohort[column].to_numpy(dtype=float) for column in propensity_vars]
    )
    outcome_x = np.column_stack(
        [np.ones(len(cohort))] + [cohort[column].to_numpy(dtype=float) for column in outcome_vars]
    )
    y_observed = cohort["outcome_z"].to_numpy(dtype=float)
    observed = cohort["R"].to_numpy(dtype=float)
    results: list[dict[str, Any]] = []
    valid = 0
    for draw in range(draws):
        selected = rng.choice(school_ids, size=len(school_ids), replace=True)
        index_parts = [school_rows[school] for school in selected]
        index = np.concatenate(index_parts)
        x_prop = propensity_x[index]
        r = observed[index]
        x_out = outcome_x[index]
        y = y_observed[index]
        beta, probability, fit_meta = logit_fit(x_prop, r)
        if not fit_meta["success"] or not np.all(np.isfinite(probability)):
            results.append({"bootstrap_draw": draw, "estimate": np.nan, "valid": False})
            continue
        rate = float(r.mean())
        weight = rate / np.maximum(probability, np.finfo(float).eps)
        keep = (r == 1) & np.isfinite(y)
        try:
            estimate = weighted_interaction_arrays(x_out[keep], y[keep], weight[keep])
        except (np.linalg.LinAlgError, ValueError, FloatingPointError):
            estimate = np.nan
        is_valid = bool(np.isfinite(estimate))
        valid += int(is_valid)
        results.append(
            {
                "bootstrap_draw": draw,
                "estimate": estimate,
                "valid": is_valid,
                "probability_min": float(probability.min()),
                "probability_max": float(probability.max()),
                "gradient_max_abs": fit_meta["gradient_max_abs"],
                "beta_norm": float(np.linalg.norm(beta)),
            }
        )
    result_frame = pd.DataFrame(results)
    estimates = result_frame.loc[result_frame["valid"], "estimate"].to_numpy(dtype=float)
    if len(estimates):
        low, high = np.quantile(estimates, [0.025, 0.975])
        two_sided = 2 * min(float(np.mean(estimates <= 0)), float(np.mean(estimates >= 0)))
    else:
        low = high = two_sided = np.nan
    summary = {
        "requested_draws": int(draws),
        "valid_draws": int(valid),
        "invalid_draws": int(draws - valid),
        "bootstrap_seed": int(seed),
        "ci_low": float(low),
        "ci_high": float(high),
        "two_sided_sign_fraction_p": float(two_sided),
    }
    return result_frame, summary


def count_rowset(frame: pd.DataFrame, mask: pd.Series, label: str) -> dict[str, Any]:
    data = frame.loc[mask].copy()
    key_count = data[["schid", "childno"]].drop_duplicates().shape[0]
    return {
        "sample": label,
        "rows_source_units": int(len(data)),
        "unique_student_keys": int(key_count),
        "schools": int(data["schid"].nunique()),
        "control_rows": int((data["treat"] == 0).sum()),
        "treated_rows": int((data["treat"] == 1).sum()),
        "control_schools": int(data.loc[data["treat"] == 0, "schid"].nunique()),
        "treated_schools": int(data.loc[data["treat"] == 1, "schid"].nunique()),
        "post_outcome_observed_rows": int(data["outcome_observed"].sum()),
        "post_outcome_missing_rows": int((~data["outcome_observed"]).sum()),
        "teacher_score_missing_rows": int(data["teacher_score"].isna().sum()),
    }


def duplicate_report(frame: pd.DataFrame, masks: dict[str, pd.Series]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for label, mask in masks.items():
        data = frame.loc[mask].copy()
        duplicated = data[data.duplicated(["schid", "childno"], keep=False)]
        for (school, child), group in duplicated.groupby(["schid", "childno"], sort=True):
            rows.append(
                {
                    "sample": label,
                    "schid": school,
                    "childno": child,
                    "rows_for_key": len(group),
                    "outcome_observed_states": ",".join(str(int(v)) for v in sorted(group["outcome_observed"].unique())),
                    "stayer_states": ",".join(str(int(v)) for v in sorted(group["stayer"].unique())),
                    "baseline_observed_states": ",".join(str(int(v)) for v in sorted(group["baseline_observed"].unique())),
                    "teacher_score": group["teacher_score"].iloc[0],
                }
            )
    return pd.DataFrame(rows)


def missing_score_school_report(frame: pd.DataFrame) -> pd.DataFrame:
    mask = frame["baseline_observed"] & frame["writing_observed"] & frame["teacher_score"].isna()
    data = frame.loc[mask].copy()
    return (
        data.groupby("schid", as_index=False)
        .agg(
            treat=("treat", "first"),
            block=("block", "first"),
            baseline_rows=("schid", "size"),
            outcome_observed_rows=("outcome_observed", "sum"),
            outcome_missing_rows=("outcome_observed", lambda values: int((~values).sum())),
            unique_child_keys=("childno", "nunique"),
        )
        .sort_values("schid")
    )


def raw_hashes() -> pd.DataFrame:
    hashes = audit.write_hashes()
    hashes = hashes.copy()
    hashes["source"] = "audit_learning_extension.write_hashes"
    script_path = Path(audit.__file__).resolve()
    hashes = pd.concat(
        [
            hashes,
            pd.DataFrame(
                [
                    {
                        "kind": "audit_script",
                        "path": str(script_path.relative_to(ROOT)),
                        "bytes": script_path.stat().st_size,
                        "sha256": sha256(script_path),
                        "source": "audit_learning_extension",
                    },
                    {
                        "kind": "attrition_script",
                        "path": str(Path(__file__).resolve().relative_to(ROOT)),
                        "bytes": Path(__file__).resolve().stat().st_size,
                        "sha256": sha256(Path(__file__).resolve()),
                        "source": "run_direction02_attrition",
                    },
                ]
            ),
        ],
        ignore_index=True,
    )
    return hashes


def methods_report(
    counts: pd.DataFrame,
    observation: dict[str, Any],
    source_main: dict[str, Any],
    clean_main: dict[str, Any],
    ipw_row: dict[str, Any],
    diagnostics: pd.DataFrame,
    bootstrap_summary: dict[str, Any],
    duplicate_keys: pd.DataFrame,
    all_post: pd.DataFrame,
) -> str:
    score_missing = all_post["baseline_observed"] & all_post["writing_observed"] & all_post["teacher_score"].isna()
    source_repeated = duplicate_keys[duplicate_keys["sample"] == "source_score_complete"].shape[0]
    lines = [
        "# Direction 0.2 post-test attrition sensitivity",
        "",
        "This is a raw-data sensitivity audit for post-test total learning moderated by the continuous pre-treatment teacher score. It uses the reconstruction in `scripts/audit_learning_extension.py`; no synthetic post-test outcome is assigned to a row whose source post verbal total is missing.",
        "",
        "## Exact cohort and outcome rule",
        "",
        "The pre-treatment eligible cohort is the intersection of: an original baseline achievement total in either verbal or written baseline test, an observed baseline writing-status flag, and an observed teacher score. Teacher-score-missing records are excluded before fitting the observation model because the treatment-by-score estimand is undefined for them. This yields the score-complete baseline cohort shown in `attrition_counts.csv`.",
        "",
        "The outcome-observation indicator is one only when the reconstructed source `post_total_v` is observed and the normalized post total exists. This preserves the original source outcome construction for observed rows while excluding rows that would obtain a zero only through the source's later missing-value fill. The complete-case contrast uses exactly the same treatment, teacher-score, interaction, and baseline-control regression on the eligible cohort with this indicator equal to one.",
        "",
        "Repeated `(schid, childno)` keys are retained as source reconstruction units so the audit does not silently deduplicate or multiply them. Counts therefore report both source rows and unique student keys. The repeated keys are listed in `attrition_duplicate_keys.csv`; they are a measurement and interpretation limitation, not evidence of additional children.",
        "",
        "## Observation model",
        "",
        "A fixed linear-probability model predicts outcome observation from treatment, standardized teacher score, treatment-by-score, the original child baseline achievement components (`pre_total_v`, source-scaled `pre_total_w`), baseline writing status, and geographic-block indicators (smallest block omitted). Its treatment-by-score coefficient is reported with school-clustered small-sample uncertainty. A logistic version of the same fixed design supplies probabilities for the weighting sensitivity.",
        "",
        f"Treatment-by-score prediction of outcome observation: **{observation['coefficient']:.3f}** (clustered SE {observation['se_clustered']:.3f}, 95% CI {observation['ci_low']:.3f} to {observation['ci_high']:.3f}, p={observation['p_value']:.3f}, N={observation['n']}, schools={observation['clusters']}).",
        "",
        "## Main and IPW contrast",
        "",
        f"The source-compatible audited complete-case reference is {source_main['coefficient']:.3f} (SE {source_main['se_clustered']:.3f}, CI {source_main['ci_low']:.3f} to {source_main['ci_high']:.3f}, p={source_main['p_value']:.3f}, N={source_main['n']}, schools={source_main['clusters']}). It contains the source rows retained by the audited stayer rule, including rows whose post verbal total is missing and was later filled to zero by the source construction.",
        "",
        f"The no-synthetic-outcome complete-case estimate on the eligible cohort is {clean_main['coefficient']:.3f} (SE {clean_main['se_clustered']:.3f}, CI {clean_main['ci_low']:.3f} to {clean_main['ci_high']:.3f}, p={clean_main['p_value']:.3f}, N={clean_main['n']}, schools={clean_main['clusters']}).",
        "",
        f"The single IPW sensitivity uses stabilized weights `mean(R)/p_hat` for observed outcomes, where `p_hat` comes from the fixed baseline logistic design above. The weighted interaction is {ipw_row['coefficient']:.3f}; its conditional school-clustered SE is {ipw_row['se_conditional']:.3f} (conditional p={ipw_row['p_conditional']:.3f}). The whole-school bootstrap used {bootstrap_summary['valid_draws']} valid draws out of {bootstrap_summary['requested_draws']} with seed {bootstrap_summary['bootstrap_seed']}; its two-sided 95% percentile CI is {bootstrap_summary['ci_low']:.3f} to {bootstrap_summary['ci_high']:.3f}.",
        "",
        "The bootstrap refits the observation model and the weighted outcome regression in every whole-school draw, so the percentile interval includes probability-estimation uncertainty. The IPW result is not treated as statistically significant when this interval includes zero. The sensitivity relies on missing at random conditional on the fixed baseline design and on positivity; these assumptions are not testable from these data.",
        "",
        "## Diagnostics and limits",
        "",
        f"Among baseline records with an observed achievement and writing flag, {int(score_missing.sum())} rows across {int(all_post.loc[score_missing, 'schid'].nunique())} schools lack a teacher score and are outside the estimand. The fitted probabilities and stabilized weights are reported in `attrition_ipw_diagnostics.csv`; the smallest fitted probability and largest observed-outcome weight are shown there. No trimming or post hoc cutpoint selection was used.",
        "",
        f"The score-complete analytic sample contains {source_repeated} repeated student keys in the retained source rows. The duplicate-key report identifies conflicting or repeated source records. The package's school-level clustering remains the inference unit, but duplicated keys limit interpretation as a unique-child panel.",
        "",
        "Teacher score is an observed pre-treatment moderator, not a randomized treatment. The interaction describes heterogeneity by measured score and does not identify a causal effect of teacher quality. IPW can address measured outcome-selection differences only under the stated MAR and positivity assumptions; it does not recover outcomes for missing-score schools or prove that missingness has been resolved.",
        "",
        "Raw-input, source-program, shipped-reference, and script SHA-256 hashes are in `attrition_raw_hashes.csv`; run metadata and the exact command are in `attrition_run_metadata.json`.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    all_post, source_post, scores = prepare_data()
    cohort = all_post.loc[all_post["eligible"]].copy()
    cohort, propensity_vars, block_columns = design_propensity(cohort)

    # The fixed outcome model is the audited Table 9A moderator specification.
    clean_mask = cohort["R"] == 1
    clean_fit = cluster_ols(cohort.loc[clean_mask], "outcome_z", BASELINE_VARS)
    source_mask = (
        all_post["writing_observed"]
        & all_post["teacher_score"].notna()
        & all_post["stayer"].eq(1)
    )
    source_fit = cluster_ols(all_post.loc[source_mask], "outcome_z", BASELINE_VARS)

    observation_fit = cluster_ols(cohort, "R", propensity_vars)
    observation_row = estimate_row(observation_fit, "treat_score_z", "linear_probability_clustered")

    propensity_x = np.column_stack(
        [np.ones(len(cohort))] + [cohort[column].to_numpy(dtype=float) for column in propensity_vars]
    )
    response = cohort["R"].to_numpy(dtype=float)
    propensity_beta, probabilities, logit_meta = logit_fit(propensity_x, response)
    cohort["p_hat"] = probabilities
    cohort["stabilized_weight"] = response.mean() / np.maximum(probabilities, np.finfo(float).eps)
    observed = cohort["R"] == 1
    ipw_fit = cluster_ols(
        cohort.loc[observed],
        "outcome_z",
        BASELINE_VARS,
        weight_column="stabilized_weight",
    )
    ipw_index = ipw_fit["names"].index("treat_score_z")
    ipw_row = {
        "model": "stabilized_ipw_same_estimand",
        "term": "treat_score_z",
        "coefficient": float(ipw_fit["beta"][ipw_index]),
        "se_conditional": float(ipw_fit["se"][ipw_index]),
        "p_conditional": float(ipw_fit["p_value"][ipw_index]),
        "conditional_ci_low": float(ipw_fit["beta"][ipw_index] - ipw_fit["ci_crit"] * ipw_fit["se"][ipw_index]),
        "conditional_ci_high": float(ipw_fit["beta"][ipw_index] + ipw_fit["ci_crit"] * ipw_fit["se"][ipw_index]),
        "n_observed": int(ipw_fit["n"]),
        "clusters_observed": int(ipw_fit["clusters"]),
    }

    bootstrap_frame, bootstrap_summary = bootstrap_ipw(
        cohort,
        propensity_vars,
        BASELINE_VARS,
        seed=SEED,
        draws=BOOTSTRAPS,
    )
    ipw_row.update(
        {
            "bootstrap_requested": bootstrap_summary["requested_draws"],
            "bootstrap_valid": bootstrap_summary["valid_draws"],
            "bootstrap_ci_low": bootstrap_summary["ci_low"],
            "bootstrap_ci_high": bootstrap_summary["ci_high"],
            "bootstrap_two_sided_sign_fraction_p": bootstrap_summary["two_sided_sign_fraction_p"],
            "bootstrap_excludes_zero": bool(
                np.isfinite(bootstrap_summary["ci_low"])
                and np.isfinite(bootstrap_summary["ci_high"])
                and (bootstrap_summary["ci_low"] > 0 or bootstrap_summary["ci_high"] < 0)
            ),
        }
    )

    # Counts are deliberately split into source rows and unique student keys.
    counts = pd.DataFrame(
        [
            count_rowset(all_post, pd.Series(True, index=all_post.index), "all_post_after_source_exclusions"),
            count_rowset(all_post, all_post["baseline_observed"], "baseline_achievement_observed"),
            count_rowset(
                all_post,
                all_post["writing_observed"] & all_post["teacher_score"].notna(),
                "source_eligible_score_complete_including_no_baseline_total",
            ),
            count_rowset(all_post, all_post["eligible"], "baseline_achievement_score_complete_cohort"),
            count_rowset(all_post, all_post["eligible"] & all_post["R"].eq(1), "no_synthetic_outcome_complete_case"),
            count_rowset(
                all_post,
                all_post["writing_observed"] & all_post["teacher_score"].notna() & all_post["stayer"].eq(1),
                "source_compatible_audited_score_sample",
            ),
        ]
    )
    counts["score_reference_schools"] = int(scores["schid"].nunique())
    counts["score_reference_mean"] = float(all_post.attrs["score_mean"])
    counts["score_reference_sd"] = float(all_post.attrs["score_sd"])

    duplicate_keys = duplicate_report(
        all_post,
        {
            "baseline_achievement_score_complete": all_post["eligible"],
            "source_score_complete": source_mask,
            "observed_no_synthetic_outcome": all_post["eligible"] & all_post["R"].eq(1),
        },
    )
    missing_scores = missing_score_school_report(all_post)

    diagnostics_rows = [
        {"metric": "eligible_rows", "value": len(cohort)},
        {"metric": "eligible_schools", "value": cohort["schid"].nunique()},
        {"metric": "outcome_observed_rate", "value": cohort["R"].mean()},
        {"metric": "fitted_probability_min", "value": probabilities.min()},
        {"metric": "fitted_probability_p01", "value": np.quantile(probabilities, 0.01)},
        {"metric": "fitted_probability_p05", "value": np.quantile(probabilities, 0.05)},
        {"metric": "fitted_probability_median", "value": np.median(probabilities)},
        {"metric": "fitted_probability_p95", "value": np.quantile(probabilities, 0.95)},
        {"metric": "fitted_probability_p99", "value": np.quantile(probabilities, 0.99)},
        {"metric": "fitted_probability_max", "value": probabilities.max()},
        {"metric": "positivity_below_0_05", "value": int((probabilities < 0.05).sum())},
        {"metric": "positivity_above_0_95", "value": int((probabilities > 0.95).sum())},
        {"metric": "observed_weight_min", "value": cohort.loc[observed, "stabilized_weight"].min()},
        {"metric": "observed_weight_p01", "value": cohort.loc[observed, "stabilized_weight"].quantile(0.01)},
        {"metric": "observed_weight_median", "value": cohort.loc[observed, "stabilized_weight"].median()},
        {"metric": "observed_weight_p99", "value": cohort.loc[observed, "stabilized_weight"].quantile(0.99)},
        {"metric": "observed_weight_max", "value": cohort.loc[observed, "stabilized_weight"].max()},
        {
            "metric": "observed_weight_effective_sample_size",
            "value": float(
                cohort.loc[observed, "stabilized_weight"].sum() ** 2
                / (cohort.loc[observed, "stabilized_weight"] ** 2).sum()
            ),
        },
        {"metric": "logit_gradient_max_abs", "value": logit_meta["gradient_max_abs"]},
        {"metric": "logit_optimizer_success", "value": int(logit_meta["optimizer_success"])},
    ]
    diagnostics = pd.DataFrame(diagnostics_rows)

    estimate_table = pd.DataFrame(
        [
            observation_row,
            {"model": "source_compatible_audited_complete_case", **estimate_row(source_fit, "treat_score_z", "source_compatible_audited_complete_case")},
            {"model": "no_synthetic_outcome_complete_case", **estimate_row(clean_fit, "treat_score_z", "no_synthetic_outcome_complete_case")},
            ipw_row,
        ]
    )

    OUT.mkdir(parents=True, exist_ok=True)
    counts.to_csv(OUT / "attrition_counts.csv", index=False)
    duplicate_keys.to_csv(OUT / "attrition_duplicate_keys.csv", index=False)
    missing_scores.to_csv(OUT / "attrition_missing_score_schools.csv", index=False)
    diagnostics.to_csv(OUT / "attrition_ipw_diagnostics.csv", index=False)
    estimate_table.to_csv(OUT / "attrition_estimates.csv", index=False)
    bootstrap_frame.to_csv(OUT / "attrition_ipw_bootstrap.csv", index=False)
    hashes = raw_hashes()
    hashes.to_csv(OUT / "attrition_raw_hashes.csv", index=False)

    metadata = {
        "command": "python3 scripts/run_direction02_attrition.py",
        "working_directory": str(ROOT),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": __import__("scipy").__version__,
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "bootstrap_seed": SEED,
        "bootstrap_draws": BOOTSTRAPS,
        "propensity_variables": propensity_vars,
        "geographic_block_columns": block_columns,
        "score_reference_schools": int(scores["schid"].nunique()),
        "score_reference_mean": float(all_post.attrs["score_mean"]),
        "score_reference_sd": float(all_post.attrs["score_sd"]),
        "missing_at_random_assumption": "Outcome observation is independent of the unobserved post outcome conditional on treatment, score, treatment-by-score, observed baseline achievement/writing, and fixed geographic block.",
        "positivity_assumption": "Every eligible baseline row has a nonzero probability of an observed post outcome under the fixed design.",
        "bootstrap_summary": bootstrap_summary,
    }
    (OUT / "attrition_run_metadata.json").write_text(json.dumps(metadata, indent=2, default=str) + "\n", encoding="utf-8")

    report = methods_report(
        counts,
        observation_row,
        estimate_row(source_fit, "treat_score_z", "source_compatible_audited_complete_case"),
        estimate_row(clean_fit, "treat_score_z", "no_synthetic_outcome_complete_case"),
        ipw_row,
        diagnostics,
        bootstrap_summary,
        duplicate_keys,
        all_post,
    )
    (OUT / "attrition_methods.md").write_text(report, encoding="utf-8")

    print(json.dumps({"counts": counts.to_dict(orient="records"), "ipw": ipw_row, "bootstrap": bootstrap_summary}, indent=2, default=str))


if __name__ == "__main__":
    main()
