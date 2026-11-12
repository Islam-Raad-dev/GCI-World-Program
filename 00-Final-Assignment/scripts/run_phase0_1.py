"""Phase 0 & Phase 1: Baseline reproduction and comprehensive data audit."""
import json
import sys
import time
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import seaborn as sns
import sklearn
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
from xgboost import XGBClassifier

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config

t0 = time.time()

# ---------------------------------------------------------
# T0.3 Environment check & versions
# ---------------------------------------------------------
versions = {
    "python": sys.version.split()[0],
    "pandas": pd.__version__,
    "numpy": np.__version__,
    "scikit_learn": sklearn.__version__,
    "xgboost": xgb.__version__,
    "scipy": scipy.__version__,
    "matplotlib": matplotlib.__version__,
    "seaborn": sns.__version__,
}
try:
    import lightgbm as lgb
    versions["lightgbm"] = lgb.__version__
except ImportError:
    versions["lightgbm"] = None

print("Versions:", versions)

# ---------------------------------------------------------
# Parse official column descriptions from ENG_Company _A_ Dataset Overview.docx
# ---------------------------------------------------------
overview_path = config.PROJECT_ROOT / "ENG_Company _A_ Dataset Overview.docx"
doc_descriptions = {}
if overview_path.exists():
    with zipfile.ZipFile(overview_path) as z:
        tree = ET.fromstring(z.read("word/document.xml"))
    rows = []
    for elem in tree.iter():
        if elem.tag.endswith("}tr"):
            cells = []
            for tc in elem.iter():
                if tc.tag.endswith("}tc"):
                    txt = "".join(t.text for t in tc.iter() if t.tag.endswith("}t") and t.text).strip()
                    cells.append(txt)
            if len(cells) >= 2:
                rows.append((cells[0], cells[1]))
    for col_name, desc in rows:
        if col_name != "Column Name":
            doc_descriptions[col_name] = desc

# ---------------------------------------------------------
# T0.4 Load and merge
# ---------------------------------------------------------
client = pd.read_csv(config.CLIENT_CSV)
record = pd.read_csv(config.RECORD_CSV)

print(f"Client shape: {client.shape}")
print(f"Record shape: {record.shape}")

assert client.shape == (100000, 50), f"Unexpected Client shape: {client.shape}"
assert record.shape == (100000, 51), f"Unexpected Record shape: {record.shape}"
assert client["Customer_ID"].is_unique, "Client Customer_ID not unique"
assert record["Customer_ID"].is_unique, "Record Customer_ID not unique"
assert (client["Customer_ID"].values == record["Customer_ID"].values).all(), "Customer_ID order mismatch"

df = record.merge(client, on="Customer_ID", how="inner")
print(f"Merged shape: {df.shape}")
assert df.shape == (100000, 100), f"Unexpected merged shape: {df.shape}"
print("Merged columns:", list(df.columns))

# Save column_map.csv
col_map_rows = []
client_cols_set = set(client.columns)
record_cols_set = set(record.columns)
for col in df.columns:
    src = "Both (Join Key)" if (col in client_cols_set and col in record_cols_set) else (
        "Client.csv" if col in client_cols_set else "Record.csv"
    )
    n_miss = int(df[col].isna().sum())
    pct_miss = round(n_miss / len(df) * 100, 4)
    n_uniq = int(df[col].nunique(dropna=True))
    desc = doc_descriptions.get(col, doc_descriptions.get(col.replace("_Mean", ""), "Not documented"))
    col_map_rows.append({
        "column": col,
        "source_file": src,
        "dtype": str(df[col].dtype),
        "n_missing": n_miss,
        "pct_missing": pct_miss,
        "n_unique": n_uniq,
        "doc_description": desc,
    })
col_map_df = pd.DataFrame(col_map_rows)
col_map_df.to_csv(config.TABLES_DIR / "column_map.csv", index=False)

# ---------------------------------------------------------
# T0.5 Reproduce tutorial baseline exactly
# ---------------------------------------------------------
df_clean = df.drop(columns=["Customer_ID"]).copy()
object_cols = df_clean.select_dtypes(include=["object", "string"]).columns.tolist()
print(f"Object/string columns ({len(object_cols)}):", object_cols)

for col in object_cols:
    encoder = LabelEncoder()
    df_clean[col] = encoder.fit_transform(df_clean[col].astype(str))

