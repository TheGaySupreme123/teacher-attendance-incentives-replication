#!/usr/bin/env python3
"""Run the frozen three-outcome Direction 0.2 learning family.

The family is recorded in
``outputs/scope_search_2026_09_22/learning/scope_family_plan.md`` before
estimation. It uses the strict observed-only post-test sample and the same
covariates for math, language, and total learning outcomes. It reports
individual and Holm-adjusted interaction tests, a same-school-covariance joint
math/language test, and the math-minus-language interaction contrast. The
corresponding geographic-block models are the only additional family member.
"""

from __future__ import annotations

import importlib.util
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "scope_search_2026_09_22" / "learning"
ATTRITION_SOURCE = ROOT / "scripts" / "run_direction02_attrition.py"
SPECS_SOURCE = ROOT / "scripts" / "run_direction02_specs.py"
PLAN = OUT / "scope_family_plan.md"

OUTCOMES = {
    "math": "z_add_post_math",
    "language": "z_add_post_lang",
    "total": "z_add_post_total",
}
BASE_TERMS = [
    "treat",
    "teacher_score_z",
    "treat_score_z",
    "pre_total_v",
    "pre_total_w",
    "pre_writ",
]
BLOCK_TERMS = ["block_2", "block_3", "block_4", "block_5"]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def holm_adjust(p_values: list[float]) -> list[float]:
    """Holm step-down adjusted p-values in original order."""
    values = np.asarray(p_values, dtype=float)
    order = np.argsort(values, kind="mergesort")
    sorted_values = values[order]
    m = len(values)
    adjusted_sorted = np.maximum.accumulate(
        np.minimum(1.0, (m - np.arange(m)) * sorted_values)
    )
    adjusted = np.empty(m, dtype=float)
    adjusted[order] = adjusted_sorted
    return adjusted.tolist()


def prepare_observed(attrition: Any, specs: Any) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_scored, source_post, scores = attrition.prepare_data()
    observed = all_scored.loc[all_scored["R"].eq(1)].copy()
    source_by_row = source_post.set_index("row_id")
    # Row-id mapping preserves the source reconstruction when school-child
    # identifiers repeat; no key-based merge is used here.
    for domain in OUTCOMES:
        observed[OUTCOMES[domain]] = observed["row_id"].map(
            source_by_row[OUTCOMES[domain]]
        )
    observed["teacher_score_z"] = observed["score_z"]
    observed["treat_score_z"] = observed["treat"] * observed["teacher_score_z"]
    observed = specs.add_geographic_block_dummies(observed)
    required = ["schid", "childno", "block"] + BASE_TERMS + list(OUTCOMES.values())
    if observed[required].isna().any().any():
        missing = observed[required].isna().sum()
        raise AssertionError(f"Strict observed sample has missing analysis fields: {missing[missing.gt(0)].to_dict()}")
    if len(observed) != 1625 or observed["schid"].nunique() != 101:
        raise AssertionError(
            f"Unexpected strict observed sample N={len(observed)}, G={observed['schid'].nunique()}"
        )
    return observed, scores


