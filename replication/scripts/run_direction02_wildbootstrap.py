#!/usr/bin/env python3
"""Null-imposed school-cluster wild-bootstrap inference for Direction 0.2.

The data construction is imported from ``audit_learning_extension.py`` after
that script's Table 9 replication gate.  The only coefficient tested here is
the post-test-total-score by baseline-teacher-score interaction in the primary
controlled model:

    y = const + treat + teacher_score_z + treat_score_z
        + pre_total_v + pre_total_w + pre_writ + error

The null-imposed bootstrap drops only ``treat_score_z`` from the restricted
model.  Thus treatment's main effect remains free under the null; this is a
test of no moderation, not a sharp null of no treatment effect.  Rademacher
weights are shared by school, and all bootstrap standard errors use the same
finite-sample clustered sandwich correction as the primary audit.

Run from the repository root with::

    python3 scripts/run_direction02_wildbootstrap.py

Only files beginning with ``bootstrap_`` are written under
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
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "direction02_significance"

# Fixed and explicit so another researcher can reproduce the exact multiplier
# sequence.  The date is only a readable identifier; it is not a data choice.
SEED = 20260922
B = 9_999
BATCH_SIZE = 500


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None


def cluster_fit(y: np.ndarray, x: np.ndarray, clusters: np.ndarray) -> dict[str, Any]:
    """OLS and school-clustered sandwich covariance for one sample."""
    n, k = x.shape
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    residual = y - x @ beta
    xtx_inv = np.linalg.inv(x.T @ x)
    unique_clusters = pd.unique(clusters)
    meat = np.zeros((k, k), dtype=float)
    for cluster in unique_clusters:
        mask = clusters == cluster
        score = x[mask].T @ residual[mask]
        meat += np.outer(score, score)
    g = len(unique_clusters)
    correction = (g / (g - 1)) * ((n - 1) / (n - k))
    covariance = correction * xtx_inv @ meat @ xtx_inv
    se = np.sqrt(np.maximum(np.diag(covariance), 0.0))
    t_stat = beta / se
    return {
        "beta": beta,
        "residual": residual,
        "xtx_inv": xtx_inv,
        "covariance": covariance,
        "se": se,
        "t": t_stat,
        "n": n,
        "k": k,
        "clusters": g,
        "correction": correction,
    }


def bootstrap_t_statistics(
    y: np.ndarray,
    x_full: np.ndarray,
    x_restricted: np.ndarray,
    clusters: np.ndarray,
    beta_restricted: np.ndarray,
    interaction_index: int,
    rng: np.random.Generator,
    repetitions: int,
    batch_size: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Draw null-imposed school wild-bootstrap t statistics.

    Returns the t statistics and the corresponding interaction coefficients.
    The calculation is vectorized within batches, while the first five draws
    are independently re-fit in ``validate_against_direct_refits`` below.
    """
    n, k = x_full.shape
    unique_clusters, cluster_codes = np.unique(clusters, return_inverse=True)
    g = len(unique_clusters)
    x_full_t = x_full.T
    x_full_xtx_inv = np.linalg.inv(x_full_t @ x_full)
    restricted_mean = x_restricted @ beta_restricted
    restricted_fit = cluster_fit(y, x_restricted, clusters)
    restricted_residual = restricted_fit["residual"]
    correction = (g / (g - 1)) * ((n - 1) / (n - k))
    leverage_map = x_full_xtx_inv @ x_full_t
    beta_null_full = np.zeros(k, dtype=float)
    # Restricted columns preserve full-model order with the interaction
    # omitted, so map by the actual column positions rather than by prefix.
    restricted_positions = [i for i in range(k) if i != interaction_index]
    beta_null_full[restricted_positions] = beta_restricted

    t_values = np.empty(repetitions, dtype=float)
    coef_values = np.empty(repetitions, dtype=float)
    start = 0
    while start < repetitions:
        stop = min(start + batch_size, repetitions)
        current = stop - start
        weights = rng.choice(np.array([-1.0, 1.0]), size=(current, g))
        weighted_residual = restricted_residual[None, :] * weights[:, cluster_codes]
        y_star = restricted_mean[None, :] + weighted_residual

        # beta_star = (X'X)^(-1) X'y_star, with X fixed across draws.
        beta_star = beta_null_full[None, :] + weighted_residual @ leverage_map.T
        residual_star = y_star - beta_star @ x_full_t

        # Build each bootstrap meat matrix from school score vectors.  Keeping
        # only the current batch bounds memory while retaining exact algebra.
        meat = np.zeros((current, k, k), dtype=float)
        for cluster_code in range(g):
            mask = cluster_codes == cluster_code
            score = residual_star[:, mask] @ x_full[mask]
            meat += score[:, :, None] * score[:, None, :]
        covariance = correction * np.einsum(
            "ij,bjk,kl->bil", x_full_xtx_inv, meat, x_full_xtx_inv, optimize=True
        )
        se = np.sqrt(np.maximum(covariance[:, interaction_index, interaction_index], 0.0))
        t_values[start:stop] = beta_star[:, interaction_index] / se
        coef_values[start:stop] = beta_star[:, interaction_index]
        start = stop
    return t_values, coef_values


