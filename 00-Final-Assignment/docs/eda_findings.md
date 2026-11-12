# Exploratory Data Analysis Findings — Company A Telecom Dataset

> **Methodology Guardrail (PRD §8.2 & Task Phase 2):** All threshold discovery and robustness checks were performed on the **70% stratified training split ($N_{\text{train}} = 70{,}000$, `SEED = 42`)**, with full-dataset ($N = 100{,}000$) figures reported solely as descriptive verification.

---

## 1. Ten Core Empirical Findings (One-Sentence Takeaways + Evidence)

1. **Target Balance vs. Real-World Prior (`T1.7` / `T2.1`):**
   - *Finding:* Observed churn in the dataset is **49.56%** ($49{,}562$ churned vs. $50{,}438$ stayed), which makes raw accuracy meaningful for model benchmarking ($50.44\%$ majority baseline) but indicates an artificially balanced or resampled cohort compared to real-world telecom monthly/bimonthly churn ($5\%\text{–}10\%$), requiring label-shift re-basing before estimating financial returns.

2. **Missingness Carries Strong Behavioral Signal (`T1.2` | `figures/missing_top20.png`):**
   - *Finding:* While high-missingness demographic columns (`numbcars` $49.37\%$, `dwllsize` $38.31\%$, `HHstatin` $37.92\%$) show only a $+1.3$ to $+2.6\text{ pp}$ churn difference when missing, missing usage-change (`change_mou` / `change_rev`, $n = 891$, $0.89\%$) exhibits a **76.09% churn rate** ($+26.77\text{ pp}$ above present rows) and missing web capability (`hnd_webcap`, $n = 10{,}189$, $10.19\%$) exhibits a **59.15% churn rate** ($+10.68\text{ pp}$), proving that missingness indicators must be preserved rather than dropped.

3. **Sharp Handset-Age Jump Across ~300 Days (`T2.1` | `figures/eqpdays_churn.png`):**
   - *Finding:* Customer churn remains below average ($36.2\%\text{–}38.3\%$) when current equipment age (`eqpdays`) is between $176$ and $300$ days ($37.97\%$ in the $276\text{–}300\text{d}$ bin on train; $36.85\%$ across $260\text{–}300\text{d}$), then jumps by **+23.83 percentage points** to **60.69%** across $301\text{–}340\text{d}$ ($59.03\%$ in $301\text{–}325\text{d}$, peaking at **62.44%** in $326\text{–}350\text{d}$ on 25-day bins and **64.5%** on 321–340d).

4. **Robustness & Structural Mechanism of the ~300-Day Jump (`T2.2` | `figures/eqpdays_robustness.png`):**
   - *Finding:* The $301\text{–}340\text{d}$ vs. $260\text{–}300\text{d}$ jump has a tight bootstrap 95% CI of **[+22.12 pp, +25.62 pp]** (local linear RD discontinuity $+23.88\text{ pp}$) and persists within `months >= 10` (**+19.46 pp**), single-handset customers (`phones == 1`: **+34.08 pp**), credit classes, and geographic areas, but drops to **+2.98 pp** within `months >= 13` because `eqpdays` and `months` co-move on a customer's original handset (`eqpdays ≈ 30 × months`) until a handset replacement resets `eqpdays`!
   - *Verdict:* **Real behavioral and contractual lifecycle signal (entangled with the 1-year renewal window and handset replacement history), not a random noise artifact—best operationalized as a combined lifecycle trigger validated via an A/B holdout pilot.**

5. **First-Year Tenure Cliff at Months 10–12 (`T2.3` | `figures/months_churn.png`):**
   - *Finding:* Churn drops steadily during the initial contract months to a minimum of **29.25%** at month 9 ($28.80\%$ full sample), surges to **40.18%** at month 10, peaks at **64.57%** at month 11 ($65.13\%$ full sample) and **61.49%** at month 12 ($61.86\%$ full sample), and then gradually declines to $47.3\%$ for $37+$ months.

6. **Two-Dimensional Entanglement of Tenure and Device Age (`T2.4` | `figures/tenure_device_heatmap.png`):**
   - *Finding:* Zero customers with tenure $\le 9$ months have `eqpdays > 300` (maximum `eqpdays` is $288$ days), and within every mature tenure band ($13\text{–}18\text{m}$, $19\text{–}24\text{m}$, and $25\text{m}+$), customers who recently refreshed their handset ($\le 200\text{d}$) churn at **15 to 24 percentage points lower rates** ($33.2\%\text{–}48.1\%$) than peers on aging handsets ($>300\text{d}$: $48.2\%\text{–}59.4\%$).

7. **Usage Collapse Segments Signal "Silent Defection" but Low Revenue Share (`T2.5` | `figures/usage_segments.png`):**
   - *Finding:* Customers with zero monthly voice usage (`mou_Mean == 0`, $n = 1{,}615$, $1.62\%$ of base) churn at **79.81%** and those with `mou_Mean <= 10` ($n = 3{,}848$) churn at **65.41%**, but zero-usage customers generate an average `rev_Mean` of only **23.11 MU** (vs. $58.72\text{ MU}$ overall, representing just **0.64%** of total company revenue), meaning many have already stopped using their SIMs ("silent defectors") and should receive low-cost automated outreach rather than expensive subsidies.

8. **Monthly Revenue Alone Does Not Separate Churners from Stayers (`T2.6`):**
   - *Finding:* Mean monthly revenue (`rev_Mean`) is virtually identical between churners (**58.21 MU**, median **47.49 MU**) and stayers (**59.22 MU**, median **48.88 MU**, correlation $r = -0.0109$), demonstrating that Company A loses high-revenue and low-revenue subscribers at similar rates and must prioritize interventions by **expected value-at-risk ($P(\text{churn}) \times \text{Value}$)**.

9. **Customer Care Calls Exhibit Reverse Selection (`T2.7`):**
   - *Finding:* Customers with zero customer-care calls (`custcare_Mean == 0`, $n = 62{,}905$) churn at **51.53%**, whereas those making $>3$ care calls/month ($n = 15{,}316$) churn at **45.28%** (and interact more heavily with the network: $694$ vs. $457$ MOU/month), indicating that engaged subscribers call support to resolve billing/network issues while disengaged subscribers leave silently.

10. **Demographic Weakness & Ethical Exclusion of Ethnicity (`T2.9`):**
    - *Finding:* Standard household demographics (`income` bands $1\text{–}9$ span $47.6\%\text{–}50.5\%$ churn; `adults` and `marital` span $48\%\text{–}51\%$) carry minimal predictive power, whereas `ethnic` roll-up codes show sharp disparities (`ethnic = 'O'` churns at **58.12%** vs. `ethnic = 'Z'` at **39.73%**); to prevent discriminatory targeting and legal/reputational exposure, we exclude `ethnic` from our production model and verify that ROC-AUC changes by less than $0.001$.
