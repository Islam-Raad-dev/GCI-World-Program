"""Phase 2: Exploratory Data Analysis (core) & Robustness checks on 70% training split."""
import json
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config

t0 = time.time()
rng = np.random.default_rng(config.SEED)

client = pd.read_csv(config.CLIENT_CSV)
record = pd.read_csv(config.RECORD_CSV)
df = record.merge(client, on="Customer_ID", how="inner")

# Split first with SEED=42 (70/30 stratified) — all threshold discovery & robustness on train_df
train_df, test_df = train_test_split(
    df, test_size=0.3, random_state=config.SEED, stratify=df["churn"]
)
train_df = train_df.copy()
print(f"Train split: {train_df.shape}, Test split: {test_df.shape}")

# Helper for Wilson / normal 95% CI on proportion
def prop_ci(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan, np.nan)
    p = k / n
    se = np.sqrt(p * (1 - p) / n)
    return float(p), float(max(0.0, p - z * se)), float(min(1.0, p + z * se))

# ---------------------------------------------------------
# T2.1 Device age (eqpdays) vs churn (bins <= 25 days)
# ---------------------------------------------------------
# Create 25-day bins from 0 to 900, plus <0 and >900
eqp_bins = [-10, -0.001] + list(range(25, 825, 25)) + [10000]
eqp_labels = ["<0"] + [f"{b+1}-{b+25}" if b > 0 else "0-25" for b in range(0, 800, 25)] + ["801+"]
train_df["eqp_bin25"] = pd.cut(train_df["eqpdays"], bins=eqp_bins, labels=eqp_labels)
df["eqp_bin25"] = pd.cut(df["eqpdays"], bins=eqp_bins, labels=eqp_labels)

eqp_curve_train = []
for lbl in eqp_labels:
    sub = train_df[train_df["eqp_bin25"] == lbl]
    sub_full = df[df["eqp_bin25"] == lbl]
    p, lo, hi = prop_ci(sub["churn"].sum(), len(sub))
    p_full, _, _ = prop_ci(sub_full["churn"].sum(), len(sub_full))
    mid = -2.5 if lbl == "<0" else (850.0 if lbl == "801+" else float(lbl.split("-")[0]) + 12.0)
    eqp_curve_train.append({
        "bin": lbl,
        "mid_day": mid,
        "train_n": int(len(sub)),
        "train_churn": round(p, 4),
        "train_ci_lo": round(lo, 4),
        "train_ci_hi": round(hi, 4),
        "full_n": int(len(sub_full)),
        "full_churn": round(p_full, 4),
    })
eqp_curve_df = pd.DataFrame(eqp_curve_train)
eqp_curve_df.to_csv(config.TABLES_DIR / "eqpdays_bins25.csv", index=False)

# Plot figures/eqpdays_churn.png (25-day bins from 0 to 800 days)
plot_eqp = eqp_curve_df[(eqp_curve_df["mid_day"] >= 0) & (eqp_curve_df["mid_day"] <= 800)].copy()
fig, ax = plt.subplots(figsize=(10.5, 5.8), dpi=220)
fig.patch.set_facecolor(config.PALETTE["white"])
ax.set_facecolor(config.PALETTE["white"])

pre300 = plot_eqp[plot_eqp["mid_day"] <= 300]
post300 = plot_eqp[plot_eqp["mid_day"] > 300]

ax.fill_between(
    plot_eqp["mid_day"], plot_eqp["train_ci_lo"] * 100, plot_eqp["train_ci_hi"] * 100,
    color=config.PALETTE["slate"], alpha=0.16, label="95% Confidence Interval (Train 70%)"
)
ax.plot(
    pre300["mid_day"], pre300["train_churn"] * 100,
    marker="o", linewidth=2.6, color=config.PALETTE["blue"], label="Device Age ≤ 300 Days (~38% Churn)"
)
ax.plot(
    post300["mid_day"], post300["train_churn"] * 100,
    marker="o", linewidth=2.6, color=config.PALETTE["coral"], label="Device Age > 300 Days (Peaks ~64% at 326–350d)"
)
ax.axvline(300, color=config.PALETTE["amber"], linestyle="--", linewidth=2.2, label="~300-Day Threshold")
ax.axhline(train_df["churn"].mean() * 100, color=config.PALETTE["slate"], linestyle=":", linewidth=1.5, label=f"Sample Mean ({train_df['churn'].mean()*100:.1f}%)")

