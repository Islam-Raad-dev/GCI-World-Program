# Testable Business & Analytical Hypotheses — Company A Telecom PoC

> **Requirement (PRD §8.2 & Task T2.11):** Formulate 3 full-sentence hypotheses directly grounded in Company A's EDA, ranked by commercial actionability and empirical evidence strength.

---

### Hypothesis 1 (Rank #1 — Lifecycle & Handset Aging Cliff)
> **"Single-handset subscribers approaching the ~300-day equipment age threshold (`eqpdays` 240–300 days) and the months 10–12 first-year renewal window are significantly more likely to churn (+19.5 to +34.1 percentage points higher churn once crossing 300 days) because initial promotional commitments or handset satisfaction expire around the one-year mark, whereas customers who refresh their handset (`eqpdays <= 200` within mature tenure) exhibit 15–24 pp lower churn; we test this in our ML feature engineering (`dev_age_gt_300`, `tenure_10_12`, `eqp_per_tenure_day`) and propose testing its causal retention lift via a randomized 90-day pre-cliff handset-refresh pilot."**
- **Evidence from Company A's Data:**
  - Across all training customers ($N=70{,}000$), churn jumps from **36.85%** ($260\text{–}300\text{d}$) to **60.69%** ($301\text{–}340\text{d}$), a **+23.83 pp** jump (95% bootstrap CI: $[+22.12, +25.62]\text{ pp}$).
  - Among mature subscribers (`months >= 25`), those with a refreshed handset ($\le 200\text{d}$) churn at **33.24%** vs. **57.08%** for handsets $>500\text{d}$.
- **Commercial Actionability:** High — CRM/retention teams know exact `eqpdays` and `months` in advance and can trigger an early upgrade / loyalty bundle at days 240–290 (months 8–9) before the subscriber shops competitors.

---

### Hypothesis 2 (Rank #2 — Multi-Signal Behavioral Decline & Overage Friction)
> **"Active subscribers whose recent monthly voice usage drops sharply relative to their 3- and 6-month historical baseline (`mou_Mean / avg3mou` and `change_mou`) while facing high recurring or overage charge burdens (`ovrrev_Mean / rev_Mean`) are more likely to defect within 31–60 days because declining network engagement paired with bill shock precedes voluntary switching; we test this by engineering usage-trajectory and billing-structure ratios and measuring whether a boosted tree ensemble improves out-of-sample ranking (ROC-AUC and Top-Decile Lift) over raw features and linear baselines."**
- **Evidence from Company A's Data:**
  - Single-feature signal is diffuse (strongest single numeric feature `eqpdays` has univariate $\text{AUC} = 0.5751$), and `rev_Mean` alone does not separate churners ($58.21\text{ MU}$) from stayers ($59.22\text{ MU}$).
  - Customers with high overage revenue (`ovrrev_Mean > 20 MU`) churn at **55.64%** vs. **47.82%** for zero-overage customers, and declining usage (`change_mou < 0`) elevates risk across all tenure bands.
- **Commercial Actionability:** High — combining ML risk probability with customer revenue (`Value-at-Risk = P(churn) × Retained Value`) allows the retention team to focus finite call-center/offer budgets on the top $k^*$% of high-value at-risk subscribers.

---

### Hypothesis 3 (Rank #3 — Zero-Usage "Silent Defectors" vs. Saveable Disengagement)
> **"Subscribers with complete usage collapse (`mou_Mean == 0` or missing `change_mou`) exhibit extreme churn rates (79.81% and 76.09%, respectively) because they have effectively already abandoned Company A's SIM card for a competitor (a common multi-SIM behavior in prepaid-heavy markets), meaning expensive human-agent or hardware subsidies on zero-usage accounts would waste retention budget on low-ARPU (23.11 MU) 'already-gone' users; we test this by segmenting zero-usage vs. declining-active accounts in our economic impact model."**
- **Evidence from Company A's Data:**
  - The $1{,}615$ customers with `mou_Mean == 0` have a **79.81%** churn rate but generate only **23.11 MU** mean monthly revenue ($0.64\%$ of total company revenue).
  - By contrast, customers with moderate declining usage (`mou_Mean > 30` but negative `change_mou`) generate **~59 MU** monthly revenue and are still actively reachable on the network.
- **Commercial Actionability:** Medium-High (Cost Avoidance) — prevents the CRM team from burning high-cost retention incentives on dead SIMs, routing zero-usage accounts to zero-marginal-cost automated SMS/push win-back campaigns instead.
