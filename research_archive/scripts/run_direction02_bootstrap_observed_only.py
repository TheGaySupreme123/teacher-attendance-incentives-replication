#!/usr/bin/env python3
"""Observed-outcome-only wild-bootstrap check for Direction 0.2.

This is a bounded sensitivity run. It reuses ``run_direction02_attrition``'s
raw-data construction and keeps only ``R == 1``: eligible source rows whose
post verbal total is observed. It fits the same controlled interaction model
as the Direction 0.2 audit, with ``score_z`` as the teacher-score moderator,
and applies the same null-imposed school-cluster wild-bootstrap-t procedure as
``run_direction02_wildbootstrap.py``.

The restricted null drops only ``treat_score_z``; treatment's main effect and
all other terms remain in the restricted model. This is an inference
sensitivity for the existing observed rows, not a new outcome construction or
a new specification search.

Run from the repository root with::

    python3 scripts/run_direction02_bootstrap_observed_only.py

Only files beginning with ``bootstrap_observed_only_`` are written under
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


def main() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    import run_direction02_attrition as attrition  # noqa: E402
    import run_direction02_wildbootstrap as wild  # noqa: E402

    all_post, _, _ = attrition.prepare_data()
    observed = all_post.loc[all_post["R"].eq(1)].copy().reset_index(drop=True)
    outcome = "outcome_z"
    xvars = list(attrition.BASELINE_VARS)
    names = ["const"] + xvars
    interaction_index = names.index("treat_score_z")
    cols = ["schid", "childno", outcome] + xvars
    data = observed[cols].dropna().reset_index(drop=True)

    y = data[outcome].to_numpy(dtype=float)
    x_full = np.column_stack(
        [np.ones(len(data), dtype=float)]
        + [data[column].to_numpy(dtype=float) for column in xvars]
    )
    names = ["const"] + xvars
    restricted_indices = [index for index, name in enumerate(names) if name != "treat_score_z"]
    restricted_names = [names[index] for index in restricted_indices]
    x_restricted = x_full[:, restricted_indices]
    clusters = data["schid"].to_numpy()
    unique_school_child_keys = int(data[["schid", "childno"]].drop_duplicates().shape[0])

    full_fit = wild.cluster_fit(y, x_full, clusters)
    restricted_fit = wild.cluster_fit(y, x_restricted, clusters)
    observed_coef = float(full_fit["beta"][interaction_index])
    observed_se = float(full_fit["se"][interaction_index])
    observed_t = float(full_fit["t"][interaction_index])
    df = int(full_fit["clusters"] - 1)
    ci_90_crit = float(stats.t.ppf(0.95, df=df))
    ci_95_crit = float(stats.t.ppf(0.975, df=df))

    rng = np.random.default_rng(SEED)
    bootstrap_t, bootstrap_coef = wild.bootstrap_t_statistics(
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

    # Independently refit the first five multiplier draws and compare them to
    # the vectorized implementation. This verifies the null construction and
    # clustered sandwich calculation for this sensitivity sample.
    validation_rng = np.random.default_rng(SEED)
    unique_clusters, cluster_codes = np.unique(clusters, return_inverse=True)
    first_weights = validation_rng.choice(np.array([-1.0, 1.0]), size=(5, len(unique_clusters)))
    validation_rows: list[dict[str, Any]] = []
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
    validation_df.to_csv(OUT / "bootstrap_observed_only_validation.csv", index=False)
    t_df.to_csv(OUT / "bootstrap_observed_only_t_statistics.csv", index=False)

    summary = {
        "candidate": "post-test total score x continuous baseline teacher score",
        "outcome": outcome,
        "full_model": names,
        "restricted_model": restricted_names,
        "sample_rule": "R == 1 from run_direction02_attrition.prepare_data(): eligible observed-outcome rows only",
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
    }
    (OUT / "bootstrap_observed_only_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    metadata = {
        "command": "python3 scripts/run_direction02_bootstrap_observed_only.py",
        "working_directory": str(ROOT),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": __import__("scipy").__version__,
        "script_sha256": sha256(Path(__file__).resolve()),
        "attrition_script_sha256": sha256(ROOT / "scripts" / "run_direction02_attrition.py"),
        "wildbootstrap_script_sha256": sha256(ROOT / "scripts" / "run_direction02_wildbootstrap.py"),
        "git_commit": git_commit(),
        "seed": SEED,
        "bootstrap_repetitions": B,
        "batch_size": BATCH_SIZE,
        "sample_observation_rows": int(full_fit["n"]),
        "unique_school_child_keys": unique_school_child_keys,
        "sample_schools": int(full_fit["clusters"]),
        "vectorized_refit_validation_pass": validation_pass,
    }
    (OUT / "bootstrap_observed_only_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    report = f"""# Direction 0.2 observed-outcome-only wild-bootstrap check

This is a bounded sensitivity check using the existing raw-data construction in `scripts/run_direction02_attrition.py`. It retains only `R == 1`: eligible rows whose reconstructed source post verbal total is observed. No synthetic post-test outcome is assigned. The source-aligned sample's repeated records remain source observation units.

The regression is the same controlled Direction 0.2 interaction model, using the attrition script's `score_z` moderator, `treat_score_z`, treatment, and the original baseline controls. The null-imposed restricted model drops only `treat_score_z`, so the treatment main effect remains free. Inference uses school-level Rademacher multipliers and the same finite-sample clustered sandwich correction as the original bootstrap run.

## Results

- Interaction estimate: **{observed_coef:.6f} SD per teacher-score SD**.
- Clustered SE: **{observed_se:.6f}**; observed t = **{observed_t:.4f}**; {df} cluster degrees of freedom.
- Classical clustered two-sided p-value: **{2 * stats.t.sf(abs(observed_t), df=df):.4f}**.
- Null-imposed wild-bootstrap two-sided p-value: **{p_value:.4f}** ({int(extreme.sum())} of {B} bootstrap |t| values at least as large as the observed |t|; Monte Carlo SE **{mc_se:.4f}**).
- 90% t interval: **[{observed_coef - ci_90_crit * observed_se:.6f}, {observed_coef + ci_90_crit * observed_se:.6f}]**.
- 95% t interval: **[{observed_coef - ci_95_crit * observed_se:.6f}, {observed_coef + ci_95_crit * observed_se:.6f}]**.
- Sample: **{full_fit['n']} analysis observation rows in {full_fit['clusters']} schools**, corresponding to **{unique_school_child_keys} unique school-child keys**.

For comparison, the source-aligned result retains 1,646 analysis records in 103 schools and has interaction coefficient 0.128862, clustered SE 0.071129, and classical p=0.0730. The observed-outcome-only sensitivity uses 1,625 records in 101 schools; its coefficient is 0.132133 and its classical p-value is {2 * stats.t.sf(abs(observed_t), df=df):.4f}. The numerical results are therefore very similar, with the same substantive uncertainty.

The fixed seed is `{SEED}` and the run uses `{B}` bootstrap repetitions. The first five vectorized draws were independently refit; validation pass: **{validation_pass}**.

## Reproduction

Run `python3 scripts/run_direction02_bootstrap_observed_only.py` from the repository root. Exact bootstrap t statistics are in `bootstrap_observed_only_t_statistics.csv`; summary values, hashes, and validation are in the other `bootstrap_observed_only_*` artifacts.
"""
    (OUT / "bootstrap_observed_only_report.md").write_text(report, encoding="utf-8")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
