# Slide-by-Slide Speaker Notes (`docs/speaker_notes.md`)

**Deck:** *From Reactive Churn Firefighting to Proactive Value Retention: A Risk-Ranked Lifecycle & Usage-Rescue PoC for Company A*
**Presenter:** Islam Raad (University of Mosul)
**Target Pacing:** ~12–15 minutes total (~50–60 seconds per slide) + Q&A.

---

## Slide 1 — Title & Executive Summary Badges
- **Key Message:** We transformed Company A's raw 100,000-subscriber dataset from a reactive classification baseline into a profit-driven, prior-calibrated retention system that beats the tutorial XGBoost baseline on every metric while cutting model overfitting in half.
- **How to Read the Visual:** Point to the three summary cards across the bottom: (1) our empirical scope (`100,000` subscribers, 100 merged columns, `SEED=42`), (2) our predictive lift (`0.7011` held-out test ROC-AUC, `81.0%` sample precision in the Top-10% tier), and (3) our re-based Base Case net value (`+138,938 MU`).
- **Numbers to Emphasize:** `100,000` subscribers, `0.7011` Test ROC-AUC (`0.7013` 5-fold CV), `+138,938 MU` Base Case net impact.
- **Transition to Slide 2:** "Before diving into the data, let's ask why surgical retention—rather than customer acquisition—is the decisive lever in saturated telecom markets like Iraq and MENA."
- **Likely Question:** *Why report Monetary Units (MU) instead of USD or IQD?* $\to$ Because the dataset (`rev_Mean` = `58.72` units) uses North American wireless billing scale; reporting MU preserves exact empirical ratios without inventing an arbitrary exchange rate.

---

## Slide 2 — Industry & Regional Context (Iraq & MENA Telecom)
- **Key Message:** In Iraq and across MENA, mobile SIM penetration has reached 100%–103% of the population, meaning greenfield subscriber growth is over and EBITDA protection depends on preventing high-value defection.
- **How to Read the Visual:** The top KPI cards contrast Iraq's `48.1M` active connections (`103%` penetration per DataReportal 2025; `100.08` per 100 people per ITU/World Bank) and MENA's `427M` unique subscribers against Reichheld & Sasser's benchmark (`+25% to +85%` profit lift per `5 pp` churn reduction). The table compares Zain Iraq (`17.9M–19.3M` users), Asiacell (`17.69M–19.13M` users), and Korek Telecom against our Company A PoC base (`100,000` users, `58.72 MU` mean ARPU).
- **Numbers to Emphasize:** `103%` mobile connection penetration in Iraq, `>85%–90%` prepaid share, and `5%–10%` real operator churn vs. `49.56%` in our case-control sample.
- **Transition to Slide 3:** "With that market imperative clear, let's examine what our audit of all 100 columns in `Client.csv` and `Record.csv` revealed."
- **Likely Question:** *How does multi-SIM behavior in Iraq affect churn modeling?* $\to$ Dual-SIM users silently shift voice/data traffic to a secondary SIM before formally disconnecting, which is why our model prioritizes 3-month usage slump ratios (`mou_ratio_3m`).

---

## Slide 3 — Dataset Audit & Hygiene (`100,000 × 100`)
- **Key Message:** Auditing all 100 merged columns exposed four critical data properties—informative missingness, `change_mou` unit mislabeling, negative `eqpdays`, and 10 near-duplicate column pairs—that directly improve model stability when fixed.
- **How to Read the Visual:** The left horizontal bar chart shows the top 20 columns by missingness percentage alongside the churn rate when missing. The right table summarizes the four engineering fixes applied before modeling.
- **Numbers to Emphasize:** `76.09%` churn when `change_mou` is missing (`n=891`), `59.15%` churn when `hnd_webcap` is missing (`n=10,189`), `r = 0.9025` proving `change_mou` is raw difference (`mou_Mean - avg3mou`), and `133` negative `eqpdays` rows.
- **Transition to Slide 4:** "Once we cleaned the schema and locked our 70/30 stratified split, our exploratory analysis uncovered three major behavioral patterns—starting with the 300-day handset age cliff."
- **Likely Question:** *Why not drop rows with missing values?* $\to$ Dropping missing rows would discard nearly half the dataset (`numbcars` is `49.4%` missing) and throw away high-risk signals like missing `change_mou` (`76.09%` churn).

---

