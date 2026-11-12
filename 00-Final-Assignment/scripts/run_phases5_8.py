"""Phases 5, 6, 7, 8: Feature engineering, model experiments (CV + test), interpretation, and business impact."""
import json
import sys
import time
from pathlib import Path

import joblib
import lightgbm as lgb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from src.economics import compute_net_impact, compute_topk_metrics
from src.features import (
    ENGINEERED_FEATURES,
    REDUNDANT_10_COLS,
    SENSITIVE_ETHNIC,
    SENSITIVE_PROXIES,
    engineer_features,
)

t0 = time.time()

# ---------------------------------------------------------
# 1. Load, merge, and engineer features
# ---------------------------------------------------------
client = pd.read_csv(config.CLIENT_CSV)
record = pd.read_csv(config.RECORD_CSV)
df = record.merge(client, on="Customer_ID", how="inner")

df_feat = engineer_features(df)
all_raw_cols = [c for c in df.columns if c not in ("Customer_ID", "churn")]
object_cols = df[all_raw_cols].select_dtypes(include=["object", "string"]).columns.tolist()
num_raw_cols = [c for c in all_raw_cols if c not in object_cols]

# Split indices (exact same 70/30 stratified split with SEED=42)
train_idx, test_idx = train_test_split(
    np.arange(len(df)), test_size=0.3, random_state=config.SEED, stratify=df["churn"]
)
y = df["churn"].values
y_train, y_test = y[train_idx], y[test_idx]

# Check univariate AUC of engineered features on train split (T5.3 leakage check)
eng_univariate = []
for col in ENGINEERED_FEATURES:
    s_tr = df_feat[col].iloc[train_idx]
    valid = s_tr.notna()
    auc_r = float(roc_auc_score(y_train[valid], s_tr[valid]))
    auc_e = max(auc_r, 1.0 - auc_r)
    assert auc_e < 0.65, f"Suspiciously high single-feature AUC for {col}: {auc_e}"
    eng_univariate.append({"feature": col, "auc_raw": round(auc_r, 4), "auc_effective": round(auc_e, 4)})
pd.DataFrame(eng_univariate).to_csv(config.TABLES_DIR / "engineered_univariate_auc.csv", index=False)
print("Max engineered single-feature AUC:", max(x["auc_effective"] for x in eng_univariate))

# Prepare encoded matrices:
# (a) Tutorial LabelEncoder style
df_le = df_feat.drop(columns=["Customer_ID", "churn"]).copy()
for col in object_cols:
    le = LabelEncoder()
    df_le[col] = le.fit_transform(df_le[col].astype(str))

# (b) Leakage-safe OrdinalEncoder (fit on train only, unknown/missing -> -1)
df_ord_train = df_feat.iloc[train_idx].drop(columns=["Customer_ID", "churn"]).copy()
df_ord_test = df_feat.iloc[test_idx].drop(columns=["Customer_ID", "churn"]).copy()
ord_enc = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1, encoded_missing_value=-2)
df_ord_train[object_cols] = ord_enc.fit_transform(df_ord_train[object_cols].astype(str))
df_ord_test[object_cols] = ord_enc.transform(df_ord_test[object_cols].astype(str))

# Feature subsets:
# - raw_98: all 98 original features
# - eng_fair_107: 98 original - 10 redundant - 1 ethnic + 20 engineered = 107 features (Fair & Clean)
# - eng_all_108: 98 original - 10 redundant + 20 engineered = 108 features (includes ethnic for fairness comparison)
# - eng_noproxy_96: eng_fair_107 minus all sensitive proxies
cols_raw_98 = all_raw_cols
cols_eng_all_108 = [c for c in all_raw_cols if c not in REDUNDANT_10_COLS] + ENGINEERED_FEATURES
cols_eng_fair_107 = [c for c in cols_eng_all_108 if c not in SENSITIVE_ETHNIC]
cols_eng_noproxy = [c for c in cols_eng_all_108 if c not in SENSITIVE_PROXIES]

print(f"Feature counts -> Raw: {len(cols_raw_98)}, Eng All: {len(cols_eng_all_108)}, Eng Fair (No Ethnic): {len(cols_eng_fair_107)}, No Proxies: {len(cols_eng_noproxy)}")

# ---------------------------------------------------------
# 2. 5-Fold Stratified CV on 70% Training Set (Phase 6)
# ---------------------------------------------------------
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=config.SEED)

# Preprocessor for Logistic Regression (impute median + missing indicator + scale numerics + one-hot categoricals)
num_fair_cols = [c for c in cols_eng_fair_107 if c not in object_cols]
cat_fair_cols = [c for c in cols_eng_fair_107 if c in object_cols]

lr_preproc = ColumnTransformer(
    transformers=[
        ("num", Pipeline([
            ("impute", SimpleImputer(strategy="median", add_indicator=True)),
            ("scale", StandardScaler()),
        ]), num_fair_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_fair_cols),
    ]
)

