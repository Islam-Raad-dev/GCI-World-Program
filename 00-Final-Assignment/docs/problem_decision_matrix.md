# Problem Framing Decision Matrix — Company A Telecom PoC

> **Task T4.1 & PRD §6.1:** Score candidate problem framings (Options A–E) on a 1–5 scale across five criteria: Evidence Strength (from Company A's EDA), Commercial Actionability, Financial Measurability, Implementation Risk (5 = lowest risk / highest feasibility), and Fit with Market Evidence (Iraq/MENA saturated telecom dynamics).

---

## 1. Decision Matrix (Scored 1–5 per Criterion; Max = 25)

| Candidate Option | Target & ML Task | Evidence Strength (1–5) | Actionability (1–5) | Measurability (1–5) | Low Risk / Realism (1–5) | Market Fit (1–5) | **Total Score** | Key Strengths & Weaknesses |
|---|---|---:|---:|---:|---:|---:|---:|---|
| **A. Risk-Ranked Retention (Core)** | `churn` (binary classification & probability ranking) | 5 | 5 | 5 | 4 | 5 | **24 / 25** | **Strengths:** Directly predicts 31–60 day defection; top-10% model ranking lifts precision to ~80% in sample (~1.6× lift).<br>**Weaknesses:** Overall AUC is ~0.70; requires label-shift re-basing from 49.56% sample churn to realistic 5–10% priors. |
| **B. Lifecycle Triggers (Complement)** | Rule/threshold triggers around `eqpdays ~ 300d` & `months 10–12` | 4 | 5 | 4 | 4 | 5 | **22 / 25** | **Strengths:** Sharpest empirical pattern (+23.8 pp jump across 300d; 65.1% peak at month 11); zero-jargon rule for CRM.<br>**Weaknesses:** Observational data cannot prove causality without an A/B holdout pilot; entangled with first-year contract cycle. |
| **D. Value-at-Risk Prioritization (Core Multiplier)** | $P(\text{churn}) \times \text{Customer Value}$ (`rev_Mean` × margin × horizon) | 4 | 5 | 5 | 4 | 5 | **23 / 25** | **Strengths:** Because `rev_Mean` does not separate churners ($58.2\text{ MU}$) from stayers ($59.2\text{ MU}$), weighting risk by value prevents wasting offers on low-ARPU zero-usage accounts ($23.1\text{ MU}$).<br>**Weaknesses:** Requires explicit margin and retention horizon assumptions. |
| **C. Early Warning on Usage Collapse Only** | Segment with `mou_Mean == 0` or $\le 10$ | 4 | 2 | 3 | 3 | 3 | **15 / 25** | **Strengths:** Very high churn rate (79.8% at `mou_Mean == 0`).<br>**Weaknesses:** Small group ($1.6\%$ of customers, $0.64\%$ of revenue) that has likely already switched SIMs ("silent defectors"). |
| **E. Unsupervised Customer Segmentation** | Clustering (`K-Means` / personas on usage & demographics) | 3 | 2 | 2 | 3 | 3 | **13 / 25** | **Strengths:** Descriptive view of customer base.<br>**Weaknesses:** Clusters alone do not predict who will leave in 31–60 days or quantify net financial return. |

---

## 2. Final Decision Gate Verdict (`T4.2`)

**Selected Framing:** **Integrated Two-Lane Retention Program combining Option A + Option D (Lane 1: Value-Aware ML Risk Ranking) with Option B (Lane 2: Pre-Cliff Lifecycle Triggers), while routing Option C (`mou_Mean == 0`) to zero-cost automated outreach.**

- **Why this combination wins:**
  1. **Lane 1 (ML Risk-Ranked Saves):** Uses our boosted-tree classifier (`XGBoost`) to score all active subscribers monthly and target the optimal top-$k^*$% ranked by risk and revenue value (`rev_Mean > 10 MU`), maximizing net retained value after intervention cost—even after re-basing sample churn from 49.56% to realistic 5%–10% market rates.
  2. **Lane 2 (Pre-Cliff Lifecycle Pilot):** Translates our strongest EDA discovery—the entangled month 10–12 tenure spike and ~300-day handset aging cliff—into a proactive **days 240–290 (months 8–9) handset-refresh & plan-check A/B pilot** with a 20% randomized holdout group to measure true causal lift before full rollout.
