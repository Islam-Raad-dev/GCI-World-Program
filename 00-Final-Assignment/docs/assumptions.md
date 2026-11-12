# Economic & Operational Assumptions Register (`docs/assumptions.md`)

Per **PRD §9.1–9.5** and **Tasks T8.1–T8.8**, every financial figure in this proposal is expressed in **Dataset Monetary Units (MU)** (`rev_Mean` units) so that unit economics remain 100% consistent with the empirical customer billing records in `Client.csv` and `Record.csv` (`[13]`), and every precision figure is explicitly **re-based from the 49.56% case-control sample prior to realistic 5%–10% production churn priors** via Bayes' theorem (`[9]`).

---

## 1. Parameter Register (With SOURCED `[ID]` vs. ASSUMPTION Tags)

| Symbol | Parameter Name | Conservative | Base Case | Optimistic | Unadjusted Sample (Reference Only) | Source / Justification Tag |
|---|---|---|---|---|---|---|
| $N$ | Active Subscriber Base Evaluated | `100,000` | `100,000` | `100,000` | `100,000` | **SOURCED `[13]`** — Exact merged subscriber count in `Client.csv` $\bowtie$ `Record.csv`. |
| $\pi_s$ | Sample Churn Base Rate | `49.56%` (`0.4956`) | `49.56%` (`0.4956`) | `49.56%` (`0.4956`) | `49.56%` (`0.4956`) | **SOURCED `[7]`, `[13]`** — Empirical churn rate in the 50/50 case-control calibration sample (`y_test.mean()`). |
| $\pi_r$ | Realistic Production Churn Prior | `5.0%` (`0.05`) | `10.0%` (`0.10`) | `10.0%` (`0.10`) | `49.56%` (Unadjusted) | **SOURCED `[3]`, `[7]`, `[8]`** — Tutorial PDF explicitly notes real-world telecom churn is **5%–10%** over a campaign/quarterly horizon (`1.5%–2.5%` monthly). |
| $k\%$ | Targeted Risk Tier Share | `Top 10%` (`10,000`) | `Top 10%` (`10,000`) | `Top 10%` (`10,000`) | `Top 10%` (`10,000`) | **SOURCED `[7]`, `[8]`** — Standard top-decile CRM retention capacity (`n = 10,000` accounts). |
| $p_{\text{sample}}(10\%)$ | Raw Sample Top-10% Precision | `81.00%` | `81.00%` | `81.00%` | `81.00%` | **SOURCED (Model M5 on Held-Out Test Set)** — `2,430` true churners among top `3,000` test accounts (`1.634x` sample lift). |
| $p_{\text{adj}}(10\%)$ | Prior-Shifted Real Precision at $k=10\%$ | **`18.59%`** (`3.72x` lift) | **`32.53%`** (`3.25x` lift) | **`32.53%`** (`3.25x` lift) | `81.00%` (Unadjusted) | **SOURCED `[9]`** — Exact Bayes prior-shift formula (Saerens et al., 2002) applied to Model M5 test predictions. |
| $\text{ARPU}$ | Monthly Revenue per User (`rev_Mean`) | `48.20 MU` (Median) | `58.72 MU` (Mean) | `58.72 MU` (Mean) | `58.72 MU` (Mean) | **SOURCED `[13]`** — Empirical dataset median (`48.20 MU`) and mean (`58.72 MU`) of `rev_Mean`. |
| $\text{margin}$ | Gross Contribution Margin | `65%` (`0.65`) | `70%` (`0.70`) | `75%` (`0.75`) | `70%` (`0.70`) | **ASSUMPTION (Industry Benchmark `[3]`, `[4]`, `[5]`)** — Standard wireless service gross margin after interconnect/direct network costs. |
| $H$ | Incremental Retained Months | `6 months` | `8 months` | `12 months` | `8 months` | **ASSUMPTION (Tested in Sensitivity Tornado)** — Average additional tenure preserved by a successful renewal/rescue intervention (`6m` half-year to `12m` full contract cycle). |
| $V$ | Protected Gross Margin per Saved Customer ($\text{ARPU} \times \text{margin} \times H$) | **`187.98 MU`** | **`328.83 MU`** | **`528.48 MU`** | **`328.83 MU`** | **DERIVED (`ARPU × margin × H`)** — Compare with tutorial toy example (`V = 300 MU`). |
| $s$ | Intervention Save / Conversion Rate | `15%` (`0.15`) | `20%` (`0.20`) | `25%` (`0.25`) | `20%` (`0.20`) | **ASSUMPTION (Benchmark `[7]`, `[8]` & Tutorial PDF)** — Tutorial uses `s = 20%`; we bracket `15%`–`25%` and test `12%`–`28%` in the tornado chart. |
| $c$ | Offer + Contact Cost per Targeted Customer | `2.50 MU` | `7.50 MU` | `10.00 MU` | `7.50 MU` | **ASSUMPTION (Operational Tiering)** — Paid on **all $n = 10,000$ targeted accounts** (including false positives). Covers outbound agent call + conditional bundle/credit cost. |
| $s^*$ | Break-Even Save Rate ($c / (p_{\text{adj}} \cdot V)$) | **`7.15%`** | **`7.01%`** | **`5.82%`** | `2.82%` | **DERIVED** — Minimum conversion rate required for net campaign value to equal `0 MU`. |