def multivariate_interaction_tests(
    frame: pd.DataFrame,
    outcomes: list[str],
    xvars: list[str],
    *,
    family: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Joint math/language Wald and their formal interaction difference.

    The two outcomes use the same design and rows.  The cross-outcome meat is
    built from paired school-level score vectors, so residual covariance within
    a school is retained in the 2x2 covariance of the interaction estimates.
    """
    columns = ["schid"] + xvars + outcomes
    data = frame[columns].dropna().copy()
    y = [data[outcome].to_numpy(dtype=float) for outcome in outcomes]
    x = np.column_stack(
        [np.ones(len(data), dtype=float)]
        + [data[var].to_numpy(dtype=float) for var in xvars]
    )
    names = ["const"] + xvars
    rank = int(np.linalg.matrix_rank(x))
    if rank != x.shape[1]:
        raise ValueError(f"Rank-deficient multivariate design {rank}/{x.shape[1]} for {family}")
    bread = np.linalg.inv(x.T @ x)
    residuals = [outcome - x @ np.linalg.lstsq(x, outcome, rcond=None)[0] for outcome in y]
    clusters = int(data["schid"].nunique())
    n = len(data)
    k = x.shape[1]
    correction = (clusters / (clusters - 1)) * ((n - 1) / (n - k))
    cluster_scores: list[list[np.ndarray]] = []
    for school, group in data.groupby("schid", sort=False):
        positions = data.index.get_indexer(group.index)
        cluster_scores.append(
            [x[positions].T @ residual[positions] for residual in residuals]
        )
    meat_blocks: dict[tuple[int, int], np.ndarray] = {}
    for left in range(2):
        for right in range(2):
            meat = np.zeros((x.shape[1], x.shape[1]), dtype=float)
            for scores in cluster_scores:
                meat += np.outer(scores[left], scores[right])
            meat_blocks[(left, right)] = meat
    cov_blocks = {
        (left, right): correction * bread @ meat_blocks[(left, right)] @ bread
        for left in range(2)
        for right in range(2)
    }
    interaction_index = names.index("treat_score_z")
    beta = np.array(
        [np.linalg.lstsq(x, outcome, rcond=None)[0][interaction_index] for outcome in y]
    )
    covariance = np.array(
        [
            [cov_blocks[(left, right)][interaction_index, interaction_index] for right in range(2)]
            for left in range(2)
        ]
    )
    if np.linalg.matrix_rank(covariance) != 2:
        raise ValueError(f"Singular interaction covariance for {family}: {covariance}")
    joint_wald = float(beta @ np.linalg.inv(covariance) @ beta)
    joint_f = joint_wald / 2.0
    joint_f_p = float(stats.f.sf(joint_f, 2, clusters - 1))
    joint_chi2_p = float(stats.chi2.sf(joint_wald, 2))
    difference = float(beta[0] - beta[1])
    difference_variance = float(
        covariance[0, 0] + covariance[1, 1] - 2 * covariance[0, 1]
    )
    if difference_variance <= 0:
        raise ValueError(f"Nonpositive difference variance for {family}: {difference_variance}")
    difference_se = float(np.sqrt(difference_variance))
    difference_t = difference / difference_se
    difference_p = float(2 * stats.t.sf(abs(difference_t), clusters - 1))
    critical = float(stats.t.ppf(0.975, clusters - 1))
    joint_row = {
        "family": family,
        "test": "joint_math_language_interactions",
        "math_interaction": float(beta[0]),
        "language_interaction": float(beta[1]),
        "cov_math_language": float(covariance[0, 1]),
        "corr_math_language": float(
            covariance[0, 1] / np.sqrt(covariance[0, 0] * covariance[1, 1])
        ),
        "wald_statistic_chi2": joint_wald,
        "wald_f_statistic": joint_f,
        "df_num": 2,
        "df_den": clusters - 1,
        "p_value_f": joint_f_p,
        "p_value_chi2": joint_chi2_p,
        "n_observations": int(n),
        "n_schools": clusters,
        "rank": rank,
        "n_parameters": int(k),
    }
    difference_row = {
        "family": family,
        "test": "math_minus_language_interaction",
        "math_interaction": float(beta[0]),
        "language_interaction": float(beta[1]),
        "estimate": difference,
        "se_clustered": difference_se,
        "t_stat": difference_t,
        "p_value_two_sided_t": difference_p,
        "ci_low_95": difference - critical * difference_se,
        "ci_high_95": difference + critical * difference_se,
        "cov_math_language": float(covariance[0, 1]),
        "corr_math_language": float(
            covariance[0, 1] / np.sqrt(covariance[0, 0] * covariance[1, 1])
        ),
        "df_t": clusters - 1,
        "n_observations": int(n),
        "n_schools": clusters,
        "rank": rank,
        "n_parameters": int(k),
    }
    return joint_row, difference_row


def p_fmt(p: float) -> str:
    return "<0.001" if p < 0.001 else f"{p:.4f}"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if not PLAN.exists():
        raise FileNotFoundError(f"Frozen family plan must exist before estimation: {PLAN}")
    attrition = load_module("direction02_attrition_scope", ATTRITION_SOURCE)
    specs = load_module("direction02_specs_scope", SPECS_SOURCE)
    observed, scores = prepare_observed(attrition, specs)

    coefficient_rows: list[dict[str, Any]] = []
    interaction_rows: list[dict[str, Any]] = []
    fits: dict[tuple[str, str], dict[str, Any]] = {}
    for family, xvars in [
        ("primary", BASE_TERMS),
        ("geographic_block_fixed_effects", BASE_TERMS + BLOCK_TERMS),
    ]:
        for domain, outcome in OUTCOMES.items():
            fit = specs.fit_cluster_ols(
                observed,
                outcome,
                xvars,
                sample_label=f"scope_{family}_{domain}",
            )
            fits[(family, domain)] = fit
            rows = specs.coefficient_rows(
                fit,
                stage="post_observed_only",
                model=family,
                estimand_note=(
                    "Frozen three-outcome domain family; same covariates and strict R=1 sample."
                ),
            )
            for row in rows:
                row["outcome_domain"] = domain
                row["outcome_variable"] = outcome
            coefficient_rows.extend(rows)
            interaction = next(row for row in rows if row["term"] == "treat_score_z")
            interaction_rows.append(
                {
                    "family": family,
                    "outcome_domain": domain,
                    "outcome_variable": outcome,
                    "term": "treat_score_z",
                    "coefficient": interaction["coefficient"],
                    "se_clustered": interaction["se_clustered"],
                    "t_stat": interaction["t_stat"],
                    "p_value_two_sided_t": interaction["p_value_two_sided_t"],
                    "ci_low_95": interaction["ci_low_95"],
                    "ci_high_95": interaction["ci_high_95"],
                    "n_observations": interaction["n_observations"],
                    "n_schools": interaction["n_schools"],
                    "df_t": interaction["df_t"],
                }
            )

    interaction_df = pd.DataFrame(interaction_rows)
    for family in interaction_df["family"].unique():
        mask = interaction_df["family"].eq(family)
        adjusted = holm_adjust(
            interaction_df.loc[mask, "p_value_two_sided_t"].astype(float).tolist()
        )
        interaction_df.loc[mask, "p_value_holm_three_outcomes"] = adjusted
    joint_rows: list[dict[str, Any]] = []
    for family, xvars in [
        ("primary", BASE_TERMS),
        ("geographic_block_fixed_effects", BASE_TERMS + BLOCK_TERMS),
    ]:
        joint, difference = multivariate_interaction_tests(
            observed,
            [OUTCOMES["math"], OUTCOMES["language"]],
            xvars,
            family=family,
        )
        joint_rows.extend([joint, difference])
    joint_df = pd.DataFrame(joint_rows)

    score_mean = float(scores["teacher_score"].mean())
    score_sd = float(scores["teacher_score"].std(ddof=1))
    plan_hash = specs.sha256(PLAN)
    metadata = {
        "command": "python3 scripts/run_scope_learning_family.py",
        "working_directory": str(ROOT),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "script_sha256": specs.sha256(Path(__file__).resolve()),
        "attrition_source_sha256": specs.sha256(ATTRITION_SOURCE),
        "specs_source_sha256": specs.sha256(SPECS_SOURCE),
        "plan_sha256": plan_hash,
        "observed_indicator": "R == 1 from run_direction02_attrition.prepare_data",
        "n_observations": int(len(observed)),
        "n_schools": int(observed["schid"].nunique()),
        "unique_school_child_keys": int(
            observed[["schid", "childno"]].drop_duplicates().shape[0]
        ),
        "repeated_school_child_rows": int(
            observed.duplicated(["schid", "childno"], keep=False).sum()
        ),
        "score_reference_schools": int(scores["schid"].nunique()),
        "score_mean": score_mean,
        "score_sd": score_sd,
        "outcomes": OUTCOMES,
        "base_terms": BASE_TERMS,
        "block_terms": BLOCK_TERMS,
        "multiplicity_adjustment": "Holm across exactly three domain interactions within each family",
        "joint_test": "math/language interaction Wald F(2,G-1) with same-school residual cross-covariance; chi-square p also reported",
        "no_cutoffs": True,
        "no_outcome_reselection": True,
        "analysis_status": "Frozen theory-led three-outcome family; individual results shown with Holm adjustment; no empirical model hunting.",
    }

    pd.DataFrame(coefficient_rows).to_csv(OUT / "scope_learning_coefficients.csv", index=False)
    interaction_df.to_csv(OUT / "scope_learning_interactions.csv", index=False)
    joint_df.to_csv(OUT / "scope_learning_joint_tests.csv", index=False)
    (OUT / "scope_learning_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Frozen three-outcome learning-family results",
        "",
        "The family was fixed in `scope_family_plan.md` before estimation. It broadens Direction 0.2 by asking whether continuous baseline teacher-score moderation differs across the existing math, language, and total learning outcomes. This is a scope analysis, not a novelty claim; paper overlap is assessed separately.",
        "",
        f"The strict observed-only sample is `R == 1` from `run_direction02_attrition.prepare_data`: N={len(observed)} observation rows, G={observed['schid'].nunique()} schools, and {observed[['schid', 'childno']].drop_duplicates().shape[0]} unique school-child keys. All outcomes use the same treatment, teacher-score, interaction, and three baseline controls. School-clustered inference uses two-sided t(G-1) p-values and 95% intervals.",
        "",
        "## Individual domain interactions",
        "",
    ]
    for _, row in interaction_df.iterrows():
        lines.append(
            f"- `{row['family']}` / **{row['outcome_domain']}**: interaction {row['coefficient']:.6f}, SE {row['se_clustered']:.6f}, raw p={p_fmt(row['p_value_two_sided_t'])}, Holm p={p_fmt(row['p_value_holm_three_outcomes'])}, 95% CI {row['ci_low_95']:.6f} to {row['ci_high_95']:.6f}."
        )
    lines += [
        "",
        "Holm adjustment is applied separately within the primary three-outcome family and within the corresponding geographic-block family. All three outcomes are shown regardless of significance.",
        "",
        "## Joint math/language tests and domain difference",
        "",
    ]
    for _, row in joint_df.iterrows():
        if row["test"] == "joint_math_language_interactions":
            lines.append(
                f"- `{row['family']}` joint math/language interaction test: Wald F={row['wald_f_statistic']:.6f}, F(2,{int(row['df_den'])}), p={p_fmt(row['p_value_f'])}; chi-square(2) p={p_fmt(row['p_value_chi2'])}. Same-school math-language residual covariance is {row['cov_math_language']:.8f} (correlation {row['corr_math_language']:.4f})."
            )
        else:
            lines.append(
                f"- `{row['family']}` math-minus-language interaction: {row['estimate']:.6f}, SE {row['se_clustered']:.6f}, t({int(row['df_t'])})={row['t_stat']:.6f}, p={p_fmt(row['p_value_two_sided_t'])}, 95% CI {row['ci_low_95']:.6f} to {row['ci_high_95']:.6f}."
            )
    lines += [
        "",
        "No score cutoff, school exclusion, subject-specific search beyond the fixed three-outcome family, outcome re-selection, or additional model was run. The geographic-block family is a corresponding pre-defined check with blocks 2--5 and block 1 as the base.",
        "",
        "Outputs are `scope_learning_coefficients.csv`, `scope_learning_interactions.csv`, `scope_learning_joint_tests.csv`, `scope_learning_metadata.json`, and this report. Hashes and the frozen family plan are recorded in the metadata and plan file.",
    ]
    (OUT / "scope_learning_methods_results.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