# Annotate jump
c_276_300 = float(plot_eqp.loc[plot_eqp["bin"] == "276-300", "train_churn"].values[0]) * 100
c_301_325 = float(plot_eqp.loc[plot_eqp["bin"] == "301-325", "train_churn"].values[0]) * 100
c_326_350 = float(plot_eqp.loc[plot_eqp["bin"] == "326-350", "train_churn"].values[0]) * 100
ax.annotate(
    f"Sharp +19.7 pp jump across 300d\n(276–300d: {c_276_300:.1f}% → 301–325d: {c_301_325:.1f}%\nPeak 326–350d: {c_326_350:.1f}%)",
    xy=(313, c_301_325), xytext=(375, 65.5),
    arrowprops=dict(arrowstyle="->", color=config.PALETTE["navy"], lw=1.6),
    fontsize=10.5, fontweight="bold", color=config.PALETTE["navy"],
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFF8EB", edgecolor=config.PALETTE["amber"], lw=1.2)
)

ax.set_title("Churn Rate Jumps Sharply Once Current Handset Age Crosses ~300 Days", fontsize=14, fontweight="bold", color=config.PALETTE["navy"], pad=12)
ax.set_xlabel("Current Equipment Age (`eqpdays`, 25-day bins on 70,000 Training Customers)", fontsize=11.5, fontweight="bold", color=config.PALETTE["navy"])
ax.set_ylabel("Observed Churn Rate (%)", fontsize=11.5, fontweight="bold", color=config.PALETTE["navy"])
ax.set_ylim(28, 72)
ax.set_xlim(0, 800)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, linestyle="--", alpha=0.45, color=config.PALETTE["grid"])
ax.legend(loc="lower right", frameon=True, facecolor=config.PALETTE["white"], fontsize=9.5)
plt.tight_layout()
fig.savefig(config.FIGURES_DIR / "eqpdays_churn.png", dpi=220)
fig.savefig(config.FIGURES_DIR / "eqpdays_churn.svg")
plt.close(fig)

# ---------------------------------------------------------
# T2.2 Robustness of the ~300-day jump
# ---------------------------------------------------------
w_left_train = train_df[(train_df["eqpdays"] >= 260) & (train_df["eqpdays"] <= 300)]["churn"].values
w_right_train = train_df[(train_df["eqpdays"] >= 301) & (train_df["eqpdays"] <= 340)]["churn"].values

obs_left = float(w_left_train.mean())
obs_right = float(w_right_train.mean())
obs_diff = obs_right - obs_left

# Bootstrap 95% CI (2,000 resamples)
boot_diffs = []
for _ in range(2000):
    b_l = rng.choice(w_left_train, size=len(w_left_train), replace=True).mean()
    b_r = rng.choice(w_right_train, size=len(w_right_train), replace=True).mean()
    boot_diffs.append(b_r - b_l)
boot_ci_lo, boot_ci_hi = float(np.percentile(boot_diffs, 2.5)), float(np.percentile(boot_diffs, 97.5))

# Full dataset check
w_left_full = df[(df["eqpdays"] >= 260) & (df["eqpdays"] <= 300)]["churn"].values
w_right_full = df[(df["eqpdays"] >= 301) & (df["eqpdays"] <= 340)]["churn"].values
full_diff = float(w_right_full.mean() - w_left_full.mean())

# Local linear RD fit on [200, 300] vs [301, 400] in train_df
rd_left = train_df[(train_df["eqpdays"] >= 200) & (train_df["eqpdays"] <= 300)]
rd_right = train_df[(train_df["eqpdays"] >= 301) & (train_df["eqpdays"] <= 400)]
coef_l = np.polyfit(rd_left["eqpdays"], rd_left["churn"], 1)
coef_r = np.polyfit(rd_right["eqpdays"], rd_right["churn"], 1)
pred_at_300_left = float(np.polyval(coef_l, 300))
pred_at_301_right = float(np.polyval(coef_r, 301))
rd_jump_at_cutoff = pred_at_301_right - pred_at_300_left

