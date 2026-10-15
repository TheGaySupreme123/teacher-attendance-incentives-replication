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
OUT = ROOT / "outputs" / "exploratory"
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
    return {
        "n": int(n),
        "clusters": int(m),
        "coef": dict(zip(["const"] + xvars, beta.ravel())),
        "se": dict(zip(["const"] + xvars, se)),
    }


def simple_kmeans(x: np.ndarray, k: int, n_init: int = 100, max_iter: int = 300, seed: int = 7):
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(n_init):
        centers = x[rng.choice(len(x), k, replace=False)].copy()
        labels = np.zeros(len(x), dtype=int)
        for _iter in range(max_iter):
            dist = ((x[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
            new_labels = dist.argmin(axis=1)
            if np.array_equal(labels, new_labels):
                break
            labels = new_labels
            for j in range(k):
                if np.any(labels == j):
                    centers[j] = x[labels == j].mean(axis=0)
                else:
                    centers[j] = x[rng.integers(0, len(x))]
        inertia = ((x - centers[labels]) ** 2).sum()
        if best is None or inertia < best[0]:
            best = (inertia, labels.copy(), centers.copy())
    return best[1], best[2], best[0]


def zscale(frame: pd.DataFrame, features: list[str]) -> np.ndarray:
    x = frame[features].astype(float).to_numpy()
    means = np.nanmean(x, axis=0)
    sds = np.nanstd(x, axis=0)
    sds[sds == 0] = 1
    return (x - means) / sds


def summarize_balance(school: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    rows = []
    for col in features:
        d = school[["treat", col]].dropna()
        treated = d.loc[d["treat"] == 1, col].astype(float)
        control = d.loc[d["treat"] == 0, col].astype(float)
        if len(treated) < 2 or len(control) < 2:
            continue
        pooled_sd = np.sqrt(((treated.var(ddof=1) + control.var(ddof=1)) / 2))
        diff = treated.mean() - control.mean()
        smd = diff / pooled_sd if pooled_sd else np.nan
        test = stats.ttest_ind(treated, control, equal_var=False, nan_policy="omit")
        rows.append(
            {
                "feature": col,
                "treated_mean": treated.mean(),
                "control_mean": control.mean(),
                "difference": diff,
                "standardized_difference": smd,
                "p_value_welch": test.pvalue,
                "n_treated": len(treated),
                "n_control": len(control),
            }
        )
    return pd.DataFrame(rows).sort_values("standardized_difference", key=lambda s: s.abs(), ascending=False)


def build_school_level() -> tuple[pd.DataFrame, pd.DataFrame]:
    rc = pd.read_stata(RAW / "RandomCheck" / "Teacher-Attendance" / "randomcheck.dta")
    rc = add_table2_time(rc)
    rc = rc[~rc["schid"].isin(DROP_CLOSED)].copy()

    assign = rc.groupby("schid", as_index=False).agg(treat=("treat", "max"), block=("block", "max"))

    baseline = (
        rc[rc["time"] == 1]
        .groupby("schid", as_index=False)
        .agg(
            baseline_open=("open", "mean"),
            baseline_students=("students", "mean"),
            baseline_inside=("inside", "mean"),
            baseline_bbused=("bbused", "mean"),
            baseline_interact=("interact_kids", "mean"),
        )
    )

    teacher = pd.read_stata(RAW / "RandomCheck" / "Teacher-Attendance" / "teacher_test.dta")
    score_cols = ["comp1", "comp2", "comp3", "clozet", "story", "attitude", "nnc1", "nc1", "nc2", "nnc2", "nnc3", "nc3", "vp", "map"]
    teacher["teacher_score"] = teacher[score_cols].sum(axis=1)
    teacher = teacher[["schid", "teacher_score"]]

    baseline_char = pd.read_stata(RAW / "Tests" / "BaselineChar.dta")
    baseline_char = baseline_char.rename(columns={"score": "baseline_char_score", "grade": "teacher_grade", "infra": "infra_index"})

    pre_v = pd.read_stata(RAW / "Tests" / "Baseline" / "pre_verbal.dta")
    for col in ["total", "total_1_to_4", "total_5_to_11"]:
        pre_v.loc[pre_v[col] < -100, col] = np.nan
    pre_v_agg = (
        pre_v.groupby("schid", as_index=False)
        .agg(
            pre_oral_n=("childno", "nunique"),
            pre_oral_total_mean=("total", "mean"),
            pre_oral_math_mean=("total_1_to_4", "mean"),
            pre_oral_lang_mean=("total_5_to_11", "mean"),
        )
    )

    pre_w = pd.read_stata(RAW / "Tests" / "Baseline" / "pre_written.dta")
    for col in ["total", "total_1_to_4", "total_5_to_11"]:
        pre_w.loc[pre_w[col] < -100, col] = np.nan
    pre_w_agg = (
        pre_w.groupby("schid", as_index=False)
        .agg(
            pre_written_n=("childno", "nunique"),
            pre_written_total_mean=("total", "mean"),
            pre_written_math_mean=("total_1_to_4", "mean"),
            pre_written_lang_mean=("total_5_to_11", "mean"),
        )
    )

    school = assign.merge(baseline, on="schid", how="left")
    school = school.merge(teacher, on="schid", how="left")
    school = school.merge(baseline_char, on="schid", how="left")
    school = school.merge(pre_v_agg, on="schid", how="left").merge(pre_w_agg, on="schid", how="left")
    school["pre_total_n"] = school["pre_oral_n"].fillna(0) + school["pre_written_n"].fillna(0)
    school["pre_written_share"] = school["pre_written_n"].fillna(0) / school["pre_total_n"].replace(0, np.nan)
    return school, rc


def treatment_effects_by_subgroup(rc: pd.DataFrame, school: pd.DataFrame) -> pd.DataFrame:
    post = rc[rc["time"] != 1].copy()
    post = post.merge(school[["schid", "teacher_score", "baseline_open", "infra_index"]], on="schid", how="left")
    post["teacher_score_group"] = np.where(post["teacher_score"] >= post["teacher_score"].median(), "teacher score: high", "teacher score: low")
    post.loc[post["teacher_score"].isna(), "teacher_score_group"] = np.nan
    post["baseline_open_group"] = np.where(post["baseline_open"] >= post["baseline_open"].median(), "baseline open: high", "baseline open: low")
    post.loc[post["baseline_open"].isna(), "baseline_open_group"] = np.nan
    post["infra_group"] = np.where(post["infra_index"] >= post["infra_index"].median(), "infra: high", "infra: low")
    post.loc[post["infra_index"].isna(), "infra_group"] = np.nan

    rows = []
    groups = [("all", None), ("teacher_score_group", "teacher_score_group"), ("baseline_open_group", "baseline_open_group"), ("infra_group", "infra_group")]
    for label, col in groups:
        if col is None:
            slices = [("all active schools", post)]
        else:
            slices = [(str(v), post[post[col] == v]) for v in sorted(post[col].dropna().unique())]
        for group_name, d in slices:
            if d["treat"].nunique() < 2 or d["schid"].nunique() < 8:
                continue
            fit = cluster_ols(d, "open", ["treat"], "schid")
            rows.append(
                {
                    "group_type": label,
                    "group": group_name,
                    "treatment_effect": fit["coef"]["treat"],
                    "se": fit["se"]["treat"],
                    "ci_low": fit["coef"]["treat"] - 1.96 * fit["se"]["treat"],
                    "ci_high": fit["coef"]["treat"] + 1.96 * fit["se"]["treat"],
                    "n": fit["n"],
                    "clusters": fit["clusters"],
                }
            )
    return pd.DataFrame(rows)


def pre_treatment_kmeans(school: pd.DataFrame, rc: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    features = ["teacher_score", "baseline_char_score", "teacher_grade", "infra_index", "pre_oral_total_mean", "pre_written_share"]
    eligible = school[["schid", "treat"] + features].dropna().copy()
    x = zscale(eligible, features)
    labels, _, _ = simple_kmeans(x, k=3, seed=21)
    eligible["pre_cluster"] = labels

    # Relabel by baseline skill/infrastructure for readability.
    summaries = eligible.groupby("pre_cluster")[features].mean()
    order = summaries["pre_oral_total_mean"].rank(method="first").astype(int).to_dict()
    eligible["pre_cluster_label"] = eligible["pre_cluster"].map(lambda c: f"pre-cluster {order[c]}")

    post = rc[rc["time"] != 1].merge(eligible[["schid", "pre_cluster_label"]], on="schid", how="inner")
    rows = []
    for cl, d in post.groupby("pre_cluster_label"):
        if d["treat"].nunique() < 2:
            continue
        fit = cluster_ols(d, "open", ["treat"], "schid")
        rows.append(
            {
                "pre_cluster_label": cl,
                "treatment_effect": fit["coef"]["treat"],
                "se": fit["se"]["treat"],
                "ci_low": fit["coef"]["treat"] - 1.96 * fit["se"]["treat"],
                "ci_high": fit["coef"]["treat"] + 1.96 * fit["se"]["treat"],
                "n": fit["n"],
                "clusters": fit["clusters"],
                "treated_schools": int(d.loc[d["treat"] == 1, "schid"].nunique()),
                "control_schools": int(d.loc[d["treat"] == 0, "schid"].nunique()),
            }
        )
    cluster_summary = eligible.groupby("pre_cluster_label").agg(
        schools=("schid", "nunique"),
        treated_share=("treat", "mean"),
        teacher_score=("teacher_score", "mean"),
        infra_index=("infra_index", "mean"),
        pre_oral_total_mean=("pre_oral_total_mean", "mean"),
        pre_written_share=("pre_written_share", "mean"),
    ).reset_index()
    return cluster_summary, pd.DataFrame(rows)


def camera_behavior_clusters() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cam = pd.read_csv(
        RAW / "RDD" / "cameras.txt",
        header=None,
        names=["schid", "year", "month", "day", "weekday", "holiday", "worked"],
    )
    cam = cam[~((cam["schid"] == 23513) & (cam["month"] == 10) & (cam["year"] == 2004))].copy()
    cam["worked_temp"] = np.where(cam["holiday"] == 1, 1, cam["worked"])
    cam["month_index"] = (cam["year"] - cam["year"].min()) * 12 + cam["month"]
    cam_workdays = cam[(cam["weekday"] != 0) & (cam["holiday"] != 1)].copy()

    monthly_work = (
        cam_workdays.groupby(["schid", "year", "month"], as_index=False)
        .agg(monthly_rate=("worked", "mean"), workdays=("worked", "size"), valid_worked_days=("worked", "sum"))
    )
    monthly_credit = cam.groupby(["schid", "year", "month"], as_index=False).agg(credited_days=("worked_temp", "sum"))
    monthly = monthly_work.merge(monthly_credit, on=["schid", "year", "month"], how="left")
    monthly["in_money_month"] = (monthly["credited_days"] > 10).astype(int)
    monthly["near_threshold_month"] = monthly["credited_days"].between(10, 12).astype(int)

    day_part = (
        cam_workdays.assign(
            early=lambda d: d["day"] <= 10,
            mid=lambda d: d["day"].between(11, 20),
            late=lambda d: d["day"] >= 21,
        )
        .groupby("schid")
        .agg(
            overall_work_rate=("worked", "mean"),
            early_rate=("worked", lambda s: s[cam_workdays.loc[s.index, "day"] <= 10].mean()),
            mid_rate=("worked", lambda s: s[cam_workdays.loc[s.index, "day"].between(11, 20)].mean()),
            late_rate=("worked", lambda s: s[cam_workdays.loc[s.index, "day"] >= 21].mean()),
        )
        .reset_index()
    )

    month_features = monthly.groupby("schid").agg(
        monthly_rate_mean=("monthly_rate", "mean"),
        monthly_rate_sd=("monthly_rate", "std"),
        in_money_share=("in_money_month", "mean"),
        near_threshold_share=("near_threshold_month", "mean"),
        average_credited_days=("credited_days", "mean"),
        months_observed=("monthly_rate", "size"),
    ).reset_index()

    features = day_part.merge(month_features, on="schid", how="inner")
    features["late_minus_early"] = features["late_rate"] - features["early_rate"]
    features = features.dropna().copy()
    k_features = [
        "overall_work_rate",
        "monthly_rate_sd",
        "in_money_share",
        "near_threshold_share",
        "late_minus_early",
        "average_credited_days",
    ]
    labels, _, _ = simple_kmeans(zscale(features, k_features), k=3, seed=99)
    features["camera_cluster"] = labels

    raw_summary = features.groupby("camera_cluster")[k_features + ["months_observed"]].mean()
    order = raw_summary["overall_work_rate"].rank(method="first").astype(int).to_dict()
    label_map = {
        cl: ("low/variable attendance" if order[cl] == 1 else "middle/threshold-sensitive" if order[cl] == 2 else "high attendance")
        for cl in raw_summary.index
    }
    features["camera_cluster_label"] = features["camera_cluster"].map(label_map)

    cluster_summary = features.groupby("camera_cluster_label").agg(
        schools=("schid", "nunique"),
        overall_work_rate=("overall_work_rate", "mean"),
        early_rate=("early_rate", "mean"),
        late_rate=("late_rate", "mean"),
        late_minus_early=("late_minus_early", "mean"),
        monthly_rate_sd=("monthly_rate_sd", "mean"),
        in_money_share=("in_money_share", "mean"),
        near_threshold_share=("near_threshold_share", "mean"),
        average_credited_days=("average_credited_days", "mean"),
        months_observed=("months_observed", "mean"),
    ).reset_index()

    monthly_plot = monthly.merge(features[["schid", "camera_cluster_label"]], on="schid", how="inner")
    monthly_plot["date"] = pd.to_datetime(dict(year=monthly_plot["year"].astype(int), month=monthly_plot["month"].astype(int), day=1))
    monthly_plot = monthly_plot.groupby(["camera_cluster_label", "date"], as_index=False).agg(monthly_rate=("monthly_rate", "mean"))
    return features, cluster_summary, monthly_plot


def plot_balance(balance: pd.DataFrame):
    top = balance.copy()
    top["abs_smd"] = top["standardized_difference"].abs()
    top = top.sort_values("abs_smd", ascending=True)
    plt.figure(figsize=(9, 5.5))
    plt.axvline(0, color="#555555", lw=1)
    plt.axvline(0.25, color="#b0b0b0", lw=1, ls="--")
    plt.axvline(-0.25, color="#b0b0b0", lw=1, ls="--")
    plt.barh(top["feature"], top["standardized_difference"], color="#2f6f9f")
    plt.xlabel("Standardized treated-control difference")
    plt.title("Randomization Balance Check")
    plt.tight_layout()
    plt.savefig(OUT / "balance_standardized_differences.png", dpi=180)
    plt.close()


def plot_effects(effects: pd.DataFrame, filename: str, title: str, label_col: str):
    d = effects.copy().sort_values("treatment_effect")
    plt.figure(figsize=(9, max(4, 0.45 * len(d) + 1.5)))
    plt.axvline(0, color="#555555", lw=1)
    y = np.arange(len(d))
    plt.errorbar(d["treatment_effect"], y, xerr=1.96 * d["se"], fmt="o", color="#c45a2c", ecolor="#6f6f6f", capsize=3)
    plt.yticks(y, d[label_col])
    plt.xlabel("Treatment effect on school open during random check")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(OUT / filename, dpi=180)
    plt.close()


def plot_camera_clusters(monthly_plot: pd.DataFrame):
    plt.figure(figsize=(10, 5.5))
    sns.lineplot(data=monthly_plot, x="date", y="monthly_rate", hue="camera_cluster_label", marker="o")
    plt.ylim(0, 1)
    plt.xlabel("Month")
    plt.ylabel("Mean workday attendance rate")
    plt.title("Treatment-School Attendance Profiles From Camera Data")
    plt.legend(title="")
    plt.tight_layout()
    plt.savefig(OUT / "camera_cluster_monthly_profiles.png", dpi=180)
    plt.close()


def main():
    school, rc = build_school_level()

    balance_features = [
        "baseline_open",
        "baseline_students",
        "baseline_inside",
        "baseline_bbused",
        "baseline_interact",
        "teacher_score",
        "baseline_char_score",
        "teacher_grade",
        "infra_index",
        "pre_oral_total_mean",
        "pre_written_total_mean",
        "pre_written_share",
        "pre_total_n",
    ]
    balance = summarize_balance(school, balance_features)
    balance.to_csv(OUT / "randomization_balance_school_level.csv", index=False)
    plot_balance(balance)

    block_counts = pd.crosstab(school["block"], school["treat"]).rename(columns={0.0: "control", 1.0: "treatment"})
    block_counts.to_csv(OUT / "randomization_block_counts.csv")

    subgroup_effects = treatment_effects_by_subgroup(rc, school)
    subgroup_effects.to_csv(OUT / "attendance_effects_by_subgroup.csv", index=False)
    plot_effects(
        subgroup_effects[subgroup_effects["group_type"].isin(["all", "teacher_score_group", "baseline_open_group", "infra_group"])],
        "attendance_effects_by_subgroup.png",
        "Attendance Effects By Exploratory Subgroup",
        "group",
    )

    pre_cluster_summary, pre_cluster_effects = pre_treatment_kmeans(school, rc)
    pre_cluster_summary.to_csv(OUT / "pre_treatment_school_clusters_summary.csv", index=False)
    pre_cluster_effects.to_csv(OUT / "attendance_effects_by_pre_treatment_cluster.csv", index=False)
    if not pre_cluster_effects.empty:
        plot_effects(
            pre_cluster_effects,
            "attendance_effects_by_pre_treatment_cluster.png",
            "Attendance Effects By Pre-Treatment K-Means Cluster",
            "pre_cluster_label",
        )

    camera_features, camera_cluster_summary, camera_monthly = camera_behavior_clusters()
    camera_features.to_csv(OUT / "camera_behavior_school_features.csv", index=False)
    camera_cluster_summary.to_csv(OUT / "camera_behavior_clusters_summary.csv", index=False)
    plot_camera_clusters(camera_monthly)

    notes = {
        "schools_active_table2": int(school["schid"].nunique()),
        "balance_features_checked": len(balance),
        "largest_abs_standardized_difference": float(balance["standardized_difference"].abs().max()),
        "largest_balance_feature": str(balance.iloc[0]["feature"]) if not balance.empty else None,
        "camera_schools_clustered": int(camera_features["schid"].nunique()),
    }
    pd.DataFrame([notes]).to_csv(OUT / "exploration_run_summary.csv", index=False)
    print(pd.DataFrame([notes]).to_string(index=False))
    print("\nTop balance signals:")
    print(balance.head(8).to_string(index=False))
    print("\nSubgroup effects:")
    print(subgroup_effects.to_string(index=False))
    print("\nPre-treatment clusters:")
    print(pre_cluster_summary.to_string(index=False))
    print(pre_cluster_effects.to_string(index=False))
    print("\nCamera behavior clusters:")
    print(camera_cluster_summary.to_string(index=False))


if __name__ == "__main__":
    main()
