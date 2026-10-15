#!/usr/bin/env python3
"""Reproducible raw-data audit for the learning-by-teacher-score extension.

This script reconstructs the Table 9 midline and post-test regressions from the
raw Stata files, compares the rounded estimates with the shipped Table 9 output,
and only then estimates the pre-specified exploratory moderator candidate:

    post-test total score = treatment x continuous baseline teacher score

The midline interaction is reported as a secondary check. No subject-specific
interaction search is performed here.

Run from the repository root with:

    python3 scripts/audit_learning_extension.py

Only files whose names begin with ``learning_`` are written below
``outputs/research_direction_audit``.
"""

from __future__ import annotations

import hashlib
import json
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "Incentives_FINAL" / "Raw-Data"
PROGRAMS = ROOT / "data" / "Incentives_FINAL" / "Programs"
SHIPPED_OUTPUT = ROOT / "data" / "Incentives_FINAL" / "Output"
OUT = ROOT / "outputs" / "research_direction_audit"

DROP_CLOSED = [1111, 1211, 5332, 5711, 2111, 5221, 5611]
DROP_CHILD = [(1113, None), (5731, 24)]
KEY = ["schid", "childno"]

MID_TABLE_EXPECTED = {
    "mid_writ": {"coef": 0.04, "se": 0.03, "n": 1893},
    "z_add_mid_math": {"coef": 0.15, "se": 0.07, "n": 1893},
    "z_add_mid_lang": {"coef": 0.16, "se": 0.06, "n": 1893},
    "z_add_mid_total": {"coef": 0.17, "se": 0.06, "n": 1893},
}
POST_TABLE_EXPECTED = {
    "post_writ": {"coef": 0.06, "se": 0.04, "n": 1760},
    "z_add_post_math": {"coef": 0.21, "se": 0.12, "n": 1760},
    "z_add_post_lang": {"coef": 0.16, "se": 0.08, "n": 1760},
    "z_add_post_total": {"coef": 0.17, "se": 0.09, "n": 1760},
}


def read_stata(path: Path) -> pd.DataFrame:
    return pd.read_stata(path, convert_categoricals=False)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def numeric_columns(frame: pd.DataFrame) -> list[str]:
    return [c for c in frame.columns if pd.api.types.is_numeric_dtype(frame[c])]


def recode_missing(frame: pd.DataFrame, sentinels: tuple[float, ...]) -> pd.DataFrame:
    """Match the midline/post merge recodes in the source do-files."""
    out = frame.copy()
    for col in numeric_columns(out):
        out[col] = out[col].mask(out[col].isin(sentinels))
    return out


def recode_post_to_zero(frame: pd.DataFrame, include_777: bool) -> pd.DataFrame:
    """Match the pre-total post-test recodes in Table-9-Post.do."""
    out = frame.copy()
    sentinels = [-999, -888, -777]
    if include_777:
        sentinels.append(777)
    for col in numeric_columns(out):
        values = out[col]
        out[col] = values.mask(values.isin(sentinels) | values.isna() | (values < 0), 0)
    return out


def sum_columns(frame: pd.DataFrame, columns: list[str]) -> pd.Series:
    return frame[columns].sum(axis=1)


def stata_merge(left: pd.DataFrame, right: pd.DataFrame, on: list[str], how: str = "outer") -> pd.DataFrame:
    """Pair duplicate keys like the legacy Stata merges in the package.

    A pandas many-to-many merge would create a Cartesian product for a handful
    of duplicate post-test keys and change the Table 9 sample. The released
    intermediate retains aligned duplicate records, so merge by within-key
    occurrence order before dropping the temporary occurrence column.
    """
    if how != "outer":
        raise ValueError("This audit only needs outer legacy merges")

    def grouped(frame: pd.DataFrame) -> dict[tuple[Any, ...], pd.DataFrame]:
        result: dict[tuple[Any, ...], pd.DataFrame] = {}
        for raw_key, group in frame.groupby(on, sort=False, dropna=False):
            key = raw_key if isinstance(raw_key, tuple) else (raw_key,)
            result[key] = group.reset_index(drop=True)
        return result

    left_groups = grouped(left)
    right_groups = grouped(right)
    keys = list(dict.fromkeys(list(left_groups) + list(right_groups)))
    right_nonkeys = [col for col in right.columns if col not in on]
    rows: list[dict[str, Any]] = []
    for key in keys:
        left_group = left_groups.get(key)
        right_group = right_groups.get(key)
        left_n = len(left_group) if left_group is not None else 0
        right_n = len(right_group) if right_group is not None else 0
        n_rows = max(left_n, right_n)
        for position in range(n_rows):
            row: dict[str, Any] = {}
            if left_group is not None:
                # When one side has one record and the other has multiple,
                # legacy many-to-one merge behavior repeats the singleton.
                left_position = position if left_n > 1 else 0
                row.update(left_group.iloc[left_position].to_dict())
            else:
                row.update(dict(zip(on, key)))
            if right_group is not None:
                right_position = position if right_n > 1 else 0
                right_row = right_group.iloc[right_position]
                for col in right_nonkeys:
                    row[col] = right_row[col]
            else:
                for col in right_nonkeys:
                    row[col] = np.nan
            rows.append(row)
    return pd.DataFrame(rows, columns=list(left.columns) + right_nonkeys)


