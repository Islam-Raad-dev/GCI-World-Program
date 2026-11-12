"""Feature engineering and leakage-safe preprocessing utilities for Company A Telecom PoC."""
import numpy as np
import pandas as pd

# 17 Interpretable, leakage-safe engineered features (PRD §8.3 & Task T5.2)
ENGINEERED_FEATURES = [
    "dev_age_gt_300",
    "dev_age_301_360_peak",
    "tenure_le_9",
    "tenure_10_12_cliff",
    "eqp_per_tenure_day",
    "mou_ratio_3m",
    "mou_ratio_6m",
    "rev_ratio_3m",
    "rev_ratio_6m",
    "drop_vce_rate",
    "blck_vce_rate",
    "unan_vce_rate",
    "completion_rate",
    "recurring_rev_share",
    "overage_rev_share",
    "custcare_per_call",
    "mou_zero_flag",
    "mou_le_10_flag",
    "missing_change_mou_flag",
    "demo_missing_count",
]

# 10 Near-duplicate columns (Spearman > 0.995) that can be optionally dropped
REDUNDANT_10_COLS = [
    "adjqty",
    "adjmou",
    "adjrev",
    "plcd_vce_Mean",
    "comp_vce_Mean",
    "comp_dat_Mean",
    "peak_dat_Mean",
    "opk_dat_Mean",
    "ovrmou_Mean",
    "ccrndmou_Mean",
]

# Sensitive demographic columns for fairness auditing (PRD §8.7)
SENSITIVE_ETHNIC = ["ethnic"]
SENSITIVE_PROXIES = ["ethnic", "income", "marital", "dwllsize", "ownrent", "HHstatin", "prizm_social_one", "kid0_2", "kid3_5", "kid6_10", "kid11_15", "kid16_17"]


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create 20 domain-grounded features without using target information or future data."""
    out = df.copy()

    # Clip negative eqpdays at 0 for ratios, and keep an explicit flag
    eqp_clean = out["eqpdays"].clip(lower=0)
    tenure_days = (out["months"].clip(lower=1) * 30.0)

    # 1. Lifecycle & threshold flags (derived from training-split EDA)
    out["dev_age_gt_300"] = (out["eqpdays"] > 300).astype(np.int8)
    out["dev_age_301_360_peak"] = ((out["eqpdays"] > 300) & (out["eqpdays"] <= 360)).astype(np.int8)
    out["tenure_le_9"] = (out["months"] <= 9).astype(np.int8)
    out["tenure_10_12_cliff"] = ((out["months"] >= 10) & (out["months"] <= 12)).astype(np.int8)
    out["eqp_per_tenure_day"] = eqp_clean / tenure_days

    # 2. Usage & revenue trajectory ratios (current vs 3m and 6m historical averages)
    out["mou_ratio_3m"] = out["mou_Mean"].clip(lower=0) / (out["avg3mou"].clip(lower=0) + 1.0)
    out["mou_ratio_6m"] = out["mou_Mean"].clip(lower=0) / (out["avg6mou"].clip(lower=0) + 1.0)
    out["rev_ratio_3m"] = out["rev_Mean"].clip(lower=0) / (out["avg3rev"].clip(lower=0) + 1.0)
    out["rev_ratio_6m"] = out["rev_Mean"].clip(lower=0) / (out["avg6rev"].clip(lower=0) + 1.0)

    # 3. Call quality & friction rates
    placed_vce = out["plcd_vce_Mean"].clip(lower=0) + 1.0
    attempted_all = out["attempt_Mean"].clip(lower=0) + 1.0
    out["drop_vce_rate"] = out["drop_vce_Mean"].clip(lower=0) / placed_vce
    out["blck_vce_rate"] = out["blck_vce_Mean"].clip(lower=0) / placed_vce
    out["unan_vce_rate"] = out["unan_vce_Mean"].clip(lower=0) / placed_vce
    out["completion_rate"] = out["complete_Mean"].clip(lower=0) / attempted_all

    # 4. Billing & revenue composition shares
    rev_denom = out["rev_Mean"].clip(lower=0) + 1.0
    out["recurring_rev_share"] = out["totmrc_Mean"].clip(lower=0) / rev_denom
    out["overage_rev_share"] = out["ovrrev_Mean"].clip(lower=0) / rev_denom

    # 5. Customer care intensity & usage collapse / missingness flags
    out["custcare_per_call"] = out["custcare_Mean"].clip(lower=0) / attempted_all
    out["mou_zero_flag"] = (out["mou_Mean"] == 0).astype(np.int8)
    out["mou_le_10_flag"] = (out["mou_Mean"] <= 10).astype(np.int8)
    out["missing_change_mou_flag"] = out["change_mou"].isna().astype(np.int8)

    demo_cols = [
        "numbcars", "dwllsize", "HHstatin", "ownrent", "dwlltype",
        "lor", "income", "adults", "infobase", "hnd_webcap", "prizm_social_one"
    ]
    present_demo_cols = [c for c in demo_cols if c in out.columns]
    out["demo_missing_count"] = out[present_demo_cols].isna().sum(axis=1).astype(np.int8)

    return out