models_spec = [
    (
        "M0",
        "Dummy Majority Baseline",
        "Predicts majority class (stayed=0)",
        cols_raw_98,
        "ordinal",
        DummyClassifier(strategy="most_frequent"),
    ),
    (
        "M1",
        "Logistic Regression (Pipeline)",
        "Linear baseline (impute + scale + OHE, 107 fair features)",
        cols_eng_fair_107,
        "raw_df",
        Pipeline([
            ("prep", lr_preproc),
            ("clf", LogisticRegression(max_iter=400, C=0.1, random_state=config.SEED)),
        ]),
    ),
    (
        "M2",
        "Shallow Decision Tree (depth=4)",
        "Rule-based explanation model (max_depth=4, 107 fair features)",
        cols_eng_fair_107,
        "ordinal",
        DecisionTreeClassifier(max_depth=4, min_samples_leaf=200, random_state=config.SEED),
    ),
    (
        "M3",
        "XGBoost (Tutorial Baseline)",
        "98 raw features, LabelEncoder, depth=6, lr=0.05, n=300",
        cols_raw_98,
        "le",
        XGBClassifier(
            n_estimators=300, learning_rate=0.05, max_depth=6,
            eval_metric="logloss", random_state=config.SEED, n_jobs=4
        ),
    ),
    (
        "M4",
        "XGBoost + Engineered Features",
        "107 fair features (20 engineered, -10 dups, no ethnic), depth=6, lr=0.05, n=300",
        cols_eng_fair_107,
        "ordinal",
        XGBClassifier(
            n_estimators=300, learning_rate=0.05, max_depth=6,
            eval_metric="logloss", random_state=config.SEED, n_jobs=4
        ),
    ),
    (
        "M5",
        "XGBoost Regularized & Tuned",
        "107 fair features, depth=5, lr=0.03, n=550, subsample=0.8, colsample=0.8, min_child_weight=20",
        cols_eng_fair_107,
        "ordinal",
        XGBClassifier(
            n_estimators=550, learning_rate=0.03, max_depth=5,
            subsample=0.8, colsample_bytree=0.8, min_child_weight=20, reg_lambda=2.0,
            eval_metric="logloss", random_state=config.SEED, n_jobs=4
        ),
    ),
    (
        "M6",
        "LightGBM (Gradient Boosted Trees)",
        "107 fair features, num_leaves=31, lr=0.03, n=500, subsample=0.8",
        cols_eng_fair_107,
        "ordinal",
        lgb.LGBMClassifier(
            n_estimators=500, learning_rate=0.03, num_leaves=31,
            subsample=0.8, colsample_bytree=0.8, min_child_samples=50,
            random_state=config.SEED, n_jobs=4, verbose=-1
        ),
    ),
]

trained_models = {}
exp_csv_path = config.TABLES_DIR / "experiment_log.csv"
if exp_csv_path.exists():
    exp_df = pd.read_csv(exp_csv_path)
    exp_rows = exp_df.to_dict(orient="records")
    print("Loaded cached 5-fold CV experiment_log.csv with", len(exp_rows), "models.")
    # Fit only M5 on full 70% train
    m5_clf = [c for mid, _, _, _, _, c in models_spec if mid == "M5"][0]
    X_tr_m5 = df_ord_train[cols_eng_fair_107]
    X_te_m5 = df_ord_test[cols_eng_fair_107]
    m5_clf.fit(X_tr_m5, y_train)
    trained_models["M5"] = (m5_clf, X_tr_m5, X_te_m5, cols_eng_fair_107)
else:
    exp_rows = []
    for mid, mname, mdesc, fcols, enc_type, clf in models_spec:
        t_m = time.time()
        if enc_type == "raw_df":
            X_tr = df_feat.iloc[train_idx][fcols].copy()
            X_tr[cat_fair_cols] = X_tr[cat_fair_cols].astype(str)
            X_te = df_feat.iloc[test_idx][fcols].copy()
            X_te[cat_fair_cols] = X_te[cat_fair_cols].astype(str)
        elif enc_type == "le":
            X_tr = df_le.iloc[train_idx][fcols]
            X_te = df_le.iloc[test_idx][fcols]
        else:
            X_tr = df_ord_train[fcols].fillna(-999) if mid == "M2" else df_ord_train[fcols]
            X_te = df_ord_test[fcols].fillna(-999) if mid == "M2" else df_ord_test[fcols]

        cv_res = cross_validate(
            clf, X_tr, y_train, cv=skf, scoring=["roc_auc", "accuracy"], n_jobs=1, return_train_score=False
        )
        cv_auc_mean = float(cv_res["test_roc_auc"].mean())
        cv_auc_std = float(cv_res["test_roc_auc"].std())
        cv_acc_mean = float(cv_res["test_accuracy"].mean())

        # Fit on full 70% train
        clf.fit(X_tr, y_train)
        trained_models[mid] = (clf, X_tr, X_te, fcols)

        p_tr = clf.predict_proba(X_tr)[:, 1]
        yhat_tr = clf.predict(X_tr)
        train_auc = float(roc_auc_score(y_train, p_tr))
        train_acc = float(accuracy_score(y_train, yhat_tr))

        # Evaluate on held-out 30% test set for reporting table
        p_te = clf.predict_proba(X_te)[:, 1]
        yhat_te = clf.predict(X_te)
        test_auc = float(roc_auc_score(y_test, p_te))
        test_acc = float(accuracy_score(y_test, yhat_te))
        test_prec = float(precision_score(y_test, yhat_te, zero_division=0))
        test_rec = float(recall_score(y_test, yhat_te, zero_division=0))
        test_f1 = float(f1_score(y_test, yhat_te, zero_division=0))

        # Top-10% precision on test
        top10_n = int(0.10 * len(y_test))
        top10_prec = float(y_test[np.argsort(-p_te)[:top10_n]].mean()) if mid != "M0" else float(y_test.mean())

        row = {
            "id": mid,
            "name": mname,
            "description": mdesc,
            "n_features": len(fcols),
            "cv_auc_mean": round(cv_auc_mean, 4),
            "cv_auc_std": round(cv_auc_std, 4),
            "cv_acc_mean": round(cv_acc_mean, 4),
            "train_auc": round(train_auc, 4),
            "train_acc": round(train_acc, 4),
            "test_auc": round(test_auc, 4),
            "test_acc": round(test_acc, 4),
            "test_precision": round(test_prec, 4),
            "test_recall": round(test_rec, 4),
            "test_f1": round(test_f1, 4),
            "test_top10_precision": round(top10_prec, 4),
            "train_test_acc_gap_pp": round((train_acc - test_acc) * 100, 2),
            "fit_time_sec": round(time.time() - t_m, 1),
        }
        exp_rows.append(row)
        print(f"[{mid}] {mname}: CV AUC = {cv_auc_mean:.4f} +/- {cv_auc_std:.4f} | Test AUC = {test_auc:.4f}, Test Acc = {test_acc:.4f}, Train Acc = {train_acc:.4f}")

    exp_df = pd.DataFrame(exp_rows)
    exp_df.to_csv(exp_csv_path, index=False)

