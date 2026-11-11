# PRD — GCI World 2026 Final Assignment
## "Company A" Telecom Churn — Data-Driven Business Proposal (PoC)

> **Audience:** an autonomous coding/research agent (Google Antigravity, Gemini) that will build the *entire* project: data audit, EDA, market research, modeling, business-impact model, slides (PDF), reproducible notebook, references, and a human-understanding pack.
> **Owner / submitter:** Islam Raad (AI Engineering student, University of Mosul, Iraq). He reviews and fully understands every step before submitting, and he is the only person who submits on Omnicampus.
> **Companion file:** `tasks.md` (ordered, checkable work breakdown). This PRD says *what and why*; `tasks.md` says *what to do next*.
> **Document date:** 11 Nov 2026. **Hard deadline:** Saturday **28 Nov 2026, 11:30 UTC (14:30 Iraq time, UTC+3)**. No late submission. Re-submission before the deadline is allowed (the last one is graded; all files must be re-attached each time).

---

## 0. How the agent must work (read first)

### 0.1 Source-of-truth precedence
If two sources disagree, follow this order:
1. `README.docx` (official assignment rules) 
2. `final_assignment_tutorial.pdf` and `tutorial.ipynb` (official walkthrough; a *reference, not a template*)
3. `ENG_Company_A_Dataset Overview.docx` (column descriptions; some are vague or wrong — see §5.4)
4. The actual data in `telecom/Client.csv` and `telecom/Record.csv` (ground truth for any number)
5. `GCI_Final_Assignment_Guide.pdf` (a prior analysis written by Claude. Its numbers are **calibration hints only**; every number used in the deliverables must be **recomputed by you** from the CSVs.)

### 0.2 First actions
Before anything else, read all five documents in the workspace. Tooling hints: `pandoc README.docx -t plain`, `python-docx`, `pdftotext -layout`, `jupyter nbconvert --to script`. If a requirement in those files is not reflected in this PRD, **the file wins**; log the difference in `docs/decision_log.md`.
If you need any information that is not in this PRD, **look for it in those files first**, then in the data, then on the web (only for market/external facts). Do not guess.

### 0.3 Non-negotiable integrity rules
1. **Never fabricate.** Every metric comes from code you ran and whose output you read. Every external number comes from a source you actually opened (URL fetched, publication date and access date logged). If you cannot verify a fact, **do not use it**.
2. **Single source of truth for numbers:** the notebook writes `outputs/results.json`; the slide builder reads from it; `scripts/verify_numbers.py` asserts that numbers printed on slides equal `results.json`.
3. **No data leakage** between train/test (see §8). The 30% test split is used for final reporting only.
4. **Honest framing.** This is a *course project* (not a real engagement). Financial impact is an *estimate under stated assumptions*, never a promise. Claims about causes are *hypotheses* unless tested.
5. **Cite everything borrowed** (data, methods, figures, text). Direct quotation must stay far below 40% of final content (target: ≈0%; paraphrase and cite).
6. **Privacy:** do not upload the CSVs anywhere; do not paste data rows into external tools; no API keys or personal data in the notebook; do not publish the data or slides publicly (the license is not stated).
7. **Reproducibility:** fixed `random_state=42`, pinned `requirements.txt`, notebook runs top-to-bottom with *Restart & Run all* without errors.
8. **Do not block on the human.** The human may be unavailable. For non-essential choices pick the default stated here, log it in `docs/decision_log.md`, and continue. Only three things require the human: (a) the exact **Omnicampus account name** (used in file names), (b) the **AI chat links / disclosure answers**, (c) the **actual submission click**.
9. **Work in small verified steps:** run → read the output → decide → log. Keep `docs/work_log.md` (timestamped, 1–3 lines per step).

---

## 1. Context and objective

### 1.1 Scenario (official)
The student is a new *Associate* at an IT-consulting firm. The sales team won a **Proof-of-Concept (PoC)** from **Company A**, an anonymous **wireless telecom operator** with data on ~100,000 customers and **no machine-learning team**. The task: analyze the data (EDA), build **at least one ML model**, identify the client's **core problem** from evidence and market analysis, and write a **data-driven business proposal** with a **quantified estimated impact** (revenue increase, cost saving, or risk reduction).

### 1.2 The single most important idea
> **The model is a tool that supports a recommendation; it is not the recommendation.** A deck that says "we built a model with X% accuracy" is a technical report and fails requirement #1. The deliverable must answer: *What is the problem? Why do we believe it (data + market evidence)? What should the company do, for whom, and when? How much do we expect to gain or save, under which assumptions, and how sure are we?*

### 1.3 Product goal
Produce a submission that is (a) compliant with every official requirement, (b) analytically honest and rigorous, (c) understandable by a non-ML manager, (d) visually professional, (e) fully reproducible, and (f) **fully understood by Islam** (he must be able to explain each slide, each notebook cell, each number, and each assumption in an interview).

### 1.4 Non-goals
- Maximizing model accuracy (explicitly *not* the grading goal; do not spend more than ~20 minutes on tuning).
- Deploying anything; building dashboards/apps.
- Using external customer data; scraping private data.

---

## 2. Deliverables and hard constraints

### 2.1 Files to submit on Omnicampus (final course page; the README says the "170 course" page — Islam confirms the live link)
| # | File | Rules |
|---|---|---|
| 1 | **Slides PDF** `<ACCOUNT_NAME>.pdf` | **≤ 15 slides total** (including title, section dividers if any, references). Extra slides may be ignored. **≤ 10 MB.** Created in any tool; exported to PDF. |
| 2 | **References** (text pasted into the Omnicampus "References" field) → keep as `references.txt` | One link/reference per line. **Must match** what the slides cite. **If any generative AI was used, paste the AI chat link(s) here.** |
| 3 | **Notebook** `<ACCOUNT_NAME>.ipynb` (or `.py`, or a `.zip` if multiple files) | Reproducible analysis; runs end-to-end; contains the EDA, features, models, evaluation, impact calculation. |

