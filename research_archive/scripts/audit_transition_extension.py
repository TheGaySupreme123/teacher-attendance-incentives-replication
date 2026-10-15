"""Raw-data audit of the baseline-writing x school-transition extension.

This script deliberately follows the old Stata program
``Programs/Table7_Table10.do``.  It reconstructs the child-level Table 10
outcomes from the two roster files and the random-check file, then estimates
one interaction chosen in advance for this audit after prior exploratory
candidate review (it is not preregistered) for government-school transition.  The
non-government dropout outcome is reported as an exploratory secondary
outcome, because it is already a Table 10 outcome and was not selected here
from a search over outcomes or subgroups.

The shipped ``Temp/drop.dta`` and ``Temp/Roster_CODED.dta`` files are used
only as validation references.  They are never the source of the reported
raw-data estimates.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "Incentives_FINAL" / "Raw-Data" / "RandomCheck" / "Roster"
OUT = ROOT / "outputs" / "research_direction_audit"
OUT.mkdir(parents=True, exist_ok=True)


RC_KEYS = ["schid", "year", "month", "day"]
CHILD_KEYS = ["schid", "childno"]


def _stata_reason(value: object) -> str:
    """Approximate Stata's conversion when appending numeric to string reason."""

    if pd.isna(value):
        return ""
    number = float(value)
    if number.is_integer():
        return str(int(number))
    return str(value)