# ---------------------------------------------------------
# 3. Fairness & Encoding Comparisons (T5.1, T5.4, T7.8)
# ---------------------------------------------------------
# Compare M5 with `ethnic` included (108 features) vs without `ethnic` (107 features) vs without any demographic proxies (96 features)
# Use an 80/20 stratified validation split inside the 70% training set for fast, leakage-free comparison
tr_sub_idx, val_sub_idx = train_test_split(
    np.arange(len(y_train)), test_size=0.2, random_state=config.SEED, stratify=y_train
)
clf_probe = XGBClassifier(
    n_estimators=250, learning_rate=0.06, max_depth=5,
    subsample=0.8, colsample_bytree=0.8, min_child_weight=20, reg_lambda=2.0,
    eval_metric="logloss", random_state=config.SEED, n_jobs=4
)
clf_probe.fit(df_ord_train[cols_eng_all_108].iloc[tr_sub_idx], y_train[tr_sub_idx])
auc_with_ethnic = float(roc_auc_score(y_train[val_sub_idx], clf_probe.predict_proba(df_ord_train[cols_eng_all_108].iloc[val_sub_idx])[:, 1]))

clf_probe.fit(df_ord_train[cols_eng_fair_107].iloc[tr_sub_idx], y_train[tr_sub_idx])
auc_without_ethnic = float(roc_auc_score(y_train[val_sub_idx], clf_probe.predict_proba(df_ord_train[cols_eng_fair_107].iloc[val_sub_idx])[:, 1]))

clf_probe.fit(df_ord_train[cols_eng_noproxy].iloc[tr_sub_idx], y_train[tr_sub_idx])
auc_no_proxies = float(roc_auc_score(y_train[val_sub_idx], clf_probe.predict_proba(df_ord_train[cols_eng_noproxy].iloc[val_sub_idx])[:, 1]))

fairness_comparison = {
    "with_ethnic_108_val_auc": round(auc_with_ethnic, 4),
    "without_ethnic_107_val_auc": round(auc_without_ethnic, 4),
    "without_all_proxies_96_val_auc": round(auc_no_proxies, 4),
    "without_ethnic_107_cv_auc": float(exp_df.loc[exp_df["id"] == "M5", "cv_auc_mean"].values[0]),
    "delta_drop_ethnic": round(auc_without_ethnic - auc_with_ethnic, 4),
    "delta_drop_all_proxies": round(auc_no_proxies - auc_with_ethnic, 4),
}
print("Fairness comparison:", fairness_comparison)

# Choose final model: M5 (XGBoost Regularized & Tuned with Engineered Features, or highest CV AUC among M4/M5/M6)
best_id = "M5"
final_clf, X_tr_final, X_te_final, final_cols = trained_models[best_id]
joblib.dump(final_clf, config.MODELS_DIR / "final_model.joblib")

p_test_final = final_clf.predict_proba(X_te_final)[:, 1]
yhat_test_final = final_clf.predict(X_te_final)
cm_final = confusion_matrix(y_test, yhat_test_final)
tn_f, fp_f, fn_f, tp_f = [int(x) for x in cm_final.ravel()]

# Save test predictions (T6.6)
test_pred_df = pd.DataFrame({
    "Customer_ID": df["Customer_ID"].iloc[test_idx].values,
    "y_true": y_test,
    "p_churn": np.round(p_test_final, 6),
    "rev_Mean": df["rev_Mean"].iloc[test_idx].values,
    "mou_Mean": df["mou_Mean"].iloc[test_idx].values,
    "eqpdays": df["eqpdays"].iloc[test_idx].values,
    "months": df["months"].iloc[test_idx].values,
})
test_pred_df.to_csv(config.TABLES_DIR / "test_predictions.csv", index=False)

# ---------------------------------------------------------
# 4. Phase 7 — Evaluation, Top-k, Calibration, Importance, PDP, Ablation
# ---------------------------------------------------------
# T7.2 Top-k% targeting table (sample & re-based to 5% and 10%)
topk_rows = compute_topk_metrics(y_test, p_test_final, k_pcts=(1, 2, 5, 10, 15, 20, 30, 50), pi_reals=(0.05, 0.10))
topk_df = pd.DataFrame(topk_rows)
topk_df.to_csv(config.TABLES_DIR / "topk_targeting.csv", index=False)
print("Top-k targeting table:\n", topk_df)

# Also compute bottom-10% churn rate on test set
bot10_n = int(0.10 * len(y_test))
bot10_churn = float(y_test[np.argsort(p_test_final)[:bot10_n]].mean())

# T7.3 Calibration curve
prob_true, prob_pred = calibration_curve(y_test, p_test_final, n_bins=10, strategy="uniform")
brier = float(brier_score_loss(y_test, p_test_final))
calib_rows = [
    {"bin_pred": round(float(pp), 4), "bin_true": round(float(pt), 4)}
    for pp, pt in zip(prob_pred, prob_true)
]

# T7.4 Feature importance: Gain and Permutation Importance on held-out data
gain_raw = final_clf.get_booster().get_score(importance_type="gain")
tot_g = sum(gain_raw.values())
gain_list = sorted(
    [{"feature": k, "gain": round(float(v), 2), "share_pct": round(float(v) / tot_g * 100, 2)} for k, v in gain_raw.items()],
    key=lambda x: x["gain"], reverse=True
)