- `<ACCOUNT_NAME>` is Islam's Omnicampus account name → **ask him once** at the end of Phase 0; until then use the placeholder `ACCOUNT_NAME` and keep one variable in `config.py`.
- Also complete the **AI-usage survey** on the submission page (draft answers in §13; Islam answers honestly himself). The survey does not affect the grade but the citation/reference rules still apply.
- **Do not include `Client.csv` / `Record.csv`** in the submission package.

### 2.2 Grading — the 7 requirements (all must be satisfied with *visible evidence*)
| # | Requirement | How this project proves it |
|---|---|---|
| R1 | Business **proposal**, not a technical report | A "Recommendation" slide whose title *is* the decision, plus an "Estimated impact" slide with numbers. |
| R2 | Based on **real EDA of this data** (challenges specific to the client) | 4–6 purpose-built charts and 3 written hypotheses from Company A's data (not generic claims). |
| R3 | **≥ 1 ML model**; model name, metric, result **written as text** on the slide; why chosen; how built; what learned | Experiments table on a slide **as live text** (not an image only). |
| R4 | **External sources and market analysis, documented** | ≥ 8 verified sources; footnote tags on slides; matching reference list. |
| R5 | Understandable to a **manager with no ML background** | Plain-language headlines; a simple diagram of how the model works; jargon defined. |
| R6 | **Multiple charts**, not raw numbers | One purposeful chart per key idea. |
| R7 | **Logical consistency** | One thread: problem → analysis → model → recommendation → impact; each slide answers the question left by the previous one. |

