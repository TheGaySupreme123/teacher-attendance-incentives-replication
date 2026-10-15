"""Reconstruct Table 10's raw child roster and audit attendance sentinels.

This is a bounded measurement audit, not a hypothesis search.  It follows
``Programs/Table7_Table10.do`` through the enrolled coded roster and the
last-five-open-check collapse, while preserving the raw attendance field and
the source-file marker before the source program's sentinel-to-zero recode.

The script writes one child-level audit file and prints algebraic bounds for
the baseline-writing interaction.  It never edits the shipped Stata files or
the existing analysis outputs.
"""

from __future__ import annotations

import json
from importlib import import_module
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "Incentives_FINAL" / "Raw-Data" / "RandomCheck" / "Roster"
OUT = ROOT / "outputs" / "scope_search_2026_09_22" / "measurement"
OUT.mkdir(parents=True, exist_ok=True)

audit = import_module("audit_transition_extension")

RC_KEYS = audit.RC_KEYS
CHILD_KEYS = audit.CHILD_KEYS
SENTINELS = {-999, -888, -777, -666, -444, -333}


def _consensus(values: pd.Series) -> float:
    observed = pd.unique(values.dropna())
    return float(observed[0]) if len(observed) == 1 else np.nan


def load_raw_coded_roster() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Follow Table7_Table10.do while preserving raw attendance/source."""

    rema = pd.read_stata(RAW / "roster_rema2012.dta", convert_categoricals=False)
    fin = pd.read_stata(RAW / "rosterfin.dta", convert_categoricals=False)
    rema["_source_file"] = "roster_rema2012"
    fin["_source_file"] = "rosterfin"
    rema["_attendance_raw"] = rema["attendance"]
    fin["_attendance_raw"] = fin["attendance"]

    # The original drop occurs on the master before append.  Do not apply it
    # to rosterfin, which is exactly why its December 2005 rows remain.
    rema = rema.loc[
        ~((rema["month"] == 12) & (rema["year"] == 2005))
    ].copy()
    roster = pd.concat([rema, fin], ignore_index=True, sort=False)
    roster = roster.loc[
        ~((roster["year"] == 2003) & (roster["month"] < 9))
        & (roster["year"] != 205)
    ].copy()
    roster = audit.assign_time(roster)

    # Exact source recode.  _attendance_raw is never changed.
    roster.loc[roster["attendance"].isin(SENTINELS), "attendance"] = 2
    roster.loc[roster["attendance"].isin([2, 22]), "attendance"] = 0

    random_checks = pd.read_stata(
        RAW / "rc_for_roster.dta", convert_categoricals=False
    )
    roster = audit.stata_merge(roster, random_checks, RC_KEYS)
    roster = roster.loc[roster["randomcheck"].notna()].copy()
    roster = roster.loc[
        ~((roster["month"] == 8) & (roster["year"] == 2003))
    ].copy()
    roster = roster.drop(columns=["_merge"])

    enrollment = pd.read_stata(RAW / "enroll1.dta", convert_categoricals=False)
    roster = audit.stata_merge(roster, enrollment, CHILD_KEYS).drop(columns=["_merge"])
    pre_writ = pd.read_stata(
        RAW / "pre_writ_attend.dta", convert_categoricals=False
    )
    roster = audit.stata_merge(roster, pre_writ, CHILD_KEYS).drop(columns=["_merge"])
    roster = roster.loc[
        (roster["time"] != 1)
        & roster["childno"].notna()
        & (roster["enrolled1"] == 1)
    ].copy()
    return roster, pre_writ


def build_child_audit(coded: pd.DataFrame, pre_writ: pd.DataFrame) -> pd.DataFrame:
    """Return one row per Table 10 child with raw and measurement flags."""

    open_rows = coded.loc[coded["open"] == 1].copy()
    all_open_counts = (
        open_rows.groupby(["schid", "childno", "treat"], as_index=False)
        .size()
        .rename(columns={"size": "all_open_checks"})
    )
    open_rows = open_rows.sort_values(
        ["schid", "childno", "year", "month", "day"],
        ascending=[True, True, False, False, False],
        kind="mergesort",
    )
    open_rows["last"] = open_rows.groupby(CHILD_KEYS, sort=False).cumcount()
    selected = open_rows.loc[open_rows["last"] < 5].copy()

    selected["raw_negative"] = selected["_attendance_raw"].isin(SENTINELS)
    selected["raw_22"] = selected["_attendance_raw"].eq(22)
    selected["raw_1"] = selected["_attendance_raw"].eq(1)
    selected["raw_2"] = selected["_attendance_raw"].eq(2)
    selected["raw_0"] = selected["_attendance_raw"].eq(0)
    selected["raw_missing"] = selected["_attendance_raw"].isna()

    children = (
        selected.groupby(["schid", "childno", "treat"], as_index=False)
        .agg(
            original_attendance_sum=("attendance", "sum"),
            n_selected_open_checks=("_attendance_raw", "size"),
            n_raw_negative=("raw_negative", "sum"),
            n_raw_22=("raw_22", "sum"),
            n_raw_1=("raw_1", "sum"),
            n_raw_2=("raw_2", "sum"),
            n_raw_0=("raw_0", "sum"),
            n_raw_missing=("raw_missing", "sum"),
            n_selected_rema=("_source_file", lambda x: (x == "roster_rema2012").sum()),
            n_selected_rosterfin=("_source_file", lambda x: (x == "rosterfin").sum()),
        )
    )
    children["original_drop"] = (
        children["original_attendance_sum"] == 0
    ).astype(int)
    children = children.merge(
        all_open_counts, on=["schid", "childno", "treat"], how="left", validate="one_to_one"
    )

    consensus = (
        pre_writ.groupby(CHILD_KEYS, as_index=False)
        .agg(
            pre_writ_consensus=("pre_writ", _consensus),
            pre_writ_rows=("pre_writ", "size"),
            pre_writ_distinct=("pre_writ", lambda x: x.nunique(dropna=True)),
        )
    )
    children = children.merge(consensus, on=CHILD_KEYS, how="left", validate="one_to_one")

    children["pre_writ_resolved"] = children["pre_writ_consensus"].isin([0.0, 1.0])
    children["lt5_open_checks"] = children["all_open_checks"] < 5
    children["has_raw_presence_1"] = children["n_raw_1"] > 0
    children["known_nondeparture_raw1"] = (
        (children["original_drop"] == 0) & children["has_raw_presence_1"]
    )
    children["sentinel_ambiguous_drop"] = (
        (children["original_drop"] == 1)
        & ((children["n_raw_negative"] + children["n_raw_22"]) > 0)
    )
    # This is intentionally a conservative union: short histories are flagged
    # even when raw 1 makes the source-coded status non-drop.  The CSV also
    # retains known_nondeparture_raw1 so that a less conservative complete-case
    # sensitivity can preserve those observations.
    children["union_sentinel_or_lt5"] = (
        children["sentinel_ambiguous_drop"] | children["lt5_open_checks"]
    )
    children["union_drop_only_sentinel_or_lt5"] = (
        children["sentinel_ambiguous_drop"]
        | (children["lt5_open_checks"] & (children["original_drop"] == 1))
    )

    ordered = [
        "schid",
        "childno",
        "treat",
        "pre_writ_consensus",
        "pre_writ_resolved",
        "pre_writ_rows",
        "pre_writ_distinct",
        "original_drop",
        "original_attendance_sum",
        "n_selected_open_checks",
        "all_open_checks",
        "lt5_open_checks",
        "n_raw_negative",
        "n_raw_22",
        "n_raw_1",
        "n_raw_2",
        "n_raw_0",
        "n_raw_missing",
        "n_selected_rema",
        "n_selected_rosterfin",
        "has_raw_presence_1",
        "known_nondeparture_raw1",
        "sentinel_ambiguous_drop",
        "union_sentinel_or_lt5",
        "union_drop_only_sentinel_or_lt5",
    ]
    return children[ordered].sort_values(["schid", "childno"]).reset_index(drop=True)


def interaction_bounds(data: pd.DataFrame, flag: str) -> dict[str, object]:
    """Algebraic no-regression bounds for beta_Txpre_writ."""

    work = data.loc[data["pre_writ_resolved"]].copy()
    cell = (
        work.groupby(["treat", "pre_writ_consensus"], as_index=False)
        .agg(
            n=("original_drop", "size"),
            observed_drop=("original_drop", "sum"),
            unknown=(flag, "sum"),
        )
    )
    lookup = {
        (float(row.treat), float(row.pre_writ_consensus)): row
        for row in cell.itertuples(index=False)
    }

    def interval(treat: float, writer: float) -> tuple[float, float]:
        row = lookup[(treat, writer)]
        fixed = float(row.observed_drop - row.unknown)
        return fixed / row.n, (fixed + row.unknown) / row.n

    cn = interval(0.0, 0.0)
    cw = interval(0.0, 1.0)
    tn = interval(1.0, 0.0)
    tw = interval(1.0, 1.0)
    beta_original = (tw[1] - cw[1]) - (tn[1] - cn[1])
    beta_min = (tw[0] - cw[1]) - (tn[1] - cn[0])
    beta_max = (tw[1] - cw[0]) - (tn[0] - cn[1])
    return {
        "flag": flag,
        "cell_counts": cell.to_dict(orient="records"),
        "beta_original": beta_original,
        "beta_min": beta_min,
        "beta_max": beta_max,
        "unknown_total": int(work[flag].sum()),
    }


def main() -> None:
    coded, pre_writ = load_raw_coded_roster()
    child = build_child_audit(coded, pre_writ)
    assert len(child) == 2197
    assert int(child["original_drop"].sum()) == 884
    assert int(child["sentinel_ambiguous_drop"].sum()) == 113
    assert int(child["lt5_open_checks"].sum()) == 147

    csv_path = OUT / "sentinel_child_audit.csv"
    child.to_csv(csv_path, index=False)

    results = {
        "child_rows": len(child),
        "resolved_pre_writ_rows": int(child["pre_writ_resolved"].sum()),
        "unresolved_pre_writ_rows": int((~child["pre_writ_resolved"]).sum()),
        "original_drop_sum": int(child["original_drop"].sum()),
        "sentinel_ambiguous_drop_sum": int(child["sentinel_ambiguous_drop"].sum()),
        "lt5_open_sum": int(child["lt5_open_checks"].sum()),
        "union_all_sum": int(child["union_sentinel_or_lt5"].sum()),
        "union_drop_only_sum": int(child["union_drop_only_sentinel_or_lt5"].sum()),
        "sentinel_bounds": interaction_bounds(child, "sentinel_ambiguous_drop"),
        "union_all_bounds": interaction_bounds(child, "union_sentinel_or_lt5"),
        "union_drop_only_bounds": interaction_bounds(
            child, "union_drop_only_sentinel_or_lt5"
        ),
    }
    summary_path = OUT / "sentinel_interaction_bounds.json"
    summary_path.write_text(json.dumps(results, indent=2, default=float) + "\n")
    print(json.dumps(results, indent=2, default=float))
    print(f"wrote {csv_path}")
    print(f"wrote {summary_path}")


if __name__ == "__main__":
    main()