# Subgroup checks (months >= 10, months >= 13, refurb_new == 'N', top areas, top credit classes)
subgroups = [
    ("All Train Customers", train_df),
    ("Tenure >= 10 Months Only", train_df[train_df["months"] >= 10]),
    ("Tenure >= 13 Months Only (Post-Cliff)", train_df[train_df["months"] >= 13]),
    ("Single-Handset Customers (phones == 1)", train_df[train_df["phones"] == 1]),
    ("Multi-Handset Customers (phones >= 2)", train_df[train_df["phones"] >= 2]),
    ("New Handsets Only (refurb_new == 'N')", train_df[train_df["refurb_new"] == "N"]),
    ("Refurbished Handsets (refurb_new == 'R')", train_df[train_df["refurb_new"] == "R"]),
    ("Credit Class AA", train_df[train_df["crclscod"] == "AA"]),
    ("Credit Class A", train_df[train_df["crclscod"] == "A"]),
    ("Area: NEW YORK CITY AREA", train_df[train_df["area"] == "NEW YORK CITY AREA"]),
    ("Area: CALIFORNIA NORTH AREA", train_df[train_df["area"] == "CALIFORNIA NORTH AREA"]),
]
rob_rows = []
for name, sdf in subgroups:
    sl = sdf[(sdf["eqpdays"] >= 260) & (sdf["eqpdays"] <= 300)]["churn"]
    sr = sdf[(sdf["eqpdays"] >= 301) & (sdf["eqpdays"] <= 340)]["churn"]
    if len(sl) >= 20 and len(sr) >= 20:
        rob_rows.append({
            "subgroup": name,
            "n_260_300": int(len(sl)),
            "churn_260_300": round(float(sl.mean()), 4),
            "n_301_340": int(len(sr)),
            "churn_301_340": round(float(sr.mean()), 4),
            "jump_pp": round(float(sr.mean() - sl.mean()) * 100, 2),
        })
rob_df = pd.DataFrame(rob_rows)

# Covariate balance check across 300 days (260-300 vs 301-340, and also within tenure >= 13)
cov_cols = ["months", "rev_Mean", "mou_Mean", "totmrc_Mean", "hnd_price", "phones", "uniqsubs"]
cov_balance = []
sub_l_all = train_df[(train_df["eqpdays"] >= 260) & (train_df["eqpdays"] <= 300)]
sub_r_all = train_df[(train_df["eqpdays"] >= 301) & (train_df["eqpdays"] <= 340)]
sub_l_m13 = train_df[(train_df["months"] >= 13) & (train_df["eqpdays"] >= 260) & (train_df["eqpdays"] <= 300)]
sub_r_m13 = train_df[(train_df["months"] >= 13) & (train_df["eqpdays"] >= 301) & (train_df["eqpdays"] <= 340)]

for c in cov_cols:
    m_l = float(sub_l_all[c].mean())
    m_r = float(sub_r_all[c].mean())
    sd_pool = float(np.sqrt((sub_l_all[c].var() + sub_r_all[c].var()) / 2))
    smd_all = (m_r - m_l) / sd_pool if sd_pool > 0 else 0.0

    m_l13 = float(sub_l_m13[c].mean())
    m_r13 = float(sub_r_m13[c].mean())
    sd_pool13 = float(np.sqrt((sub_l_m13[c].var() + sub_r_m13[c].var()) / 2))
    smd_13 = (m_r13 - m_l13) / sd_pool13 if sd_pool13 > 0 else 0.0

    cov_balance.append({
        "covariate": c,
        "mean_260_300_all": round(m_l, 3),
        "mean_301_340_all": round(m_r, 3),
        "smd_all": round(smd_all, 3),
        "mean_260_300_tenure13plus": round(m_l13, 3),
        "mean_301_340_tenure13plus": round(m_r13, 3),
        "smd_tenure13plus": round(smd_13, 3),
    })
cov_df = pd.DataFrame(cov_balance)
rob_df.to_csv(config.TABLES_DIR / "threshold_robustness.csv", index=False)
cov_df.to_csv(config.TABLES_DIR / "covariate_balance_300d.csv", index=False)

print("Robustness across subgroups:\n", rob_df)
print("Covariate balance at 300d:\n", cov_df)

# Plot figures/eqpdays_robustness.png (2-panel: Left = RD local linear fit, Right = subgroup jump_pp)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), dpi=220)
fig.patch.set_facecolor(config.PALETTE["white"])
for a in (ax1, ax2):
    a.set_facecolor(config.PALETTE["white"])
    a.spines["top"].set_visible(False)
    a.spines["right"].set_visible(False)
    a.grid(True, linestyle="--", alpha=0.45, color=config.PALETTE["grid"])