# Permutation importance on a 3,000-row subsample of test set for speed
perm_res = permutation_importance(
    final_clf, X_te_final.iloc[:3000], y_test[:3000],
    scoring="roc_auc", n_repeats=3, random_state=config.SEED, n_jobs=1
)
perm_list = sorted(
    [
        {"feature": col, "auc_drop_mean": round(float(m), 5), "auc_drop_std": round(float(s), 5)}
        for col, m, s in zip(final_cols, perm_res.importances_mean, perm_res.importances_std)
    ],
    key=lambda x: x["auc_drop_mean"], reverse=True
)
pd.DataFrame(gain_list[:25]).to_csv(config.TABLES_DIR / "feature_importance_gain.csv", index=False)
pd.DataFrame(perm_list[:25]).to_csv(config.TABLES_DIR / "feature_importance_permutation.csv", index=False)

# T7.5 Partial Dependence (PDP) for eqpdays and months
pdp_sample = X_tr_final.sample(n=2000, random_state=config.SEED).copy()
eqp_grid = [30, 90, 150, 210, 250, 280, 300, 315, 335, 360, 420, 500, 650, 800]
pdp_eqp = []
for val in eqp_grid:
    tmp = pdp_sample.copy()
    tmp["eqpdays"] = val
    tmp["dev_age_gt_300"] = int(val > 300)
    tmp["dev_age_301_360_peak"] = int(300 < val <= 360)
    tmp["eqp_per_tenure_day"] = max(val, 0) / (tmp["months"].clip(lower=1) * 30.0)
    pdp_eqp.append({"eqpdays": val, "mean_pred_prob": round(float(final_clf.predict_proba(tmp)[:, 1].mean()), 4)})

months_grid = list(range(6, 37, 2))
pdp_months = []
for val in months_grid:
    tmp = pdp_sample.copy()
    tmp["months"] = val
    tmp["tenure_le_9"] = int(val <= 9)
    tmp["tenure_10_12_cliff"] = int(10 <= val <= 12)
    tmp["eqp_per_tenure_day"] = tmp["eqpdays"].clip(lower=0) / (max(val, 1) * 30.0)
    pdp_months.append({"months": val, "mean_pred_prob": round(float(final_clf.predict_proba(tmp)[:, 1].mean()), 4)})

# T7.6 Ablation: drop top feature (`dev_age_gt_300` and `eqpdays`) and retrain on train_sub -> evaluate on val_sub
top1_feat = gain_list[0]["feature"]
cols_drop_top1 = [c for c in final_cols if c != top1_feat]
cols_drop_all_eqp = [c for c in final_cols if c not in ("eqpdays", "dev_age_gt_300", "dev_age_301_360_peak", "eqp_per_tenure_day")]

clf_probe.fit(X_tr_final[cols_drop_top1].iloc[tr_sub_idx], y_train[tr_sub_idx])
auc_drop_top1 = float(roc_auc_score(y_train[val_sub_idx], clf_probe.predict_proba(X_tr_final[cols_drop_top1].iloc[val_sub_idx])[:, 1]))

clf_probe.fit(X_tr_final[cols_drop_all_eqp].iloc[tr_sub_idx], y_train[tr_sub_idx])
auc_drop_all_eqp = float(roc_auc_score(y_train[val_sub_idx], clf_probe.predict_proba(X_tr_final[cols_drop_all_eqp].iloc[val_sub_idx])[:, 1]))

ablation_res = {
    "top1_feature_dropped": top1_feat,
    "base_val_auc": round(auc_without_ethnic, 4),
    "drop_top1_val_auc": round(auc_drop_top1, 4),
    "drop_all_eqpdays_signals_val_auc": round(auc_drop_all_eqp, 4),
    "delta_drop_all_eqpdays": round(auc_drop_all_eqp - auc_without_ethnic, 4),
}
print("Ablation results:", ablation_res)

# ---------------------------------------------------------
# 5. Phase 8 — Business Impact Model (Scenarios, Optimal k*, Sensitivity, Lane 2 Pilot)
# ---------------------------------------------------------
# ARPU from data: mean rev_Mean = 58.72 MU, median = 48.20 MU; for active customers (mou_Mean > 0): mean = 59.30 MU
arpu_mean = round(float(df["rev_Mean"].mean()), 2)
arpu_median = round(float(df["rev_Mean"].median()), 2)

# Lookup re-based precision at each k in {1, 2, 5, 10, 15, 20, 30, 50}
topk_map = {r["k_pct"]: r for r in topk_rows}

# Evaluate Net Impact across k_pcts for 3 Realistic Scenarios + Sample Unadjusted comparison
# Conservative: pi_r = 5% (tutorial lower bound), ARPU = 48.20 MU (median), margin = 65%, H = 6 months (V = 187.98 MU), s = 15%, c = 3.0 MU (digital/SMS + modest plan credit)
# Base Case:    pi_r = 10% (tutorial upper bound / prepaid benchmark), ARPU = 58.72 MU (mean), margin = 70%, H = 8 months (V = 328.83 MU), s = 20%, c = 8.0 MU (outbound call + targeted loyalty discount)
# Optimistic:   pi_r = 10%, ARPU = 58.72 MU, margin = 75%, H = 12 months (V = 528.48 MU), s = 25%, c = 10.0 MU (proactive device/plan bundle)
scenario_defs = [
    {
        "name": "Conservative (5% Real Churn Prior)",
        "short_name": "Conservative",
        "pi_r": 0.05,
        "prec_col": "precision_rebased_5pct",
        "arpu": arpu_median,
        "margin": 0.65,
        "horizon_months": 6,
        "s": 0.15,
        "c": 2.50,
    },
    {
        "name": "Base Case (10% Real Churn Prior)",
        "short_name": "Base Case",
        "pi_r": 0.10,
        "prec_col": "precision_rebased_10pct",
        "arpu": arpu_mean,
        "margin": 0.70,
        "horizon_months": 8,
        "s": 0.20,
        "c": 7.50,
    },
    {
        "name": "Optimistic (10% Prior + 12m Horizon)",
        "short_name": "Optimistic",
        "pi_r": 0.10,
        "prec_col": "precision_rebased_10pct",
        "arpu": arpu_mean,
        "margin": 0.75,
        "horizon_months": 12,
        "s": 0.25,
        "c": 10.00,
    },
]