X = df_clean.drop("churn", axis=1)
y = df_clean["churn"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=config.SEED, stratify=y
)

tut_model = XGBClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    eval_metric="logloss",
    random_state=config.SEED,
    n_jobs=4,
)
tut_model.fit(X_train, y_train)

y_pred_test = tut_model.predict(X_test)
y_proba_test = tut_model.predict_proba(X_test)[:, 1]
y_pred_train = tut_model.predict(X_train)
y_proba_train = tut_model.predict_proba(X_train)[:, 1]

maj_baseline_acc = float(max(y_test.mean(), 1 - y_test.mean()))
tut_test_acc = float(accuracy_score(y_test, y_pred_test))
tut_test_auc = float(roc_auc_score(y_test, y_proba_test))
tut_train_acc = float(accuracy_score(y_train, y_pred_train))
tut_train_auc = float(roc_auc_score(y_train, y_proba_train))
tut_prec = float(precision_score(y_test, y_pred_test))
tut_rec = float(recall_score(y_test, y_pred_test))
tut_f1 = float(f1_score(y_test, y_pred_test))
cm = confusion_matrix(y_test, y_pred_test)
tn, fp, fn, tp = [int(x) for x in cm.ravel()]

print(f"Tutorial Baseline -> Test Acc: {tut_test_acc:.4f}, Test AUC: {tut_test_auc:.4f}, Train Acc: {tut_train_acc:.4f}, Train AUC: {tut_train_auc:.4f}")
print(f"Precision: {tut_prec:.4f}, Recall: {tut_rec:.4f}, F1: {tut_f1:.4f}")
print(f"Confusion Matrix: TN={tn}, FP={fp}, FN={fn}, TP={tp}")

# Top-15 gain importance in tutorial model
gain_imp = tut_model.get_booster().get_score(importance_type="gain")
total_gain = sum(gain_imp.values())
gain_sorted = sorted(
    [{"feature": k, "gain": float(v), "gain_share_pct": round(float(v) / total_gain * 100, 3)} for k, v in gain_imp.items()],
    key=lambda x: x["gain"],
    reverse=True,
)
weight_imp = tut_model.get_booster().get_score(importance_type="weight")
total_weight = sum(weight_imp.values())
weight_sorted = sorted(
    [{"feature": k, "weight": float(v), "weight_share_pct": round(float(v) / total_weight * 100, 3)} for k, v in weight_imp.items()],
    key=lambda x: x["weight"],
    reverse=True,
)

# ---------------------------------------------------------
# Phase 1 — Data Audit (T1.1 - T1.7)
# ---------------------------------------------------------
# T1.1 Dtypes & structure
dtype_counts = df.dtypes.astype(str).value_counts().to_dict()
mem_mb = round(float(df.memory_usage(deep=True).sum() / (1024 ** 2)), 2)
n_dup_rows = int(df.duplicated().sum())
n_dup_ids = int(df["Customer_ID"].duplicated().sum())
dtypes_df = pd.DataFrame([
    {"dtype": k, "column_count": int(v)} for k, v in dtype_counts.items()
])
dtypes_df.to_csv(config.TABLES_DIR / "dtypes.csv", index=False)

# T1.2 Missing values & churn when missing vs present
overall_churn = float(df["churn"].mean())
missing_rows = []
for col in df.columns:
    if col in ("Customer_ID", "churn"):
        continue
    is_miss = df[col].isna()
    n_m = int(is_miss.sum())
    pct_m = round(n_m / len(df) * 100, 4)
    if n_m > 0:
        churn_m = float(df.loc[is_miss, "churn"].mean())
        churn_p = float(df.loc[~is_miss, "churn"].mean())
        diff_pp = round((churn_m - churn_p) * 100, 2)
    else:
        churn_m = None
        churn_p = overall_churn
        diff_pp = 0.0
    missing_rows.append({
        "column": col,
        "source_file": "Client.csv" if col in client_cols_set else "Record.csv",
        "dtype": str(df[col].dtype),
        "n_missing": n_m,
        "pct_missing": pct_m,
        "churn_when_missing": round(churn_m, 4) if churn_m is not None else None,
        "churn_when_present": round(churn_p, 4),
        "churn_diff_pp": diff_pp,
    })
missing_df = pd.DataFrame(missing_rows).sort_values("n_missing", ascending=False)
missing_df.to_csv(config.TABLES_DIR / "missing.csv", index=False)