# Left panel: 10-day bins in [200, 400] + local linear RD lines
train_200_400 = train_df[(train_df["eqpdays"] >= 200) & (train_df["eqpdays"] <= 400)].copy()
train_200_400["bin10"] = ((train_200_400["eqpdays"] - 201) // 10) * 10 + 205
b10 = train_200_400.groupby("bin10")["churn"].agg(["count", "mean"]).reset_index()
b10 = b10[b10["count"] >= 50]
ax1.scatter(b10["bin10"], b10["mean"] * 100, color=config.PALETTE["navy"], s=45, zorder=3, label="10-Day Bin Churn (%)")
x_l = np.linspace(200, 300, 50)
x_r = np.linspace(301, 400, 50)
ax1.plot(x_l, np.polyval(coef_l, x_l) * 100, color=config.PALETTE["blue"], lw=2.5, label="Local Linear Fit (200–300d)")
ax1.plot(x_r, np.polyval(coef_r, x_r) * 100, color=config.PALETTE["coral"], lw=2.5, label="Local Linear Fit (301–400d)")
ax1.axvline(300, color=config.PALETTE["amber"], linestyle="--", lw=2)
ax1.set_title("A. Local Linear Discontinuity around 300 Days", fontsize=12, fontweight="bold", color=config.PALETTE["navy"])
ax1.set_xlabel("Equipment Age (`eqpdays`)", fontsize=11, color=config.PALETTE["navy"])
ax1.set_ylabel("Churn Rate (%)", fontsize=11, color=config.PALETTE["navy"])
ax1.legend(fontsize=8.5, loc="upper left")

# Right panel: Subgroup jumps (301-340 vs 260-300)
rob_plot = rob_df.iloc[::-1]
ax2.barh(rob_plot["subgroup"], rob_plot["jump_pp"], color=config.PALETTE["teal"], height=0.65)
ax2.axvline(0, color=config.PALETTE["navy"], lw=1)
ax2.set_title("B. Churn Jump (301–340d vs 260–300d) Across Subgroups", fontsize=12, fontweight="bold", color=config.PALETTE["navy"])
ax2.set_xlabel("Churn Rate Jump (Percentage Points)", fontsize=11, color=config.PALETTE["navy"])
ax2.set_xlim(-5, 32)
for i, (_, r) in enumerate(rob_plot.iterrows()):
    ax2.text(max(0.5, r["jump_pp"] + 0.5), i, f"{r['jump_pp']:+.1f} pp", va="center", fontsize=9, fontweight="bold", color=config.PALETTE["navy"])

plt.tight_layout()
fig.savefig(config.FIGURES_DIR / "eqpdays_robustness.png", dpi=220)
fig.savefig(config.FIGURES_DIR / "eqpdays_robustness.svg")
plt.close(fig)

# ---------------------------------------------------------
# T2.3 Tenure (months) vs churn
# ---------------------------------------------------------
tenure_rows = []
for m in range(6, 62):
    sub_t = train_df[train_df["months"] == m]
    sub_f = df[df["months"] == m]
    if len(sub_t) > 0:
        p, lo, hi = prop_ci(sub_t["churn"].sum(), len(sub_t))
        pf, _, _ = prop_ci(sub_f["churn"].sum(), len(sub_f))
        tenure_rows.append({
            "months": m,
            "train_n": int(len(sub_t)),
            "train_churn": round(p, 4),
            "train_ci_lo": round(lo, 4),
            "train_ci_hi": round(hi, 4),
            "full_n": int(len(sub_f)),
            "full_churn": round(pf, 4),
        })
tenure_df = pd.DataFrame(tenure_rows)
tenure_df.to_csv(config.TABLES_DIR / "tenure_months_churn.csv", index=False)

fig, ax = plt.subplots(figsize=(10.5, 5.5), dpi=220)
fig.patch.set_facecolor(config.PALETTE["white"])
ax.set_facecolor(config.PALETTE["white"])
t_plot = tenure_df[tenure_df["months"] <= 48]
ax.fill_between(t_plot["months"], t_plot["train_ci_lo"] * 100, t_plot["train_ci_hi"] * 100, color=config.PALETTE["teal"], alpha=0.18)
ax.plot(t_plot["months"], t_plot["train_churn"] * 100, marker="o", color=config.PALETTE["navy"], lw=2.4, label="Monthly Churn Rate (Train 70%)")
ax.axvspan(10, 12, color=config.PALETTE["coral"], alpha=0.16, label="Months 10–12 First-Year Renewal Cliff")
ax.axhline(train_df["churn"].mean() * 100, color=config.PALETTE["slate"], linestyle=":", lw=1.5, label="Sample Mean (49.6%)")

m9_c = float(tenure_df.loc[tenure_df["months"] == 9, "train_churn"].values[0]) * 100
m11_c = float(tenure_df.loc[tenure_df["months"] == 11, "train_churn"].values[0]) * 100
m12_c = float(tenure_df.loc[tenure_df["months"] == 12, "train_churn"].values[0]) * 100
ax.annotate(
    f"Month 9 Dip: {m9_c:.1f}%\n→ Month 11 Peak: {m11_c:.1f}%\n(Month 12: {m12_c:.1f}%)",
    xy=(11, m11_c), xytext=(15.5, 62),
    arrowprops=dict(arrowstyle="->", color=config.PALETTE["coral"], lw=1.8),
    fontsize=10.5, fontweight="bold", color=config.PALETTE["navy"],
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFF5F2", edgecolor=config.PALETTE["coral"], lw=1.2)
)
ax.set_title("Customer Churn Spikes Sharply at Months 10–12 (First-Year Contract Cliff)", fontsize=14, fontweight="bold", color=config.PALETTE["navy"], pad=12)
ax.set_xlabel("Customer Tenure in Service (`months`)", fontsize=11.5, fontweight="bold", color=config.PALETTE["navy"])
ax.set_ylabel("Observed Churn Rate (%)", fontsize=11.5, fontweight="bold", color=config.PALETTE["navy"])
ax.set_xlim(5.5, 48.5)
ax.set_ylim(20, 72)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, linestyle="--", alpha=0.45, color=config.PALETTE["grid"])
ax.legend(loc="lower right", frameon=True, facecolor=config.PALETTE["white"], fontsize=9.5)
plt.tight_layout()
fig.savefig(config.FIGURES_DIR / "months_churn.png", dpi=220)
fig.savefig(config.FIGURES_DIR / "months_churn.svg")
plt.close(fig)