## Slide 4 — EDA Finding 1: The 300-Day Handset Age Cliff
- **Key Message:** Customer churn jumps by `+23.83 percentage points` once current handset age (`eqpdays`) crosses 300 days (`36.85%` in days `260–300` vs. `60.69%` in days `301–340`).
- **How to Read the Visual:** The left curve plots observed churn across 25-day `eqpdays` bins on the 70% training split (`n=70,000`) with 95% confidence bands, showing a stable ~37%–44% plateau below 300 days and an abrupt vertical step at 300 days peaking at `62.44%` in days `326–350`. The right table proves this jump holds across subgroups.
- **Numbers to Emphasize:** `+23.83 pp` jump (`95% bootstrap CI: [+22.12, +25.62] pp`), `+23.88 pp` local linear regression-discontinuity estimate, and `+34.08 pp` jump among single-handset subscribers (`phones == 1`).
- **Transition to Slide 5:** "A skeptical data scientist should immediately ask: is 300 days (~10 months) purely a hardware aging effect, or is it entangled with the customer's first-year contract tenure? Slide 5 answers that."
- **Likely Question:** *Does old hardware directly cause churn?* $\to$ Not by itself—it is a compound lifecycle signal combining contract renewal timing and device aging, as we show on Slide 5.

---

## Slide 5 — EDA Finding 2: First-Year Renewal Cliff & Tenure-Device Entanglement
- **Key Message:** The 300-day handset spike coincides with the Month 10–12 first-year contract renewal cliff (`29.25%` churn at Month 9 doubling to `64.57%` at Month 11), yet handset age continues to separate churn risk by 15–24 pp even among mature 19–25+ month subscribers.
- **How to Read the Visual:** Left is the tenure churn curve (`months` 6–36) showing the sharp spike at Months 10–12. Right top is the 2D `months × eqpdays` heatmap showing that the top-right cells (`6–9m` and `eqpdays > 300`) are structurally empty (`n=0`, max `eqpdays = 288d`), while in rows `19–24m` and `25m+`, churn rises monotonically from left (`≤200d`: `33.2%–39.3%`) to right (`501d+`: `55.0%–57.1%`).
- **Numbers to Emphasize:** `29.25%` (Month 9) $\to$ `64.57%` (Month 11), `0` customers with `months ≤ 9` and `eqpdays > 300`, and `33.2% vs. 57.1%` (`-23.8 pp` gap) in mature `25m+` accounts.
- **Transition to Slide 6:** "Beyond lifecycle timing, how do usage behavior, monthly revenue, and demographics interact with churn? Let's look at Slide 6."
- **Likely Question:** *How does this entanglement change your business recommendation?* $\to$ Instead of shipping expensive phones to everyone at Day 300, Lane 2 combines a Month 8–9 renewal check with an installment trade-in voucher and tests it in an 80/20 holdout pilot.

---

## Slide 6 — EDA Finding 3: Usage Disengagement, Flat Static ARPU & Fairness Audit
- **Key Message:** Zero-usage accounts (`mou_Mean == 0`) churn at `79.81%` but carry only `23.11 MU` mean ARPU (`0.64%` of total revenue), meaning an unguarded ML model will waste human call-center budget on dormant SIMs unless we gate offers by active value.
- **How to Read the Visual:** The left bar chart compares churn rate and ARPU across five usage tiers from Zero Usage (`79.8%` churn, `23.1 MU` ARPU) to Active Baseline (`mou_Mean > 30`: `48.6%` churn, `61.3 MU` ARPU, `96.85%` of total revenue). The right cards detail three commercial traps: Dormant SIMs, Static ARPU blindness (`58.21` vs. `59.22 MU`), and `ethnic` disparity (`18.37 pp` gap).
- **Numbers to Emphasize:** `79.81%` zero-MOU churn at `23.11 MU` ARPU, `58.21 vs. 59.22 MU` churned vs. stayed mean ARPU, and `-0.0016` validation AUC cost of excluding `ethnic`.
- **Transition to Slide 7:** "These three EDA findings directly shaped our problem formulation and leakage-safe modeling pipeline on Slide 7."
- **Likely Question:** *Why exclude `ethnic` if it has predictive signal?* $\to$ Allocating retention subsidies by ethnicity creates ethical and regulatory risk, and our ablation proves removing `ethnic` changes validation AUC by only `-0.0016`.

---