def load_pretest() -> pd.DataFrame:
    verbal = read_stata(RAW / "Tests" / "Baseline" / "pre_verbal.dta")
    verbal = verbal.rename(
        columns={
            "total_1_to_4": "pre_math_v",
            "total_5_to_11": "pre_lang_v",
            "total": "pre_total_v",
        }
    )
    verbal["pre_writ"] = 0
    verbal = verbal[KEY + ["pre_math_v", "pre_lang_v", "pre_total_v", "pre_writ"]]

    written = read_stata(RAW / "Tests" / "Baseline" / "pre_written.dta")
    written = written.rename(
        columns={
            "total_1_to_4": "pre_math_w",
            "total_5_to_11": "pre_lang_w",
            "total": "pre_total_w",
        }
    )
    written["pre_writ"] = 1
    written = written[KEY + ["pre_math_w", "pre_lang_w", "pre_total_w", "pre_writ"]]

    # The source uses append, preserving both records for the few children who
    # appear in both baseline instruments.
    return pd.concat([verbal, written], ignore_index=True, sort=False)


def load_midline_outcomes() -> pd.DataFrame:
    verbal = read_stata(RAW / "Tests" / "Midline" / "mid_verbal.dta")
    verbal = verbal.rename(
        columns={
            "tot_1_to_4": "mid_math_v",
            "tot_5_to_11": "mid_lang_v",
            "total": "mid_total_v",
        }
    )
    verbal = verbal[KEY + ["mid_math_v", "mid_lang_v", "mid_total_v"]].copy()
    verbal["schid"] = verbal["schid"].replace({2493: 2492})

    written = read_stata(RAW / "Tests" / "Midline" / "mid_written.dta")
    written = written.rename(
        columns={
            "total_1_to_5": "mid_math_w",
            "total_6_to_16": "mid_lang_w",
            "total": "mid_total_w",
        }
    )
    written["mid_writ"] = 1
    written = written[KEY + ["mid_math_w", "mid_lang_w", "mid_total_w", "mid_writ"]].copy()
    written["schid"] = written["schid"].replace({2493: 2492})

    return stata_merge(verbal, written, KEY, how="outer")


POST_VERBAL_MATH = ["ques7", "ques8", "ques9", "ques10"]
POST_VERBAL_LANG = ["ques1", "ques2", "ques3", "ques4", "ques5", "ques6"]
POST_WRITTEN_MATH = [
    "_6a",
    "_6b",
    "_7a",
    "_7b",
    "_7c",
    "_8a",
    "_8b",
    "_8c",
    "_8d",
    "_8e",
    "_8f",
    "_8g",
    "_8h",
    "_9a",
    "_9b",
    "_9c",
    "_9d",
    "_9e",
    "_9f",
    "_9g",
    "_9h",
    "c62",
    "c63",
    "c64",
    "c65",
]
POST_WRITTEN_LANG = [
    "_1a",
    "_1b",
    "_1c",
    "_1d",
    "_1e",
    "_1f",
    "_1g",
    "_1h",
    "_1i",
    "_1j",
    "_2a",
    "_2b",
    "_2c",
    "_2d",
    "_2e",
    "_2f",
    "_2g",
    "_2h",
    "_2i",
    "_2j",
    "_3a",
    "_3b",
    "_3c",
    "_3d",
    "_3e",
    "_4a",
    "_4b",
    "_4c",
    "_4d",
    "_4e",
    "_4f",
    "_4g",
    "_5a",
    "_5b",
    "_5c",
    "_5d",
    "_5e",
]


def load_postline_outcomes() -> pd.DataFrame:
    verbal = recode_post_to_zero(
        read_stata(RAW / "Tests" / "Endline" / "post_verbal.dta"), include_777=False
    )
    verbal["post_math_v"] = 10 * sum_columns(verbal, POST_VERBAL_MATH) / 8
    verbal["post_lang_v"] = 10 * sum_columns(verbal, POST_VERBAL_LANG) / 12
    verbal["post_total_v"] = verbal["post_math_v"] + verbal["post_lang_v"]
    verbal = verbal.rename(columns={"idnum": "schid"})
    verbal = verbal[KEY + ["post_math_v", "post_lang_v", "post_total_v"]].copy()
    verbal["schid"] = verbal["schid"].replace({2493: 2492})

    written = recode_post_to_zero(
        read_stata(RAW / "Tests" / "Endline" / "post_written.dta"), include_777=True
    )
    written["post_math_w"] = 10 * sum_columns(written, POST_WRITTEN_MATH) / 45
    written["post_lang_w"] = 10 * sum_columns(written, POST_WRITTEN_LANG) / 55
    written["post_total_w"] = written["post_math_w"] + written["post_lang_w"]
    written = written.rename(columns={"sch_id": "schid", "ch_no_": "childno"})
    written["post_writ"] = 1
    written = written[KEY + ["post_math_w", "post_lang_w", "post_total_w", "post_writ"]].copy()
    written["schid"] = written["schid"].replace({2493: 2492})

    return stata_merge(verbal, written, KEY, how="outer")