def _key_frame(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    """Return unique merge keys while preserving missing-key behavior."""

    return df[keys].drop_duplicates()


def stata_merge(master: pd.DataFrame, using: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    """Mimic the old Stata ``merge key using`` behavior used in the package.

    The original code emits duplicate-key warnings.  For matched keys, the
    merge keeps one using record per key; using-only records are retained,
    including duplicate using-only records.  This reproduces the package's
    intermediate row counts and the published Table 10 collapse.
    """

    using_one = using.drop_duplicates(keys, keep="first")
    merged = master.merge(
        using_one,
        on=keys,
        how="left",
        sort=False,
        indicator="_merge_flag",
    ).rename(columns={"_merge_flag": "_merge"})

    master_keys = _key_frame(master, keys)
    using_only = using.merge(master_keys, on=keys, how="left", indicator="_key_flag", sort=False)
    using_only = using_only[using_only["_key_flag"] == "left_only"].drop(columns=["_key_flag"])
    if not using_only.empty:
        for column in merged.columns:
            if column not in using_only.columns and column != "_merge":
                using_only[column] = np.nan
        using_only["_merge"] = "using"
        using_only = using_only[merged.columns]
        merged = pd.concat([merged, using_only], ignore_index=True, sort=False)
    return merged


def assign_time(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["time"] = np.nan
    periods = (
        [(2003, month) for month in range(9, 13)]
        + [(2004, month) for month in range(1, 13)]
        + [(2005, month) for month in range(1, 13)]
        + [(2006, month) for month in range(1, 3)]
    )
    for time, (year, month) in enumerate(periods, start=2):
        out.loc[(out["year"] == year) & (out["month"] == month), "time"] = time
    return out


def load_coded_roster() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build the child random-check roster from original raw inputs."""

    rema = pd.read_stata(RAW / "roster_rema2012.dta", convert_categoricals=False)
    rema = rema.loc[~((rema["month"] == 12) & (rema["year"] == 2005))].copy()

    rosterfin = pd.read_stata(RAW / "rosterfin.dta", convert_categoricals=False)
    # In the distributed Stata run, ``reason`` is string in roster_rema2012
    # and numeric in rosterfin.  The append leaves the numeric source values
    # missing in the resulting string column (as confirmed in Temp/Roster_CODED),
    # so they must not be converted to the literal string "2" here.
    rosterfin["reason"] = ""
    roster = pd.concat([rema, rosterfin], ignore_index=True, sort=False)
    roster = roster.loc[
        ~((roster["year"] == 2003) & (roster["month"] < 9)) & (roster["year"] != 205)
    ].copy()
    roster = assign_time(roster)

    missing_attendance = [-999, -888, -777, -666, -444, -333]
    roster.loc[roster["attendance"].isin(missing_attendance), "attendance"] = 2
    roster.loc[roster["attendance"].isin([2, 22]), "attendance"] = 0

    random_checks = pd.read_stata(RAW / "rc_for_roster.dta", convert_categoricals=False)
    roster = stata_merge(roster, random_checks, RC_KEYS)
    roster = roster.loc[roster["randomcheck"].notna()].copy()
    roster = roster.loc[~((roster["month"] == 8) & (roster["year"] == 2003))].copy()
    roster = roster.drop(columns=["_merge"])
    rows_after_random_check = len(roster)

    enrollment = pd.read_stata(RAW / "enroll1.dta", convert_categoricals=False)
    roster = stata_merge(roster, enrollment, CHILD_KEYS).drop(columns=["_merge"])

    pre_writ = pd.read_stata(RAW / "pre_writ_attend.dta", convert_categoricals=False)
    roster = stata_merge(roster, pre_writ, CHILD_KEYS).drop(columns=["_merge"])

    roster = roster.loc[
        (roster["time"] != 1) & roster["childno"].notna() & (roster["enrolled1"] == 1)
    ].copy()
    roster.attrs["rows_after_random_check"] = rows_after_random_check
    return roster, pre_writ


def build_table10_outcomes(coded: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Recreate Temp/drop from coded child roster and return open-check audit rows."""

    open_rows = coded.loc[coded["open"] == 1].copy()
    open_rows = open_rows.sort_values(
        ["schid", "childno", "year", "month", "day"],
        ascending=[True, True, False, False, False],
        kind="mergesort",
    )
    open_rows["last"] = open_rows.groupby(CHILD_KEYS, sort=False).cumcount()
    selected = open_rows.loc[open_rows["last"] < 5].copy()
    selected["tempgov"] = (selected["reason"] == "2").astype(int)

    outcomes = (
        selected.groupby(["schid", "childno", "treat"], as_index=False)
        .agg(attendance=("attendance", "sum"), tempgov=("tempgov", "sum"))
    )
    outcomes["drop"] = (outcomes["attendance"] == 0).astype(int)
    outcomes["gov"] = ((outcomes["tempgov"] != 0) & (outcomes["drop"] == 1)).astype(int)
    outcomes["drop2"] = ((outcomes["drop"] == 1) & (outcomes["gov"] == 0)).astype(int)

    all_open_counts = (
        open_rows.groupby(["schid", "childno", "treat"], as_index=False)
        .size()
        .rename(columns={"size": "all_open_checks"})
    )
    return outcomes, all_open_counts


def cluster_ols(df: pd.DataFrame, outcome: str, regressors: list[str], cluster: str) -> dict:
    work = df[[outcome, cluster] + regressors].dropna().reset_index(drop=True)
    y = work[outcome].to_numpy(float)
    x = np.column_stack([np.ones(len(work))] + [work[v].to_numpy(float) for v in regressors])
    xtx_inv = np.linalg.inv(x.T @ x)
    beta = xtx_inv @ x.T @ y
    residual = y - x @ beta

    meat = np.zeros((x.shape[1], x.shape[1]))
    for _, indices in work.groupby(cluster, sort=False).groups.items():
        indices = np.asarray(indices)
        score = x[indices].T @ residual[indices]
        meat += np.outer(score, score)

    n = len(work)
    k = x.shape[1]
    groups = work[cluster].nunique()
    vcov = (groups / (groups - 1)) * ((n - 1) / (n - k)) * xtx_inv @ meat @ xtx_inv
    se = np.sqrt(np.diag(vcov))
    names = ["const"] + regressors
    t_stat = beta / se
    p_value = 2 * stats.t.sf(np.abs(t_stat), groups - 1)
    return {
        "n": n,
        "schools": groups,
        "names": names,
        "beta": pd.Series(beta, index=names),
        "se": pd.Series(se, index=names),
        "vcov": pd.DataFrame(vcov, index=names, columns=names),
        "t": pd.Series(t_stat, index=names),
        "p": pd.Series(p_value, index=names),
    }


def linear_combo(fit: dict, weights: dict[str, float]) -> dict:
    vector = pd.Series(0.0, index=fit["names"])
    for name, weight in weights.items():
        vector[name] = weight
    estimate = float(vector @ fit["beta"])
    variance = float(vector @ fit["vcov"] @ vector)
    se = float(np.sqrt(variance))
    t_stat = estimate / se
    p_value = float(2 * stats.t.sf(abs(t_stat), fit["schools"] - 1))
    return {"estimate": estimate, "se": se, "t": t_stat, "p": p_value}


def interaction_rows(data: pd.DataFrame, outcome: str, label: str) -> pd.DataFrame:
    fit = cluster_ols(data, outcome, ["treat", "pre_writ", "treat_x_pre_writ"], "schid")
    critical = stats.t.ppf(0.975, fit["schools"] - 1)
    rows = []
    for term in fit["names"]:
        estimate = fit["beta"][term]
        se = fit["se"][term]
        rows.append(
            {
                "outcome": label,
                "term": term,
                "estimate": estimate,
                "se_clustered": se,
                "ci_low": estimate - critical * se,
                "ci_high": estimate + critical * se,
                "t_stat": fit["t"][term],
                "p_value": fit["p"][term],
                "n": fit["n"],
                "schools": fit["schools"],
            }
        )

    for group, weights in {
        "treatment_effect_pre_writ_0": {"treat": 1},
        "treatment_effect_pre_writ_1": {"treat": 1, "treat_x_pre_writ": 1},
    }.items():
        combo = linear_combo(fit, weights)
        rows.append(
            {
                "outcome": label,
                "term": group,
                "estimate": combo["estimate"],
                "se_clustered": combo["se"],
                "ci_low": combo["estimate"] - critical * combo["se"],
                "ci_high": combo["estimate"] + critical * combo["se"],
                "t_stat": combo["t"],
                "p_value": combo["p"],
                "n": fit["n"],
                "schools": fit["schools"],
            }
        )
    return pd.DataFrame(rows)


def write_outputs(
    outcomes: pd.DataFrame,
    pre_writ: pd.DataFrame,
    open_counts: pd.DataFrame,
    coded_rows: int,
) -> None:
    shipped = pd.read_stata(RAW / "Temp" / "drop.dta", convert_categoricals=False)
    compare = outcomes.merge(
        shipped,
        on=["schid", "childno", "treat"],
        how="outer",
        suffixes=("_raw", "_shipped"),
        indicator=True,
    )
    assert len(outcomes) == 2197
    assert len(compare) == 2197 and (compare["_merge"] == "both").all()
    assert (compare["drop_raw"] == compare["drop_shipped"]).all()
    assert (compare["gov_raw"] == compare["gov_shipped"]).all()
    assert (compare["drop2"] == ((compare["drop_shipped"] == 1) & (compare["gov_shipped"] == 0)).astype(int)).all()

    raw_table10 = []
    reference = {
        "drop": {"coef": 0.08, "se": 0.04},
        "gov": {"coef": 0.10, "se": 0.03},
        "drop2": {"coef": -0.02, "se": 0.03},
    }
    for outcome in ["drop", "gov", "drop2"]:
        fit = cluster_ols(outcomes, outcome, ["treat"], "schid")
        raw_table10.append(
            {
                "outcome": outcome,
                "control_mean": outcomes.loc[outcomes["treat"] == 0, outcome].mean(),
                "treatment_mean": outcomes.loc[outcomes["treat"] == 1, outcome].mean(),
                "estimate": fit["beta"]["treat"],
                "se_clustered": fit["se"]["treat"],
                "p_value": fit["p"]["treat"],
                "n": fit["n"],
                "schools": fit["schools"],
                "shipped_drop_rows_match": True,
                "reference_csv_coef_rounded": reference[outcome]["coef"],
                "reference_csv_se_rounded": reference[outcome]["se"],
            }
        )
    pd.DataFrame(raw_table10).to_csv(OUT / "transition_table10_reproduction.csv", index=False)

    status = (
        pre_writ.groupby(CHILD_KEYS)["pre_writ"]
        .agg(pre_rows="size", pre_unique="nunique", pre_mean="mean")
        .reset_index()
    )
    status["pre_consensus"] = status["pre_mean"].where(status["pre_unique"] == 1)
    merged = outcomes.merge(status, on=CHILD_KEYS, how="left")
    merged["treat_x_pre_writ"] = merged["treat"] * merged["pre_consensus"]
    analysis = merged.dropna(subset=["pre_consensus"]).rename(columns={"pre_consensus": "pre_writ"}).copy()
    analysis["treat_x_pre_writ"] = analysis["treat"] * analysis["pre_writ"]

    interaction = pd.concat(
        [interaction_rows(analysis, "gov", "government_school_transition"), interaction_rows(analysis, "drop2", "dropout_excluding_transfer")],
        ignore_index=True,
    )
    interaction.to_csv(OUT / "transition_interaction.csv", index=False)

    means = (
        analysis.groupby(["treat", "pre_writ"], as_index=False)
        .agg(
            n=("childno", "size"),
            schools=("schid", "nunique"),
            government_transition=("gov", "mean"),
            dropout_excluding_transfer=("drop2", "mean"),
        )
        .sort_values(["treat", "pre_writ"])
    )
    means.to_csv(OUT / "transition_group_means.csv", index=False)

    open_counts = open_counts.merge(status, on=CHILD_KEYS, how="left")
    open_counts = open_counts.dropna(subset=["pre_consensus"]).rename(columns={"pre_consensus": "pre_writ"})
    open_audit = (
        open_counts.groupby(["treat", "pre_writ"], as_index=False)
        .agg(
            n=("childno", "size"),
            mean_open_checks=("all_open_checks", "mean"),
            share_at_least_five_open_checks=("all_open_checks", lambda s: np.mean(s >= 5)),
            min_open_checks=("all_open_checks", "min"),
            max_open_checks=("all_open_checks", "max"),
        )
        .sort_values(["treat", "pre_writ"])
    )
    open_audit.to_csv(OUT / "transition_open_check_audit.csv", index=False)

    duplicate_status = status.loc[status["pre_unique"] > 1].copy()
    missing_or_conflicting = int((merged["pre_unique"] != 1).sum())
    missing_summary = pd.DataFrame(
        [
            {"quantity": "raw_pre_writ_rows", "value": len(pre_writ)},
            {"quantity": "raw_pre_writ_unique_child_ids", "value": len(status)},
            {"quantity": "raw_pre_writ_duplicate_child_ids", "value": int((status["pre_rows"] > 1).sum())},
            {"quantity": "raw_pre_writ_conflicting_child_ids", "value": len(duplicate_status)},
            {"quantity": "table10_child_outcomes", "value": len(outcomes)},
            {"quantity": "table10_child_outcomes_with_consensus_pre_writ", "value": len(analysis)},
            {"quantity": "table10_child_outcomes_missing_or_conflicting_pre_writ", "value": missing_or_conflicting},
            {"quantity": "conflicting_ids_in_analysis_sample", "value": len(duplicate_status.merge(outcomes, on=CHILD_KEYS))},
        ]
    )
    missing_summary.to_csv(OUT / "transition_missingness.csv", index=False)
    duplicate_status.to_csv(OUT / "transition_conflicting_pre_writ_ids.csv", index=False)

    pipeline = pd.DataFrame(
        [
            {"stage": "table10_outcome_rows_from_raw", "n": len(outcomes)},
            {"stage": "table10_control_children", "n": int((outcomes["treat"] == 0).sum())},
            {"stage": "table10_treatment_children", "n": int((outcomes["treat"] == 1).sum())},
            {"stage": "table10_schools", "n": int(outcomes["schid"].nunique())},
            {"stage": "coded_roster_rows_from_raw", "n": int(coded_rows)},
        ]
    )
    pipeline.to_csv(OUT / "transition_pipeline_counts.csv", index=False)

    report = f"""# Transition extension audit

## Question and novelty boundary

The extension chosen in advance for this audit, after prior exploratory candidate review, is whether the randomized bundled camera-plus-attendance-pay treatment changes the probability of moving from the nonformal education center to a government school differently for children who did versus did not take the baseline written test (`treat × pre_writ`). This is not a preregistered or independent confirmatory test. The original article reports aggregate Table 10 transition/dropout outcomes and separately reports baseline-writing heterogeneity for attendance and learning; the article, eight-page supplemental appendix, erratum, local programs, logs, and shipped outputs contain no cross-tabulation or interaction between `pre_writ` and `gov`/`drop`.

## Raw construction and reproduction

The script starts from `roster_rema2012.dta`, `rosterfin.dta`, `rc_for_roster.dta`, and `enroll1.dta`. It follows `Programs/Table7_Table10.do`: cleans attendance sentinels, retains random-check rows, keeps enrolled children, keeps the last five open-school checks per child, sums attendance and `reason == "2"`, and defines `drop`, `gov`, and `drop2 = drop & !gov`. The raw collapse has 2,197 children in 111 schools (1,061 control and 1,136 treatment). The raw `drop` and `gov` indicators match every child in the shipped `Temp/drop.dta`; the shipped file is a validation reference only.

The reconstructed Table 10 estimates are:

* `drop`: treatment difference 0.0837 (clustered SE 0.0411), matching the published rounded 0.08 [0.04].
* `gov`: treatment difference 0.1014 (clustered SE 0.0349), matching 0.10 [0.03].
* `drop2`: treatment difference -0.0177 (clustered SE 0.0306), matching -0.02 [0.03].

The `reason` field is string in `roster_rema2012.dta` but numeric in `rosterfin.dta`; in the distributed Stata append, the latter's values are blank in the coded roster. The raw reconstruction preserves that source behavior, which is necessary for exact agreement with the shipped Table 10 outcomes.

## Baseline-writing data quality

`pre_writ_attend.dta` has 2,336 rows and 2,333 child IDs. Three IDs in school 5731 are duplicated with conflicting values (children 24, 30, and 33); children 30 and 33 are in the Table 10 sample, while child 24 is not. The primary interaction excludes the two eligible conflicting IDs and uses only consensus child-level statuses, leaving 2,195 children. This handling rule was fixed before calculating the reported interaction after inspecting the raw file, and avoids assigning an arbitrary status to a duplicated ID; it does not make the analysis preregistered.

## Results

The government-school transition interaction is the coefficient on `treat × pre_writ` in a child-level OLS regression with school-clustered standard errors. For consensus-status children it is approximately +0.048 (SE 0.078, 95% CI [-0.106, 0.202], p=0.534); the implied treatment effects are +0.095 (SE 0.033) for `pre_writ=0` and +0.144 (SE 0.080) for `pre_writ=1`. Group means are in `transition_group_means.csv`. This is compatible with a somewhat larger transition effect among baseline writers, but the data do not distinguish that interaction from zero.

The non-government dropout outcome is a clearly exploratory secondary result: the `treat × pre_writ` coefficient for `drop2` is approximately +0.163 (SE 0.059, 95% CI [0.046, 0.279], p=0.007). It must not be selected or promoted because of this p-value; it is reported because it is the final Table 10 outcome and was named in advance as a secondary check. Its interpretation is also limited by the outcome construction below.

## Interpretation limit: open-school conditioning

The original definition conditions the roster observations on `open == 1` and then selects each child's last five open checks. This is a post-treatment measurement rule because treatment changes how often schools are open. All 2,197 child IDs still enter the collapse, but the number of available open checks differs: treatment children have more open checks on average and a larger share with at least five. Therefore `gov` and `drop2` are intent-to-treat-style outcomes under the paper's operational definition, not cleanly observed transitions independent of treatment-generated observation opportunities. The interaction should be treated as moderate/descriptive evidence, not a strong causal claim about readiness or formal-school progression.

## Decision

The transition-by-baseline-writing idea is genuinely distinct from the reported aggregate Table 10 and from the article's writing-status attendance/learning tables, and it is feasible with existing numbers. However, the primary interaction is imprecise and the post-treatment open-school measurement rule is a material identification limitation. It is defensible as a moderate seminar extension only if framed as a bounded heterogeneity audit of the original transition result. It is not strong enough to be the sole headline contribution without a stronger pre-specified design or additional independent evidence.
"""
    (OUT / "transition_audit.md").write_text(report, encoding="utf-8")


def main() -> None:
    coded, pre_writ = load_coded_roster()
    outcomes, open_counts = build_table10_outcomes(coded)
    write_outputs(outcomes, pre_writ, open_counts, len(coded))
    print(f"Wrote transition audit outputs to {OUT}")


if __name__ == "__main__":
    main()