curves_by_scenario = {}
scenario_summary_at_k10 = []
optimal_k_by_scenario = {}

for sc in scenario_defs:
    sc_rows = []
    for k in (1, 2, 5, 10, 15, 20, 30, 50):
        p_adj = topk_map[k][sc["prec_col"]]
        res_k = compute_net_impact(
            n_base=100000,
            k_pct=k,
            p_adj=p_adj,
            s=sc["s"],
            arpu=sc["arpu"],
            margin=sc["margin"],
            horizon_months=sc["horizon_months"],
            cost_per_target=sc["c"],
        )
        res_k["scenario"] = sc["short_name"]
        res_k["pi_r"] = sc["pi_r"]
        sc_rows.append(res_k)
    curves_by_scenario[sc["short_name"]] = sc_rows
    best_k_row = max(sc_rows, key=lambda x: x["net_impact_mu"])
    optimal_k_by_scenario[sc["short_name"]] = best_k_row
    k10_row = [r for r in sc_rows if r["k_pct"] == 10][0]
    scenario_summary_at_k10.append(k10_row)

# Also compute Unadjusted Sample Prior (49.56% churn) at k=10% with Base Case parameters to show the overstatement!
unadjusted_k10 = compute_net_impact(
    n_base=100000,
    k_pct=10,
    p_adj=topk_map[10]["precision_sample"],
    s=0.20,
    arpu=arpu_mean,
    margin=0.70,
    horizon_months=8,
    cost_per_target=7.50,
)
unadjusted_k10["scenario"] = "Unadjusted Sample (49.6% Prior)"
unadjusted_k10["pi_r"] = round(float(y_test.mean()), 4)

print("Scenarios at k=10%:\n", pd.DataFrame(scenario_summary_at_k10 + [unadjusted_k10]))
print("Optimal k* per scenario:\n", pd.DataFrame(list(optimal_k_by_scenario.values())))

# T8.5 Sensitivity Tornado around Base Case at k*=10%
base_k10 = [r for r in scenario_summary_at_k10 if r["scenario"] == "Base Case"][0]
base_net = base_k10["net_impact_mu"]

tornado_specs = [
    ("Real Churn Base Rate (π_real: 5% vs 15%)",
     compute_net_impact(100000, 10, topk_map[10]["precision_rebased_5pct"], 0.20, arpu_mean, 0.70, 8, 7.50)["net_impact_mu"],
     compute_net_impact(100000, 10, compute_topk_metrics(y_test, p_test_final, k_pcts=(10,), pi_reals=(0.15,))[0]["precision_rebased_15pct"], 0.20, arpu_mean, 0.70, 8, 7.50)["net_impact_mu"]),
    ("Intervention Success Rate (s: 12% vs 28%)",
     compute_net_impact(100000, 10, base_k10["p_adj"], 0.12, arpu_mean, 0.70, 8, 7.50)["net_impact_mu"],
     compute_net_impact(100000, 10, base_k10["p_adj"], 0.28, arpu_mean, 0.70, 8, 7.50)["net_impact_mu"]),
    ("Retained Horizon (H: 5m vs 11m)",
     compute_net_impact(100000, 10, base_k10["p_adj"], 0.20, arpu_mean, 0.70, 5, 7.50)["net_impact_mu"],
     compute_net_impact(100000, 10, base_k10["p_adj"], 0.20, arpu_mean, 0.70, 11, 7.50)["net_impact_mu"]),
    ("Offer Cost per Customer (c: 10.5 MU vs 4.5 MU)",
     compute_net_impact(100000, 10, base_k10["p_adj"], 0.20, arpu_mean, 0.70, 8, 10.50)["net_impact_mu"],
     compute_net_impact(100000, 10, base_k10["p_adj"], 0.20, arpu_mean, 0.70, 8, 4.50)["net_impact_mu"]),
    ("Customer ARPU (Median 48.2 vs P75 70.8 MU)",
     compute_net_impact(100000, 10, base_k10["p_adj"], 0.20, arpu_median, 0.70, 8, 7.50)["net_impact_mu"],
     compute_net_impact(100000, 10, base_k10["p_adj"], 0.20, 70.75, 0.70, 8, 7.50)["net_impact_mu"]),
    ("Targeting Cutoff (k: 20% vs 15%)",
     curves_by_scenario["Base Case"][5]["net_impact_mu"],
     curves_by_scenario["Base Case"][4]["net_impact_mu"]),
]
tornado_rows = []
for label, low_val, high_val in tornado_specs:
    tornado_rows.append({
        "parameter": label,
        "low_net_mu": low_val,
        "high_net_mu": high_val,
        "base_net_mu": base_net,
        "swing_mu": abs(high_val - low_val),
    })
tornado_df = pd.DataFrame(tornado_rows).sort_values("swing_mu", ascending=False)
tornado_df.to_csv(config.TABLES_DIR / "sensitivity_tornado.csv", index=False)