# Check the 1,732 demographic missing block
demo_block_cols = ["truck", "rv", "marital", "forgntvl", "ethnic", "creditcd", "kid0_2", "kid3_5", "kid6_10", "kid11_15", "kid16_17"]
block_mask = df["truck"].isna()
exact_same_block = all((df[c].isna() == block_mask).all() for c in demo_block_cols)
block_n = int(block_mask.sum())
block_churn = float(df.loc[block_mask, "churn"].mean())
print(f"Demographic missing block (11 cols): exact_match={exact_same_block}, n={block_n}, churn={block_churn:.4f}")

# Plot figures/missing_top20.png
top20_miss = missing_df.head(20).iloc[::-1]
fig, ax1 = plt.subplots(figsize=(10, 6.5), dpi=220)
fig.patch.set_facecolor(config.PALETTE["white"])
ax1.set_facecolor(config.PALETTE["white"])
colors = [
    config.PALETTE["coral"] if (r["churn_when_missing"] is not None and r["churn_when_missing"] > 0.60)
    else config.PALETTE["blue"]
    for _, r in top20_miss.iterrows()
]
bars = ax1.barh(top20_miss["column"], top20_miss["pct_missing"], color=colors, height=0.72)
ax1.set_xlabel("Missing Values (% of 100,000 Customers)", fontsize=12, fontweight="bold", color=config.PALETTE["navy"])
ax1.set_title(
    "Top 20 Columns by Missingness (Coral = High Churn Signal When Missing)",
    fontsize=13.5, fontweight="bold", color=config.PALETTE["navy"], pad=14,
)
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)
ax1.grid(axis="x", linestyle="--", alpha=0.5, color=config.PALETTE["grid"])
ax1.set_xlim(0, 58)
for bar, (_, r) in zip(bars, top20_miss.iterrows()):
    w = bar.get_width()
    cm_pct = r["churn_when_missing"] * 100 if r["churn_when_missing"] is not None else 0
    label = f" {w:.1f}% (churn: {cm_pct:.1f}%)"
    ax1.text(w + 0.4, bar.get_y() + bar.get_height() / 2, label, va="center", fontsize=9.5, color=config.PALETTE["navy"])
plt.tight_layout()
fig.savefig(config.FIGURES_DIR / "missing_top20.png", dpi=220)
fig.savefig(config.FIGURES_DIR / "missing_top20.svg")
plt.close(fig)

# T1.3 Negative / impossible values & T1.4 Outliers & skew
num_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in ("Customer_ID", "churn")]
quantiles_rows = []
negatives_summary = {}
for col in num_cols:
    s = df[col].dropna()
    n_neg = int((s < 0).sum())
    n_zero = int((s == 0).sum())
    pct_zero = round(n_zero / len(df) * 100, 3)
    neg_churn = float(df.loc[df[col] < 0, "churn"].mean()) if n_neg > 0 else None
    if n_neg > 0:
        negatives_summary[col] = {
            "count": n_neg,
            "min": float(s.min()),
            "churn_rate": round(neg_churn, 4),
            "n_equal_minus_1": int((s == -1).sum()),
        }
    quantiles_rows.append({
        "column": col,
        "count": int(len(s)),
        "mean": round(float(s.mean()), 4),
        "std": round(float(s.std()), 4),
        "min": round(float(s.min()), 4),
        "p01": round(float(s.quantile(0.01)), 4),
        "p25": round(float(s.quantile(0.25)), 4),
        "p50": round(float(s.quantile(0.50)), 4),
        "p75": round(float(s.quantile(0.75)), 4),
        "p99": round(float(s.quantile(0.99)), 4),
        "max": round(float(s.max()), 4),
        "skew": round(float(s.skew()), 3),
        "n_negative": n_neg,
        "neg_churn_rate": round(neg_churn, 4) if neg_churn is not None else None,
        "pct_zero": pct_zero,
    })
quantiles_df = pd.DataFrame(quantiles_rows)
quantiles_df.to_csv(config.TABLES_DIR / "numeric_audit.csv", index=False)
print("Columns with negative values:", negatives_summary)

# T1.5 Near-duplicate columns (Spearman |rho| > 0.97) and zero-heavy columns
corr_spearman = df[num_cols].corr(method="spearman")
dup_pairs = []
for i in range(len(num_cols)):
    for j in range(i + 1, len(num_cols)):
        c1, c2 = num_cols[i], num_cols[j]
        rho = float(corr_spearman.loc[c1, c2])
        if abs(rho) > 0.97:
            dup_pairs.append({
                "col_1": c1,
                "col_2": c2,
                "spearman_rho": round(rho, 5),
            })