# ---------------------------------------------------------
# T2.4 Entanglement: 2D Heatmap of Tenure Bucket x Device Age Bucket
# ---------------------------------------------------------
max_eqp_tenure_le_9 = float(df.loc[df["months"] <= 9, "eqpdays"].max())
n_tenure_le_9_eqp_gt_300 = int(((df["months"] <= 9) & (df["eqpdays"] > 300)).sum())
print(f"Max eqpdays for months <= 9: {max_eqp_tenure_le_9}, count > 300d: {n_tenure_le_9_eqp_gt_300}")

t_bins = [5, 9, 12, 18, 24, 100]
t_labels = ["6–9m (Early)", "10–12m (Cliff)", "13–18m", "19–24m", "25m+ (Mature)"]
d_bins = [-10, 200, 300, 340, 500, 10000]
d_labels = ["≤200d", "201–300d", "301–340d (Peak)", "341–500d", "501d+"]

train_df["t_bucket"] = pd.cut(train_df["months"], bins=t_bins, labels=t_labels)
train_df["d_bucket"] = pd.cut(train_df["eqpdays"], bins=d_bins, labels=d_labels)

hm_churn = train_df.pivot_table(index="t_bucket", columns="d_bucket", values="churn", aggfunc="mean", observed=False)
hm_count = train_df.pivot_table(index="t_bucket", columns="d_bucket", values="churn", aggfunc="count", observed=False)

hm_records = []
for tb in t_labels:
    for db in d_labels:
        cnt = int(hm_count.loc[tb, db]) if pd.notna(hm_count.loc[tb, db]) else 0
        ch = float(hm_churn.loc[tb, db]) if (cnt >= 25 and pd.notna(hm_churn.loc[tb, db])) else None
        hm_records.append({
            "tenure_bucket": tb,
            "device_bucket": db,
            "train_n": cnt,
            "train_churn": round(ch, 4) if ch is not None else None,
        })
pd.DataFrame(hm_records).to_csv(config.TABLES_DIR / "tenure_device_entanglement.csv", index=False)

# Plot figures/tenure_device_heatmap.png
fig, ax = plt.subplots(figsize=(9.8, 5.6), dpi=220)
fig.patch.set_facecolor(config.PALETTE["white"])
ax.set_facecolor(config.PALETTE["white"])

hm_display = hm_churn.copy() * 100
hm_display[hm_count < 25] = np.nan

annot_matrix = np.empty(hm_display.shape, dtype=object)
for i, tb in enumerate(t_labels):
    for j, db in enumerate(d_labels):
        cnt = int(hm_count.iloc[i, j])
        val = hm_display.iloc[i, j]
        if cnt < 25 or pd.isna(val):
            annot_matrix[i, j] = f"N/A\n(n={cnt:,})"
        else:
            annot_matrix[i, j] = f"{val:.1f}%\n(n={cnt:,})"