## Slide 7 — Problem Formulation & Leakage-Safe Methodology
- **Key Message:** Before training complex models, we evaluated three candidate problem framings against a weighted decision matrix and designed a four-stage leakage-safe workflow centered on Top-$k\%$ probability ranking.
- **How to Read the Visual:** The top SVG diagram traces our 4-step pipeline (`Data Audit & 70/30 Split` $\to$ `20 Domain Features & Fairness Filter` $\to$ `5-Fold Stratified CV across 7 Models` $\to$ `Top-10% Profit Engine`). The bottom table scores Framing P1 (`4.78/5.00`), Framing P2 (`4.38/5.00`), and Framing P3 (`3.40/5.00`).
- **Numbers to Emphasize:** `70,000` train / `30,000` test split (`SEED=42`), `107` fair features (`98 raw - 10 duplicates - 1 ethnic + 20 engineered`), and `4.78 / 5.00` decision score.
- **Transition to Slide 8:** "Before looking at model scores, we must address the single biggest statistical pitfall in the dataset: the 49.56% case-control sample prior."
- **Likely Question:** *Why optimize ROC-AUC and Top-10% Precision instead of threshold-0.5 Accuracy?* $\to$ Threshold-0.5 flags ~50% of the base regardless of call-center capacity; ranking by $\hat{p}_i$ lets CRM target the exact top $k\%$ that maximizes net profit.

---

## Slide 8 — Solving the Case-Control Trap: Prior-Shift Re-Basing
- **Key Message:** Because the dataset is a 50/50 case-control sample (`49.56%` churn) whereas real operator churn is `5%–10%`, unadjusted sample precision overstates campaign net profit by `3.3×`; we correct this using Saerens et al.'s (2002) exact Bayes prior-shift formula.
- **How to Read the Visual:** The left card presents the mathematical formula converting sample precision $P_s(k)$ under prior $\pi_s = 0.4956$ to production precision $P_{\text{real}}(k)$ under $\pi_r \in \{5\%, 10\%\}$. The right table compares Top-10% metrics across Unadjusted (`81.00%` precision), Base Case 10% prior (`32.53%` precision, `3.25×` lift), and Conservative 5% prior (`18.59%` precision, `3.72×` lift).
- **Numbers to Emphasize:** `81.00%` sample precision $\to$ `32.53%` re-based precision (`3.25×` lift at 10% prior) and `18.59%` (`3.72×` lift at 5% prior); `+138,938 MU` realistic Base Case vs. `+457,708 MU` unadjusted.
- **Transition to Slide 9:** "Now let's examine how our 7 candidate models performed under 5-fold cross-validation and on the held-out 30,000-customer test set."
- **Likely Question:** *Does prior shift change which customers are in the Top 10%?* $\to$ No! Because Bayes prior shift is a strictly monotonic transformation of $\hat{p}_i$, customer ranking and ROC-AUC are 100% invariant.

---

## Slide 9 — Model Selection & Validation (R3 Live-Text Benchmark Table)
- **Key Message:** Our final selected model—**M5 (Regularized & Tuned XGBoost on 107 fair features)**—achieves `0.7013` 5-fold CV ROC-AUC and `0.7011` held-out Test ROC-AUC (`64.13%` Test Accuracy, `81.0%` Top-10% Precision), beating the tutorial baseline while cutting the train-test overfitting gap nearly in half (`9.92 pp` $\to$ `5.23 pp`).
- **How to Read the Visual:** The top live-text table reports all 7 models (`M0` Dummy through `M6` LightGBM). The bottom-left bar chart visualizes 5-fold CV and Test ROC-AUC against the `0.6940` tutorial baseline, and the bottom-right panel explains why `M5` was chosen.
- **Numbers to Emphasize:** `0.6938` $\to$ `0.7011` Test ROC-AUC (`+0.0073`), `0.6357` $\to$ `0.6413` Test Accuracy (`+0.56 pp`), `79.2%` $\to$ `81.0%` Top-10% precision, and `9.92 pp` $\to$ `5.23 pp` train-test gap.
- **Transition to Slide 10:** "What signals inside M5 actually drive those predictions, and how can a non-technical business team act on them? Let's look at Slide 10."
- **Likely Question:** *Why choose M5 (XGBoost) over M6 (LightGBM) when both have ~0.701 Test AUC?* $\to$ M5 achieves the highest 5-fold CV mean (`0.7013` vs. `0.7002`), highest Test Accuracy (`64.13%`), and lowest train-test overfitting gap (`5.23 pp` vs. `7.07 pp`).