Official notes: if a model is clearly **unsuitable** for the data/task, R3 does not count — so match model to task (e.g., never use classification for a continuous target). The README prefers comparing **more than one model**.
Success tiers (from the tutorial's recap slide): *Completed* requires submitting the Final Assignment. Honors/Outstanding depend on overall course rankings; **no exact formula is published**, so the only rational strategy is meeting all 7 requirements at high quality.

### 2.3 Citation & AI rules (from README/FAQ)
- Cite any external data, method, figure or text — even paraphrased. Uncited borrowing may count as plagiarism.
- Additional public data is allowed but must be cited and its effect on the proposal explained.
- Short cite or footnote on the slide itself **and** the same item in the reference list; the two lists must match.
- AI-generated output is not "the student's own work" by itself; the chat link is mandatory in references; the organizers confirmed on Slack (via Islam) that full AI use is acceptable **as long as the student understands everything he submits**. That is why §14 (Human-Understanding Pack) is a required deliverable.

---

## 3. Environment and workspace

### 3.1 Workspace layout (as it exists on Islam's machine)
```
~/Projects/Final Assignment/
├── telecom/
│   ├── Client.csv                      # 100,000 rows x 50 cols  (customer/device/demographics/lifetime totals)
│   └── Record.csv                      # 100,000 rows x 51 cols  (monthly usage/quality + target `churn`)
├── ENG_Company_A_Dataset Overview.docx # column descriptions (some wrong/missing)
├── final_assignment_tutorial.pdf       # official tutorial slides
├── GCI_Final_Assignment_Guide.pdf      # prior analysis/guide (calibration only)
├── README.docx                         # official rules
└── tutorial.ipynb                      # official reference notebook
```

### 3.2 Folders the agent must create
```
~/Projects/Final Assignment/
├── prd.md, tasks.md                    # these two files (do not edit; propose changes in docs/decision_log.md)
├── config.py                           # DATA_DIR, SEED=42, ACCOUNT_NAME, paths, palette
├── requirements.txt                    # pinned versions
├── notebooks/
│   ├── 00_explore_scratch.ipynb        # free exploration (not submitted)
│   └── ACCOUNT_NAME.ipynb              # the clean, submitted notebook
├── src/                                # helper modules (features.py, evaluate.py, economics.py, plotting.py)
├── scripts/                            # build_slides.py, verify_numbers.py, export_pdf.sh, check_pdf.py
├── outputs/
│   ├── figures/                        # PNG (≥200 dpi) + SVG for every chart used
│   ├── tables/                         # CSV of every table used
│   ├── results.json                    # SINGLE SOURCE OF TRUTH for numbers on slides
│   └── models/                         # saved final model (joblib) — not submitted
├── research/
│   ├── sources_log.md                  # every external source: title, publisher, date, URL, access date, what was used
│   └── notes/                          # short extracts/paraphrases per source
├── slides/
│   ├── src/ (HTML/CSS/assets)          # slide source
│   └── build/ACCOUNT_NAME.pdf
├── docs/
│   ├── decision_log.md, work_log.md, assumptions.md
│   ├── UNDERSTANDING_GUIDE_AR.md       # Arabic explanation for Islam (see §14)
│   ├── INTERVIEW_QA.md, speaker_notes.md, numbers_cheatsheet.md
│   ├── ai_disclosure_template.md
└── submission/                         # final package (3 files + references.txt)
```

### 3.3 Software
- Python ≥ 3.10; `pandas, numpy, scikit-learn, xgboost, matplotlib, seaborn, scipy`; optional `lightgbm`, `shap` (guard imports with a pip-install cell and a fallback so the notebook still runs without them). Slide build: `playwright` (Chromium) or `weasyprint`; `pdftoppm`/`PyMuPDF` for visual QA; Ghostscript for PDF compression if needed.
- The notebook must also run on **Google Colab** (the tutorial's environment): use `DATA_DIR` auto-detection: local `telecom/` → Colab `/content/drive/MyDrive/Final Assignment/telecom/`. Keep notebook runtime under ~10 minutes.
- Keep the *submitted notebook* free of web calls. External facts live in slides/`research/`, with any constants used in code placed in a clearly labelled **assumptions cell** that cites its source.

---

## 4. Success criteria (definition of done)

The project is done when **all** of these are true:
1. All 7 requirements (§2.2) pass the self-review checklist in `tasks.md` Phase 14.
2. `Restart & Run all` of `ACCOUNT_NAME.ipynb` finishes without errors; `results.json` regenerates identically (same seed).
3. `verify_numbers.py` reports **0 mismatches** between slides and `results.json`.
4. PDF: ≤ 15 pages, ≤ 10 MB, fonts embedded, no text overflow/overlap in the rendered PNG check of every page, all numbers readable at 100% zoom.
5. Every source on a slide appears in `references.txt` and vice-versa; every URL opened successfully when logged.
6. The Human-Understanding Pack (§14) exists and covers every slide, every notebook section, every number and assumption.
7. The impact calculation is reproducible from a short assumptions table and includes scenarios and sensitivity analysis, plus a **realism adjustment for the 49.6% churn rate** (§9.4).

---

## 5. Data specification

### 5.1 Files and structure (verified by prior analysis; re-verify and log)
- **`Client.csv`**: 100,000 × 50 → `Customer_ID` + 49 features (21 text/`object`, 28 numeric).
- **`Record.csv`**: 100,000 × 51 → `Customer_ID` + 49 features (all numeric) + target **`churn`**.
- **Join key:** `Customer_ID` (the Overview doc and some notes call it `ID_Customer`; **use the actual column name** found in the files). 1-to-1 perfect match, no duplicates, IDs 1000001–1100000, same order in both files.
- **Merged** (inner join): **100,000 × 100** (confirmed in Islam's notebook run). After dropping the ID: 99 columns (98 features + target).
- **Target `churn`:** 1 = customer left within **31–60 days after the observation date**. Distribution ≈ **49.56% churn (49,562) vs 50.44% stayed (50,438)**. Real telecom churn is far lower (the tutorial cites ~5–10%) → the sample looks **balanced/resampled** (reason undocumented). Consequence: raw precision/recall and any financial estimate computed directly on this sample are **overstated**; see §9.4.
- **Tenure:** `months` (in `Record.csv`, *not* `Client.csv`) ranges ~6–61 (median ≈ 16); nobody under 6 months. → the sample contains only customers with ≥ 6 months of service.
- **Always print `df.columns` after merging** — never assume which file a column lives in.

### 5.2 Column map (names are indicative; verify against the real header)
| Group | Source | Columns (examples) |
|---|---|---|
| Account | Client | `actvsubs`, `uniqsubs`, `new_cell`, `crclscod` (credit class), `asl_flag` |
| Device | Client | `eqpdays` (device age in days), `hnd_price`/`price_hnd`, `models`, `phones`, `refurb_new`, `hnd_webcap`, `dualband` |
| Lifetime history | Client | `totcalls, totmou, totrev, adjrev, adjmou, adjqty, avgrev, avgmou, avgqty`, `avg3*`, `avg6*` |
| Tenure | Record | `months` |
| Monthly revenue/usage | Record | `rev_Mean, mou_Mean, totmrc_Mean, da_Mean, ovrmou_Mean, ovrrev_Mean, vceovr_Mean, datovr_Mean, roam_Mean, change_mou, change_rev` |
| Call quality | Record | `drop_vce_Mean, drop_dat_Mean, blck_vce_Mean, blck_dat_Mean, unan_vce_Mean, unan_dat_Mean, plcd_*, recv_*, comp_*, attempt_Mean, complete_Mean, drop_blk_Mean` |
| Customer care / patterns | Record | `custcare_Mean, ccrndmou_Mean, cc_mou_Mean, callwait, callfwdv, threeway, inonemin`, peak/off-peak columns, `iwylis_vce_Mean`, `mou_*`-family |
| Demographics | Client | `prizm_social_one, area, truck, rv, ownrent, lor, dwlltype, marital, adults, infobase, income, numbcars, HHstatin, dwllsize, forgntvl, ethnic, kid0_2 … kid16_17, creditcd` |
| Target | Record | `churn` |

### 5.3 Data-quality facts to verify (calibration hints from the prior analysis — recompute!)
- **Missing values:** `numbcars` ≈ 49%; `dwllsize`, `HHstatin`, `ownrent`, `dwlltype` ≈ 32–38%; `lor`, `income`, `adults`, `infobase` ≈ 22–30%; `hnd_webcap`, `prizm_social_one` ≈ 7–10%; `avg6*` ≈ 2.8%; a block of ≈ 1.7% (≈1,732 rows) is missing in the *same rows* across many demographic columns; `change_mou/change_rev` ≈ 0.9% missing and those rows churn ≈ 76% → **missingness can carry signal**; check churn rate of "missing vs present" before dropping anything.
- **Near-duplicate columns** (Spearman > 0.97, about 20 pairs; e.g., `totcalls`~`adjqty`, `totmou`~`adjmou`, `totrev`~`adjrev`, `attempt_Mean`~`plcd_vce_Mean`, `comp_vce_Mean`~`complete_Mean`). Dropping 10 of them did not change AUC (≈0.696) → simplify only for explainability.
- **Near-empty columns** (≥ 97% zeros): `callfwdv`, `recv_sms_Mean`, `blck_dat_Mean`, `drop_dat_Mean`, `unan_dat_Mean`. Many data-call columns are 85–93% zeros.
- **Extreme/odd values:** `totcalls`/`totmou` very skewed; `uniqsubs` max ≈ 196 (a handful of outliers); `rev_Mean` has ≈ 5 negative values; `eqpdays` has **negative values (~133 rows)**; `totmrc_Mean` has ~23 negatives; `price_hnd` has only ~17 distinct values (price tiers, not continuous). Expect `RuntimeWarning` from `log1p` on negatives — **handle explicitly** (clip, flag, or exclude — and document).
- **Documentation vs data:** `change_mou` / `change_rev` are described as *percent change*, but ≈ 22.6% of `change_mou` values are < −100 (impossible for a percentage) and they correlate ≈ 0.90–0.94 with `mou_Mean − avg3mou` / `rev_Mean − avg3rev` → treat as an **absolute difference vs. the previous 3-month average**, and label it "change in minutes/revenue" on slides, not "%". `recv_sms_Mean`, `iwylis_vce_Mean` have no description (the latter behaves like incoming wireless-to-wireless calls).
- **Currency/units:** no currency is documented → write **"monetary units (MU)"**.

### 5.4 Reference results to calibrate the pipeline (re-run; do not copy blindly)
Tutorial config (LabelEncoder on text columns, `XGBClassifier(n_estimators=300, learning_rate=0.05, max_depth=6, eval_metric='logloss', random_state=42)`, 70/30 stratified split, seed 42):
- **Accuracy ≈ 0.636** on the 30,000-row test set (Islam's run: **0.6357**). Majority-class baseline ≈ 0.504.
- **AUC ≈ 0.694**; train accuracy ≈ 0.735 (visible overfitting); precision ≈ 0.64, recall ≈ 0.65.
- If you get ≥ 0.80 accuracy → suspect leakage; if ≈ 0.50 → suspect a broken join.
- 5-fold CV AUC ≈ 0.697 (tutorial encoding) → ≈ 0.7015 with ~17 engineered features. Hyper-parameter tuning added ≈ 0. Logistic regression ≈ 0.657 AUC. Fold standard deviation ≈ 0.002–0.004 → differences below ~0.003 are noise.
- Prior top-k targeting table (best model, out-of-sample): top 5% precision ≈ 85%, top 10% ≈ 80% (lift ≈ 1.6), top 20% ≈ 74%, top 30% ≈ 70%, top 50% ≈ 64%; bottom 10% churn ≈ 18%. (Sample base rate 49.6%.)
- Feature importance (gain) is **flat** (top feature ≈ 4.6%): signal is spread across many weak features → modest AUC is expected; do not oversell.

### 5.5 Patterns found by the prior analysis — treat as **hypotheses to test**, not facts
1. **Device-age threshold near 300 days (`eqpdays`)**: churn ≈ 37–38% for devices ≤ 300 days, jumping to ≈ 55% just above 300 and peaking ≈ 64% around 321–340 days. Possible causes: device-upgrade eligibility, end of a ~300-day commitment/promotion, or a sampling artifact (undeterminable from the files).
2. **Tenure pattern around months 10–11**: churn falls to ≈ 29% at month 9, rises to ≈ 40% at month 10, peaks ≈ 65% at month 11, ≈ 62% at 12, then declines slowly to ≈ 47% for 37+ months. Possible causes: promo/contract expiry (hypothesis).
3. **Entanglement:** nobody with ≤ 9 months tenure has a device older than 300 days (new subscribers have new devices) → the two effects overlap; separate them (e.g., compare within tenure ≥ 10 months only).
4. **Usage collapse segment:** customers with `mou_Mean == 0` (~1,600) churn ≈ 80%; `mou_Mean ≤ 10` ≈ 65%; missing `change_mou` ≈ 76%. Small, high-precision group; check how much revenue it represents (zero-usage customers' mean revenue is far below average).
5. **Revenue does not separate churners from stayers** (mean `rev_Mean` ≈ 58.2 churners vs ≈ 59.2 stayers) → "valuable customer" cannot be defined by revenue alone.
6. **Customer-care calls vs churn is counter-intuitive** (more calls → *less* churn). Do not claim "calls retain customers"; test explanations (e.g., engaged customers contact care; disengaged ones leave silently).
7. **`ethnic`** has strong group differences — **do not use it for targeting** (fairness/legal risk); report this as an ethical choice (§8.7).
8. Demographics (income, adults, marital status) are weak (churn 48–51% across groups). `infobase` showed up in importance — check its meaning before relying on it.

---

## 6. Analytical strategy (default storyline; the agent may revise only at the Decision Gate, Task 5.x)

### 6.1 Candidate problem framings (score them in a decision matrix: evidence strength, actionability, measurability, risk, fit with market evidence)
| Option | Target / task | What data supports | Weaknesses |
|---|---|---|---|
| **A. Risk-ranked retention (default core)** | `churn` / binary classification, rank customers | Target exists; model beats baseline; top-decile precision ≫ base rate | Weak overall signal (AUC ≈ 0.70); unrealistic base rate |
| **B. Lifecycle triggers (default complement)** | device-age and tenure thresholds → timed offers | Sharp, interpretable jumps | Cause unknown; may be sampling artifact; no offers/contract columns |
| C. Early warning on usage decline | small segment with ~0 usage | Very high churn rate | Small, low revenue; may have already left |
| D. Value-at-risk | P(churn) × customer value | Revenue does not separate classes → value-ranking is useful | Needs lifetime-value assumptions |
| E. Segmentation (clustering) | unsupervised | Clear device/tenure/usage clusters | Segmentation alone does not say what to do |

### 6.2 Recommended default proposal (to be confirmed or adjusted by evidence)
**"A two-lane retention program for Company A": (Lane 1) a monthly *risk score* that ranks customers so the retention team contacts only the riskiest k% (k chosen by net value, not by habit); (Lane 2) *lifecycle triggers*: proactively offer a device refresh before devices cross ~300 days, and a loyalty check before the tenure cliff (~month 9–10) — each launched as a small controlled pilot with a holdout group to measure real incremental effect.**
- Problem sentence (draft): *"Company A is losing customers it could keep, but its retention spend is untargeted. Churn risk is concentrated in identifiable moments (aging devices, early-tenure cliff, collapsing usage). We propose to score customers monthly and trigger timed, value-aware retention offers, validated by an A/B pilot."*
- Task type: supervised binary classification (+ rule-based lifecycle triggers derived from EDA).
- Who acts: the retention/CRM team; **action:** proactive contact/offer for top-k% by *value-at-risk*; device-refresh offer in the window before ~300 days.
- If the thresholds **do not replicate** under robust checks (§8.2) or the artifact explanation dominates, drop Lane 2's causal framing, keep it as "monitoring hypotheses" and make Lane 1 + value-at-risk the core. Log the decision.

### 6.3 Market lens
The tutorial rewards a proposal "grounded in a local market you can describe concretely." Use **Iraq's mobile market** (operators such as Zain Iraq, Asiacell, Korek; regulator CMC — Communications and Media Commission; also ITU/GSMA/DataReportal) as the market lens. **State explicitly** that Company A is anonymous and the data are not claimed to be Iraqi; the market section explains why churn/retention economics matter in a competitive, saturated, prepaid-heavy market. Never invent Iraqi figures: use only verified, citable numbers; if local numbers are unavailable, say so and use regional/global ones with clear labels.

---

## 7. Market-research requirements (Phase 3)
Research questions (answer each in `research/notes/`, then compress to 1 slide + footnotes):
1. State of the (Iraqi/regional) mobile market: number of subscribers/penetration, major players, market share (verified, dated).
2. Local dynamics driving churn: competition/promotions, SIM multi-ownership, price/regulatory changes, network quality, new technology (e.g., 5G rollout/eSIM) — with sources.
3. Economics of retention vs acquisition (cost multiples cited from a credible source or paper).
4. Voluntary vs involuntary churn and which part a model can influence.
5. Handset-upgrade/commitment cycles and their relation to churn (supports the device-age hypothesis).
6. Typical retention-campaign success rates / offer costs (for scenario inputs; if not found, label as assumption).
7. Academic evidence on churn prediction in telecom (≥ 1–2 peer-reviewed or reputable papers) to justify tree-based models on tabular data.
Quality bar: ≥ 8 sources, mixing: regulator/ITU/GSMA/operator annual reports/credible media/academic papers; prefer primary sources; log publication + access dates; **open every URL** and verify the claimed fact appears; paraphrase, quote ≤ 15 words max and only if essential. Include 1 line on each slide footnote like `[3]` matching the reference list order.

---

## 8. Methodology requirements

### 8.1 Data audit & preparation
- Report shape, dtypes, missingness (table + chart), duplicates, ID uniqueness, outliers, negative values, near-duplicate pairs, zero-heavy columns, doc-vs-data discrepancies (§5.3). Log each decision (what, why, effect).
- **Encoding:** compare (a) tutorial `LabelEncoder` (turns `NaN` into the string `'nan'`; imposes artificial order) vs (b) a leakage-safe alternative (native categorical in XGBoost with `enable_categorical=True`, or ordinal/one-hot inside a `Pipeline`). Report whether it matters (prior result: negligible for trees).
- **Missing values:** trees handle `NaN` natively; for logistic regression impute (median) **inside the pipeline** and add missing-indicator flags. Add `n_missing_demographics` and a "demographics-missing" flag.
- **Negatives & outliers:** decide per column (clip at 0 for `eqpdays` negatives? flag them?), document why; log-transform only for plots/linear models, not required for trees.

### 8.2 EDA — required analyses (each needs a chart + 1-sentence finding)
1. Target balance and why accuracy is meaningful here but dangerous at 5% churn.
2. Missingness map + "churn when missing vs present" for top missing columns.
3. `eqpdays`: churn rate in narrow bins (≤ 25 days wide) — look for the ~300-day jump; **robustness:** bootstrap 95% CI of the jump (e.g., 260–300 vs 301–340), local linear fit each side (regression-discontinuity style), repeat within subgroups (tenure ≥ 10 months, `area`, `crclscod`), and **covariate-balance check** at 300 days (do `rev_Mean`, `hnd_price`, `months`, `mou_Mean` also jump? If many variables jump at 300, suspect a sampling artifact).
4. `months`: churn rate per month 6–61; locate the cliff; check overlap with `eqpdays` (2-D heat-map: churn by tenure bucket × device-age bucket, with counts).
5. Usage-collapse segments (`mou_Mean` = 0, ≤ 10, ≤ 30; missing `change_mou`): size, churn rate, revenue share, lifetime totals.
6. Revenue vs churn (distributions, medians by class) → implications for "customer value".
7. `custcare` calls vs churn → competing explanations (listed as hypotheses).
8. Quality metrics (dropped/blocked calls) vs churn; roaming/overage vs churn.
9. Demographics vs churn (and the ethical note for `ethnic`).
10. Correlation/duplicate analysis for explainability.
Output: **4–6 final EDA charts** for the slides (2 slides) + **3 written hypotheses** (full sentences: "Segment X is more likely to churn because Y; we test with Z"), ranked by actionability.

### 8.3 Feature engineering (hypothesis before experiment)
Write one line per feature in `docs/feature_dictionary.md`: *name, formula, business reason, leakage check*. Candidate list (create ≥ 10, keep only those that help or are explainable):
- `dev_age_gt_300` (threshold flag, only if EDA supports it), `tenure_le_9`, `tenure_10_12`, `eqp_per_tenure = eqpdays / (months*30)`.
- Usage trend: `mou_Mean / avg3mou`, `mou_Mean / avg6mou`, `rev_Mean / avg3rev`, `rev_Mean / avg6rev`, `change_mou`, `change_rev` (label as absolute change), safe division with epsilon.
- Quality: `drop_rate = drop_vce_Mean / plcd_vce_Mean`, `block_rate`, `unanswered_rate`, `completion_rate`.
- Economics: `recurring_share = totmrc_Mean / rev_Mean`, `overage_share = ovrrev_Mean / rev_Mean`, `roam_share`.
- Care: `custcare_per_call`, `has_custcare`.
- Zero-usage flags: `mou_zero`, `mou_le_10`.
- Missingness flags.
**Leakage rule:** every feature must be computable at prediction time, before the churn window; never derive from `churn` or from post-window data; target-encoding only inside CV folds.

### 8.4 Modeling protocol (strict)
- **Split:** stratified 70/30 on `churn`, `random_state=42` (identical to the tutorial for comparability). The **test set is touched only for final candidates** (record every touch in the experiment log; max 2).
- **Selection:** 5-fold stratified CV **on the training 70% only**. Thresholds/binning chosen in EDA must be derived from the **training split** (the prior analysis used all rows; avoid that optimism).
- **Models (compare ≥ 4):**
  - M0 majority-class baseline (`DummyClassifier`);
  - M1 Logistic Regression (pipeline: impute + scale + indicators) — interpretable baseline;
  - M2 shallow Decision Tree (depth ≤ 4) — **explanation device** (shows rules like "device > 300 days") not necessarily the final model;
  - M3 XGBoost with tutorial hyper-parameters (reproduction);
  - M4 XGBoost + engineered features;
  - M5 XGBoost tuned with a **time-boxed** randomized search (≤ 30 configs, ≤ 20 min), small depth, subsampling; report the (probably tiny) gain honestly;
  - optional M6 LightGBM/RandomForest if time permits.
- **Metrics:** primary **ROC-AUC** (ranking quality) and **precision/recall/lift at top-k%**; also accuracy (for tutorial comparability), precision, recall, F1, confusion matrix, calibration curve. Report CV mean ± std and final test score.
- **Over-fitting check:** train vs test gap (prior: 73.5% vs 63.6%). **Experiment log:** `outputs/tables/experiment_log.csv` (id, change, features, params, CV AUC ± std, accuracy).
- **Guardrail:** accuracy ≥ 75% or AUC ≥ 0.80 → investigate leakage before celebrating.
- **Choosing the final model:** best CV AUC; ties within 1 std → choose the simpler/more explainable one. The final deck names the model, metric and value **as text**.

### 8.5 Interpretation
- Feature importance by **gain** *and* **permutation importance** (on held-out data) — explain why gain ≠ weight (tutorial's point). Optional SHAP.
- **Partial-dependence / ICE** for `eqpdays` and `months` to see the thresholds in the *model's* eyes.
- **Ablation:** drop the top feature and retrain: does the story change (single strong signal vs. many correlated ones)?
- For each of the top 3–5 features: **can the company change it?** (lever vs. predictor) — device age and customer-care interactions are actionable; tenure/demographics are not (they help target, not intervene).
- Use cautious language: "indicator of risk", **not** "cause".

### 8.6 Evaluation for decisions
- Confusion matrix at a stated threshold (with cost interpretation: false positive = wasted offer; false negative = lost customer).
- **Top-k% table** (k = 1, 2, 5, 10, 15, 20, 30, 50): precision, recall, lift, number of customers; plot gain/lift curve.
- Calibration plot; if probabilities are used in money terms, calibrate (isotonic) on a validation fold.

### 8.7 Ethics and fairness
- Exclude `ethnic` from the final model; also test excluding other sensitive proxies (`income`, `marital`, `kid*`, `dwllsize`, …) and report the AUC change. State the decision on the Risks slide: *"We target on behavior, not on identity."*
- Report group-wise performance (e.g., by `area`, income band) as a sanity check if feasible.

---

## 9. Business-impact model (the core of the proposal)

### 9.1 Net impact formula
`Net = n × p_adj(k) × s × V − n × c`
- `n` = customers targeted = k × N (N = Company A's customer base; use 100,000 as the base, and state it).
- `p_adj(k)` = precision in the top-k% **after re-basing churn to a realistic rate** (see §9.4).
- `s` = **success rate** of the retention action (share of would-be churners actually retained).
- `V` = value of a retained customer = `ARPU × margin × H` where ARPU from data (`rev_Mean`; give mean and median), `margin` assumption (gross margin %), `H` months of extra lifetime retained (assumption, e.g., 6–12 months).
- `c` = cost per targeted customer (contact + expected offer cost). **Paid on all targeted customers, including those who would have stayed.**
- Show the toy example from the tutorial *only as method explanation*, never as results.

### 9.2 Scenarios (conservative / base / optimistic)
Table of inputs with **source or "assumption"** flags (every assumption in `docs/assumptions.md`). `s`, `c`, `V`, `H`, margin, and realistic churn base rate must vary across scenarios. Provide a table + a bar/waterfall chart.

### 9.3 Sensitivity and optimal k
- Tornado chart over `s, c, V, π_real, k`.
- Net-value-vs-k curve per scenario → choose **k\*** (the best k) and justify.
- **Break-even success rate:** `s* = c / (p_adj × V)`; show how far the base case is above break-even.
- Lane 2 (lifecycle triggers): size the window (e.g., customers aged 240–300 days) × (observed churn gap) × share of gap an offer can plausibly close; label clearly as hypothesis to be tested by an A/B pilot; include the pilot design (treatment/holdout, duration, KPI = incremental retention).

### 9.4 Realism adjustment for the 49.6% churn rate (must do)
Assume the model's score distribution *given class* stays the same but the class prior changes (label-shift). With sample prior π_s ≈ 0.4956 and realistic prior π_r (scenarios: 5% and 10%, citing the tutorial and any better source), re-weight each test row: positives by `π_r/π_s`, negatives by `(1−π_r)/(1−π_s)`; compute **weighted precision@k and lift@k**. Present both "as observed in sample" and "re-based" numbers, clearly labelled. This is a mature, defensible way to avoid overstating impact.

### 9.5 What the proposal must *not* claim
No guaranteed savings; no causal language for thresholds; no use of sample precision as real-world precision; no revenue per customer without stating units (MU) and source (`rev_Mean`).

---

## 10. Slide deck specification (PDF, ≤ 15 slides)

### 10.1 Format & tooling
- 16:9, 1920×1080 px per page. Preferred pipeline: HTML/CSS slides rendered with Playwright/Chromium (`page.pdf`, `print_background=True`, fonts embedded) → `slides/build/ACCOUNT_NAME.pdf`. Charts exported from the notebook as PNG ≥ 200 dpi (or SVG). Alternative: `python-pptx` + LibreOffice export. Keep PDF ≤ 10 MB (compress images / Ghostscript if needed).
- Text on slides must be **live text** (selectable) wherever the rubric requires it — especially **model name, metric, result** (R3).
- **Language:** English (the program and graders are English-language). Slide titles are complete sentences stating the takeaway; reading only the titles must tell the whole story (R5/R7).

### 10.2 Design system
- **Palette:** Navy `#0B1F3A` (titles), Teal `#0F8B8D` (accent/primary), Coral `#E4572E` (churn/risk), Blue `#3B7DD8` (stayed/baseline), Slate `#5B6B7B` (secondary text), Light `#F5F7FA` (background), Amber `#F2A541` (highlight/callout). Colorblind-safe pairing: coral vs. blue for churn vs. stayed — consistent across *all* charts.
- **Type:** Inter (or Noto Sans), title 44–48 px bold, body ≥ 26 px, chart labels ≥ 18 px, source footnotes 16 px. Max 2 lines per title (≤ 14 words), ≤ 3 bullets per slide, ≥ 96 px margins; one idea per slide; generous whitespace.
- **Every slide:** short section tag (top-left), slide number, a footnote with source tags like `[2][5]` when external facts appear. No decorative clip-art. Charts: clean axes, units, annotated key points (e.g., vertical line at ~300 days), direct labels instead of legends where possible.
- **Plain-language diagram** (slide 10) created as SVG/PNG: *Customer profile → many small decision trees "vote" → risk score (0–100%) → rank → top-k% receive the offer*.

### 10.3 Slide-by-slide blueprint (exactly 15; fill with *real* numbers from `results.json`)
| # | Slide (title = takeaway) | Content | Visual |
|---|---|---|---|
| 1 | **Title**: *"Keeping customers before they leave: a data-driven retention proposal for Company A"* | Subtitle (GCI World 2026 September — Final Assignment, course project), name: Islam Raad, University of Mosul, date | Clean cover, subtle motif |
| 2 | **Executive summary** — the answer first | Problem (1 line) · Recommendation (1 line) · Estimated impact range (MU, with key assumption) · How sure we are | 3-block layout with big numbers |
| 3 | **Market context**: *why churn is the profit lever in a saturated market* | 3 sourced facts (market size/competition, retention vs acquisition economics, local dynamics); Iraq lens + disclaimer that Company A is anonymous | Small chart/map-less infographic of verified numbers; footnotes `[n]` |
| 4 | **The data**: *what we have and what it cannot tell us* | 100,000 customers, 98 features, 2 tables; churn 49.6% (unrealistic, why it matters); quality highlights; what is missing (offers, contracts, dates, costs) | Data-structure graphic + missingness bar |
| 5 | **EDA #1**: *"Risk jumps once a customer's device passes ~300 days"* (verify wording/number) | Churn rate by device-age bins; the CI/robustness note; hypothesis (upgrade window) + caveat | Line/bar with annotated threshold |
| 6 | **EDA #2**: *"Churn also spikes at months 10–12 and when usage collapses"* | Tenure curve; tenure×device-age heat-map note (entanglement); zero-usage segment size/churn/revenue | 2–3 small multiples |
| 7 | **Problem definition**: *"We rank customers by risk so retention offers go to the right people"* | Question in one sentence · target `churn` (31–60 days) · task: classification/ranking · who acts · what action · success KPI | Simple flow: Data → Score → Decision → Action |
| 8 | **Features**: *"We turned raw columns into signals about behavior and lifecycle"* | Preprocessing decisions + the key engineered features (table: name · idea · why) | Table + mini icons |
| 9 | **Experiments**: *"A boosted-tree model ranks churners best; extra tuning adds little"* | **Live-text table:** model · metric (AUC, accuracy) · CV ± std · test result; baseline; what we learned | Table + small bar chart |
| 10 | **How the model works (for managers) and what it learned** | The plain-language diagram; top 3–5 drivers with "can the company change it?" tags | Diagram + importance bar |
| 11 | **Targeting power**: *"Contacting the riskiest 10% finds X× more churners than random"* | Confusion matrix (explained in words), top-k table (sample vs re-based), lift curve | Lift/gain curve + matrix |
| 12 | **Recommendation**: *"Launch a two-lane retention program: risk-ranked saves + timed lifecycle offers"* | Who · what · when · owner · pilot design (holdout) | Lane diagram/timeline |
| 13 | **Estimated impact**: *"Under stated assumptions the program nets X–Y MU a year"* | Formula in words; scenario table; break-even `s*`; k\* ; 49.6%→realistic re-basing | Scenario bars + tornado |
| 14 | **Risks, ethics and next steps**: *"What could go wrong and how we would find out"* | Limits (sample balance, no causal proof, no offer/cost data), fairness choice (no ethnicity), 90-day pilot plan, monitoring | Risk matrix + 3-step roadmap |
| 15 | **References** | Numbered list identical to `references.txt` (includes AI chat link line) | Text |

### 10.4 Quality gates for the deck
- Reading only titles tells a coherent story; each slide opens the question the next answers.
- No chart without a takeaway; no number without a unit/definition; no jargon unexplained (define AUC as "how well the model puts churners above stayers", lift as "× better than random").
- Rendered-PNG check of all 15 pages (no overflow, no clipped labels); contrast ≥ 4.5:1; font ≥ 24 px for body.
- `verify_numbers.py` passes; every `[n]` tag resolves to the reference list.
- Speaker notes (not in PDF) in `docs/speaker_notes.md`: 60–90 s per slide.

---

## 11. Notebook specification
Structure (markdown headers mirror the slides): 0 Title/Overview & AI statement · 1 Setup & config (paths, seed, versions) · 2 Load & merge (assertions: shapes, unique IDs, 1:1 join) · 3 Data audit · 4 EDA (+ robustness checks for thresholds) · 5 Problem definition (text) · 6 Preprocessing & features (pipelines) · 7 Modeling (experiment log) · 8 Evaluation & interpretation · 9 Business impact (assumptions cell with sources, scenarios, sensitivity, re-basing) · 10 Export (`results.json`, figures, tables) · 11 Conclusion & limits.
Requirements: first cell describes purpose + folder structure + how to run; all randomness seeded; no hard-coded absolute paths; **no API keys/personal data**; remove dead/experimental cells; each section ends with a one-sentence "so what"; outputs saved in the notebook; execution time < ~10 min; passes `jupyter nbconvert --to notebook --execute`. A short markdown cell may state that generative AI assisted and refer to the references for chat links.

---

## 12. References & disclosure
- `references.txt`: numbered, one reference per line, **identical to slide 15** and to footnote tags. Include: (1) every market/academic source; (2) library citations (scikit-learn, XGBoost, pandas); (3) the dataset line (*"Company A telecom dataset, GCI World 2026 September Final Assignment materials (Matsuo-Iwasawa Lab, University of Tokyo)"* — not redistributed); (4) **AI chat link line(s)** — placeholders `[AI-CHAT-LINK-1: Claude planning conversation]`, `[AI-CHAT-LINK-2: Antigravity/Gemini session export]` for Islam to replace (platform-specific sharing steps are unverified → Islam asks organizers if sharing isn't possible).
- No unverifiable citations; never cite a source you did not open.

## 13. AI-usage survey (draft; Islam answers honestly)
The submission page has: **Q1** used generative AI (1 = yes, 2 = no); **Q2** which parts (comma-separated numbers: 1 market research/ideas, 2 EDA/plots, 3 preprocessing/feature engineering, 4 model building/interpretation, 5 translating ML into a quantified proposal, 6 slides/writing/translation, 7 references/citations, 8 other); **Q3** which tools (1 ChatGPT, 2 Claude, 3 Gemini, 4 GitHub Copilot, 5 other, 6 can't recall/prefer not to say); **Q4** how much of the AI-assisted content he can explain in his own words (1 = all/100%, 2 = most 75–99%, 3 = more than half, 4 = 25–50%, 5 = little, 6 = unsure/prefer not to say). Each answer 1–500 characters; total ≤ 2000. **Do not paste chat transcripts or personal information into the survey.** Draft in `docs/ai_disclosure_template.md`: Q1 = 1; Q2 = 1,2,3,4,5,6,7 (or what really happened); Q3 = 2,3 (+5 for Antigravity); **Q4 = honest** — only "1" if Islam truly passes the self-test in §14.

## 14. Human-Understanding Pack (required deliverable; Islam must be able to defend everything)
Language: **Arabic (simple, Iraqi-friendly Modern Standard)**, keeping English technical terms in parentheses. Files in `docs/`:
1. `UNDERSTANDING_GUIDE_AR.md` — for **every phase**: *what we did · why · how (plain words + tiny example) · the result with the real number · what could go wrong · what to say if asked*. Include a glossary (churn, EDA, feature, leakage, overfitting, cross-validation, AUC, precision/recall, lift, confusion matrix, baseline, XGBoost, gain vs permutation importance, label-shift re-basing, break-even, sensitivity analysis, A/B holdout).
2. `numbers_cheatsheet.md` — every number on the slides: value · where computed (notebook cell) · what it means · how it changes under the assumptions.
3. `INTERVIEW_QA.md` — ≥ 30 likely questions (technical + business + ethics + "why not a better model?") with model answers; plus a 2-minute story (problem → data → key finding → model → recommendation → impact → limits).
4. `speaker_notes.md` — per slide.
5. **Self-test** (20 questions with answers hidden at the end) so Islam can check he understands before answering survey Q4.
6. `HOW_TO_RERUN.md` — exact commands/clicks to re-run the notebook and rebuild the PDF.

## 15. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Thresholds (300 days, month 10–11) are sampling artifacts | Robustness checks (§8.2); wording "hypothesis"; Lane 2 framed as pilot; fall back to Lane 1 core |
| Weak AUC (~0.70) tempts over-claiming | State it plainly; sell **ranking/targeting lift**, not accuracy; compare to baseline |
| 49.6% churn inflates impact | Re-basing (§9.4) shown next to raw numbers |
| Hallucinated sources/numbers | Open-every-URL rule; sources log; `verify_numbers.py` |
| Notebook fails on grader's machine | Relative paths, pinned requirements, Restart-and-run-all test, minimal dependencies |
| Slides overflow / exceed 10 MB | Rendered-PNG QA; image compression; page-count check |
| Time pressure (human unavailable) | MVP-first plan in `tasks.md`; v1 must be *submittable* before polish |
| AI-disclosure/plagiarism concerns | Understanding Pack; honest Q4; AI chat links in references |

## 16. Open questions for the human (ask once, at the end of Phase 0 — do not block)
1. Exact **Omnicampus account name** (for file names).
2. Where the AI chat links will come from (Claude conversation share link; Antigravity session export) — Islam fills the placeholders.
3. Does he want the PDF slide language to remain English? (Default: yes.)

## Appendix A — `results.json` schema (minimum keys)
`data{n_rows,n_cols,churn_rate,missing_top[],negatives{}}`, `eda{device_age_bins[],tenure_curve[],jump_ci{},zero_usage{n,churn,rev_mean}}`, `models[{id,name,cv_auc_mean,cv_auc_std,cv_acc,test_auc,test_acc,test_precision,test_recall,test_f1}]`, `final_model{name,test_auc,test_acc,train_acc}`, `topk[{k,n,precision,recall,lift,precision_rebased_5,precision_rebased_10}]`, `importance{gain[],permutation[]}`, `impact{assumptions{},scenarios[{name,net,retained,cost}],k_star,breakeven_s,sensitivity[]}`, `meta{seed,versions,run_time}`.

## Appendix B — Quick definitions for slides
- **Churn:** customer leaves within 31–60 days after the observation date.
- **AUC:** probability the model scores a random churner higher than a random stayer (0.5 = coin flip, 1.0 = perfect).
- **Lift@k:** churn rate among the top-k% scored customers ÷ overall churn rate.
- **Value-at-risk:** P(churn) × value of the customer if retained.