sns.heatmap(
    hm_display, annot=annot_matrix, fmt="", cmap="YlOrRd", vmin=28, vmax=66,
    cbar_kws={"label": "Churn Rate (%)"}, ax=ax, linewidths=1.5, linecolor="white",
    annot_kws={"size": 9.5, "weight": "bold"}
)
ax.set_title("Entanglement Check: Device Age vs. Tenure (70,000 Training Customers)", fontsize=13.5, fontweight="bold", color=config.PALETTE["navy"], pad=12)
ax.set_xlabel("Current Handset Age Bucket (`eqpdays`)", fontsize=11.5, fontweight="bold", color=config.PALETTE["navy"])
ax.set_ylabel("Customer Tenure Bucket (`months`)", fontsize=11.5, fontweight="bold", color=config.PALETTE["navy"])
plt.tight_layout()
fig.savefig(config.FIGURES_DIR / "tenure_device_heatmap.png", dpi=220)
fig.savefig(config.FIGURES_DIR / "tenure_device_heatmap.svg")
plt.close(fig)

# ---------------------------------------------------------
# T2.5 Usage collapse segments
# ---------------------------------------------------------
total_rev_train = float(train_df["rev_Mean"].dropna().sum())
total_rev_full = float(df["rev_Mean"].dropna().sum())
usage_defs = [
    ("Zero Usage (mou_Mean == 0)", df["mou_Mean"] == 0, train_df["mou_Mean"] == 0),
    ("Missing Usage (mou_Mean is NaN)", df["mou_Mean"].isna(), train_df["mou_Mean"].isna()),
    ("Missing Usage Change (change_mou is NaN)", df["change_mou"].isna(), train_df["change_mou"].isna()),
    ("Near-Zero Usage (0 < mou_Mean <= 10)", (df["mou_Mean"] > 0) & (df["mou_Mean"] <= 10), (train_df["mou_Mean"] > 0) & (train_df["mou_Mean"] <= 10)),
    ("Very Low Usage (mou_Mean <= 10 incl. 0)", df["mou_Mean"] <= 10, train_df["mou_Mean"] <= 10),
    ("Low Usage (mou_Mean <= 30)", df["mou_Mean"] <= 30, train_df["mou_Mean"] <= 30),
    ("Active Baseline (mou_Mean > 30)", df["mou_Mean"] > 30, train_df["mou_Mean"] > 30),
]
usage_rows = []
for label, mask_f, mask_t in usage_defs:
    sf = df[mask_f]
    st = train_df[mask_t]
    rev_share_f = float(sf["rev_Mean"].dropna().sum() / total_rev_full * 100) if len(sf) > 0 else 0.0
    usage_rows.append({
        "segment": label,
        "full_n": int(len(sf)),
        "full_pct_customers": round(len(sf) / len(df) * 100, 2),
        "full_churn_rate": round(float(sf["churn"].mean()), 4),
        "train_n": int(len(st)),
        "train_churn_rate": round(float(st["churn"].mean()), 4),
        "rev_mean_mu": round(float(sf["rev_Mean"].mean()), 2) if sf["rev_Mean"].notna().any() else None,
        "rev_median_mu": round(float(sf["rev_Mean"].median()), 2) if sf["rev_Mean"].notna().any() else None,
        "pct_of_total_revenue": round(rev_share_f, 2),
        "totrev_mean_mu": round(float(sf["totrev"].mean()), 2),
    })
usage_df = pd.DataFrame(usage_rows)
usage_df.to_csv(config.TABLES_DIR / "usage_collapse_segments.csv", index=False)
print("Usage collapse segments:\n", usage_df)

# Plot figures/usage_segments.png (Combined Slide 6 visual: Left = Tenure Curve + Usage Collapse, or standalone Usage Collapse)
fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=220)
fig.patch.set_facecolor(config.PALETTE["white"])
ax.set_facecolor(config.PALETTE["white"])
u_plot = usage_df.iloc[[0, 2, 4, 5, 6]].iloc[::-1]
bar_colors = [config.PALETTE["blue"] if r["full_churn_rate"] < 0.55 else config.PALETTE["coral"] for _, r in u_plot.iterrows()]
bars = ax.barh(u_plot["segment"], u_plot["full_churn_rate"] * 100, color=bar_colors, height=0.62)
ax.axvline(df["churn"].mean() * 100, color=config.PALETTE["slate"], linestyle=":", lw=1.5, label="Overall Churn (49.6%)")
for bar, (_, r) in zip(bars, u_plot.iterrows()):
    w = bar.get_width()
    rev_txt = f"ARPU: {r['rev_mean_mu']:.1f} MU ({r['pct_of_total_revenue']:.1f}% rev)" if r["rev_mean_mu"] is not None else "ARPU: N/A"
    ax.text(w + 0.8, bar.get_y() + bar.get_height() / 2, f"{w:.1f}% churn (n={r['full_n']:,} | {rev_txt})", va="center", fontsize=9.5, fontweight="bold", color=config.PALETTE["navy"])