# T8.6 Lane 2 Sizing (Pre-300-Day Handset Refresh & Months 8-9 Renewal Check Pilot)
# Window: Customers with eqpdays in [240, 300] and rev_Mean >= 30 MU
lane2_cohort = df[(df["eqpdays"] >= 240) & (df["eqpdays"] <= 300) & (df["rev_Mean"] >= 30)]
n_lane2_window = int(len(lane2_cohort))
lane2_arpu = round(float(lane2_cohort["rev_Mean"].mean()), 2)
# Observed sample jump across 300d is +23.83 pp; re-based to 10% real prior, excess hazard gap is ~5.5 pp
# In a 90-day controlled A/B pilot (80% treatment = 5,522 customers, 20% holdout = 1,380 customers),
# if an early handset refresh closes 25% of the re-based hazard gap at cost 6 MU:
lane2_pilot = {
    "cohort_definition": "Active subscribers with eqpdays in [240, 300] days and rev_Mean >= 30 MU",
    "n_cohort_in_100k": n_lane2_window,
    "cohort_arpu_mu": lane2_arpu,
    "treatment_share": 0.80,
    "n_treatment": int(round(n_lane2_window * 0.80)),
    "n_holdout_control": int(n_lane2_window - round(n_lane2_window * 0.80)),
    "pilot_duration_days": 90,
    "assumed_rebased_excess_churn_gap": 0.055,
    "assumed_gap_closure_share": 0.25,
    "cost_per_offer_mu": 4.0,
    "v_customer_mu": round(lane2_arpu * 0.70 * 8, 2),
}
lane2_Incremental_saves = lane2_pilot["n_treatment"] * lane2_pilot["assumed_rebased_excess_churn_gap"] * lane2_pilot["assumed_gap_closure_share"]
lane2_gross_mu = lane2_Incremental_saves * lane2_pilot["v_customer_mu"]
lane2_cost_mu = lane2_pilot["n_treatment"] * lane2_pilot["cost_per_offer_mu"]
lane2_pilot["expected_incremental_saves"] = round(lane2_Incremental_saves, 1)
lane2_pilot["expected_gross_saved_mu"] = round(lane2_gross_mu, 0)
lane2_pilot["expected_pilot_cost_mu"] = round(lane2_cost_mu, 0)
lane2_pilot["expected_net_pilot_mu"] = round(lane2_gross_mu - lane2_cost_mu, 0)

# ---------------------------------------------------------
# 6. Generate Charts for Slides 9, 10, 11, 13
# ---------------------------------------------------------
# Chart Slide 9: Model Comparison Bar Chart (figures/model_comparison.png)
fig, ax = plt.subplots(figsize=(8.8, 4.8), dpi=220)
fig.patch.set_facecolor(config.PALETTE["white"])
ax.set_facecolor(config.PALETTE["white"])
m_plot = exp_df[exp_df["id"] != "M0"].copy()
m_labels = [f"{r['id']}: {r['name'].split('(')[0].strip()}" for _, r in m_plot.iterrows()]
y_pos = np.arange(len(m_plot))
colors_m = [config.PALETTE["teal"] if r["id"] == best_id else config.PALETTE["blue"] for _, r in m_plot.iterrows()]
bars = ax.barh(y_pos, m_plot["cv_auc_mean"], xerr=m_plot["cv_auc_std"], color=colors_m, height=0.6, capsize=3)
ax.set_yticks(y_pos)
ax.set_yticklabels(m_labels, fontsize=10.5, fontweight="bold", color=config.PALETTE["navy"])
ax.set_xlim(0.60, 0.785)
ax.axvline(0.6940, color=config.PALETTE["amber"], linestyle="--", lw=1.8, label="Tutorial XGBoost Baseline (0.6940)")
for bar, (_, r) in zip(bars, m_plot.iterrows()):
    w = bar.get_width()
    ax.text(w + 0.003, bar.get_y() + bar.get_height() / 2, f"CV: {w:.4f} | Test: {r['test_auc']:.4f} (Acc: {r['test_acc']*100:.1f}%)", va="center", fontsize=9.2, fontweight="bold", color=config.PALETTE["navy"])
ax.set_title("5-Fold Cross-Validation & Test ROC-AUC Across Candidate Models", fontsize=12.5, fontweight="bold", color=config.PALETTE["navy"], pad=10)
ax.set_xlabel("ROC-AUC Score (0.50 = Random Guess)", fontsize=11, fontweight="bold", color=config.PALETTE["navy"])
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(axis="x", linestyle="--", alpha=0.45, color=config.PALETTE["grid"])
ax.legend(loc="lower right", fontsize=9.5)
plt.tight_layout()
fig.savefig(config.FIGURES_DIR / "model_comparison.png", dpi=220)
fig.savefig(config.FIGURES_DIR / "model_comparison.svg")
plt.close(fig)

# Chart Slide 10: Top 10 Feature Importance by Gain + Lever Classification (figures/feature_importance_levers.png)
lever_map = {
    "dev_age_gt_300": ("Handset Age > 300d Flag", "Direct Lever (Upgrade Offer)"),
    "tenure_le_9": ("Early Tenure (≤ 9 Months)", "Targeting Window"),
    "tenure_10_12_cliff": ("First-Year Cliff (Months 10–12)", "Direct Lever (Renewal Check)"),
    "eqpdays": ("Current Handset Age (Days)", "Direct Lever (Upgrade Offer)"),
    "months": ("Service Tenure (Months)", "Targeting Window"),
    "mou_zero_flag": ("Zero Voice Usage Flag", "Automated Digital Triage"),
    "refurb_new": ("Refurbished vs. New Handset", "Direct Lever (Device Quality)"),
    "hnd_price": ("Handset Price Tier", "Direct Lever (Device Subsidy)"),
    "eqp_per_tenure_day": ("Device Age / Tenure Ratio", "Direct Lever (Upgrade Offer)"),
    "mou_le_10_flag": ("Very Low Usage (≤ 10 MOU)", "Automated Digital Triage"),
    "change_mou": ("Change in Monthly Minutes", "Early Warning Behavioral Signal"),
    "asl_flag": ("Account Spending Limit Flag", "Direct Lever (Plan Flexibility)"),
    "mou_Mean": ("Mean Monthly Voice Minutes", "Early Warning Behavioral Signal"),
    "mou_ratio_3m": ("Current vs. 3m Usage Ratio", "Early Warning Behavioral Signal"),
    "totmrc_Mean": ("Base Monthly Recurring Charge", "Direct Lever (Plan Right-Sizing)"),
    "recurring_rev_share": ("Recurring Revenue Share", "Direct Lever (Plan Right-Sizing)"),
}
top10_g = gain_list[:10][::-1]
fig, ax = plt.subplots(figsize=(9.2, 5.0), dpi=220)
fig.patch.set_facecolor(config.PALETTE["white"])
ax.set_facecolor(config.PALETTE["white"])
f_names = [lever_map.get(x["feature"], (x["feature"], "Behavioral Predictor"))[0] for x in top10_g]
f_levers = [lever_map.get(x["feature"], (x["feature"], "Behavioral Predictor"))[1] for x in top10_g]
f_colors = [
    config.PALETTE["coral"] if "Direct Lever" in lv else (config.PALETTE["teal"] if "Early Warning" in lv else config.PALETTE["blue"])
    for lv in f_levers
]
bars = ax.barh(f_names, [x["share_pct"] for x in top10_g], color=f_colors, height=0.65)
for bar, x, lv in zip(bars, top10_g, f_levers):
    w = bar.get_width()
    ax.text(w + 0.3, bar.get_y() + bar.get_height() / 2, f"{w:.1f}% gain  [{lv}]", va="center", fontsize=9.0, fontweight="bold", color=config.PALETTE["navy"])
