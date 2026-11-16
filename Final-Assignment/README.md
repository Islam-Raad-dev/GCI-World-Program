# Customer Churn Prediction & Retention Strategy

End-to-end machine learning project for a telecom company (anonymized as **"Company A"**): predict which subscribers will churn, then decide with numbers whether a retention campaign is actually worth running.

Final project of the **GCI World Program** (Matsuo-Iwasawa Lab, University of Tokyo, 2026).

---

## Overview

A telecom operator loses subscribers every month, and a retention offer costs money even when it is sent to someone who would have stayed anyway. So the question is not only *"who will leave?"* but also *"is it profitable to spend on this segment?"*

This project answers both:

1. **Predict** the probability that each customer churns within 31–60 days after the observation date.
2. **Explain** the behavioral patterns behind churn (device age, subscription tenure, usage drop, bill shock).
3. **Convert** predictions into money: profit model, break-even analysis, sensitivity analysis.
4. **Recommend** a safe rollout: a narrow pilot plus a 90-day A/B test to measure the real effect of an offer.

## Key Results

| Item | Result |
|---|---|
| Data | 100,000 customers (`98,385` active lines; `1,615` silent `0-MOU` SIMs excluded), 98 raw features + 28 engineered features (`125` production cols, `ethnic` excluded) |
| Final model | XGBoost M5 (tuned, regularized) |
| ROC-AUC | **~0.703** (5-fold CV: `0.7017 ± 0.0015`, held-out 30% test: **`0.7028`**, test acc: `0.6427`, `ECE = 0.0083`) |
| Improvement over logistic regression | **`+4.1 pp`** Test ROC-AUC (`0.7028` vs. `0.6614`) |
| Targeting power | Top 10% highest-risk customers churn at **`81.4%`** raw (**`3.31×`** lift / `33.1%` at `10%` prior; **`3.80×`** / `19.0%` at `5%` prior; **`4.17×`** / `8.3%` at `2%` prior) |
| Estimated Base net margin (`k=10%`) | **`+83,276 MU`** at `10%` prior (`+90,940 MU` at `k*=15%`, `s*=9.80%`); **`+13,659 MU`** at `5%` (`+23,730 MU` at `k*=3%`); **`-38,906 MU`** at `2%` (`+3,590 MU` at `k*=1%`) |
| Break-even | Campaign at `k=10%` is profitable above **`4.17%`** (`~4.2%`) true churn prior |
| Recommendation | Exclude `1,615` silent SIMs; run Top 1–2% Lane 1 pilot + **Lane 2** 90-day 50/50 A/B pilot across **`13,008`** non-overlapping (`97.0%`) pre-cliff lines (`+4,691 MU` pilot / **`+30,510 MU`** at scale) |

### Main Findings

- **Device age threshold:** churn jumps by **`+23.83 pp`** (`95%` bootstrap CI `[+22.05, +25.63] pp`) once the phone passes 300 days, validated with a local regression discontinuity check (`+23.22 pp`) and consistency across all 19 areas and 8 credit classes.
- **First-year cliff:** churn drops to `29.25%` at month 9 and spikes to **`64.57%` in month 11** of the subscription, consistent with a first-year contract or offer ending.
- **Usage collapse & silent SIMs:** recent 3-month voice drop (`mou_ratio_3m`, `-28.53e-3` perm drop) is the #1 driver; **`1,615` silent `0-MOU` SIMs** (`1,120` in train at `78.48%`) churn at **`79.81%`** while generating just `0.62%` of revenue and are excluded before targeting.
- **Missing data is informative:** missing `change_mou` carries **`76.09%`** churn, so native XGBoost missingness routing and indicator flags were preserved instead of blind median imputation.
- **Fairness:** excluding `ethnic` shifts Test AUC by `-0.0007` (`0.7028` vs. `0.7035`, `CV: 0.7017` vs. `0.7030`), and dropping all `8` socioeconomic proxies yields `0.7023` Test AUC (`CV: 0.7020`).

> These are observational patterns, not proof of causation. This is why the plan includes a randomized A/B test.

## Methodology

| Stage | What was done |
|---|---|
| Data loading | Merged `Client.csv` and `Record.csv` on customer ID (validated one-to-one) |
| Data audit | Missing values, impossible values, outliers, duplicated columns, documentation vs. reality |
| EDA | Churn rate by bins with Wilson confidence intervals, heatmaps, robustness tests |
| Split | Stratified 70/30 train/test split (seed 42); all decisions made on training data only |
| Feature engineering | 28 behavioral features (thresholds, ratios, shares, missing flags) with a per-feature leakage check |
| Pipeline | Leakage-safe scikit-learn `Pipeline` + `ColumnTransformer` |
| Modeling | 7 models (M0–M6) compared with stratified 5-fold cross-validation |
| Evaluation | ROC-AUC, Precision@k, Lift@k, calibration (ECE, Brier), permutation importance, PDP, ablation |
| Recalibration | Label-shift correction (Saerens et al., 2002) because the sample has ~49.6% churners while real telecom churn is far lower |
| Financial model | Net profit = n × p_adj × s × V − n × c, break-even rate, scenarios, tornado sensitivity |
| Experiment design | 90-day A/B test with a holdout group and a clear expansion rule |

