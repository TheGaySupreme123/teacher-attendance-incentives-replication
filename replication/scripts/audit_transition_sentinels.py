"""Audit raw attendance sentinels in the Table 10 NFE-departure endpoint.

The original Table7/Table10 program maps negative attendance codes and 22 to
zero before defining ``drop``.  The data files do not provide a codebook for
those values.  This script preserves the original operational outcome as the
main result, records child-level raw-code composition, and runs one fixed
complete-observed-outcome sensitivity: exclude only children classified as
``drop=1`` who have any negative sentinel or 22 in the selected open checks.
Children with a raw presence value of 1 remain in the sensitivity sample even
if another selected row contains a sentinel; those are known non-departures
under the observed data.  No values or outcomes are imputed.
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
from scripts import audit_transition_scope as scope  # noqa: E402

NEGATIVE_SENTINELS = {-999, -888, -777, -666, -444, -333}
AMBIGUOUS_CODES = NEGATIVE_SENTINELS | {22}


def load_coded_with_raw_attendance() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Rebuild the coded roster while retaining pre-recode attendance."""

    rema = pd.read_stata(raw.RAW / "roster_rema2012.dta", convert_categoricals=False)
    rema = rema.loc[~((rema["month"] == 12) & (rema["year"] == 2005))].copy()
    rosterfin = pd.read_stata(raw.RAW / "rosterfin.dta", convert_categoricals=False)
    rosterfin["reason"] = ""
    rema["raw_attendance"] = rema["attendance"]
    rosterfin["raw_attendance"] = rosterfin["attendance"]
    roster = pd.concat([rema, rosterfin], ignore_index=True, sort=False)
    roster = roster.loc[
        ~((roster["year"] == 2003) & (roster["month"] < 9)) & (roster["year"] != 205)
    ].copy()
    roster = raw.assign_time(roster)

    roster.loc[roster["attendance"].isin(NEGATIVE_SENTINELS), "attendance"] = 2
    roster.loc[roster["attendance"].isin([2, 22]), "attendance"] = 0

    random_checks = pd.read_stata(raw.RAW / "rc_for_roster.dta", convert_categoricals=False)
    roster = raw.stata_merge(roster, random_checks, raw.RC_KEYS)
    roster = roster.loc[roster["randomcheck"].notna()].copy()
    roster = roster.loc[~((roster["month"] == 8) & (roster["year"] == 2003))].drop(columns=["_merge"])

    enrollment = pd.read_stata(raw.RAW / "enroll1.dta", convert_categoricals=False)
    roster = raw.stata_merge(roster, enrollment, raw.CHILD_KEYS).drop(columns=["_merge"])
    pre_writ = pd.read_stata(raw.RAW / "pre_writ_attend.dta", convert_categoricals=False)
    roster = raw.stata_merge(roster, pre_writ, raw.CHILD_KEYS).drop(columns=["_merge"])
    roster = roster.loc[
        (roster["time"] != 1) & roster["childno"].notna() & (roster["enrolled1"] == 1)
    ].copy()
    return roster, pre_writ


def build_child_audit(coded: pd.DataFrame, pre_writ: pd.DataFrame) -> pd.DataFrame:
    open_rows = coded.loc[coded["open"] == 1].copy()
    all_open = (
        open_rows.groupby(["schid", "childno", "treat"], as_index=False)
        .size()
        .rename(columns={"size": "all_open_checks"})
    )
    open_rows = open_rows.sort_values(
        ["schid", "childno", "year", "month", "day"],
        ascending=[True, True, False, False, False],
        kind="mergesort",
    )
    open_rows["last"] = open_rows.groupby(raw.CHILD_KEYS, sort=False).cumcount()
    selected = open_rows.loc[open_rows["last"] < 5].copy()
    selected["negative_sentinel"] = selected["raw_attendance"].isin(NEGATIVE_SENTINELS)
    selected["code_22"] = selected["raw_attendance"].eq(22)
    selected["raw_presence_1"] = selected["raw_attendance"].eq(1)
    selected["raw_absence_2"] = selected["raw_attendance"].eq(2)

    child = (
        selected.groupby(["schid", "childno", "treat"], as_index=False)
        .agg(
            attendance_sum=("attendance", "sum"),
            selected_open_checks=("attendance", "size"),
            negative_sentinel_rows=("negative_sentinel", "sum"),
            code_22_rows=("code_22", "sum"),
            raw_presence_1_rows=("raw_presence_1", "sum"),
            raw_absence_2_rows=("raw_absence_2", "sum"),
        )
    )
    child["source_drop"] = (child["attendance_sum"] == 0).astype(int)
    child["any_ambiguous_attendance_code"] = (
        (child["negative_sentinel_rows"] + child["code_22_rows"]) > 0
    ).astype(int)
    child["ambiguous_classification"] = (
        (child["source_drop"] == 1) & (child["any_ambiguous_attendance_code"] == 1)
    ).astype(int)
    child["all_selected_codes_ambiguous"] = (
        (child["source_drop"] == 1)
        & (child["raw_presence_1_rows"] == 0)
        & (child["raw_absence_2_rows"] == 0)
        & (child["any_ambiguous_attendance_code"] == 1)
    ).astype(int)
    child["complete_observed_drop"] = child["source_drop"].where(
        child["ambiguous_classification"] == 0
    )
    child = child.merge(all_open, on=["schid", "childno", "treat"], how="left", validate="one_to_one")
    child["fewer_than_five_open_checks"] = (child["all_open_checks"] < 5).astype(int)

    status = (
        pre_writ.groupby(raw.CHILD_KEYS)["pre_writ"]
        .agg(pre_rows="size", pre_unique="nunique", pre_mean="mean")
        .reset_index()
    )
    status["pre_writ_consensus"] = status["pre_mean"].where(status["pre_unique"] == 1)
    child = child.merge(status, on=raw.CHILD_KEYS, how="left", validate="one_to_one")
    child["pre_writ_conflict"] = (child["pre_unique"] != 1).astype(int)
    child["analysis_consensus"] = child["pre_writ_consensus"].notna().astype(int)
    return child