def add_assignment_and_clean(tests: pd.DataFrame, pre_or_post: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Merge raw baseline data, assignment, and source-defined sample flags."""
    pre = load_pretest()
    combined = stata_merge(tests, pre, KEY, how="outer")

    # These are the three corrections made by both source Table 9 programs.
    combined.loc[(combined["schid"] == 4231) & (combined["childno"] == 3), "pre_math_w"] = 56
    combined.loc[(combined["schid"] == 3511) & (combined["childno"] == 17), "pre_total_v"] = 11
    combined.loc[(combined["schid"] == 4252) & (combined["childno"] == 22), "pre_total_w"] = 34

    combined = recode_missing(combined, (-999, -888, -777))

    treatment_ids = set(read_stata(RAW / "Tests" / "treatschool.dta")["schid"].tolist())
    combined["treat"] = combined["schid"].isin(treatment_ids).astype(float)
    combined["block"] = np.floor(combined["schid"] / 1000)

    # The source does not remove these records in Table 9 until after the
    # treatment merge. These exclusions are retained exactly.
    combined = combined[~combined["schid"].isin(DROP_CLOSED)].copy()
    combined = combined[combined["schid"] != 1113].copy()
    combined = combined[~((combined["schid"] == 5731) & (combined["childno"] == 24))].copy()

    if pre_or_post == "mid":
        outcome_col = "mid_total_v"
    else:
        outcome_col = "post_total_v"
    combined["entry"] = (
        combined["pre_total_v"].isna()
        & combined["pre_total_w"].isna()
        & combined[outcome_col].notna()
    ).astype(int)
    combined["missing"] = (
        (combined["pre_total_v"].notna() | combined["pre_total_w"].notna())
        & combined[outcome_col].isna()
    ).astype(int)
    combined["stayer"] = ((combined["missing"] == 0) & (combined["entry"] == 0)).astype(int)
    return combined, combined[combined["stayer"] == 1].copy()


def prepare_midline() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw_outcomes = load_midline_outcomes()
    all_rows, analytic = add_assignment_and_clean(raw_outcomes, "mid")
    written_cols = [
        "pre_math_w",
        "pre_lang_w",
        "pre_total_w",
        "mid_math_w",
        "mid_lang_w",
        "mid_total_w",
    ]
    for col in written_cols:
        analytic[col] = analytic[col] / 5
    score_cols = [
        "pre_math_v",
        "pre_lang_v",
        "pre_total_v",
        "pre_math_w",
        "pre_lang_w",
        "pre_total_w",
        "mid_math_v",
        "mid_lang_v",
        "mid_total_v",
        "mid_math_w",
        "mid_lang_w",
        "mid_total_w",
    ]
    analytic[score_cols] = analytic[score_cols].fillna(0)
    analytic["add_mid_math"] = analytic["mid_math_v"] + analytic["mid_math_w"]
    analytic["add_mid_lang"] = analytic["mid_lang_v"] + analytic["mid_lang_w"]
    analytic["add_mid_total"] = analytic["mid_total_v"] + analytic["mid_total_w"]
    for col in ["add_mid_math", "add_mid_lang", "add_mid_total"]:
        controls = analytic.loc[analytic["treat"] == 0, col]
        analytic[f"z_{col}"] = (analytic[col] - controls.mean()) / controls.std(ddof=1)
    analytic["mid_writ"] = analytic["mid_writ"].fillna(0)
    return all_rows, analytic


def prepare_postline() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw_outcomes = load_postline_outcomes()
    all_rows, analytic = add_assignment_and_clean(raw_outcomes, "post")
    written_cols = [
        "pre_math_w",
        "pre_lang_w",
        "pre_total_w",
    ]
    for col in written_cols:
        analytic[col] = analytic[col] / 5
    score_cols = [
        "pre_math_v",
        "pre_lang_v",
        "pre_total_v",
        "pre_math_w",
        "pre_lang_w",
        "pre_total_w",
        "post_math_v",
        "post_lang_v",
        "post_total_v",
        "post_math_w",
        "post_lang_w",
        "post_total_w",
    ]
    analytic[score_cols] = analytic[score_cols].fillna(0)
    analytic["add_post_math"] = analytic["post_math_v"] + analytic["post_math_w"]
    analytic["add_post_lang"] = analytic["post_lang_v"] + analytic["post_lang_w"]
    analytic["add_post_total"] = analytic["post_total_v"] + analytic["post_total_w"]

    normalization = read_stata(RAW / "Tests" / "Endline" / "normalization.dta")
    for outcome, normalizer in [
        ("add_post_math", "math_old"),
        ("add_post_lang", "lang_old"),
        ("add_post_total", "total_old"),
    ]:
        controls = normalization.loc[normalization[normalizer].notna(), normalizer]
        # The source computes these moments from the control observations in
        # the student data after merging normalization.dta.
        merged = analytic[["schid", "childno", "treat", outcome]].merge(
            normalization[["schid", "childno", normalizer]], on=KEY, how="left", sort=False
        )
        controls = merged.loc[(merged["treat"] == 0) & merged[normalizer].notna(), normalizer]
        analytic[f"z_{outcome}"] = (analytic[outcome] - controls.mean()) / controls.std(ddof=1)
    analytic["post_writ"] = analytic["post_writ"].fillna(0)
    return all_rows, analytic


def cluster_ols(frame: pd.DataFrame, outcome: str, xvars: list[str]) -> dict[str, Any]:
    cols = [outcome, "schid"] + xvars
    data = frame[cols].dropna().copy()
    y = data[outcome].to_numpy(dtype=float)
    x = np.column_stack([np.ones(len(data))] + [data[col].to_numpy(dtype=float) for col in xvars])
    names = ["const"] + xvars
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    residual = y - x @ beta
    xtx_inv = np.linalg.inv(x.T @ x)
    meat = np.zeros((x.shape[1], x.shape[1]))
    for _, group in data.groupby("schid", sort=False):
        positions = data.index.get_indexer(group.index)
        xu = x[positions].T @ residual[positions]
        meat += np.outer(xu, xu)
    n = len(data)
    k = x.shape[1]
    clusters = data["schid"].nunique()
    correction = (clusters / (clusters - 1)) * ((n - 1) / (n - k))
    covariance = correction * xtx_inv @ meat @ xtx_inv
    se = np.sqrt(np.diag(covariance))
    df = clusters - 1
    t_stat = beta / se
    p_value = 2 * stats.t.sf(np.abs(t_stat), df=df)
    ci_crit = stats.t.ppf(0.975, df=df)
    y_centered = y - y.mean()
    r2 = 1 - (residual @ residual) / (y_centered @ y_centered)
    return {
        "names": names,
        "beta": beta,
        "se": se,
        "p_value": p_value,
        "covariance": covariance,
        "n": int(n),
        "clusters": int(clusters),
        "df": int(df),
        "r2": float(r2),
        "ci_crit": float(ci_crit),
        "data": data,
    }


def result_row(stage: str, model: str, outcome: str, fit: dict[str, Any], term: str) -> dict[str, Any]:
    idx = fit["names"].index(term)
    coef = float(fit["beta"][idx])
    se = float(fit["se"][idx])
    crit = fit["ci_crit"]
    return {
        "stage": stage,
        "model": model,
        "outcome": outcome,
        "term": term,
        "coefficient": coef,
        "se_clustered": se,
        "p_value": float(fit["p_value"][idx]),
        "ci_low": coef - crit * se,
        "ci_high": coef + crit * se,
        "n": fit["n"],
        "clusters": fit["clusters"],
        "r_squared": fit["r2"],
    }


def parse_shipped_table(path: Path, outcomes: list[str]) -> dict[str, dict[str, Any]]:
    table = pd.read_csv(path)
    result: dict[str, dict[str, Any]] = {}
    for outcome, col in zip(outcomes, table.columns[1:]):
        coefficient = float(table.loc[1, col])
        se_match = re.search(r"-?\d+(?:\.\d+)?", str(table.loc[2, col]))
        se = float(se_match.group(0)) if se_match else np.nan
        n = int(float(table.loc[3, col]))
        r2 = float(table.loc[4, col])
        result[str(outcome)] = {"coef": coefficient, "se": se, "n": n, "r2": r2}
    return result


def source_replication_rows(mid: pd.DataFrame, post: pd.DataFrame) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    comparisons: list[dict[str, Any]] = []
    baseline_char = read_stata(RAW / "Tests" / "BaselineChar.dta")[["schid", "score", "infra"]]
    mid_with_controls = mid.merge(baseline_char, on="schid", how="left", sort=False)
    post_with_controls = post.merge(baseline_char, on="schid", how="left", sort=False)
    specs = {
        "mid_A": (
            mid,
            SHIPPED_OUTPUT / "Table9A_mid.csv",
            "table9A_raw_reconstruction",
            [
                ("mid_writ", ["treat", "pre_math_v", "pre_math_w", "pre_writ"]),
                ("z_add_mid_math", ["treat", "pre_math_v", "pre_math_w", "pre_writ"]),
                ("z_add_mid_lang", ["treat", "pre_lang_v", "pre_lang_w", "pre_writ"]),
                ("z_add_mid_total", ["treat", "pre_total_v", "pre_total_w", "pre_writ"]),
            ],
        ),
        "post_A": (
            post,
            SHIPPED_OUTPUT / "Table9A_post.csv",
            "table9A_raw_reconstruction",
            [
                ("post_writ", ["treat", "pre_math_v", "pre_math_w", "pre_writ"]),
                ("z_add_post_math", ["treat", "pre_math_v", "pre_math_w", "pre_writ"]),
                ("z_add_post_lang", ["treat", "pre_lang_v", "pre_lang_w", "pre_writ"]),
                ("z_add_post_total", ["treat", "pre_total_v", "pre_total_w", "pre_writ"]),
            ],
        ),
        "mid_B": (
            mid_with_controls,
            SHIPPED_OUTPUT / "Table9B_mid.csv",
            "table9B_raw_reconstruction",
            [
                ("mid_writ", ["treat", "pre_math_v", "pre_math_w", "pre_writ", "block", "score", "infra"]),
                ("z_add_mid_math", ["treat", "pre_math_v", "pre_math_w", "pre_writ", "block", "score", "infra"]),
                ("z_add_mid_lang", ["treat", "pre_lang_v", "pre_lang_w", "pre_writ", "block", "score", "infra"]),
                ("z_add_mid_total", ["treat", "pre_total_v", "pre_total_w", "pre_writ", "block", "score", "infra"]),
            ],
        ),
        "post_B": (
            post_with_controls,
            SHIPPED_OUTPUT / "Table9B_post.csv",
            "table9B_raw_reconstruction",
            [
                ("post_writ", ["treat", "pre_math_v", "pre_math_w", "pre_writ", "block", "score", "infra"]),
                ("z_add_post_math", ["treat", "pre_math_v", "pre_math_w", "pre_writ", "block", "score", "infra"]),
                ("z_add_post_lang", ["treat", "pre_lang_v", "pre_lang_w", "pre_writ", "block", "score", "infra"]),
                ("z_add_post_total", ["treat", "pre_total_v", "pre_total_w", "pre_writ", "block", "score", "infra"]),
            ],
        ),
    }
    for spec_name, (data, shipped_path, model_name, model_specs) in specs.items():
        stage = "mid" if spec_name.startswith("mid") else "post"
        shipped = parse_shipped_table(shipped_path, [outcome for outcome, _ in model_specs])
        for outcome, xvars in model_specs:
            fit = cluster_ols(data, outcome, xvars)
            rows.extend(result_row(stage, model_name, outcome, fit, "treat") for _ in [0])
            expected = shipped[outcome]
            raw_coef = float(fit["beta"][fit["names"].index("treat")])
            raw_se = float(fit["se"][fit["names"].index("treat")])
            raw_n = fit["n"]
            raw_r2 = fit["r2"]
            core_estimate_match = (
                round(raw_coef, 2) == round(expected["coef"], 2)
                and round(raw_se, 2) == round(expected["se"], 2)
                and raw_n == expected["n"]
            )
            r2_display_match = abs(raw_r2 - expected["r2"]) <= 0.0101
            rounded_match = core_estimate_match and r2_display_match
            comparisons.append(
                {
                    "stage": stage,
                    "outcome": outcome,
                    "shipped_output": str(shipped_path.relative_to(ROOT)),
                    "raw_coefficient": raw_coef,
                    "shipped_coefficient_rounded": expected["coef"],
                    "coefficient_difference": raw_coef - expected["coef"],
                    "raw_se_clustered": raw_se,
                    "shipped_se_rounded": expected["se"],
                    "se_difference": raw_se - expected["se"],
                    "raw_n": raw_n,
                    "shipped_n": expected["n"],
                    "raw_r_squared": raw_r2,
                    "shipped_r_squared_rounded": expected["r2"],
                    "r_squared_difference": raw_r2 - expected["r2"],
                    "core_estimate_match": core_estimate_match,
                    "r_squared_display_match_within_0_01": r2_display_match,
                    "rounded_match": rounded_match,
                }
            )
    return rows, comparisons


def add_teacher_score(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    teacher = read_stata(RAW / "RandomCheck" / "Teacher-Attendance" / "teacher_test.dta")
    score_columns = [
        "comp1",
        "comp2",
        "comp3",
        "clozet",
        "story",
        "attitude",
        "nnc1",
        "nc1",
        "nc2",
        "nnc2",
        "nnc3",
        "nc3",
        "vp",
        "map",
    ]
    teacher["teacher_score"] = teacher[score_columns].sum(axis=1)
    teacher = teacher[["schid", "teacher_score"]].drop_duplicates("schid")

    # BaselineChar is not used for the estimates. It is checked as a source
    # crosswalk because the original Table 2 code derives the score from the
    # teacher_test item columns.
    baseline_char = read_stata(RAW / "Tests" / "BaselineChar.dta")[["schid", "score"]]
    crosswalk = teacher.merge(baseline_char, on="schid", how="outer", indicator=True)
    crosswalk["difference"] = crosswalk["teacher_score"] - crosswalk["score"]

    out = frame.merge(teacher, on="schid", how="left", sort=False)
    return out, crosswalk


def score_reference(frame_mid: pd.DataFrame, frame_post: pd.DataFrame) -> pd.DataFrame:
    school_ids = set(pd.concat([frame_mid[["schid"]], frame_post[["schid"]]], ignore_index=True)["schid"].dropna())
    teacher = read_stata(RAW / "RandomCheck" / "Teacher-Attendance" / "teacher_test.dta")
    score_columns = [
        "comp1",
        "comp2",
        "comp3",
        "clozet",
        "story",
        "attitude",
        "nnc1",
        "nc1",
        "nc2",
        "nnc2",
        "nnc3",
        "nc3",
        "vp",
        "map",
    ]
    teacher["teacher_score"] = teacher[score_columns].sum(axis=1)
    scores = teacher[teacher["schid"].isin(school_ids)][["schid", "teacher_score"]].drop_duplicates("schid")
    scores = scores[scores["teacher_score"].notna()].copy()
    treatment_ids = set(read_stata(RAW / "Tests" / "treatschool.dta")["schid"].tolist())
    scores["treat"] = scores["schid"].isin(treatment_ids).astype(float)
    mean = scores["teacher_score"].mean()
    sd = scores["teacher_score"].std(ddof=1)
    scores["teacher_score_z"] = (scores["teacher_score"] - mean) / sd
    scores["score_tercile"] = pd.qcut(scores["teacher_score"].rank(method="first"), 3, labels=["low", "middle", "high"])
    return scores


def extension_results(mid: pd.DataFrame, post: pd.DataFrame) -> tuple[list[dict[str, Any]], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    mid, _ = add_teacher_score(mid)
    post, _ = add_teacher_score(post)
    scores = score_reference(mid, post)
    score_mean = scores["teacher_score"].mean()
    score_sd = scores["teacher_score"].std(ddof=1)
    for frame in [mid, post]:
        frame["teacher_score_z"] = (frame["teacher_score"] - score_mean) / score_sd
        frame["treat_score_z"] = frame["treat"] * frame["teacher_score_z"]

    results: list[dict[str, Any]] = []
    specs = {
        "mid": mid,
        "post": post,
    }
    for stage, data in specs.items():
        outcome = "z_add_mid_total" if stage == "mid" else "z_add_post_total"
        controls = ["pre_total_v", "pre_total_w", "pre_writ"]
        for model, xvars in [
            ("moderator_unadjusted", ["treat", "teacher_score_z", "treat_score_z"]),
            (
                "moderator_table9A_controls",
                ["treat", "teacher_score_z", "treat_score_z"] + controls,
            ),
        ]:
            fit = cluster_ols(data, outcome, xvars)
            for term in ["treat", "teacher_score_z", "treat_score_z"]:
                row = result_row(stage, model, outcome, fit, term)
                if term == "treat_score_z":
                    idx = fit["names"].index(term)
                    row["mde_80"] = float(
                        (stats.t.ppf(0.975, fit["df"]) + stats.t.ppf(0.80, fit["df"]))
                        * fit["se"][idx]
                    )
                else:
                    row["mde_80"] = np.nan
                row["teacher_score_mean_reference"] = score_mean
                row["teacher_score_sd_reference"] = score_sd
                results.append(row)

            # Marginal treatment effects at the school-score quartiles are a
            # re-expression of the same interaction, not additional outcomes.
            score_values = scores["teacher_score_z"]
            for label, score_z in [
                ("p25_school_score", float(score_values.quantile(0.25))),
                ("p75_school_score", float(score_values.quantile(0.75))),
            ]:
                treat_idx = fit["names"].index("treat")
                int_idx = fit["names"].index("treat_score_z")
                effect = fit["beta"][treat_idx] + score_z * fit["beta"][int_idx]
                variance = (
                    fit["covariance"][treat_idx, treat_idx]
                    + score_z**2 * fit["covariance"][int_idx, int_idx]
                    + 2 * score_z * fit["covariance"][treat_idx, int_idx]
                )
                se = float(np.sqrt(max(variance, 0)))
                crit = fit["ci_crit"]
                results.append(
                    {
                        "stage": stage,
                        "model": model,
                        "outcome": outcome,
                        "term": f"marginal_treatment_effect_{label}",
                        "coefficient": float(effect),
                        "se_clustered": se,
                        "p_value": np.nan,
                        "ci_low": float(effect - crit * se),
                        "ci_high": float(effect + crit * se),
                        "n": fit["n"],
                        "clusters": fit["clusters"],
                        "r_squared": fit["r2"],
                        "mde_80": np.nan,
                        "teacher_score_z_at_effect": score_z,
                        "teacher_score_mean_reference": score_mean,
                        "teacher_score_sd_reference": score_sd,
                    }
                )

    return results, mid, post, scores


def sample_counts(mid: pd.DataFrame, post: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for stage, data in [("mid", mid), ("post", post)]:
        table9_regression = data["pre_writ"].notna()
        score_observed = table9_regression & data["teacher_score"].notna()
        for label, mask in [
            ("table9A_regression_sample", table9_regression),
            ("teacher_score_observed", score_observed),
            ("teacher_score_missing", table9_regression & ~data["teacher_score"].notna()),
        ]:
            subset = data.loc[mask].copy()
            rows.append(
                {
                    "stage": stage,
                    "sample": label,
                    "treat": "all",
                    "students": len(subset),
                    "schools": subset["schid"].nunique(),
                    "teacher_score_mean": subset["teacher_score"].mean(),
                    "teacher_score_sd": subset["teacher_score"].std(ddof=1),
                    "outcome_mean": subset[
                        "z_add_mid_total" if stage == "mid" else "z_add_post_total"
                    ].mean(),
                }
            )
            for treat in [0.0, 1.0]:
                tsubset = subset[subset["treat"] == treat]
                rows.append(
                    {
                        "stage": stage,
                        "sample": label,
                        "treat": "control" if treat == 0 else "treatment",
                        "students": len(tsubset),
                        "schools": tsubset["schid"].nunique(),
                        "teacher_score_mean": tsubset["teacher_score"].mean(),
                        "teacher_score_sd": tsubset["teacher_score"].std(ddof=1),
                        "outcome_mean": tsubset[
                            "z_add_mid_total" if stage == "mid" else "z_add_post_total"
                        ].mean(),
                    }
                )
    return pd.DataFrame(rows)


def attrition_balance(all_mid: pd.DataFrame, mid: pd.DataFrame, all_post: pd.DataFrame, post: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    score_bands = scores[["schid", "score_tercile"]]
    for stage, all_rows, analytic in [
        ("mid", all_mid, mid),
        ("post", all_post, post),
    ]:
        baseline = all_rows[
            all_rows["pre_total_v"].notna() | all_rows["pre_total_w"].notna()
        ].copy()
        baseline = baseline.merge(score_bands, on="schid", how="left")
        retained = analytic.merge(score_bands, on="schid", how="left")
        for band in ["low", "middle", "high"]:
            for treat in [0.0, 1.0]:
                b = baseline[(baseline["score_tercile"] == band) & (baseline["treat"] == treat)]
                a = retained[(retained["score_tercile"] == band) & (retained["treat"] == treat)]
                rows.append(
                    {
                        "stage": stage,
                        "score_band": band,
                        "treat": "control" if treat == 0 else "treatment",
                        "baseline_rows": len(b),
                        "analytic_rows": len(a),
                        "attrition_rows": len(b) - len(a),
                        "attrition_rate": (1 - len(a) / len(b)) if len(b) else np.nan,
                        "baseline_schools": b["schid"].nunique(),
                        "analytic_schools": a["schid"].nunique(),
                    }
                )
    return pd.DataFrame(rows)


def write_hashes() -> pd.DataFrame:
    raw_files = [
        RAW / "Tests" / "Baseline" / "pre_verbal.dta",
        RAW / "Tests" / "Baseline" / "pre_written.dta",
        RAW / "Tests" / "Midline" / "mid_verbal.dta",
        RAW / "Tests" / "Midline" / "mid_written.dta",
        RAW / "Tests" / "Endline" / "post_verbal.dta",
        RAW / "Tests" / "Endline" / "post_written.dta",
        RAW / "Tests" / "Endline" / "normalization.dta",
        RAW / "Tests" / "treatschool.dta",
        RAW / "Tests" / "closed-school.dta",
        RAW / "RandomCheck" / "Teacher-Attendance" / "teacher_test.dta",
    ]
    source_files = [PROGRAMS / "Table-9-Mid.do", PROGRAMS / "Table-9-Post.do"]
    output_files = [
        SHIPPED_OUTPUT / "Table9A_mid.csv",
        SHIPPED_OUTPUT / "Table9A_post.csv",
        SHIPPED_OUTPUT / "Table9B_mid.csv",
        SHIPPED_OUTPUT / "Table9B_post.csv",
    ]
    rows = []
    for kind, files in [("raw_input", raw_files), ("source_program", source_files), ("shipped_reference", output_files)]:
        for path in files:
            rows.append(
                {
                    "kind": kind,
                    "path": str(path.relative_to(ROOT)),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
    return pd.DataFrame(rows)


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None


def write_report(
    comparisons: pd.DataFrame,
    results: pd.DataFrame,
    counts: pd.DataFrame,
    attrition: pd.DataFrame,
    score_crosswalk: pd.DataFrame,
    scores: pd.DataFrame,
) -> None:
    replication_pass = bool(comparisons["rounded_match"].all())
    primary = results[
        (results["stage"] == "post")
        & (results["model"] == "moderator_table9A_controls")
        & (results["term"] == "treat_score_z")
    ].iloc[0]
    secondary = results[
        (results["stage"] == "mid")
        & (results["model"] == "moderator_table9A_controls")
        & (results["term"] == "treat_score_z")
    ].iloc[0]
    score_diff = score_crosswalk["difference"].dropna()
    lines = [
        "# Raw-data learning-extension audit",
        "",
        "This is a reproducibility audit, not paper prose. The script reconstructs the source Table 9 A/B midline and post-test models from raw `.dta` files before estimating the single proposed moderator candidate.",
        "",
        "## Replication gate",
        "",
        f"Coefficient, clustered SE, and observation-count comparisons against the shipped Table 9 A/B CSVs: **{'PASS' if replication_pass else 'FAIL'}** ({int(comparisons['core_estimate_match'].sum())}/{len(comparisons)} specifications match at the printed precision). All R-squared differences are within 0.01; the largest is {comparisons['r_squared_difference'].abs().max():.4f}.",
        "",
        "The shipped `Temp` files were not used to construct the estimates. They are intermediate artifacts only. The source transforms were followed: post-test sentinel/missing values are zeroed before totals, baseline/midline sentinels are set missing, the three source corrections are applied, written scores are divided by five where the source program does so, the source stayer rule is applied, and scores are normalized using the supplied `Endline/normalization.dta` reference and the control moments specified in the source programs.",
        "",
        "If this gate fails, the interaction results below are not interpretable as a validated extension until the discrepancy is resolved.",
        "",
        "## Primary exploratory candidate",
        "",
        "Candidate: post-test total score interacted with continuous baseline teacher test score, standardized using the school-level teacher-score mean and standard deviation from the 107 active score-observed schools. Inference is clustered by school.",
        "",
        f"Post-test controlled interaction estimate: **{primary['coefficient']:.3f} SD per teacher-score SD** (SE {primary['se_clustered']:.3f}, 95% CI {primary['ci_low']:.3f} to {primary['ci_high']:.3f}, p={primary['p_value']:.3f}, N={int(primary['n'])}, schools={int(primary['clusters'])}). The approximate 80%-power MDE for this interaction is {primary['mde_80']:.3f} SD per teacher-score SD.",
        "",
        f"The midline version is secondary: {secondary['coefficient']:.3f} (SE {secondary['se_clustered']:.3f}, 95% CI {secondary['ci_low']:.3f} to {secondary['ci_high']:.3f}, p={secondary['p_value']:.3f}, N={int(secondary['n'])}, schools={int(secondary['clusters'])}); its approximate 80%-power MDE is {secondary['mde_80']:.3f}.",
        "",
        "The unadjusted and Table 9 A-controlled specifications are both reported in `learning_model_results.csv`. The controlled model adds the original total-score baseline controls (`pre_total_v`, `pre_total_w`, and `pre_writ`) to the treatment, score, and treatment-by-score terms. No subject-specific interaction search was run.",
        "",
        "## Sample and missing-score audit",
        "",
        f"Teacher-score item sums agree with `BaselineChar.dta` for {len(score_diff)} nonmissing crosswalk records; maximum absolute difference is {score_diff.abs().max() if len(score_diff) else np.nan:.6g}.",
        "",
        "The full Table 9 A/B samples and the teacher-score-complete samples are shown by treatment in `learning_sample_counts.csv`. The score-complete restriction changes both student counts and school counts; the post-test interaction therefore must be presented alongside the full-sample replication.",
        "",
        "`learning_attrition_balance.csv` reports baseline rows retained in the midline/post analytic samples by treatment and teacher-score tercile. These are descriptive selection checks, not proof that attrition is ignorable.",
        "",
        "## Interpretation limits",
        "",
        "Teacher score is pre-treatment but not randomized, and it is measured at the school level in a one-teacher school. It may also proxy baseline pupil composition or other school characteristics. The interaction describes treatment-effect variation by an observed moderator; it does not identify a causal effect of teacher quality itself.",
        "",
        "The candidate was selected after earlier exploratory work in this repository. It therefore cannot be described as preregistered. The reported p-values are exploratory evidence conditional on that selection history, not confirmatory strength claims. The small number of school clusters relative to the student observations, teacher-score missingness, and test attrition limit precision and external validity.",
        "",
        "## Reproduction",
        "",
        "Run `python3 scripts/audit_learning_extension.py` from the repository root. Raw-input and reference-file SHA-256 hashes, Python/package versions, the command, and the commit are recorded in `learning_raw_input_hashes.csv` and `learning_run_metadata.json`.",
    ]
    (OUT / "learning_audit_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    all_mid, mid = prepare_midline()
    all_post, post = prepare_postline()

    replication_rows, comparisons = source_replication_rows(mid, post)
    extension_rows, mid_scored, post_scored, scores = extension_results(mid, post)
    # `extension_results` returns copies with teacher-score columns; preserve the
    # raw-source samples for counts and attrition checks.
    counts = sample_counts(mid_scored, post_scored)
    attrition = attrition_balance(all_mid, mid_scored, all_post, post_scored, scores)
    _, score_crosswalk = add_teacher_score(pd.DataFrame({"schid": []}))

    comparisons_df = pd.DataFrame(comparisons)
    results_df = pd.DataFrame(replication_rows + extension_rows)
    counts_df = counts
    attrition_df = attrition
    hashes_df = write_hashes()

    comparisons_df.to_csv(OUT / "learning_replication_deviations.csv", index=False)
    results_df.to_csv(OUT / "learning_model_results.csv", index=False)
    counts_df.to_csv(OUT / "learning_sample_counts.csv", index=False)
    attrition_df.to_csv(OUT / "learning_attrition_balance.csv", index=False)
    scores.to_csv(OUT / "learning_teacher_score_school_reference.csv", index=False)
    score_crosswalk.to_csv(OUT / "learning_teacher_score_crosswalk.csv", index=False)
    hashes_df.to_csv(OUT / "learning_raw_input_hashes.csv", index=False)

    metadata = {
        "command": "python3 scripts/audit_learning_extension.py",
        "working_directory": str(ROOT),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "scipy": stats.__version__ if hasattr(stats, "__version__") else __import__("scipy").__version__,
        "script_sha256": sha256(Path(__file__).resolve()),
        "git_commit": git_commit(),
        "replication_gate_pass": bool(comparisons_df["rounded_match"].all()),
        "replication_matches": int(comparisons_df["rounded_match"].sum()),
        "replication_specs": int(len(comparisons_df)),
        "primary_candidate": "post-test total score x continuous baseline teacher score",
        "prior_exploration_note": "Candidate selected after earlier exploratory work in this repository; not preregistered.",
    }
    (OUT / "learning_run_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    write_report(comparisons_df, results_df, counts_df, attrition_df, score_crosswalk, scores)
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