### Model Ladder

| ID | Model | CV AUC | Test AUC (Acc) |
|---|---|---|---|
| M0 | Majority-class baseline | `0.5000 ± 0.0000` | `0.5000` (`50.44%`) |
| M1 | Logistic Regression + 28 features | `0.6603 ± 0.0040` | `0.6614` (`61.76%`) |
| M2 | Decision Tree (depth 4) | `0.6400 ± 0.0030` | `0.6401` (`59.58%`) |
| M3 | XGBoost on raw 97 features (`no ethnic`) | `0.6924 ± 0.0018` | `0.6925` (`63.55%`) |
| M4 | XGBoost + 28 engineered features | `0.7000 ± 0.0016` | `0.6992` (`63.98%`) |
| **M5** | **XGBoost tuned (final)** | **`0.7017 ± 0.0015`** | **`0.7028`** (`64.27%`) |
| M6 | LightGBM + 28 features | `0.7001 ± 0.0020` | `0.7012` (`64.20%`) |

M5 was selected using 5-fold cross-validation (`0.7017 > 0.7001`), not the test set, to keep the held-out estimate honest (`7.92 pp` train–test accuracy gap). All values match the saved Google Colab execution (`Python 3.13.18`); re-running locally in another library environment may change the last digits slightly.

### Financial Assumptions

The data contains no cost, margin, or offer-success information, so these are **explicit assumptions**, not measured values:

| Parameter | Base value |
|---|---|
| Average ARPU (from data) | `58.72 MU` (median `48.20 MU`) |
| Margin | `70%` |
| Time horizon | `6 months` |
| Offer save rate (`s`) | `20%` (`3.0 MU` assumed for Lane 2 pilot cost `c_lane2`) |
| Offer cost per customer (`c`) | `8 monetary units (MU)` |
| Customer value (`V`) | `ARPU × margin × months = 246.62 MU` |

Because the outcome depends strongly on the real churn rate in the market (`+83,276 MU` at `10%` prior, `+13,659 MU` at `5%` prior, and `-38,906 MU` at `2%` prior when targeting `k=10%`), the project reports scenario bands and optimal depth (`k*=1%` -> `+3,590 MU` at `2%` prior; `k*=15%` -> `+90,940 MU` at `10%` prior) rather than a single point estimate.

## Repository Structure

```
Customer_Churn_Prediction_Project/

├── dataset/
│   ├── Client.csv
│   ├── Record.csv
│   └── Company _A_ Dataset Overview.docx
├── docs/
│   └── UNDERSTANDING_AR.md          # Detailed project guide (Arabic)
├── notebooks/
│   └── churn_prediction.ipynb       # Full analysis, modeling
├── outputs/
│   ├── figures/                     # Charts used in the report
│   ├── models/
│   │   └── final_xgb_m5_pipeline.joblib
│   └── tables/
│       ├── experiment_log.csv
│       └── test_predictions.csv
├── reports/
│   ├── Project-overview.pdf         # Final 15-slide presentation
│   └── references.txt
├── README.md
├── requirements.txt
```


## Tech Stack

- **Language:** Python 3.13.18 (Google Colab)
- **Data:** pandas 2.2.3, NumPy 2.4.6
- **Modeling:** scikit-learn 1.6.1, XGBoost 3.4.1, LightGBM 4.6.0
- **Statistics:** SciPy 1.16.3
- **Visualization:** Matplotlib 3.10.0
- **Persistence:** joblib 1.6.0
- **Environment:** Google Colab / Jupyter Notebook

## Data

The data comes from the GCI World 2026 course material: an anonymized telecom dataset (`Client.csv` with 50 columns and `Record.csv` with 51 columns, 100,000 customers each). It is **not** data from an Iraqi or any specific real company, and it is used here for educational purposes only. Column names closely resemble the public Cell2Cell churn dataset, but this was not confirmed by the course. See `dataset/Company _A_ Dataset Overview.docx` for the official description.

## Limitations

- The sample is nearly balanced (~49.6% churners), which is unrealistic; this is handled with recalibration, but the real churn rate is still an assumption.
- Financial results depend on assumed margin, save rate, and offer cost, which are not in the data.
- Patterns such as the 300-day threshold are correlational. Only the A/B test can prove that an offer actually retains customers.
- ROC-AUC of ~0.70 is typical for noisy human-behavior data: the model ranks customers usefully, but it does not predict each individual with high accuracy.

## Disclosure

AI assistants were used during development, as permitted by the program, and are disclosed in the references. All results and decisions in this repository were reviewed and are understood by the author.