---

## Slide 10 — Model Explainability & Commercial Levers (Plain-Language View)
- **Key Message:** Gradient-boosted trees combine three intuitive signal families—handset lifecycle (`dev_age_gt_300`, `eqpdays`, `refurb_new`), tenure renewal windows (`months`, `tenure_10_12_cliff`), and 3-month usage slumps (`mou_ratio_3m`)—each mapping directly to a commercial intervention.
- **How to Read the Visual:** Left is the Top-10 gain importance chart color-coded by commercial lever type. Top-right is a plain-language diagram showing how tree groups add/subtract risk points to separate the Top-10% risk tier (`81.0%` sample churn) from the Bottom-10% safe tier (`18.4%` churn). Bottom-right triangulates gain, permutation importance, and partial dependence (PDP).
- **Numbers to Emphasize:** `15.2%` gain share on `dev_age_gt_300` (`4.6%` on `eqpdays`), `#1` permutation importance on `mou_ratio_3m` (`+0.0304` AUC drop), and `-0.0065` ablation AUC drop when `eqpdays` signals are removed.
- **Transition to Slide 11:** "Let's translate these individual risk scores into a decile targeting table on Slide 11."
- **Likely Question:** *Why rank features by both Gain and Permutation Importance?* $\to$ Binary splits like `dev_age_gt_300` naturally concentrate tree gain at the root, whereas permutation importance on held-out test data measures how much total ranking power depends on continuous behavioral ratios like `mou_ratio_3m`.

---

## Slide 11 — Top-$k\%$ Targeting & Decile Lift Table
- **Key Message:** Targeting the Top-10% highest-risk subscribers (`score ≥ 0.713`, `n = 10,000` per `100,000` base) concentrates true churners by `3.25×` under a 10% real churn prior (`32.5%` precision) and `3.72×` under a 5% prior (`18.6%` precision).
- **How to Read the Visual:** Top-left shows the Precision@$k\%$ curve (comparing sample precision vs. 10% and 5% re-based precision). Top-right shows the Lift multiplier curve peaking above `6.2×` at Top-1% and sitting at `3.25×` at Top-10%. The bottom table provides exact cutoffs from Top-1% to Top-50%.
- **Numbers to Emphasize:** Top-10% threshold `p̂_i ≥ 0.713`, `81.0%` sample precision (`1.63×` lift), `32.5%` re-based precision at 10% prior (`3.25×` lift, `3,253` true churners reached), vs. `18.4%` sample churn in the Bottom-10% safe tier (`4.40×` separation).
- **Transition to Slide 12:** "How do we operationalize this Top-10% list in Company A's monthly CRM workflow? Slide 12 lays out our Two-Lane Retention Program."
- **Likely Question:** *Why choose $k = 10\%$ as the primary pilot cutoff?* $\to$ Top-10% (`10,000` accounts) matches realistic monthly outbound CRM capacity, maximizes Conservative net profit (`+27,418 MU`), and captures `+138,938 MU` at a `185.3%` ROI in the Base Case.

---

## Slide 12 — Proposed Operational Solution: Two-Lane Retention Program & 80/20 Pilot
- **Key Message:** Instead of sending a generic discount to every high-risk customer, we route targeted subscribers into two root-cause intervention lanes while filtering dormant zero-MOU accounts to zero-cost digital SMS and gating scale-up on a 90-day 80/20 randomized holdout pilot.
- **How to Read the Visual:** The top architecture diagram shows monthly batch scoring (`N=100,000`), the value guardrail filter (`rev_Mean ≥ 30 MU`, `mou_Mean > 0`), routing into **Lane 1 (Usage-Slump & Plan-Fit Rescue)** and **Lane 2 (Pre-300-Day Handset Refresh & Month 8–9 Renewal Check)**, and the **80/20 A/B Holdout Gate**. The three bottom cards detail the offer and unit economics for each lane.
- **Numbers to Emphasize:** Lane 1 cost `c = 7.50 MU` protecting `V = 328.83 MU` (`break-even s* = 7.01%`); Lane 2 eligible cohort `8,815` accounts (`ARPU = 66.91 MU`, `c = 4.00 MU`, `+8,125 MU` net 90-day pilot return); Dormant guardrail for `1,615` zero-MOU accounts (`ARPU = 23.11 MU`).
- **Transition to Slide 13:** "Let's stress-test the financial return of this program across Conservative, Base, and Optimistic scenarios on Slide 13."
- **Likely Question:** *Why use an 80% treatment / 20% control split during the 90-day pilot?* $\to$ It captures 80% of the expected retention value immediately while preserving a statistically powered (`n=2,000` in Lane 1; `n=1,763` in Lane 2) control group to verify true causal uplift.