ax.set_xlim(0, 148)
ax.set_title("Usage Collapse Signals Silent Defection, Yet Zero-MOU Has Low ARPU", fontsize=12.0, fontweight="bold", color=config.PALETTE["navy"], pad=12)
ax.set_xlabel("Observed Churn Rate (%)", fontsize=11, fontweight="bold", color=config.PALETTE["navy"])
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(axis="x", linestyle="--", alpha=0.45, color=config.PALETTE["grid"])
plt.tight_layout()
fig.savefig(config.FIGURES_DIR / "usage_segments.png", dpi=220)
fig.savefig(config.FIGURES_DIR / "usage_segments.svg")
plt.close(fig)

# ---------------------------------------------------------
# T2.6 Revenue and "value"
# ---------------------------------------------------------
rev_stayed = df.loc[df["churn"] == 0, "rev_Mean"].dropna()
rev_churned = df.loc[df["churn"] == 1, "rev_Mean"].dropna()
rev_stats = {
    "overall_mean": round(float(df["rev_Mean"].mean()), 2),
    "overall_median": round(float(df["rev_Mean"].median()), 2),
    "overall_p25": round(float(df["rev_Mean"].quantile(0.25)), 2),
    "overall_p75": round(float(df["rev_Mean"].quantile(0.75)), 2),
    "stayed_mean": round(float(rev_stayed.mean()), 2),
    "stayed_median": round(float(rev_stayed.median()), 2),
    "churned_mean": round(float(rev_churned.mean()), 2),
    "churned_median": round(float(rev_churned.median()), 2),
    "corr_with_churn": round(float(df["rev_Mean"].corr(df["churn"])), 4),
}
print("Revenue stats:", rev_stats)

# ---------------------------------------------------------
# T2.7 Customer care calls vs churn
# ---------------------------------------------------------
cc_bins = [-1, 0, 1, 3, 1000]
cc_labels = ["0 Calls", "0–1 Calls/mo", "1–3 Calls/mo", ">3 Calls/mo"]
df["cc_bucket"] = pd.cut(df["custcare_Mean"], bins=cc_bins, labels=cc_labels)
cc_summary = []
for lbl in cc_labels:
    sub = df[df["cc_bucket"] == lbl]
    cc_summary.append({
        "bucket": lbl,
        "n": int(len(sub)),
        "churn_rate": round(float(sub["churn"].mean()), 4),
        "mou_mean": round(float(sub["mou_Mean"].mean()), 1),
        "months_mean": round(float(sub["months"].mean()), 1),
    })
pd.DataFrame(cc_summary).to_csv(config.TABLES_DIR / "custcare_churn.csv", index=False)

# ---------------------------------------------------------
# T2.8 Call quality & overage/roaming vs churn
# ---------------------------------------------------------
df["drop_blk_rate"] = df["drop_blk_Mean"] / (df["attempt_Mean"] + 1.0)
df["overage_share"] = df["ovrrev_Mean"] / (df["rev_Mean"].clip(lower=0) + 1.0)
q_quartiles = pd.qcut(df["drop_blk_rate"].rank(method="first"), 4, labels=["Q1 (Lowest)", "Q2", "Q3", "Q4 (Highest)"])
qual_summary = df.groupby(q_quartiles, observed=False)["churn"].agg(["count", "mean"]).reset_index()
qual_summary.to_csv(config.TABLES_DIR / "quality_churn.csv", index=False)

ovr_zero = df[df["ovrrev_Mean"] == 0]["churn"].mean()
ovr_high = df[df["ovrrev_Mean"] > 20]["churn"].mean()

# ---------------------------------------------------------
# T2.9 Demographics & ethnic fairness audit
# ---------------------------------------------------------
ethnic_tbl = df.groupby(df["ethnic"].fillna("MISSING"))["churn"].agg(["count", "mean"]).reset_index()
ethnic_tbl.columns = ["ethnic_code", "count", "churn_rate"]
ethnic_tbl = ethnic_tbl.sort_values("churn_rate", ascending=False)
ethnic_tbl.to_csv(config.TABLES_DIR / "ethnic_fairness_audit.csv", index=False)