---

## 2. Summary of Estimated Financial Impact at $k = 10\%$ ($n = 10{,}000$ Targeted Accounts)

$$\text{Net Impact (MU)} = \underbrace{n \cdot p_{\text{adj}}(k) \cdot s \cdot (\text{ARPU} \cdot \text{margin} \cdot H)}_{\text{Gross Retained Margin}} \;-\; \underbrace{n \cdot c}_{\text{Total Campaign Cost (incl. False Positives)}}$$

| Scenario | Real Prior $\pi_r$ | Re-Based Precision $p_{\text{adj}}$ | True Churners Reached | Saved Customers ($n \cdot p_{\text{adj}} \cdot s$) | Gross Margin Saved (MU) | Campaign Cost (MU) | **Estimated Net Impact (MU)** | **ROI (%)** | **Break-Even $s^*$** |
|---|---|---|---|---|---|---|---|---|---|
| **Conservative** | `5.0%` | `18.59%` | `1,859` | `278.8` | `52,418 MU` | `25,000 MU` | **`+27,418 MU`** | `+109.7%` | `7.15%` |
| **Base Case** | `10.0%` | `32.53%` | `3,253` | `650.6` | `213,938 MU` | `75,000 MU` | **`+138,938 MU`** | `+185.3%` | `7.01%` |
| **Optimistic** | `10.0%` | `32.53%` | `3,253` | `813.2` | `429,786 MU` | `100,000 MU` | **`+329,786 MU`** | `+329.8%` | `5.82%` |
| *Unadjusted Sample (Why Re-basing Matters)* | *`49.56%`* | *`81.00%`* | *`8,100`* | *`1,620.0`* | *`532,708 MU`* | *`75,000 MU`* | *`+457,708 MU` (3.3× overstated)* | *`+610.3%`* | *`2.82%`* |

---

## 3. Lane 2 Pilot Sizing (Pre-300-Day Handset Refresh & Month 8–9 Renewal Check)

- **Eligible Cohort in $N = 100{,}000$:** Subscribers with `240 <= eqpdays <= 300` and `rev_Mean >= 30 MU` $\Rightarrow$ **`8,815` subscribers** (`cohort ARPU = 66.91 MU`, 8-month gross margin $V = 374.70\text{ MU}$).
- **90-Day Randomized Pilot Design:**
  - **80% Treatment (`7,052` accounts):** Receive proactive trade-in / installment upgrade voucher + 12-month renewal bonus (`c = 4.00 MU` expected cost per account).
  - **20% Holdout Control (`1,763` accounts):** Receive standard business-as-usual treatment to measure true causal uplift.
- **Expected Pilot Return (Under Stated Assumptions):**
  - Assuming the `300`-day transition represents a `5.5 pp` re-based excess churn hazard and the early refresh closes `25%` of that gap (`97.0` incremental saves), the 90-day pilot protects **`36,333 MU`** in gross margin against **`28,208 MU`** in campaign cost, yielding **`+8,125 MU` net pilot value** while establishing causal ground truth before full rollout.

---

## 4. Mandatory One-Paragraph Honest Impact Statement (Task T8.8 / PRD §9.5)

> **Estimated Impact Statement:** Across an active base of $N = 100{,}000$ subscribers, targeting the top $10\%$ highest-risk accounts ($n = 10{,}000$) using our regularized XGBoost ranking model (`M5`, held-out test $\text{ROC-AUC} = 0.7011$, sample top-$10\%$ precision $= 81.0\%$, prior-shifted precision $= 32.53\%$ at a realistic $10\%$ churn base rate and $18.59\%$ at a $5\%$ base rate) is **estimated under stated assumptions** to retain **279 to 813 subscribers** and generate **+27,418 MU (Conservative) to +138,938 MU (Base Case) to +329,786 MU (Optimistic)** in net retained contribution margin after deducting all outreach and incentive costs across both true and false positives (compared to an unadjusted sample estimate of +457,708 MU if case-control oversampling were ignored). Because observational billing logs cannot prove the causal conversion rate ($s$) of a new retention offer in advance, deployment is gated on a **90-day randomized 80/20 holdout pilot** whose break-even conversion threshold is just **$s^* = 7.01\%$** in the Base Case.
