from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "Incentives_FINAL" / "Raw-Data"
OUT = ROOT / "outputs" / "teacher_score_extension"
OUT.mkdir(parents=True, exist_ok=True)

DROP_CLOSED = [1111, 1211, 2493, 5221, 5231, 5332, 5711]


def add_table2_time(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["time"] = np.nan
    t = 1
    for year, months in [(2003, range(8, 13)), (2004, range(1, 13)), (2005, range(1, 13)), (2006, range(1, 3))]:
        for month in months:
            df.loc[(df["year"] == year) & (df["month"] == month), "time"] = t
            t += 1
    df.loc[(df["month"] == 8) & (df["day"] > 24), "time"] = 2
    return df


def cluster_ols(df: pd.DataFrame, y: str, xvars: list[str], cluster: str) -> dict:
    d = df[[y, cluster] + xvars].dropna().copy()
    yv = d[y].to_numpy(float)[:, None]
    x = np.column_stack([np.ones(len(d))] + [d[v].to_numpy(float) for v in xvars])
    xtx_inv = np.linalg.inv(x.T @ x)
    beta = xtx_inv @ (x.T @ yv)
    resid = yv - x @ beta

    idx_to_pos = {idx: i for i, idx in enumerate(d.index)}
    meat = np.zeros((x.shape[1], x.shape[1]))
    for _, g in d.groupby(cluster):
        pos = np.array([idx_to_pos[i] for i in g.index])
        xg = x[pos, :]
        ug = resid[pos, :]
        xu = xg.T @ ug
        meat += xu @ xu.T

    n = len(d)
    k = x.shape[1]
    m = d[cluster].nunique()
    vcov = (m / (m - 1)) * ((n - 1) / (n - k)) * xtx_inv @ meat @ xtx_inv
    se = np.sqrt(np.diag(vcov))
    names = ["const"] + xvars
    return {
        "names": names,
        "n": int(n),
        "clusters": int(m),
        "beta": pd.Series(beta.ravel(), index=names),
        "se": pd.Series(se, index=names),
        "vcov": pd.DataFrame(vcov, index=names, columns=names),
    }


def add_fixed_effects(df: pd.DataFrame, cols: list[str]) -> tuple[pd.DataFrame, list[str]]:
    out = df.copy()
    fe_vars: list[str] = []
    for col in cols:
        dummies = pd.get_dummies(out[col].astype("Int64").astype(str), prefix=f"fe_{col}", drop_first=True)
        dummies = dummies.astype(float)
        out = pd.concat([out, dummies], axis=1)
        fe_vars.extend(dummies.columns.tolist())
    return out, fe_vars


def load_attendance_data() -> pd.DataFrame:
    rc = pd.read_stata(RAW / "RandomCheck" / "Teacher-Attendance" / "randomcheck.dta")
    rc = add_table2_time(rc)
    rc = rc[~rc["schid"].isin(DROP_CLOSED)].copy()
    rc = rc[rc["time"] != 1].copy()

    teacher = pd.read_stata(RAW / "RandomCheck" / "Teacher-Attendance" / "teacher_test.dta")
    score_cols = ["comp1", "comp2", "comp3", "clozet", "story", "attitude", "nnc1", "nc1", "nc2", "nnc2", "nnc3", "nc3", "vp", "map"]
    teacher["teacher_score"] = teacher[score_cols].sum(axis=1)
    teacher = teacher[["schid", "teacher_score"]]

    df = rc.merge(teacher, on="schid", how="inner")
    school_scores = teacher["teacher_score"].dropna()
    median = school_scores.median()
    mean = school_scores.mean()
    sd = school_scores.std(ddof=1)
    df["low_score"] = (df["teacher_score"] < median).astype(float)
    df["score_z"] = (df["teacher_score"] - mean) / sd
    df["treat_low"] = df["treat"] * df["low_score"]
    df["treat_score_z"] = df["treat"] * df["score_z"]
    df["period"] = np.select(
        [df["time"] < 9, (df["time"] > 8) & (df["time"] < 16), df["time"] > 15],
        ["until_midtest", "mid_to_posttest", "after_posttest"],
        default="other",
    )
    return df


def format_model_rows(model_name: str, fit: dict, vars_to_keep: list[str]) -> list[dict]:
    rows = []
    df = max(fit["clusters"] - 1, 1)
    for v in vars_to_keep:
        coef = fit["beta"][v]
        se = fit["se"][v]
        t = coef / se
        p = 2 * stats.t.sf(abs(t), df)
        rows.append(
            {
                "model": model_name,
                "term": v,
                "coef": coef,
                "se_clustered": se,
                "t_stat": t,
                "p_value_approx": p,
                "n": fit["n"],
                "clusters": fit["clusters"],
            }
        )
    return rows


def linear_combo(fit: dict, weights: dict[str, float]) -> dict:
    beta = sum(weight * fit["beta"][term] for term, weight in weights.items())
    var = 0.0
    for term_i, weight_i in weights.items():
        for term_j, weight_j in weights.items():
            var += weight_i * weight_j * fit["vcov"].loc[term_i, term_j]
    se = np.sqrt(var)
    t = beta / se
    return {
        "estimate": beta,
        "se": se,
        "t_stat": t,
        "p_value_approx": 2 * stats.t.sf(abs(t), max(fit["clusters"] - 1, 1)),
    }


def binary_interaction_models(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    specs = {
        "binary_no_fe": [],
        "binary_time_fe": ["time"],
        "binary_block_fe": ["block"],
        "binary_time_block_fe": ["time", "block"],
    }
    for name, fes in specs.items():
        work = df.copy()
        xvars = ["treat", "low_score", "treat_low"]
        if fes:
            work, fe_vars = add_fixed_effects(work, fes)
            xvars += fe_vars
        fit = cluster_ols(work, "open", xvars, "schid")
        rows += format_model_rows(name, fit, ["treat", "low_score", "treat_low"])
        high = fit["beta"]["treat"]
        low = fit["beta"]["treat"] + fit["beta"]["treat_low"]
        var_low = fit["vcov"].loc["treat", "treat"] + fit["vcov"].loc["treat_low", "treat_low"] + 2 * fit["vcov"].loc["treat", "treat_low"]
        se_low = np.sqrt(var_low)
        rows.append(
            {
                "model": name,
                "term": "implied_treatment_effect_low_score",
                "coef": low,
                "se_clustered": se_low,
                "t_stat": low / se_low,
                "p_value_approx": 2 * stats.t.sf(abs(low / se_low), max(fit["clusters"] - 1, 1)),
                "n": fit["n"],
                "clusters": fit["clusters"],
            }
        )
        rows.append(
            {
                "model": name,
                "term": "implied_treatment_effect_high_score",
                "coef": high,
                "se_clustered": fit["se"]["treat"],
                "t_stat": high / fit["se"]["treat"],
                "p_value_approx": 2 * stats.t.sf(abs(high / fit["se"]["treat"]), max(fit["clusters"] - 1, 1)),
                "n": fit["n"],
                "clusters": fit["clusters"],
            }
        )
    return pd.DataFrame(rows)


def gap_closing_decomposition(df: pd.DataFrame) -> pd.DataFrame:
    fit = cluster_ols(df, "open", ["treat", "low_score", "treat_low"], "schid")
    high_effect = linear_combo(fit, {"treat": 1})
    low_effect = linear_combo(fit, {"treat": 1, "treat_low": 1})
    low_minus_high_control = linear_combo(fit, {"low_score": 1})
    low_minus_high_treatment = linear_combo(fit, {"low_score": 1, "treat_low": 1})
    control_gap_high_minus_low = -low_minus_high_control["estimate"]
    treatment_gap_high_minus_low = -low_minus_high_treatment["estimate"]
    gap_closed = control_gap_high_minus_low - treatment_gap_high_minus_low
    share_closed = gap_closed / control_gap_high_minus_low if control_gap_high_minus_low else np.nan

    rows = [
        {"quantity": "high_score_treatment_effect", **high_effect},
        {"quantity": "low_score_treatment_effect", **low_effect},
        {"quantity": "low_minus_high_interaction", **linear_combo(fit, {"treat_low": 1})},
        {
            "quantity": "control_gap_high_minus_low",
            "estimate": control_gap_high_minus_low,
            "se": low_minus_high_control["se"],
            "t_stat": -low_minus_high_control["t_stat"],
            "p_value_approx": low_minus_high_control["p_value_approx"],
        },
        {
            "quantity": "treatment_gap_high_minus_low",
            "estimate": treatment_gap_high_minus_low,
            "se": low_minus_high_treatment["se"],
            "t_stat": -low_minus_high_treatment["t_stat"],
            "p_value_approx": low_minus_high_treatment["p_value_approx"],
        },
        {
            "quantity": "share_of_control_gap_closed",
            "estimate": share_closed,
            "se": np.nan,
            "t_stat": np.nan,
            "p_value_approx": np.nan,
        },
    ]
    out = pd.DataFrame(rows)
    out["n"] = fit["n"]
    out["clusters"] = fit["clusters"]
    return out


def continuous_interaction_models(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    marginal_rows = []
    specs = {
        "continuous_no_fe": [],
        "continuous_time_fe": ["time"],
        "continuous_block_fe": ["block"],
        "continuous_time_block_fe": ["time", "block"],
    }
    percentiles = [10, 25, 50, 75, 90]
    score_values = np.percentile(df[["schid", "teacher_score"]].drop_duplicates()["teacher_score"], percentiles)

    for name, fes in specs.items():
        work = df.copy()
        xvars = ["treat", "score_z", "treat_score_z"]
        if fes:
            work, fe_vars = add_fixed_effects(work, fes)
            xvars += fe_vars
        fit = cluster_ols(work, "open", xvars, "schid")
        rows += format_model_rows(name, fit, ["treat", "score_z", "treat_score_z"])

        if name == "continuous_time_block_fe":
            score_mean = df[["schid", "teacher_score"]].drop_duplicates()["teacher_score"].mean()
            score_sd = df[["schid", "teacher_score"]].drop_duplicates()["teacher_score"].std(ddof=1)
            for pct, score in zip(percentiles, score_values):
                z = (score - score_mean) / score_sd
                eff = fit["beta"]["treat"] + z * fit["beta"]["treat_score_z"]
                var = (
                    fit["vcov"].loc["treat", "treat"]
                    + z**2 * fit["vcov"].loc["treat_score_z", "treat_score_z"]
                    + 2 * z * fit["vcov"].loc["treat", "treat_score_z"]
                )
                se = np.sqrt(var)
                marginal_rows.append(
                    {
                        "score_percentile": pct,
                        "teacher_score": score,
                        "score_z": z,
                        "marginal_treatment_effect": eff,
                        "se": se,
                        "ci_low": eff - 1.96 * se,
                        "ci_high": eff + 1.96 * se,
                    }
                )
    return pd.DataFrame(rows), pd.DataFrame(marginal_rows)


def means_and_periods(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    means = (
        df.groupby(["low_score", "treat"], as_index=False)
        .agg(open_rate=("open", "mean"), observations=("open", "size"), schools=("schid", "nunique"), teacher_score=("teacher_score", "mean"))
        .replace({"low_score": {0.0: "high_score", 1.0: "low_score"}, "treat": {0.0: "control", 1.0: "treatment"}})
    )
    period_rows = []
    for period, d in df.groupby("period"):
        if period == "other":
            continue
        fit = cluster_ols(d, "open", ["treat", "low_score", "treat_low"], "schid")
        high = fit["beta"]["treat"]
        low = fit["beta"]["treat"] + fit["beta"]["treat_low"]
        var_low = fit["vcov"].loc["treat", "treat"] + fit["vcov"].loc["treat_low", "treat_low"] + 2 * fit["vcov"].loc["treat", "treat_low"]
        se_low = np.sqrt(var_low)
        period_rows.append({"period": period, "score_group": "high_score", "effect": high, "se": fit["se"]["treat"], "ci_low": high - 1.96 * fit["se"]["treat"], "ci_high": high + 1.96 * fit["se"]["treat"], "n": fit["n"], "clusters": fit["clusters"]})
        period_rows.append({"period": period, "score_group": "low_score", "effect": low, "se": se_low, "ci_low": low - 1.96 * se_low, "ci_high": low + 1.96 * se_low, "n": fit["n"], "clusters": fit["clusters"]})
        period_rows.append({"period": period, "score_group": "low_minus_high", "effect": fit["beta"]["treat_low"], "se": fit["se"]["treat_low"], "ci_low": fit["beta"]["treat_low"] - 1.96 * fit["se"]["treat_low"], "ci_high": fit["beta"]["treat_low"] + 1.96 * fit["se"]["treat_low"], "n": fit["n"], "clusters": fit["clusters"]})
    return means, pd.DataFrame(period_rows)


def score_band_effects(df: pd.DataFrame, q: int = 4) -> pd.DataFrame:
    schools = df[["schid", "teacher_score", "treat"]].drop_duplicates().copy()
    schools["score_band_index"] = pd.qcut(schools["teacher_score"], q, labels=False, duplicates="drop")
    max_band = int(schools["score_band_index"].max())
    labels = {
        0: "Q1 lowest scores",
        max_band: f"Q{max_band + 1} highest scores",
    }
    for i in range(max_band + 1):
        labels.setdefault(i, f"Q{i + 1}")
    schools["score_band"] = schools["score_band_index"].map(labels)
    work = df.merge(schools[["schid", "score_band_index", "score_band"]], on="schid", how="left")
    rows = []
    for band_idx, d in work.sort_values("score_band_index").groupby("score_band_index", observed=True):
        schools_band = schools[schools["score_band_index"] == band_idx]
        fit = cluster_ols(d, "open", ["treat"], "schid")
        effect = fit["beta"]["treat"]
        se = fit["se"]["treat"]
        control_open = d.loc[d["treat"] == 0, "open"].mean()
        treatment_open = d.loc[d["treat"] == 1, "open"].mean()
        rows.append(
            {
                "score_band": schools_band["score_band"].iloc[0],
                "score_min": schools_band["teacher_score"].min(),
                "score_max": schools_band["teacher_score"].max(),
                "mean_teacher_score": schools_band["teacher_score"].mean(),
                "effect": effect,
                "se": se,
                "ci_low": effect - 1.96 * se,
                "ci_high": effect + 1.96 * se,
                "p_value_approx": 2 * stats.t.sf(abs(effect / se), max(fit["clusters"] - 1, 1)),
                "control_open_rate": control_open,
                "treatment_open_rate": treatment_open,
                "n": fit["n"],
                "clusters": fit["clusters"],
                "control_schools": int(d.loc[d["treat"] == 0, "schid"].nunique()),
                "treated_schools": int(d.loc[d["treat"] == 1, "schid"].nunique()),
            }
        )
    return pd.DataFrame(rows)


def tercile_effects(df: pd.DataFrame) -> pd.DataFrame:
    schools = df[["schid", "teacher_score"]].drop_duplicates()
    schools["score_tercile"] = pd.qcut(schools["teacher_score"], 3, labels=["low tercile", "middle tercile", "high tercile"])
    work = df.merge(schools[["schid", "score_tercile"]], on="schid", how="left")
    rows = []
    for tercile, d in work.groupby("score_tercile", observed=True):
        fit = cluster_ols(d, "open", ["treat"], "schid")
        effect = fit["beta"]["treat"]
        se = fit["se"]["treat"]
        rows.append(
            {
                "score_tercile": str(tercile),
                "effect": effect,
                "se": se,
                "ci_low": effect - 1.96 * se,
                "ci_high": effect + 1.96 * se,
                "n": fit["n"],
                "clusters": fit["clusters"],
                "treated_schools": int(d.loc[d["treat"] == 1, "schid"].nunique()),
                "control_schools": int(d.loc[d["treat"] == 0, "schid"].nunique()),
                "mean_teacher_score": d[["schid", "teacher_score"]].drop_duplicates()["teacher_score"].mean(),
            }
        )
    return pd.DataFrame(rows)


def performance_when_open(df: pd.DataFrame) -> pd.DataFrame:
    open_df = df[df["open"] == 1].copy()
    outcomes = ["inside", "bbused", "interact_kids", "students"]
    rows = []
    for outcome in outcomes:
        for group_name, d in [("all", open_df), ("high_score", open_df[open_df["low_score"] == 0]), ("low_score", open_df[open_df["low_score"] == 1])]:
            if d[outcome].notna().sum() < 50:
                continue
            fit = cluster_ols(d, outcome, ["treat"], "schid")
            effect = fit["beta"]["treat"]
            se = fit["se"]["treat"]
            rows.append(
                {
                    "outcome": outcome,
                    "score_group": group_name,
                    "effect": effect,
                    "se": se,
                    "ci_low": effect - 1.96 * se,
                    "ci_high": effect + 1.96 * se,
                    "n": fit["n"],
                    "clusters": fit["clusters"],
                }
            )
    return pd.DataFrame(rows)


def school_level_scores(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["schid", "treat"], as_index=False)
        .agg(post_open_rate=("open", "mean"), teacher_score=("teacher_score", "max"), observations=("open", "size"), block=("block", "max"))
        .assign(treatment=lambda d: np.where(d["treat"] == 1, "Treatment", "Control"))
    )


def teacher_score_balance(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    schools = df[["schid", "treat", "teacher_score", "low_score", "block"]].drop_duplicates().copy()
    rows = []
    for outcome, label in [("teacher_score", "baseline teacher score"), ("low_score", "below-median teacher score share")]:
        fit = cluster_ols(schools, outcome, ["treat"], "schid")
        control_mean = schools.loc[schools["treat"] == 0, outcome].mean()
        treatment_mean = schools.loc[schools["treat"] == 1, outcome].mean()
        diff = fit["beta"]["treat"]
        se = fit["se"]["treat"]
        rows.append(
            {
                "outcome": label,
                "control_mean": control_mean,
                "treatment_mean": treatment_mean,
                "treatment_minus_control": diff,
                "se": se,
                "p_value_approx": 2 * stats.t.sf(abs(diff / se), max(fit["clusters"] - 1, 1)),
                "schools": fit["n"],
            }
        )

    counts = (
        schools.assign(score_group=lambda d: np.where(d["low_score"] == 1, "low_score", "high_score"))
        .groupby(["score_group", "treat"], as_index=False)
        .agg(schools=("schid", "nunique"), mean_score=("teacher_score", "mean"))
        .replace({"treat": {0.0: "control", 1.0: "treatment"}})
    )
    return pd.DataFrame(rows), counts


def teacher_score_distribution_by_treatment(df: pd.DataFrame) -> pd.DataFrame:
    schools = df[["schid", "treat", "teacher_score", "low_score"]].drop_duplicates().copy()
    rows = []
    for treat, d in schools.groupby("treat"):
        rows.append(
            {
                "group": "treatment" if treat == 1 else "control",
                "schools": len(d),
                "mean": d["teacher_score"].mean(),
                "sd": d["teacher_score"].std(ddof=1),
                "median": d["teacher_score"].median(),
                "q25": d["teacher_score"].quantile(0.25),
                "q75": d["teacher_score"].quantile(0.75),
                "min": d["teacher_score"].min(),
                "max": d["teacher_score"].max(),
                "below_median_share": d["low_score"].mean(),
            }
        )
    return pd.DataFrame(rows)


def school_level_gradient_model(schools: pd.DataFrame) -> pd.DataFrame:
    work = schools.copy()
    mean = work["teacher_score"].mean()
    sd = work["teacher_score"].std(ddof=1)
    work["score_z"] = (work["teacher_score"] - mean) / sd
    work["treat_score_z"] = work["treat"] * work["score_z"]
    fit = cluster_ols(work, "post_open_rate", ["treat", "score_z", "treat_score_z"], "schid")
    rows = format_model_rows("school_level_gradient", fit, ["treat", "score_z", "treat_score_z"])

    control_slope = fit["beta"]["score_z"]
    treatment_slope = fit["beta"]["score_z"] + fit["beta"]["treat_score_z"]
    var_treatment_slope = (
        fit["vcov"].loc["score_z", "score_z"]
        + fit["vcov"].loc["treat_score_z", "treat_score_z"]
        + 2 * fit["vcov"].loc["score_z", "treat_score_z"]
    )
    se_treatment_slope = np.sqrt(var_treatment_slope)
    rows.append(
        {
            "model": "school_level_gradient",
            "term": "implied_control_score_slope",
            "coef": control_slope,
            "se_clustered": fit["se"]["score_z"],
            "t_stat": control_slope / fit["se"]["score_z"],
            "p_value_approx": 2 * stats.t.sf(abs(control_slope / fit["se"]["score_z"]), max(fit["clusters"] - 1, 1)),
            "n": fit["n"],
            "clusters": fit["clusters"],
        }
    )
    rows.append(
        {
            "model": "school_level_gradient",
            "term": "implied_treatment_score_slope",
            "coef": treatment_slope,
            "se_clustered": se_treatment_slope,
            "t_stat": treatment_slope / se_treatment_slope,
            "p_value_approx": 2 * stats.t.sf(abs(treatment_slope / se_treatment_slope), max(fit["clusters"] - 1, 1)),
            "n": fit["n"],
            "clusters": fit["clusters"],
        }
    )
    return pd.DataFrame(rows)


def plot_school_score_gradient(schools: pd.DataFrame):
    plt.figure(figsize=(9, 5.5))
    sns.scatterplot(data=schools, x="teacher_score", y="post_open_rate", hue="treatment", s=58, alpha=0.85)
    sns.regplot(data=schools[schools["treat"] == 0], x="teacher_score", y="post_open_rate", scatter=False, color="#555555", line_kws={"lw": 2, "ls": "--"})
    sns.regplot(data=schools[schools["treat"] == 1], x="teacher_score", y="post_open_rate", scatter=False, color="#c45a2c", line_kws={"lw": 2})
    plt.ylim(0, 1.02)
    plt.xlabel("Teacher baseline test score")
    plt.ylabel("Mean post-baseline school-open rate")
    plt.title("Treatment Flattens The Teacher-Score Attendance Gradient")
    plt.legend(title="")
    plt.tight_layout()
    plt.savefig(OUT / "teacher_score_attendance_gradient.png", dpi=180)
    plt.close()


def plot_catchup_means(means: pd.DataFrame):
    d = means.copy()
    d["score_group"] = pd.Categorical(d["low_score"], categories=["high_score", "low_score"], ordered=True)
    plt.figure(figsize=(8.5, 5.2))
    ax = sns.barplot(data=d, x="score_group", y="open_rate", hue="treat", order=["high_score", "low_score"], palette=["#555555", "#c45a2c"])
    ax.set_ylim(0, 0.9)
    ax.set_xlabel("")
    ax.set_ylabel("Mean school-open rate")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["High score", "Low score"])
    ax.legend(title="")
    ax.set_title("Treatment Nearly Erases The Low-Score Attendance Gap")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", padding=3)
    plt.tight_layout()
    plt.savefig(OUT / "teacher_score_catchup_open_rates.png", dpi=180)
    plt.close()


def plot_score_band_effects(bands: pd.DataFrame):
    plt.figure(figsize=(9, 5.3))
    ax = sns.pointplot(data=bands, x="score_band", y="effect", errorbar=None, color="#c45a2c")
    for i, row in bands.iterrows():
        ax.errorbar(i, row["effect"], yerr=1.96 * row["se"], color="#666666", capsize=3, fmt="none")
    ax.axhline(0, color="#555555", lw=1)
    ax.set_xlabel("Teacher-score quartile")
    ax.set_ylabel("Treatment effect on school-open rate")
    ax.set_title("Top Score Quartile Shows The Smallest Treatment Effect")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(OUT / "teacher_score_quartile_effects.png", dpi=180)
    plt.close()


def plot_period_effects(period_effects: pd.DataFrame):
    d = period_effects[period_effects["score_group"].isin(["high_score", "low_score"])].copy()
    order = ["until_midtest", "mid_to_posttest", "after_posttest"]
    d["period"] = pd.Categorical(d["period"], categories=order, ordered=True)
    plt.figure(figsize=(9, 5.5))
    sns.pointplot(data=d, x="period", y="effect", hue="score_group", dodge=0.35, errorbar=None, markers="o")
    ax = plt.gca()
    for i, period in enumerate(order):
        sub = d[d["period"] == period]
        for j, (_, row) in enumerate(sub.iterrows()):
            offset = -0.18 if row["score_group"] == "high_score" else 0.18
            ax.errorbar(i + offset, row["effect"], yerr=1.96 * row["se"], color="#666666", capsize=3, fmt="none")
    plt.axhline(0, color="#555555", lw=1)
    plt.ylabel("Treatment effect on school-open rate")
    plt.xlabel("")
    plt.title("Low-Score Teacher Effect Is Largest After The Post-Test")
    plt.tight_layout()
    plt.savefig(OUT / "teacher_score_period_effects.png", dpi=180)
    plt.close()


def plot_marginal_effects(marginal: pd.DataFrame):
    plt.figure(figsize=(8.5, 5.2))
    plt.errorbar(marginal["teacher_score"], marginal["marginal_treatment_effect"], yerr=1.96 * marginal["se"], fmt="o-", color="#c45a2c", ecolor="#666666", capsize=3)
    plt.axhline(0, color="#555555", lw=1)
    plt.xlabel("Teacher baseline test score value at selected percentiles")
    plt.ylabel("Estimated treatment effect")
    plt.title("Estimated Treatment Effect Declines With Teacher Score")
    plt.tight_layout()
    plt.savefig(OUT / "teacher_score_marginal_effects.png", dpi=180)
    plt.close()


def main():
    df = load_attendance_data()
    df.to_csv(OUT / "teacher_score_attendance_analysis_dataset.csv", index=False)

    binary = binary_interaction_models(df)
    binary.to_csv(OUT / "binary_teacher_score_interaction_models.csv", index=False)
    gap_closing = gap_closing_decomposition(df)
    gap_closing.to_csv(OUT / "teacher_score_gap_closing_decomposition.csv", index=False)

    continuous, marginal = continuous_interaction_models(df)
    continuous.to_csv(OUT / "continuous_teacher_score_interaction_models.csv", index=False)
    marginal.to_csv(OUT / "continuous_score_marginal_treatment_effects.csv", index=False)

    means, period_effects = means_and_periods(df)
    means.to_csv(OUT / "teacher_score_group_means.csv", index=False)
    period_effects.to_csv(OUT / "teacher_score_period_effects.csv", index=False)
    score_bands = score_band_effects(df)
    score_bands.to_csv(OUT / "teacher_score_quartile_effects.csv", index=False)

    terciles = tercile_effects(df)
    terciles.to_csv(OUT / "teacher_score_tercile_effects.csv", index=False)

    perf = performance_when_open(df)
    perf.to_csv(OUT / "performance_when_open_by_score_group.csv", index=False)

    schools = school_level_scores(df)
    schools.to_csv(OUT / "school_level_score_attendance.csv", index=False)
    balance, score_counts = teacher_score_balance(df)
    balance.to_csv(OUT / "teacher_score_randomization_balance.csv", index=False)
    score_counts.to_csv(OUT / "teacher_score_group_school_counts.csv", index=False)
    score_distribution = teacher_score_distribution_by_treatment(df)
    score_distribution.to_csv(OUT / "teacher_score_distribution_by_treatment.csv", index=False)
    gradient = school_level_gradient_model(schools)
    gradient.to_csv(OUT / "school_level_score_gradient_model.csv", index=False)
    plot_school_score_gradient(schools)
    plot_catchup_means(means)
    plot_score_band_effects(score_bands)
    plot_period_effects(period_effects)
    plot_marginal_effects(marginal)

    summary = {
        "observations": len(df),
        "schools": df["schid"].nunique(),
        "teacher_score_median": df[["schid", "teacher_score"]].drop_duplicates()["teacher_score"].median(),
        "main_high_score_effect": float(binary[(binary["model"] == "binary_no_fe") & (binary["term"] == "implied_treatment_effect_high_score")]["coef"].iloc[0]),
        "main_low_score_effect": float(binary[(binary["model"] == "binary_no_fe") & (binary["term"] == "implied_treatment_effect_low_score")]["coef"].iloc[0]),
        "low_minus_high_interaction": float(binary[(binary["model"] == "binary_no_fe") & (binary["term"] == "treat_low")]["coef"].iloc[0]),
        "low_minus_high_p_value": float(binary[(binary["model"] == "binary_no_fe") & (binary["term"] == "treat_low")]["p_value_approx"].iloc[0]),
        "control_gap_high_minus_low": float(gap_closing.loc[gap_closing["quantity"] == "control_gap_high_minus_low", "estimate"].iloc[0]),
        "treatment_gap_high_minus_low": float(gap_closing.loc[gap_closing["quantity"] == "treatment_gap_high_minus_low", "estimate"].iloc[0]),
        "share_of_control_gap_closed": float(gap_closing.loc[gap_closing["quantity"] == "share_of_control_gap_closed", "estimate"].iloc[0]),
        "continuous_interaction_time_block": float(continuous[(continuous["model"] == "continuous_time_block_fe") & (continuous["term"] == "treat_score_z")]["coef"].iloc[0]),
        "continuous_interaction_time_block_p": float(continuous[(continuous["model"] == "continuous_time_block_fe") & (continuous["term"] == "treat_score_z")]["p_value_approx"].iloc[0]),
    }
    pd.DataFrame([summary]).to_csv(OUT / "teacher_score_extension_summary.csv", index=False)

    print(pd.DataFrame([summary]).to_string(index=False))
    print("\nBinary interaction models:")
    print(binary.to_string(index=False))
    print("\nGap closing decomposition:")
    print(gap_closing.to_string(index=False))
    print("\nContinuous interactions:")
    print(continuous.to_string(index=False))
    print("\nGroup means:")
    print(means.to_string(index=False))
    print("\nTeacher-score quartile effects:")
    print(score_bands.to_string(index=False))
    print("\nPeriod effects:")
    print(period_effects.to_string(index=False))
    print("\nTercile effects:")
    print(terciles.to_string(index=False))
    print("\nPerformance conditional on open:")
    print(perf.to_string(index=False))
    print("\nTeacher score balance:")
    print(balance.to_string(index=False))
    print("\nTeacher score distribution by treatment:")
    print(score_distribution.to_string(index=False))
    print("\nSchool-level gradient:")
    print(gradient.to_string(index=False))


if __name__ == "__main__":
    main()