ax.set_xlim(0, max(x["share_pct"] for x in top10_g) * 1.72)
ax.set_title("Top 10 Signals by Model Gain Importance & Commercial Intervenability", fontsize=12.5, fontweight="bold", color=config.PALETTE["navy"], pad=10)
ax.set_xlabel("Share of Total Tree Gain Importance (%)", fontsize=11, fontweight="bold", color=config.PALETTE["navy"])
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(axis="x", linestyle="--", alpha=0.45, color=config.PALETTE["grid"])
plt.tight_layout()
fig.savefig(config.FIGURES_DIR / "feature_importance_levers.png", dpi=220)
fig.savefig(config.FIGURES_DIR / "feature_importance_levers.svg")
plt.close(fig)

# Chart Slide 11: Lift & Precision Curve Across Top-k% (figures/topk_lift_curve.png)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.9), dpi=220)
fig.patch.set_facecolor(config.PALETTE["white"])
for a in (ax1, ax2):
    a.set_facecolor(config.PALETTE["white"])
    a.spines["top"].set_visible(False)
    a.spines["right"].set_visible(False)
    a.grid(True, linestyle="--", alpha=0.45, color=config.PALETTE["grid"])

ax1.plot(topk_df["k_pct"], topk_df["precision_sample"] * 100, marker="o", lw=2.5, color=config.PALETTE["coral"], label="Sample Precision (49.6% Base)")
ax1.axhline(y_test.mean() * 100, color=config.PALETTE["slate"], linestyle=":", lw=1.5, label="Sample Random Base (49.6%)")
ax1.plot(topk_df["k_pct"], topk_df["precision_rebased_10pct"] * 100, marker="s", lw=2.5, color=config.PALETTE["teal"], label="Re-based Precision (10% Real Base)")
ax1.plot(topk_df["k_pct"], topk_df["precision_rebased_5pct"] * 100, marker="^", lw=2.2, color=config.PALETTE["blue"], label="Re-based Precision (5% Real Base)")
ax1.set_title("A. Precision@k% (Sample vs. Label-Shift Re-based)", fontsize=12, fontweight="bold", color=config.PALETTE["navy"])
ax1.set_xlabel("Top-k% Customers Targeted by Risk Score", fontsize=10.5, fontweight="bold", color=config.PALETTE["navy"])
ax1.set_ylabel("True Churners Among Targeted (%)", fontsize=10.5, fontweight="bold", color=config.PALETTE["navy"])
ax1.legend(fontsize=8.5, loc="upper right")

ax2.plot(topk_df["k_pct"], topk_df["lift_rebased_10pct"], marker="s", lw=2.5, color=config.PALETTE["teal"], label="Re-based Lift@k (10% Real Base)")
ax2.plot(topk_df["k_pct"], topk_df["lift_sample"], marker="o", lw=2.5, color=config.PALETTE["coral"], label="Sample Lift@k (49.6% Base)")
ax2.axhline(1.0, color=config.PALETTE["slate"], linestyle=":", lw=1.5, label="Random Targeting (1.0x Lift)")
ax2.annotate(
    f"Top 10% Cutoff:\nSample Precision: {topk_map[10]['precision_sample']*100:.1f}% ({topk_map[10]['lift_sample']:.2f}x)\nRe-based (10%): {topk_map[10]['precision_rebased_10pct']*100:.1f}% ({topk_map[10]['lift_rebased_10pct']:.2f}x)",
    xy=(10, topk_map[10]["lift_rebased_10pct"]), xytext=(18, 2.7),
    arrowprops=dict(arrowstyle="->", color=config.PALETTE["navy"], lw=1.6),
    fontsize=9.5, fontweight="bold", color=config.PALETTE["navy"],
    bbox=dict(boxstyle="round,pad=0.35", facecolor="#F0FDF4", edgecolor=config.PALETTE["teal"], lw=1.2)
)
ax2.set_title("B. Targeting Lift Multiplier Over Random Selection", fontsize=12, fontweight="bold", color=config.PALETTE["navy"])
ax2.set_xlabel("Top-k% Customers Targeted by Risk Score", fontsize=10.5, fontweight="bold", color=config.PALETTE["navy"])
ax2.set_ylabel("Lift Multiplier (× Random Selection)", fontsize=10.5, fontweight="bold", color=config.PALETTE["navy"])
ax2.legend(fontsize=8.5, loc="upper right")

plt.tight_layout()
fig.savefig(config.FIGURES_DIR / "topk_lift_curve.png", dpi=220)
fig.savefig(config.FIGURES_DIR / "topk_lift_curve.svg")
plt.close(fig)

# Chart Slide 13: Net Value vs k% Curve + Sensitivity Tornado (figures/impact_scenarios_tornado.png)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 5.0), dpi=220)
fig.patch.set_facecolor(config.PALETTE["white"])
for a in (ax1, ax2):
    a.set_facecolor(config.PALETTE["white"])
    a.spines["top"].set_visible(False)
    a.spines["right"].set_visible(False)
    a.grid(True, linestyle="--", alpha=0.45, color=config.PALETTE["grid"])