---

## Slide 13 — Estimated Financial Impact & Sensitivity Tornado
- **Key Message:** Under realistic prior-shifted assumptions at $k=10\%$ (`n=10,000`), the program is estimated to deliver **`+27,418 MU` (Conservative, 5% prior)**, **`+138,938 MU` (Base Case, 10% prior, 185.3% ROI)**, and **`+329,786 MU` (Optimistic, 12m horizon)** in annual net contribution margin—remaining net positive across every single sensitivity stress test.
- **How to Read the Visual:** Top-left plots Net Impact (in thousands of MU) across targeting cutoffs $k\%$ from 1% to 50% for all three scenarios. Top-right is the one-at-a-time Sensitivity Tornado around the `+138.9k MU` Base Case. The bottom table documents every parameter (`π_r`, `p_adj`, `s`, `ARPU`, `margin`, `H`, `V`, `c`) alongside the `+457,708 MU` unadjusted sample reference.
- **Numbers to Emphasize:** `+27,418 MU` Conservative, `+138,938 MU` Base Case (`650.6` saved accounts, `213,938 MU` gross saved minus `75,000 MU` cost), `+329,786 MU` Optimistic, and `s* = 7.01%` break-even conversion rate.
- **Transition to Slide 14:** "To ensure these projected returns materialize safely in production, Slide 14 pairs five operational risks with concrete mitigations and a 90-day rollout plan."
- **Likely Question:** *Which parameter has the largest impact on net profit?* $\to$ As the tornado chart shows, the intervention save rate (`s: 12% vs. 28%`, swing `171k MU`) and real churn prior (`π_r: 5% vs. 15%`, swing `163k MU`) are the top two drivers—and even at `s = 12%` or `π_r = 5%`, net impact exceeds `+47,000 MU`.

---

## Slide 14 — Key Limitations, Operational Risks & 90-Day Roadmap
- **Key Message:** We address five real-world deployment risks—observational vs. causal uplift, prior drift, "sleeping dog" outreach backfire, subsidy cannibalization, and demographic proxy bias—through a phased 90-day rollout with a hard scale-up gate at Day 90.
- **How to Read the Visual:** The left table maps each of the 5 risks to its specific engineering or commercial control. The right navy panel outlines Phase 1 (Days 1–30: Shadow Scoring & CRM Wiring), Phase 2 (Days 31–60: Launch 80/20 Holdout Pilot), and Phase 3 (Days 61–90: Uplift Readout & Scale Gate).
- **Numbers to Emphasize:** `20%` randomized control group, `rev_Mean ≥ 30 MU` subsidy floor, `-0.0016` AUC impact of excluding `ethnic`, and `s ≥ 7.01%` Day-90 scale gate.
- **Transition to Slide 15:** "Slide 15 provides our complete numbered bibliography and tool disclosures matching `references.txt`."
- **Likely Question:** *What is the "sleeping dog" effect in telecom churn?* $\to$ Some passive subscribers only realize their contract expired when CRM calls them; restricting outbound calls to the Top-10% (`p̂_i ≥ 0.713`) and tracking weekly treatment-vs-control churn prevents outreach backfire.

---

## Slide 15 — Verified References & AI Disclosure
- **Key Message:** Every market statistic, academic methodology paper, software library, dataset source, and AI assistance log is cited transparently with 1-to-1 numbering `[1]–[14]` matching `submission/references.txt`.
- **How to Read the Visual:** Two-column numbered reference grid `[1]–[14]` dynamically generated from `references.txt`.
- **Numbers to Emphasize:** `14` verified sources (`[1]–[5]` Iraq/MENA telecom market & operator disclosures, `[6]–[9]` retention & prior-shift literature, `[10]–[12]` ML libraries, `[13]` GCI dataset, `[14]` AI disclosure).
- **Closing Line:** "Thank you—I welcome your questions on our data audit, our regularized XGBoost ranking engine, or our prior-shifted financial model."