dup_pairs_df = pd.DataFrame(dup_pairs).sort_values("spearman_rho", ascending=False, key=abs)
dup_pairs_df.to_csv(config.TABLES_DIR / "near_duplicate_pairs.csv", index=False)
print(f"Found {len(dup_pairs_df)} pairs with |Spearman rho| > 0.97")

zero_heavy_df = quantiles_df[quantiles_df["pct_zero"] >= 85.0].sort_values("pct_zero", ascending=False)
zero_heavy_df.to_csv(config.TABLES_DIR / "zero_heavy_columns.csv", index=False)

# Quick CV test: tutorial encoding on train 70% vs dropping 10 redundant columns
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=config.SEED)
cv_model = XGBClassifier(
    n_estimators=300, learning_rate=0.05, max_depth=6, eval_metric="logloss", random_state=config.SEED, n_jobs=4
)
cv_full_scores = cross_val_score(cv_model, X_train, y_train, cv=skf, scoring="roc_auc", n_jobs=1)
redundant_10 = [
    "adjqty", "adjmou", "adjrev", "plcd_vce_Mean", "comp_vce_Mean",
    "comp_dat_Mean", "peak_dat_Mean", "opk_dat_Mean", "ovrmou_Mean", "ccrndmou_Mean"
]
cv_drop10_scores = cross_val_score(
    cv_model, X_train.drop(columns=redundant_10), y_train, cv=skf, scoring="roc_auc", n_jobs=1
)
print(f"5-fold CV AUC (all 98 features): {cv_full_scores.mean():.5f} +/- {cv_full_scores.std():.5f}")
print(f"5-fold CV AUC (drop 10 redundant): {cv_drop10_scores.mean():.5f} +/- {cv_drop10_scores.std():.5f}")

# T1.6 Documentation vs Data Audit
valid_cm = df[["change_mou", "mou_Mean", "avg3mou"]].dropna()
pct_cm_lt_neg100 = float((valid_cm["change_mou"] < -100).mean() * 100)
diff_mou = valid_cm["mou_Mean"] - valid_cm["avg3mou"]
pct_diff_mou = (valid_cm["mou_Mean"] - valid_cm["avg3mou"]) / valid_cm["avg3mou"].replace(0, np.nan) * 100
corr_cm_abs_diff = float(valid_cm["change_mou"].corr(diff_mou))
corr_cm_pct_diff = float(valid_cm["change_mou"].corr(pct_diff_mou))

valid_cr = df[["change_rev", "rev_Mean", "avg3rev"]].dropna()
pct_cr_lt_neg100 = float((valid_cr["change_rev"] < -100).mean() * 100)
diff_rev = valid_cr["rev_Mean"] - valid_cr["avg3rev"]
corr_cr_abs_diff = float(valid_cr["change_rev"].corr(diff_rev))

iwylis_corr_mou = float(df["iwylis_vce_Mean"].corr(df["mouiwylisv_Mean"]))
iwylis_corr_ow = float(df["iwylis_vce_Mean"].corr(df["owylis_vce_Mean"]))
recv_sms_nonzero = int((df["recv_sms_Mean"].fillna(0) != 0).sum())
infobase_vc = df["infobase"].value_counts(dropna=False).to_dict()
infobase_churn = df.groupby(df["infobase"].fillna("MISSING"))["churn"].agg(["count", "mean"]).to_dict(orient="index")
hnd_price_tiers = sorted([round(float(x), 2) for x in df["hnd_price"].dropna().unique()])

# Single-feature univariate AUCs (on train split to prevent leakage)
univariate_aucs = []
for col in num_cols:
    valid_idx = X_train[col].notna()
    if valid_idx.sum() > 100 and X_train.loc[valid_idx, col].nunique() > 1:
        auc_raw = float(roc_auc_score(y_train.loc[valid_idx], X_train.loc[valid_idx, col]))
        auc_eff = max(auc_raw, 1.0 - auc_raw)
        univariate_aucs.append({
            "column": col,
            "auc_raw": round(auc_raw, 4),
            "auc_effective": round(auc_eff, 4),
            "direction": "higher -> more churn" if auc_raw >= 0.5 else "higher -> less churn",
        })