def interaction_fit(data: pd.DataFrame, outcome: str) -> dict:
    fit = scope.cluster_fit(data, outcome, ["treat", "pre_writ", "treat_x_pre_writ"])
    index = fit["names"].index("treat_x_pre_writ")
    df = fit["clusters"] - 1
    estimate = float(fit["beta"][index])
    se = float(fit["se"][index])
    critical = float(stats.t.ppf(0.975, df))
    return {
        "estimate": estimate,
        "se_clustered": se,
        "t_stat": float(fit["t"][index]),
        "p_value": float(2 * stats.t.sf(abs(fit["t"][index]), df)),
        "ci_low": estimate - critical * se,
        "ci_high": estimate + critical * se,
        "n": int(fit["n"]),
        "schools": int(fit["clusters"]),
        "cluster_df": int(df),
    }


def group_effects(data: pd.DataFrame, outcome: str) -> pd.DataFrame:
    fit = scope.cluster_fit(data, outcome, ["treat", "pre_writ", "treat_x_pre_writ"])
    rows = []
    df = fit["clusters"] - 1
    critical = float(stats.t.ppf(0.975, df))
    names = fit["names"]
    for pre_group in [0, 1]:
        weights = np.zeros(len(names))
        weights[names.index("treat")] = 1
        if pre_group == 1:
            weights[names.index("treat_x_pre_writ")] = 1
        estimate = float(weights @ fit["beta"])
        se = float(np.sqrt(weights @ fit["covariance"] @ weights))
        treated = data[(data["treat"] == 1) & (data["pre_writ"] == pre_group)]
        control = data[(data["treat"] == 0) & (data["pre_writ"] == pre_group)]
        rows.append(
            {
                "outcome": outcome,
                "pre_writ": pre_group,
                "treatment_effect": estimate,
                "se_clustered": se,
                "ci_low": estimate - critical * se,
                "ci_high": estimate + critical * se,
                "p_value": float(2 * stats.t.sf(abs(estimate / se), df)),
                "n_control": len(control),
                "n_treated": len(treated),
                "control_mean": float(control[outcome].mean()),
                "treated_mean": float(treated[outcome].mean()),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    coded, pre_writ = load_coded_with_raw_attendance()
    child = build_child_audit(coded, pre_writ)
    child.to_csv(OUT / "sentinel_child_audit.csv", index=False)

    consensus = child.loc[child["analysis_consensus"] == 1].copy()
    consensus["pre_writ"] = consensus["pre_writ_consensus"]
    consensus["treat_x_pre_writ"] = consensus["treat"] * consensus["pre_writ"]
    operational = interaction_fit(consensus, "source_drop")
    complete = consensus.loc[consensus["ambiguous_classification"] == 0].copy()
    complete["treat_x_pre_writ"] = complete["treat"] * complete["pre_writ"]
    sensitivity = interaction_fit(complete, "source_drop")
    group = pd.concat(
        [group_effects(consensus, "source_drop"), group_effects(complete, "source_drop")],
        ignore_index=True,
    )
    group.insert(0, "sample", ["operational_original"] * 2 + ["exclude_ambiguous_drop"] * 2)
    group.to_csv(OUT / "sentinel_drop_group_effects.csv", index=False)

    model = pd.DataFrame(
        [
            {"sample": "operational_original", **operational},
            {"sample": "exclude_ambiguous_drop", **sensitivity},
        ]
    )
    model.to_csv(OUT / "sentinel_drop_interaction.csv", index=False)

    summary = (
        consensus.groupby(["treat", "pre_writ"], as_index=False)
        .agg(
            children=("source_drop", "size"),
            source_drop_children=("source_drop", "sum"),
            ambiguous_drop_children=("ambiguous_classification", "sum"),
            all_sentinel_drop_children=("all_selected_codes_ambiguous", "sum"),
            fewer_than_five_open_checks=("fewer_than_five_open_checks", "sum"),
            negative_sentinel_rows=("negative_sentinel_rows", "sum"),
            code_22_rows=("code_22_rows", "sum"),
        )
    )
    summary.to_csv(OUT / "sentinel_summary_by_cell.csv", index=False)

    all_sentinel = consensus.loc[consensus["all_selected_codes_ambiguous"] == 1]
    all_sentinel.to_csv(OUT / "sentinel_all_ambiguous_children.csv", index=False)

    bootstrap_summary, t_stats, validation = scope.wild_bootstrap(complete, "source_drop")
    (OUT / "sentinel_complete_wildbootstrap_summary.json").write_text(
        json.dumps(bootstrap_summary, indent=2) + "\n", encoding="utf-8"
    )
    t_stats.to_csv(OUT / "sentinel_complete_wildbootstrap_t_statistics.csv", index=False)
    validation.to_csv(OUT / "sentinel_complete_wildbootstrap_validation.csv", index=False)

    report = f"""# Raw attendance-sentinel audit

The main result remains the original Table7/Table10 operational `drop` endpoint. The source program recodes negative attendance values and code 22 to zero before defining `drop`; the data package provides no value-label codebook explaining whether those values are absences or unresolved/missing observations.

## Child-level audit

The audit rebuilds the raw roster pipeline and preserves raw attendance before the original recode. It audits the 2,195 children with consensus baseline-writing status. A child is classified as an ambiguous departure when the original operational `source_drop=1` and at least one of the selected open-check attendance values is a negative sentinel or 22. Children with a raw presence value of 1 are kept when they are not operationally classified as `drop=1`; no outcome is filled.

The ambiguous departure counts are: control nonwriters {int(summary.loc[(summary.treat==0)&(summary.pre_writ==0),'ambiguous_drop_children'].iloc[0])}, control writers {int(summary.loc[(summary.treat==0)&(summary.pre_writ==1),'ambiguous_drop_children'].iloc[0])}, treated nonwriters {int(summary.loc[(summary.treat==1)&(summary.pre_writ==0),'ambiguous_drop_children'].iloc[0])}, and treated writers {int(summary.loc[(summary.treat==1)&(summary.pre_writ==1),'ambiguous_drop_children'].iloc[0])}; total {int(consensus['ambiguous_classification'].sum())}. The all-selected-code ambiguous subset has {len(all_sentinel)} children; these are concentrated in the short-history control school 2491 as shown in `sentinel_all_ambiguous_children.csv`.

## Fixed complete-observed-outcome sensitivity

The operational original interaction is {operational['estimate']:.3f} (SE {operational['se_clustered']:.3f}, p={operational['p_value']:.4f}; 95% CI [{operational['ci_low']:.3f}, {operational['ci_high']:.3f}]). Excluding all 113 ambiguous operational departure classifications, while retaining known nondeparture children, gives {sensitivity['estimate']:.3f} (SE {sensitivity['se_clustered']:.3f}, p={sensitivity['p_value']:.4f}; 95% CI [{sensitivity['ci_low']:.3f}, {sensitivity['ci_high']:.3f}]) in {sensitivity['n']} children and {sensitivity['schools']} schools. The fixed complete-observed-outcome sensitivity wild-bootstrap p-value is {bootstrap_summary['wild_bootstrap_p_value']:.4f} ({bootstrap_summary['bootstrap_repetitions']} draws, seed {bootstrap_summary['bootstrap_seed']}; validation={bootstrap_summary['validation_pass']}).

This exclusion is a selection sensitivity, not the main estimate: sentinel meanings are undocumented and the ambiguous children are not missing at random by treatment (or necessarily by baseline writing). The seminar result should retain the original operational endpoint for comparability and display this sensitivity as a measurement limitation.

Re-run with:

```bash
python3 scripts/audit_transition_sentinels.py
```
"""
    (OUT / "sentinel_audit.md").write_text(report, encoding="utf-8")
    print(json.dumps({"operational": operational, "sensitivity": sensitivity, "bootstrap": bootstrap_summary}, indent=2))


if __name__ == "__main__":
    main()
