#!/usr/bin/env python3
"""Exploratory post-test total distribution contrasts.

The scope is locked in ``outputs/scope_search_2026_09_22/distribution/
scope_audit.md`` before this script computes any contrast. The sample is the
existing raw-data reconstruction from ``run_direction02_attrition`` with
baseline achievement, baseline writing status, and observed post-test total
required. Teacher-score availability is deliberately irrelevant to this
distributional family.

Only P25, P50, P75, and the IQR contrast are computed. P25 is the declared
primary contrast; the other three remain visible as secondary prespecified
contrasts. School pairs are resampled separately by treatment arm, retaining
all source observation rows for each selected school.

Run from the repository root with::

    python3 scripts/run_distribution_quantile_bootstrap.py

Only files beginning with ``distribution_`` are written under
``outputs/scope_search_2026_09_22/distribution``.
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


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "scope_search_2026_09_22" / "distribution"
SEED = 20260922
B = 9_999
QUANTILES = (0.25, 0.50, 0.75)


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


def quantile_values(values: np.ndarray) -> dict[float, float]:
    return {q: float(np.quantile(values, q, method="linear")) for q in QUANTILES}


def contrast_values(treated: np.ndarray, control: np.ndarray) -> dict[str, float]:
    treated_q = quantile_values(treated)
    control_q = quantile_values(control)
    contrasts = {
        "p25": treated_q[0.25] - control_q[0.25],
        "p50": treated_q[0.50] - control_q[0.50],
        "p75": treated_q[0.75] - control_q[0.75],
        "iqr": (treated_q[0.75] - treated_q[0.25])
        - (control_q[0.75] - control_q[0.25]),
    }
    return {key: float(value) for key, value in contrasts.items()}


def school_pair_bootstrap(
    data: pd.DataFrame, seed: int, repetitions: int
) -> pd.DataFrame:
    """Resample complete schools separately within treatment and control arms."""
    rng = np.random.default_rng(seed)
    school_rows: dict[float, dict[Any, np.ndarray]] = {}
    school_ids: dict[float, np.ndarray] = {}
    for arm in (0.0, 1.0):
        arm_data = data.loc[data["treat"] == arm].reset_index(drop=True)
        grouped = {
            school: group.index.to_numpy(dtype=int)
            for school, group in arm_data.groupby("schid", sort=False)
        }
        school_rows[arm] = grouped
        school_ids[arm] = np.asarray(list(grouped), dtype=object)

    rows: list[dict[str, float | int]] = []
    control_data = data.loc[data["treat"] == 0.0].reset_index(drop=True)
    treated_data = data.loc[data["treat"] == 1.0].reset_index(drop=True)
    for replicate in range(1, repetitions + 1):
        replicate_values: dict[float, list[np.ndarray]] = {0.0: [], 1.0: []}
        for arm, arm_data in ((0.0, control_data), (1.0, treated_data)):
            selected = rng.choice(school_ids[arm], size=len(school_ids[arm]), replace=True)
            for school in selected:
                replicate_values[arm].append(
                    arm_data.loc[school_rows[arm][school], "outcome_z"].to_numpy(dtype=float)
                )
        control = np.concatenate(replicate_values[0.0])
        treated = np.concatenate(replicate_values[1.0])
        values = contrast_values(treated, control)
        rows.append({"replicate": replicate, **values})
    return pd.DataFrame(rows)


def holm_adjust(p_values: dict[str, float]) -> dict[str, float]:
    """Holm step-down adjustment for the four visible contrasts."""
    ordered = sorted(p_values.items(), key=lambda item: (item[1], item[0]))
    adjusted: dict[str, float] = {}
    running_max = 0.0
    count = len(ordered)
    for rank, (name, p_value) in enumerate(ordered):
        running_max = max(running_max, min(1.0, (count - rank) * p_value))
        adjusted[name] = running_max
    return adjusted


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    scope_path = OUT / "scope_audit.md"
    if not scope_path.exists():
        raise FileNotFoundError(
            f"Locked scope audit is required before computation: {scope_path}"
        )

    sys.path.insert(0, str(ROOT / "scripts"))
    import run_direction02_attrition as attrition  # noqa: E402

    all_post, _, _ = attrition.prepare_data()
    mask = (
        all_post["baseline_observed"]
        & all_post["writing_observed"]
        & all_post["outcome_observed"]
        & all_post["outcome_z"].notna()
    )
    data = all_post.loc[mask, ["schid", "childno", "treat", "outcome_z"]].copy()
    data = data.reset_index(drop=True)
    if data.empty:
        raise ValueError("Locked distribution sample is empty")
    if data["treat"].nunique() != 2:
        raise ValueError("Locked distribution sample must contain both treatment arms")
    if data.groupby("schid")["treat"].nunique().max() != 1:
        raise ValueError("Treatment must be constant within school for school bootstrap")

    treated = data.loc[data["treat"] == 1.0, "outcome_z"].to_numpy(dtype=float)
    control = data.loc[data["treat"] == 0.0, "outcome_z"].to_numpy(dtype=float)
    observed = contrast_values(treated, control)
    bootstrap = school_pair_bootstrap(data, SEED, B)

    rows: list[dict[str, Any]] = []
    raw_p: dict[str, float] = {}
    for name in ("p25", "p50", "p75", "iqr"):
        values = bootstrap[name].to_numpy(dtype=float)
        estimate = observed[name]
        centered = values - estimate
        exceedances = int(np.count_nonzero(np.abs(centered) >= abs(estimate)))
        p_value = float((1 + exceedances) / (B + 1))
        raw_p[name] = p_value
        low, high = np.quantile(values, [0.025, 0.975], method="linear")
        rows.append(
            {
                "contrast": name,
                "role": "primary" if name == "p25" else "secondary",
                "estimate_treatment_minus_control": estimate,
                "bootstrap_se": float(values.std(ddof=1)),
                "ci95_percentile_low": float(low),
                "ci95_percentile_high": float(high),
                "centered_bootstrap_exceedances": exceedances,
                "centered_bootstrap_p_approx": p_value,
                "bootstrap_repetitions": B,
                "bootstrap_seed": SEED,
            }
        )
    adjusted = holm_adjust(raw_p)
    result = pd.DataFrame(rows)
    result["holm_p_approx"] = result["contrast"].map(adjusted)
    result.to_csv(OUT / "distribution_contrasts.csv", index=False)
    bootstrap.to_csv(OUT / "distribution_bootstrap.csv", index=False)

    group_rows: list[dict[str, Any]] = []
    for arm, label, values in [(0.0, "control", control), (1.0, "treatment", treated)]:
        q = quantile_values(values)
        group_rows.append(
            {
                "group": label,
                "treat": int(arm),
                "observation_rows": int(len(values)),
                "unique_school_child_keys": int(
                    data.loc[data["treat"] == arm, ["schid", "childno"]].drop_duplicates().shape[0]
                ),
                "schools": int(data.loc[data["treat"] == arm, "schid"].nunique()),
                "p25": q[0.25],
                "p50": q[0.50],
                "p75": q[0.75],
                "iqr": q[0.75] - q[0.25],
            }
        )
    pd.DataFrame(group_rows).to_csv(OUT / "distribution_group_quantiles.csv", index=False)

    input_hashes = attrition.raw_hashes()
    input_hashes.to_csv(OUT / "distribution_input_hashes.csv", index=False)

    unique_keys = int(data[["schid", "childno"]].drop_duplicates().shape[0])
    sample_summary = {
        "all_post_rows_before_locked_filter": int(len(all_post)),
        "analysis_observation_rows": int(len(data)),
        "unique_school_child_keys": unique_keys,
        "schools": int(data["schid"].nunique()),
        "control_observation_rows": int((data["treat"] == 0.0).sum()),
        "treatment_observation_rows": int((data["treat"] == 1.0).sum()),
        "control_schools": int(data.loc[data["treat"] == 0.0, "schid"].nunique()),
        "treatment_schools": int(data.loc[data["treat"] == 1.0, "schid"].nunique()),
        "teacher_score_filter_applied": False,
        "outcome": "outcome_z",
        "quantile_interpolation": "numpy_linear",
    }
    summary = {
        "scope": "post-test total-learning distribution",
        "scope_audit_sha256": sha256(scope_path),
        "primary_contrast": "p25",
        "contrasts": ["p25", "p50", "p75", "iqr"],
        "sample": sample_summary,
        "bootstrap": {
            "method": "school-pair resampling stratified by treatment arm, retaining all rows from selected schools",
            "repetitions": B,
            "seed": SEED,
            "ci": "95% percentile",
            "p_value": "approximate centered two-sided bootstrap p with +1 adjustment",
            "holm_family_size": 4,
        },
        "input_script": "scripts/run_direction02_attrition.py",
        "exploratory_status": "newly screened exploratory family; not confirmatory",
    }
    (OUT / "distribution_summary.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8"
    )

    metadata = {
        "command": "python3 scripts/run_distribution_quantile_bootstrap.py",
        "working_directory": str(ROOT),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "git_commit": git_commit(),
        "script_sha256": sha256(Path(__file__).resolve()),
        "attrition_script_sha256": sha256(ROOT / "scripts" / "run_direction02_attrition.py"),
        "scope_audit_sha256": sha256(scope_path),
        "seed": SEED,
        "bootstrap_repetitions": B,
        "sample": sample_summary,
        "no_individual_standard_errors": True,
        "no_rank_preservation_claim": True,
    }
    (OUT / "distribution_metadata.json").write_text(
        json.dumps(metadata, indent=2, default=str) + "\n", encoding="utf-8"
    )

    report_lines = [
        "# Post-test total-learning distribution contrasts",
        "",
        "This is the newly screened exploratory distribution family fixed in `scope_audit.md`; it is not confirmatory.",
        "",
        "## Locked sample and estimands",
        "",
        f"The sample contains **{len(data)} analysis observation rows**, **{unique_keys} unique school-child keys**, and **{data['schid'].nunique()} schools**. It includes rows with observed baseline achievement, observed baseline writing status, and an observed reconstructed post-test total. Teacher-score availability was not required or used. There are {int((data['treat'] == 0.0).sum())} control rows in {int(data.loc[data['treat'] == 0.0, 'schid'].nunique())} schools and {int((data['treat'] == 1.0).sum())} treatment rows in {int(data.loc[data['treat'] == 1.0, 'schid'].nunique())} schools.",
        "",
        "The prespecified contrasts are treatment minus control at P25, P50, and P75, and treatment IQR minus control IQR. P25 was fixed as primary before computation; the other three are secondary. Quantiles use NumPy's linear interpolation, and source rows and ties are retained.",
        "",
        "## Results",
        "",
        "The bootstrap uses separate school resampling within each treatment arm, carries every source row from each selected school, reports 95% percentile intervals and bootstrap standard deviations, and uses an approximate centered two-sided p-value with `(1 + exceedances)/(B + 1)`. Holm adjustment covers all four visible contrasts.",
        "",
    ]
    for row in rows:
        adjusted_p = adjusted[row["contrast"]]
        report_lines.append(
            f"- **{row['contrast']} ({row['role']})**: contrast **{row['estimate_treatment_minus_control']:.6f}**, bootstrap SE {row['bootstrap_se']:.6f}, 95% percentile CI [{row['ci95_percentile_low']:.6f}, {row['ci95_percentile_high']:.6f}], approximate centered p={row['centered_bootstrap_p_approx']:.4f}, Holm-adjusted p={adjusted_p:.4f}."
        )
    report_lines.extend(
        [
            "",
            f"The run used **{B}** school-pair bootstrap repetitions with fixed seed `{SEED}`. These p-values are descriptive bootstrap approximations for the prespecified contrasts. They do not provide individual-level standard errors, assert rank preservation, or identify a structural quantile treatment effect. Missing post-test observations and source-aligned repeated rows remain interpretation limits.",
            "",
            "## Reproduction",
            "",
            "Run `python3 scripts/run_distribution_quantile_bootstrap.py`. The locked scope is in `scope_audit.md`; exact replicate contrasts are in `distribution_bootstrap.csv`, and summaries, input hashes, and metadata are in the other `distribution_*` artifacts.",
        ]
    )
    (OUT / "distribution_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(json.dumps({"summary": summary, "contrasts": rows}, indent=2, default=str))


if __name__ == "__main__":
    main()