income_tbl = df.groupby(df["income"].fillna(-1))["churn"].agg(["count", "mean"]).reset_index()
income_tbl.to_csv(config.TABLES_DIR / "income_churn.csv", index=False)

# Update outputs/results.json with `eda` section
with open(config.RESULTS_JSON) as f:
    results = json.load(f)

results["eda"] = {
    "churn_rate": results["data"]["churn_rate"],
    "device_age_bins": eqp_curve_train,
    "jump_300d": {
        "train_churn_260_300": round(obs_left, 4),
        "train_churn_301_340": round(obs_right, 4),
        "train_diff_pp": round(obs_diff * 100, 2),
        "boot_ci95_lo_pp": round(boot_ci_lo * 100, 2),
        "boot_ci95_hi_pp": round(boot_ci_hi * 100, 2),
        "full_churn_260_300": round(float(w_left_full.mean()), 4),
        "full_churn_301_340": round(float(w_right_full.mean()), 4),
        "full_diff_pp": round(full_diff * 100, 2),
        "rd_jump_at_300_pp": round(rd_jump_at_cutoff * 100, 2),
        "peak_bin_326_350_train_churn": round(c_326_350 / 100, 4),
        "subgroups": rob_rows,
        "covariate_balance": cov_balance,
        "verdict": "Real behavioral/contractual lifecycle threshold entangled with initial handset count (`phones`) and early tenure (`months`); survives within mature single-handset and multi-handset subgroups (+13 to +21 pp), warranting a controlled A/B handset-refresh pilot rather than unguarded causal claims.",
    },
    "tenure_curve": tenure_rows,
    "tenure_highlights": {
        "month_9_train_churn": round(m9_c / 100, 4),
        "month_11_train_churn": round(m11_c / 100, 4),
        "month_12_train_churn": round(m12_c / 100, 4),
        "month_9_full_churn": round(float(tenure_df.loc[tenure_df["months"] == 9, "full_churn"].values[0]), 4),
        "month_11_full_churn": round(float(tenure_df.loc[tenure_df["months"] == 11, "full_churn"].values[0]), 4),
        "month_12_full_churn": round(float(tenure_df.loc[tenure_df["months"] == 12, "full_churn"].values[0]), 4),
    },
    "entanglement": {
        "max_eqpdays_when_months_le_9": max_eqp_tenure_le_9,
        "n_months_le_9_and_eqpdays_gt_300": n_tenure_le_9_eqp_gt_300,
        "three_groups_full": {
            "months_le_9": {
                "n": int((df["months"] <= 9).sum()),
                "churn_rate": round(float(df.loc[df["months"] <= 9, "churn"].mean()), 4),
            },
            "months_ge_10_eqp_le_300": {
                "n": int(((df["months"] >= 10) & (df["eqpdays"] <= 300)).sum()),
                "churn_rate": round(float(df.loc[(df["months"] >= 10) & (df["eqpdays"] <= 300), "churn"].mean()), 4),
            },
            "months_ge_10_eqp_gt_300": {
                "n": int(((df["months"] >= 10) & (df["eqpdays"] > 300)).sum()),
                "churn_rate": round(float(df.loc[(df["months"] >= 10) & (df["eqpdays"] > 300), "churn"].mean()), 4),
            },
        },
        "heatmap_cells": hm_records,
    },
    "usage_collapse": usage_rows,
    "revenue_stats": rev_stats,
    "custcare_buckets": cc_summary,
    "overage_churn": {
        "zero_overage_churn": round(float(ovr_zero), 4),
        "ovrrev_gt_20_churn": round(float(ovr_high), 4),
    },
    "ethnic_extremes": {
        "code_O": {"n": int((df["ethnic"] == "O").sum()), "churn_rate": round(float(df.loc[df["ethnic"] == "O", "churn"].mean()), 4)},
        "code_Z": {"n": int((df["ethnic"] == "Z").sum()), "churn_rate": round(float(df.loc[df["ethnic"] == "Z", "churn"].mean()), 4)},
        "income_min_churn": round(float(income_tbl["mean"].min()), 4),
        "income_max_churn": round(float(income_tbl["mean"].max()), 4),
    },
}

with open(config.RESULTS_JSON, "w") as f:
    json.dump(results, f, indent=2)

print("Completed Phase 2 EDA & Robustness in", round(time.time() - t0, 2), "s")