univariate_df = pd.DataFrame(univariate_aucs).sort_values("auc_effective", ascending=False)
univariate_df.to_csv(config.TABLES_DIR / "univariate_auc.csv", index=False)

# T1.7 Target audit
churn_counts = df["churn"].value_counts().to_dict()
n_churn_1 = int(churn_counts[1])
n_churn_0 = int(churn_counts[0])
churn_rate = round(n_churn_1 / len(df), 6)

# Save Phase 0 & Phase 1 results to outputs/results.json
results = {
    "meta": {
        "seed": config.SEED,
        "versions": versions,
        "run_time_sec": round(time.time() - t0, 2),
    },
    "data": {
        "n_rows": int(len(df)),
        "n_cols_merged": int(df.shape[1]),
        "n_features_raw": int(df.shape[1] - 2),
        "client_shape": list(client.shape),
        "record_shape": list(record.shape),
        "dtypes_count": {k: int(v) for k, v in dtype_counts.items()},
        "memory_mb": mem_mb,
        "n_duplicate_rows": n_dup_rows,
        "n_duplicate_ids": n_dup_ids,
        "id_min": int(df["Customer_ID"].min()),
        "id_max": int(df["Customer_ID"].max()),
        "churn_count_1": n_churn_1,
        "churn_count_0": n_churn_0,
        "churn_rate": churn_rate,
        "churn_rate_pct": round(churn_rate * 100, 2),
        "stayed_rate_pct": round((1 - churn_rate) * 100, 2),
        "months_min": int(df["months"].min()),
        "months_max": int(df["months"].max()),
        "months_median": float(df["months"].median()),
        "months_mean": round(float(df["months"].mean()), 2),
        "missing_top20": missing_df.head(20).to_dict(orient="records"),
        "demo_missing_block": {
            "columns": demo_block_cols,
            "exact_same_rows": exact_same_block,
            "n_rows": block_n,
            "pct_rows": round(block_n / len(df) * 100, 2),
            "churn_rate": round(block_churn, 4),
        },
        "negatives": negatives_summary,
        "near_duplicate_pairs_count": int(len(dup_pairs_df)),
        "near_duplicate_top10": dup_pairs_df.head(10).to_dict(orient="records"),
        "cv_auc_all_98": round(float(cv_full_scores.mean()), 4),
        "cv_auc_drop_10_dups": round(float(cv_drop10_scores.mean()), 4),
        "doc_discrepancies": {
            "change_mou_pct_lt_neg100": round(pct_cm_lt_neg100, 2),
            "change_mou_corr_abs_diff": round(corr_cm_abs_diff, 4),
            "change_mou_corr_pct_diff": round(corr_cm_pct_diff, 4),
            "change_rev_pct_lt_neg100": round(pct_cr_lt_neg100, 2),
            "change_rev_corr_abs_diff": round(corr_cr_abs_diff, 4),
            "iwylis_corr_mouiwylisv": round(iwylis_corr_mou, 4),
            "iwylis_corr_owylis": round(iwylis_corr_ow, 4),
            "recv_sms_nonzero_count": recv_sms_nonzero,
            "hnd_price_n_tiers": len(hnd_price_tiers),
            "hnd_price_tiers": hnd_price_tiers,
            "infobase_breakdown": {str(k): {"count": int(v["count"]), "churn_rate": round(float(v["mean"]), 4)} for k, v in infobase_churn.items()},
        },
        "univariate_top10": univariate_df.head(10).to_dict(orient="records"),
    },
    "tutorial_baseline": {
        "majority_baseline_acc": round(maj_baseline_acc, 4),
        "test_acc": round(tut_test_acc, 4),
        "test_auc": round(tut_test_auc, 4),
        "train_acc": round(tut_train_acc, 4),
        "train_auc": round(tut_train_auc, 4),
        "test_precision": round(tut_prec, 4),
        "test_recall": round(tut_rec, 4),
        "test_f1": round(tut_f1, 4),
        "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
        "cv5_auc_mean": round(float(cv_full_scores.mean()), 4),
        "cv5_auc_std": round(float(cv_full_scores.std()), 4),
        "top_gain_features": gain_sorted[:10],
        "top_weight_features": weight_sorted[:10],
    },
}

with open(config.RESULTS_JSON, "w") as f:
    json.dump(results, f, indent=2)

print("Successfully wrote outputs/results.json in", round(time.time() - t0, 2), "s")