sc_colors = {"Conservative": config.PALETTE["blue"], "Base Case": config.PALETTE["teal"], "Optimistic": config.PALETTE["coral"]}
for sc_name, rows_sc in curves_by_scenario.items():
    ks = [r["k_pct"] for r in rows_sc]
    nets = [r["net_impact_mu"] / 1000.0 for r in rows_sc]
    ax1.plot(ks, nets, marker="o", lw=2.4, color=sc_colors[sc_name], label=sc_name)
ax1.axhline(0, color=config.PALETTE["navy"], lw=1.2, linestyle=":")
ax1.axvline(10, color=config.PALETTE["amber"], lw=2.0, linestyle="--", label="Recommended Pilot Cutoff (k=10%)")
ax1.set_title("A. Re-Based Annual Net Impact Across Cutoff k%", fontsize=10.8, fontweight="bold", color=config.PALETTE["navy"])
ax1.set_xlabel("Targeted Customer Share k% (of 100,000 Base)", fontsize=10.5, fontweight="bold", color=config.PALETTE["navy"])
ax1.set_ylabel("Estimated Net Impact (Thousands of MU)", fontsize=10.5, fontweight="bold", color=config.PALETTE["navy"])
ax1.legend(fontsize=8.5, loc="upper left")

# Right panel: Tornado chart around Base Case at k=10%
t_plot = tornado_df.iloc[::-1]
y_t = np.arange(len(t_plot))
low_deltas = (t_plot["low_net_mu"] - base_net) / 1000.0
high_deltas = (t_plot["high_net_mu"] - base_net) / 1000.0
ax2.barh(y_t, low_deltas, left=base_net / 1000.0, color=config.PALETTE["coral"], alpha=0.85, height=0.58, label="Downside Case")
ax2.barh(y_t, high_deltas, left=base_net / 1000.0, color=config.PALETTE["teal"], alpha=0.85, height=0.58, label="Upside Case")
ax2.axvline(base_net / 1000.0, color=config.PALETTE["navy"], lw=1.8, label=f"Base Case (k=10%): {base_net/1000:.0f}k MU")
ax2.axvline(0, color=config.PALETTE["slate"], lw=1.2, linestyle=":")
ax2.set_yticks(y_t)
ax2.set_yticklabels(t_plot["parameter"], fontsize=9.0, fontweight="bold", color=config.PALETTE["navy"])
ax2.set_title("B. Sensitivity Tornado (Base Case k=10%, '000 MU)", fontsize=10.8, fontweight="bold", color=config.PALETTE["navy"])
ax2.set_xlabel("Estimated Net Financial Impact (Thousands of MU)", fontsize=10.5, fontweight="bold", color=config.PALETTE["navy"])
ax2.legend(fontsize=8.5, loc="lower right")

plt.tight_layout()
fig.savefig(config.FIGURES_DIR / "impact_scenarios_tornado.png", dpi=220)
fig.savefig(config.FIGURES_DIR / "impact_scenarios_tornado.svg")
plt.close(fig)

# ---------------------------------------------------------
# 7. Save all Modeling, Evaluation, and Impact Results to outputs/results.json
# ---------------------------------------------------------
with open(config.RESULTS_JSON) as f:
    results = json.load(f)

results["models"] = exp_rows
results["final_model"] = {
    "id": best_id,
    "name": exp_df.loc[exp_df["id"] == best_id, "name"].values[0],
    "n_features": int(exp_df.loc[exp_df["id"] == best_id, "n_features"].values[0]),
    "cv_auc_mean": float(exp_df.loc[exp_df["id"] == best_id, "cv_auc_mean"].values[0]),
    "cv_auc_std": float(exp_df.loc[exp_df["id"] == best_id, "cv_auc_std"].values[0]),
    "cv_acc_mean": float(exp_df.loc[exp_df["id"] == best_id, "cv_acc_mean"].values[0]),
    "test_auc": float(exp_df.loc[exp_df["id"] == best_id, "test_auc"].values[0]),
    "test_acc": float(exp_df.loc[exp_df["id"] == best_id, "test_acc"].values[0]),
    "train_auc": float(exp_df.loc[exp_df["id"] == best_id, "train_auc"].values[0]),
    "train_acc": float(exp_df.loc[exp_df["id"] == best_id, "train_acc"].values[0]),
    "test_precision": float(exp_df.loc[exp_df["id"] == best_id, "test_precision"].values[0]),
    "test_recall": float(exp_df.loc[exp_df["id"] == best_id, "test_recall"].values[0]),
    "test_f1": float(exp_df.loc[exp_df["id"] == best_id, "test_f1"].values[0]),
    "confusion_matrix": {"tn": tn_f, "fp": fp_f, "fn": fn_f, "tp": tp_f},
    "brier_score": round(brier, 4),
    "calibration_bins": calib_rows,
    "bottom10_test_churn": round(bot10_churn, 4),
    "fairness_comparison": fairness_comparison,
    "ablation": ablation_res,
}
results["topk"] = topk_rows
results["importance"] = {
    "gain_top15": gain_list[:15],
    "permutation_top15": perm_list[:15],
    "pdp_eqpdays": pdp_eqp,
    "pdp_months": pdp_months,
}
results["impact"] = {
    "customer_base_n": 100000,
    "arpu_mean_mu": arpu_mean,
    "arpu_median_mu": arpu_median,
    "scenarios_at_k10": scenario_summary_at_k10,
    "unadjusted_sample_at_k10": unadjusted_k10,
    "optimal_k_by_scenario": optimal_k_by_scenario,
    "curves_by_scenario": curves_by_scenario,
    "sensitivity_tornado": tornado_df.to_dict(orient="records"),
    "lane2_pilot": lane2_pilot,
}

with open(config.RESULTS_JSON, "w") as f:
    json.dump(results, f, indent=2)

print("Completed Phases 5-8 in", round(time.time() - t0, 2), "s")