def direct_bootstrap_refit(
    y: np.ndarray,
    x_full: np.ndarray,
    x_restricted: np.ndarray,
    clusters: np.ndarray,
    beta_restricted: np.ndarray,
    weights: np.ndarray,
    interaction_index: int,
) -> tuple[float, float, float]:
    """Independent per-draw refit used to validate vectorized bootstrap math."""
    y_star = x_restricted @ beta_restricted + (y - x_restricted @ beta_restricted) * weights
    fit = cluster_fit(y_star, x_full, clusters)
    return (
        float(fit["beta"][interaction_index]),
        float(fit["se"][interaction_index]),
        float(fit["t"][interaction_index]),
    )


def build_primary_data() -> tuple[pd.DataFrame, list[str]]:
    # Import only after ROOT is known; this keeps the script runnable directly.
    sys.path.insert(0, str(ROOT))
    from scripts.audit_learning_extension import (  # pylint: disable=import-outside-toplevel
        extension_results,
        prepare_midline,
        prepare_postline,
    )

    _, mid = prepare_midline()
    _, post = prepare_postline()
    _, _, post_scored, _ = extension_results(mid, post)
    outcome = "z_add_post_total"
    xvars = [
        "treat",
        "teacher_score_z",
        "treat_score_z",
        "pre_total_v",
        "pre_total_w",
        "pre_writ",
    ]
    # Retain childno solely to report the distinction between aligned analysis
    # records and unique school-child keys. It is not an outcome or regressor.
    cols = ["schid", "childno", outcome] + xvars
    data = post_scored[cols].dropna().reset_index(drop=True)
    return data, [outcome] + xvars


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    data, model_columns = build_primary_data()
    outcome, *xvars = model_columns
    y = data[outcome].to_numpy(dtype=float)
    x_full = np.column_stack(
        [np.ones(len(data), dtype=float)]
        + [data[column].to_numpy(dtype=float) for column in xvars]
    )
    names = ["const"] + xvars
    interaction_index = names.index("treat_score_z")
    restricted_names = [name for name in names if name != "treat_score_z"]
    restricted_indices = [names.index(name) for name in restricted_names]
    x_restricted = x_full[:, restricted_indices]
    clusters = data["schid"].to_numpy()
    unique_school_child_keys = int(data[["schid", "childno"]].drop_duplicates().shape[0])

    full_fit = cluster_fit(y, x_full, clusters)
    restricted_fit = cluster_fit(y, x_restricted, clusters)
    observed_coef = float(full_fit["beta"][interaction_index])
    observed_se = float(full_fit["se"][interaction_index])
    observed_t = float(full_fit["t"][interaction_index])
    df = int(full_fit["clusters"] - 1)
    ci_90_crit = float(stats.t.ppf(0.95, df=df))
    ci_95_crit = float(stats.t.ppf(0.975, df=df))

    rng = np.random.default_rng(SEED)
    bootstrap_t, bootstrap_coef = bootstrap_t_statistics(
        y=y,
        x_full=x_full,
        x_restricted=x_restricted,
        clusters=clusters,
        beta_restricted=restricted_fit["beta"],
        interaction_index=interaction_index,
        rng=rng,
        repetitions=B,
        batch_size=BATCH_SIZE,
    )
    extreme = np.abs(bootstrap_t) >= abs(observed_t)
    p_value = float((1 + int(extreme.sum())) / (B + 1))
    mc_se = float(np.sqrt(p_value * (1 - p_value) / (B + 1)))

    # Generate the same first five multiplier draws independently and compare
    # their direct refits to the vectorized output.  This catches any mismatch
    # in the null construction, cluster indexing, or sandwich calculation.
    validation_rng = np.random.default_rng(SEED)
    unique_clusters, cluster_codes = np.unique(clusters, return_inverse=True)
    first_weights = validation_rng.choice(np.array([-1.0, 1.0]), size=(5, len(unique_clusters)))
    validation_rows: list[dict[str, Any]] = []
    restricted_residual = restricted_fit["residual"]
    for draw in range(5):
        weights_by_row = first_weights[draw, cluster_codes]
        direct_coef, direct_se, direct_t = direct_bootstrap_refit(
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
    validation_df = pd.DataFrame(validation_rows)
    validation_pass = bool(
        (validation_df["abs_t_difference"] < 1e-10).all()
        and (validation_df["abs_coefficient_difference"] < 1e-10).all()
    )

    t_df = pd.DataFrame(
        {
            "replicate": np.arange(1, B + 1),
            "wild_t_interaction": bootstrap_t,
            "interaction_coefficient": bootstrap_coef,
            "absolute_t": np.abs(bootstrap_t),
            "as_extreme_as_observed": extreme,
        }
    )
    t_df.to_csv(OUT / "bootstrap_t_statistics.csv", index=False)
    validation_df.to_csv(OUT / "bootstrap_validation.csv", index=False)

    summary = {
        "candidate": "post-test total score x continuous baseline teacher score",
        "outcome": outcome,
        "full_model": names,
        "restricted_model": restricted_names,
        "null": "treat_score_z = 0; treatment main effect and all other terms remain unrestricted",
        "inference": "null-imposed school-cluster wild bootstrap-t with Rademacher multipliers",
        "observed_coefficient": observed_coef,
        "observed_clustered_se": observed_se,
        "observed_t": observed_t,
        "classical_clustered_p_value": float(2 * stats.t.sf(abs(observed_t), df=df)),
        "wild_bootstrap_p_value": p_value,
        "wild_bootstrap_extreme_count": int(extreme.sum()),
        "bootstrap_repetitions": B,
        "bootstrap_seed": SEED,
        "bootstrap_monte_carlo_se": mc_se,
        "bootstrap_batch_size": BATCH_SIZE,
        "sample_observation_rows": int(full_fit["n"]),
        "unique_school_child_keys": unique_school_child_keys,
        "sample_schools": int(full_fit["clusters"]),
        "degrees_of_freedom": df,
        "cluster_correction": float(full_fit["correction"]),
        "ci_90": {
            "critical_value": ci_90_crit,
            "lower": observed_coef - ci_90_crit * observed_se,
            "upper": observed_coef + ci_90_crit * observed_se,
        },
        "ci_95": {
            "critical_value": ci_95_crit,
            "lower": observed_coef - ci_95_crit * observed_se,
            "upper": observed_coef + ci_95_crit * observed_se,
        },
        "vectorized_refit_validation_pass": validation_pass,
        "restricted_residual_mean": float(restricted_residual.mean()),
        "restricted_residual_sd": float(restricted_residual.std(ddof=1)),
    }
    (OUT / "bootstrap_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    metadata = {
        "command": "python3 scripts/run_direction02_wildbootstrap.py",
        "working_directory": str(ROOT),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": __import__("scipy").__version__,
        "script_sha256": sha256(Path(__file__).resolve()),
        "learning_audit_script_sha256": sha256(ROOT / "scripts" / "audit_learning_extension.py"),
        "git_commit": git_commit(),
        "seed": SEED,
        "bootstrap_repetitions": B,
        "batch_size": BATCH_SIZE,
        "sample_observation_rows": int(full_fit["n"]),
        "unique_school_child_keys": unique_school_child_keys,
        "sample_schools": int(full_fit["clusters"]),
        "vectorized_refit_validation_pass": validation_pass,
    }
    (OUT / "bootstrap_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    report = f"""# Direction 0.2 wild-bootstrap significance check

This bounded inference run uses the raw-data reconstruction and primary controlled model from `scripts/audit_learning_extension.py`. The replication gate for the original Table 9 specifications must be passed before interpreting this extension.

## Model and null

The outcome is post-test total score standardized as in the source analysis. The full model includes treatment, continuous baseline teacher score, their interaction, and the original baseline controls (`pre_total_v`, `pre_total_w`, and `pre_writ`). The null-imposed restricted model drops only the interaction; treatment's main effect remains in the model, so the test allows a nonzero average treatment effect.

Inference uses school-level Rademacher wild multipliers, one multiplier shared by all analysis records in a school, and the same finite-sample clustered sandwich correction as the primary estimate. It is a Studentized bootstrap-t test, with two-sided p-value `(1 + exceedances) / (B + 1)`.

## Results

- Interaction estimate: **{observed_coef:.6f} SD per teacher-score SD**.
- Clustered SE: **{observed_se:.6f}**; observed t = **{observed_t:.4f}**; {full_fit['clusters'] - 1} cluster degrees of freedom.
- Classical clustered two-sided p-value: **{2 * stats.t.sf(abs(observed_t), df=df):.4f}**.
- Null-imposed wild-bootstrap two-sided p-value: **{p_value:.4f}** ({int(extreme.sum())} of {B} bootstrap |t| values at least as large as the observed |t|; Monte Carlo SE **{mc_se:.4f}**).
- 90% t interval: **[{observed_coef - ci_90_crit * observed_se:.6f}, {observed_coef + ci_90_crit * observed_se:.6f}]**.
- 95% t interval: **[{observed_coef - ci_95_crit * observed_se:.6f}, {observed_coef + ci_95_crit * observed_se:.6f}]**.
- Complete-case sample: **{full_fit['n']} analysis observation rows in {full_fit['clusters']} schools**, corresponding to **{unique_school_child_keys} unique school-child keys**. The source-aligned sample is retained as constructed; this audit does not adjudicate whether reused keys represent duplicated measurements or distinct children.

The fixed seed is `{SEED}` and the run uses `{B}` bootstrap repetitions. The first five vectorized draws were independently refit observation-by-observation; validation pass: **{validation_pass}**.

The estimate is positive, but the bootstrap result should be reported with its p-value and interval rather than converted into a threshold claim. In particular, if the p-value is near 0.10, that is evidence compatible with a modestly positive moderation pattern while remaining uncertain under a conventional 5% standard.

## Reproduction

Run `python3 scripts/run_direction02_wildbootstrap.py` from the repository root. The exact bootstrap t statistics are in `bootstrap_t_statistics.csv`; summary values, seed, model, and validation are in `bootstrap_summary.json`, `bootstrap_metadata.json`, and `bootstrap_validation.csv`.
"""
    (OUT / "bootstrap_report.md").write_text(report, encoding="utf-8")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
