# tasks.md — Execution Plan for the Antigravity (Gemini) Agent
## GCI World 2026 — Final Assignment (Company A Telecom Churn PoC)

> Read `prd.md` first. This file is the ordered, checkable work breakdown. **Do tasks in order.** Tick `[x]` only when the "Done when" condition is truly met and logged in `docs/work_log.md`.
> **Workspace:** `~/Projects/Final Assignment/` (see PRD §3 for the full layout).
> **Deadline:** Sat 28 Nov 2026, 11:30 UTC (14:30 Iraq). The human (Islam) is **unavailable for a period starting ~13 Nov**. Therefore: **produce a complete, submittable v1 as fast as possible (MVP-first), then polish.**
> If you need information not in these files, look in: `README.docx`, `final_assignment_tutorial.pdf`, `tutorial.ipynb`, `ENG_Company_A_Dataset Overview.docx`, `GCI_Final_Assignment_Guide.pdf`, then the data itself, then the web (market facts only).

---

## Operating rules (apply to every task)
1. **Run → read output → decide → log.** Never state a result you didn't see. If code errors, fix and re-run; do not paper over.
2. **Every number on a slide must come from `outputs/results.json`** (written by the notebook). Never type numbers by hand into slides.
3. **Every external fact needs a verified source** (open the URL; log in `research/sources_log.md` with publication date + access date). If unverifiable → don't use it.
4. **Do not block on the human.** Choose the PRD default, log it in `docs/decision_log.md` (date · decision · alternatives · reason), continue. Ask the human only for: Omnicampus account name, AI chat links, the final submission click.
5. **Seed 42 everywhere.** Keep the test set (30%) untouched except for final candidates (≤ 2 touches, logged).
6. **Do not upload/share the CSVs.** No API keys or personal data in notebooks.
7. After each phase: update `docs/work_log.md`, regenerate `outputs/results.json`, and commit/checkpoint (copy the notebook to `notebooks/checkpoints/` if no git).
8. Language: deliverables in **English**; the Human-Understanding Pack in **Arabic** (technical terms in English in parentheses).

## Priority & time plan (MVP-first)
| Block | Phases | Goal |
|---|---|---|
| **Block A (first)** | 0 → 2 → 4 (core) → 7 (core) → 9 (basic) → 11 (draft) | A complete, honest, working v1 deck + notebook |
| **Block B** | 3 (market), 5, 6, 8, 9 (full), 11 (polish), 12 | Rigor, sources, impact scenarios, design quality |
| **Block C** | 13, 14 | Understanding pack + final QA + submission package |
If time runs short, **protect**: submitted files, a clear recommendation with quantified impact, model name/metric/result as text, real EDA with multiple charts, documented sources, logical flow. **Cut first**: extra models, heavy tuning, SHAP, decorative graphics, appendix.

---

## Phase 0 — Orientation, setup, baseline reproduction  *(Block A)*
- [ ] **T0.1 Read the workspace documents** (README, tutorial PDF, tutorial notebook, dataset overview, guide PDF). Produce `docs/requirements_digest.md`: the 7 grading requirements, deliverable rules, citation/AI rules, deadlines, and any conflicts between sources. *Done when:* digest exists and every PRD rule is traced to a source file or marked "PRD-only".
- [ ] **T0.2 Create the folder structure** from PRD §3.2, `config.py` (`SEED=42`, `DATA_DIR` auto-detect local → Colab path, `ACCOUNT_NAME="ACCOUNT_NAME"`, palette constants), `requirements.txt` (pin the versions actually installed), `docs/*` stubs. *Done when:* `python -c "import config"` works.
- [ ] **T0.3 Environment check.** Import all libs; record versions into `outputs/results.json → meta.versions`. Optional libs (lightgbm, shap) guarded. *Done when:* no import errors.
- [ ] **T0.4 Load and merge.** Read `telecom/Client.csv` and `telecom/Record.csv`; **print `df.columns`**; assert shapes (100000×50, 100000×51), `Customer_ID` unique in both, 1:1 inner merge → (100000, 100). Save column-to-file map to `outputs/tables/column_map.csv`. *Done when:* assertions pass and are in the notebook.
- [ ] **T0.5 Reproduce the tutorial baseline exactly** (LabelEncoder on `object` columns, `XGBClassifier(n_estimators=300, learning_rate=0.05, max_depth=6, eval_metric='logloss', random_state=42)`, stratified 70/30, seed 42). Record test accuracy (expect ≈ 0.636; Islam's run: 0.6357), **add AUC (≈ 0.694), train accuracy (≈ 0.735), precision/recall/F1, confusion matrix**, majority-class baseline (≈ 0.504). *Done when:* numbers within ±0.01 of expectations or an explanation is logged.
- [ ] **T0.6 Ask the human once (non-blocking):** Omnicampus account name; placeholders remain until answered. Write the question in `docs/questions_for_islam.md`.

## Phase 1 — Data audit  *(Block A)*
- [ ] **T1.1 Structure & types:** dtypes count (expected float64 69 / int64 10 / object 21), memory, duplicates, ID checks. → `outputs/tables/dtypes.csv`.
- [ ] **T1.2 Missing values:** full table (count, %) for all columns; bar chart of top 20; check **"same rows missing across many demographic columns"** (≈1.7% block); for each of the top missing columns compute churn rate when missing vs present. → `outputs/tables/missing.csv`, `figures/missing_top20.png`.
- [ ] **T1.3 Negative / impossible values** in `rev_Mean, mou_Mean, totmrc_Mean, eqpdays, avg6rev` etc.; count, min, churn rate of those rows; decision log entry per column (clip / flag / keep). Explain the `log1p` RuntimeWarnings seen in the tutorial's pairplot (negative inputs → invalid value; value −1 → divide by zero).
- [ ] **T1.4 Outliers & skew:** quantiles (p1, p50, p99, max) for numeric columns; list extreme cases (`uniqsubs`, `totcalls`, `totmou`).
- [ ] **T1.5 Near-duplicate and constant-ish columns:** Spearman |ρ| > 0.97 pairs (table of top 20), columns with ≥ 90% zeros. Test (quick CV) whether dropping duplicates changes AUC (expect ≈ none).
- [ ] **T1.6 Documentation vs data audit:** test the claim that `change_mou` / `change_rev` are percentages (share < −100, correlation with `mou_Mean − avg3mou`, `rev_Mean − avg3rev`); check `recv_sms_Mean`, `iwylis_vce_Mean`, `infobase` meaning; list all discrepancies in `docs/data_doc_discrepancies.md` and the wording to use on slides.
- [ ] **T1.7 Target audit:** churn counts and rate (expect 49.56%); document why accuracy is meaningful here (balanced) but misleading at 5% churn; record `eda.churn_rate` in `results.json`.
*Done when:* all tables/figures saved; discrepancies documented; no unexplained anomalies left.

## Phase 2 — Exploratory data analysis (core)  *(Block A)*
Every analysis = a clear chart + a one-sentence finding saved in `docs/eda_findings.md`. Use **training split only** for any threshold discovery (split first with seed 42, then explore the train part; replicate on the full data only as a descriptive check).
- [ ] **T2.1 Device age (`eqpdays`) vs churn:** churn rate by bins ≤ 25 days; plot with CI bands; identify jumps. Handle negative `eqpdays` per T1.3. → `figures/eqpdays_churn.png`.
- [ ] **T2.2 Robustness of the ~300-day jump:** (a) bootstrap 95% CI of churn(301–340) − churn(260–300); (b) local linear fit each side; (c) repeat within `months ≥ 10`, by `area`, by `crclscod`; (d) **covariate-balance check** at 300 days (`rev_Mean, hnd_price, months, mou_Mean, uniqsubs`) — if many covariates also jump, flag *possible sampling artifact*. → `outputs/tables/threshold_robustness.csv`, `figures/eqpdays_robustness.png`. *Done when:* a written verdict: "real-looking", "uncertain", or "likely artifact" with reasons.
- [ ] **T2.3 Tenure (`months`) vs churn:** churn rate for each month 6–61 (+counts); locate the cliff (~10–12); → `figures/months_churn.png`.
- [ ] **T2.4 Entanglement:** 2-D table/heat-map of churn by tenure bucket × device-age bucket with counts (do customers with ≤ 9 months and device > 300 days exist? expect none); compare device-age effect **within tenure ≥ 10** only. → `figures/tenure_device_heatmap.png`.
- [ ] **T2.5 Usage collapse segments:** `mou_Mean == 0`, ≤ 10, ≤ 30, ≤ 65, missing `change_mou`: size, churn rate, mean revenue, share of total revenue, lifetime totals. Is it a standalone intervention target or "already gone"? → table + `figures/usage_segments.png`.
- [ ] **T2.6 Revenue and "value":** distributions and medians by churn class; correlation with churn; implication for defining a "valuable customer" (expect revenue does not separate classes).
- [ ] **T2.7 Customer-care calls vs churn:** churn by care-call bucket; list ≥ 3 competing explanations as hypotheses (do not assert causality).
- [ ] **T2.8 Call quality & overage/roaming vs churn:** dropped/blocked/unanswered rates; overage and roaming shares.
- [ ] **T2.9 Demographics vs churn:** income, adults, marital, `ethnic`, etc.; write the fairness note for `ethnic` and similar fields.
- [ ] **T2.10 Select final EDA visuals:** 4–6 charts for slides 4–6 (consistent palette; coral = churn, blue = stayed). Export PNG ≥ 200 dpi and SVG.
- [ ] **T2.11 Write 3 hypotheses** (full sentences: "Segment X is more likely to churn because Y; we will test with Z"), ranked by actionability and evidence; save to `docs/hypotheses.md`.
*Done when:* 4–6 final charts + 3 hypotheses + robustness verdict exist, and key stats are in `results.json → eda`.

## Phase 3 — Market research  *(Block B; can run in parallel with Phase 2)*
- [ ] **T3.1 Search plan:** list queries for each research question in PRD §7 (market structure in Iraq, subscribers/penetration, operators, regulator CMC, ITU/GSMA/DataReportal, retention-vs-acquisition cost, handset cycle & churn, campaign success rates, academic churn-prediction papers).
- [ ] **T3.2 Collect ≥ 8 sources** (target 10–12): mix of regulator/ITU/GSMA/operator reports/credible media/peer-reviewed papers. For each: **open the page**, verify the fact, log in `research/sources_log.md` (ID · title · publisher · publication date · URL · access date · fact used · reliability note). Paraphrase in `research/notes/`; quotes ≤ 15 words only if essential.
- [ ] **T3.3 Answer each research question** in 3–6 lines with citations `[ID]`. Where Iraqi data are unavailable, say so and use regional/global data with explicit labels.
- [ ] **T3.4 Choose 3 facts for slide 3** (market structure / retention economics / local dynamics) and any numeric inputs for the impact model (churn base rate, success rate, offer cost, margin, horizon). If a number can't be sourced, mark it **ASSUMPTION** in `docs/assumptions.md`.
- [ ] **T3.5 Build `references.txt` (draft)** in the order cited; one line each; keep IDs stable for slide tags.
*Done when:* ≥ 8 verified sources logged; every number intended for slides has a source ID or is flagged as an assumption.

## Phase 4 — Problem definition (Decision Gate)  *(Block B, but decide early)*
- [ ] **T4.1 Decision matrix** for options A–E (PRD §6.1) scored 1–5 on evidence strength, actionability, measurability, risk, market fit. Save `docs/problem_decision_matrix.md`.
- [ ] **T4.2 Decide** between: (i) default two-lane proposal (risk ranking + lifecycle triggers), (ii) risk ranking + value-at-risk only (if T2.2 verdict = "likely artifact"). Log the decision and why.
- [ ] **T4.3 Write the problem paragraph (3–5 sentences):** problem · for whom · target · ML task type and why · expected decision/action. Save to `docs/problem_definition.md` (feeds slide 7).
- [ ] **T4.4 Define success KPI and decision owner** (e.g., incremental retention rate in a pilot; owner = retention/CRM team).
*Done when:* the paragraph is clear enough that a non-technical manager can restate it. **If you cannot write it clearly, do not proceed to modeling.**

## Phase 5 — Preprocessing and feature engineering  *(Block A core, Block B polish)*
- [ ] **T5.1 Build a leakage-safe preprocessing pipeline** (`sklearn.Pipeline`/`ColumnTransformer`): for trees → native NaN + categorical handling (`enable_categorical=True` or ordinal with a "missing" category); for logistic regression → median impute + missing flags + scaling + one-hot for low-cardinality categoricals. Compare vs tutorial LabelEncoder.
- [ ] **T5.2 Engineer ≥ 10 features** per PRD §8.3 (lifecycle flags, ratios of current/historical usage, quality rates, revenue-composition shares, care ratios, zero-usage flags, missingness flags); safe division with epsilon; handle negatives per T1.3. For each feature: row in `docs/feature_dictionary.md` (name · formula · business reason · leakage check · included?).
- [ ] **T5.3 Leakage review:** confirm each feature is available before the churn window; no use of `churn`; any target-based statistic only inside CV folds. Sanity check: no feature alone gives AUC > 0.65 unexpectedly (prior single-feature max ≈ 0.57).
- [ ] **T5.4 Fairness variants:** prepare feature sets with and without sensitive/proxy fields (`ethnic`, `income`, `marital`, `kid*`, …).
*Done when:* features documented, pipeline runs, and no leakage red flags remain.

## Phase 6 — Modeling and experiments  *(Block A core)*
- [ ] **T6.1 Split:** stratified 70/30, seed 42 (identical to the tutorial). Save indices.
- [ ] **T6.2 Models (≥ 4):** M0 majority baseline; M1 logistic regression; M2 decision tree (depth ≤ 4, for explanation); M3 XGBoost tutorial params; M4 XGBoost + engineered features; M5 XGBoost tuned (randomized search ≤ 30 configs, ≤ 20 min, shallow trees, subsampling); optional M6 LightGBM/RandomForest.
- [ ] **T6.3 5-fold stratified CV on the training 70% only:** record AUC mean ± std and accuracy for each model in `outputs/tables/experiment_log.csv` (id · change · features · params · CV AUC · std · accuracy). Treat differences < 1 std as noise.
- [ ] **T6.4 Pick the final model** by CV AUC (ties → simpler/more explainable). Log the reasoning. Expect the final CV AUC ≈ 0.70 (prior: tutorial 0.697 → engineered 0.7015; tuning ≈ +0.000).
- [ ] **T6.5 Final test evaluation (≤ 2 touches):** AUC, accuracy, precision, recall, F1, confusion matrix, train–test gap. If accuracy ≥ 0.75 or AUC ≥ 0.80 → run leakage hunt before accepting.
- [ ] **T6.6 Save** the final model (`outputs/models/final_model.joblib`) and test predictions/probabilities (`outputs/tables/test_predictions.csv`: row id, y_true, p_churn) for later impact calculations.
*Done when:* the experiment log is complete; final model chosen; test results recorded; `results.json → models, final_model` populated.

## Phase 7 — Evaluation and interpretation  *(Block A core)*
- [ ] **T7.1 Confusion matrix** at the chosen threshold; explain false positives (wasted offers) vs false negatives (lost customers) in words.
- [ ] **T7.2 Top-k% targeting table** for k ∈ {1, 2, 5, 10, 15, 20, 30, 50}: customers targeted, precision, recall, lift; **lift/gain curve** figure. → `results.json → topk`.
- [ ] **T7.3 Calibration** curve; optionally isotonic calibration on a validation fold.
- [ ] **T7.4 Feature importance:** gain (tutorial) **and** permutation importance on held-out data; explain the difference (gain vs weight). Optional SHAP.
- [ ] **T7.5 Partial dependence** for `eqpdays` and `months` — do the model's curves show the thresholds?
- [ ] **T7.6 Ablation:** drop the top feature and retrain; report change in CV AUC; conclude "one strong signal" vs "many weak ones".
- [ ] **T7.7 Lever table:** top 3–5 drivers → "can the company change it?" (yes/partly/no) and what action it implies.
- [ ] **T7.8 Fairness check:** AUC with vs without sensitive/proxy fields; decision on the final feature set.
*Done when:* all tables/figures saved and interpretations written in cautious language ("indicator", not "cause").

## Phase 8 — Business impact model  *(Block A basic → Block B full)*
- [ ] **T8.1 Assumptions table** (`docs/assumptions.md`): ARPU (mean and median of `rev_Mean`, unit = monetary units, MU), margin %, horizon H (months retained), success rate `s`, cost per targeted customer `c`, customer base N (100,000), realistic churn priors π_r ∈ {5%, 10%} — each marked **SOURCED [ID]** or **ASSUMPTION** with rationale.
- [ ] **T8.2 Re-basing (label-shift) function** in `src/economics.py`: weights positives by π_r/π_s and negatives by (1−π_r)/(1−π_s); compute weighted precision@k and lift@k on the test predictions. Unit-test with a toy example. Report both sample and re-based numbers.
- [ ] **T8.3 Net-impact function:** `Net = n·p_adj·s·V − n·c` with `V = ARPU × margin × H`; vectorized over k; produce scenario table (conservative/base/optimistic) → `results.json → impact`.
- [ ] **T8.4 Optimal k\*** per scenario (max net) and **break-even success rate** `s* = c/(p_adj·V)`; figure: net vs k per scenario.
- [ ] **T8.5 Sensitivity:** tornado over `s, c, V, π_r, k`; figure.
- [ ] **T8.6 Lane 2 sizing (only if the threshold hypothesis survived T2.2):** size the window (e.g., customers aged 240–300 days), observed churn gap, assumed share of gap closable by an offer (scenarios), net value; label **hypothesis → pilot**. Design the **A/B pilot** (treatment vs holdout, duration, sample size rule of thumb, KPI = incremental retention).
- [ ] **T8.7 Sanity checks:** units (MU), no double counting, results independent of random seed beyond rounding, scenarios ordered logically.
- [ ] **T8.8 Write the one-paragraph impact statement** with the range and the key assumption(s). Use "estimated … under stated assumptions".
*Done when:* scenario table, k\*, break-even, tornado and the re-based vs raw comparison exist and are in `results.json`.

## Phase 9 — Notebook assembly and reproducibility  *(Block A draft → Block C final)*
- [ ] **T9.1 Assemble `notebooks/ACCOUNT_NAME.ipynb`** following PRD §11 structure; first cell = purpose, folder structure, how to run; headers mirror slides; each section ends with a one-line "so what".
- [ ] **T9.2 Make it self-contained:** relative `DATA_DIR` with Colab fallback; seed set once; no absolute paths; optional libs guarded; no web calls; no API keys.
- [ ] **T9.3 Write `outputs/results.json`, figures, tables from the notebook.** Include the `meta` block (versions, seed, runtime).
- [ ] **T9.4 Restart-and-run-all test** with `jupyter nbconvert --to notebook --execute`; runtime < ~10 min; compare regenerated `results.json` with the previous one (must be identical up to float rounding).
- [ ] **T9.5 Clean up:** remove dead/experimental cells, huge outputs, unused imports; keep outputs visible; export a copy of the executed notebook.
*Done when:* nbconvert passes with zero errors and results are reproducible.

## Phase 10 — Slides (PDF)  *(Block A draft → Block B polish)*
- [ ] **T10.1 Set up the slide pipeline** (HTML/CSS + Playwright→PDF preferred): 1920×1080, palette/typography per PRD §10.2, reusable layout templates (title, takeaway+chart, two-column, table, diagram, references). `scripts/build_slides.py` reads `results.json` and `outputs/figures/`.
- [ ] **T10.2 Create the diagram assets:** (a) data-to-decision flow (slide 7), (b) "how the model works" for managers (slide 10): customer profile → many small decision trees vote → risk score → rank → top-k% get the offer, (c) two-lane program (slide 12).
- [ ] **T10.3 Build slides 1–15** per PRD §10.3. Titles are takeaway sentences (≤ 14 words, ≤ 2 lines). **Slide 9 table is live text:** model name · metric · value for every model. **Slide 11** has the confusion matrix explained in words + top-k table + lift curve. **Slide 13** shows formula in words, scenarios, break-even, k\*, raw vs re-based. **Slide 15** = references identical to `references.txt`.
- [ ] **T10.4 Footnotes:** every external fact has `[n]`; every `[n]` exists on slide 15 and in `references.txt`.
- [ ] **T10.5 Story test:** extract titles only → read as a story: problem → evidence → model → decision → impact → risks. Rewrite until each title leads naturally to the next.
- [ ] **T10.6 Render and inspect:** export PDF; render each page to PNG (`pdftoppm -r 100`); inspect every page for overflow, clipped labels, low contrast, tiny fonts (< 24 px body), inconsistent colors; fix and rebuild.
- [ ] **T10.7 Constraints check (`scripts/check_pdf.py`):** pages ≤ 15; file ≤ 10 MB (compress with Ghostscript/image downsampling if needed); fonts embedded; text selectable (verify the slide-9 table text extracts with `pdftotext`).
- [ ] **T10.8 `scripts/verify_numbers.py`:** extract numbers from the PDF text and compare with `results.json`; **0 mismatches**.
- [ ] **T10.9 Speaker notes** (60–90 s per slide) → `docs/speaker_notes.md`.
*Done when:* T10.5–T10.8 pass.

## Phase 11 — References and AI disclosure  *(Block B/C)*
- [ ] **T11.1 Finalize `references.txt`:** numbered; one per line; includes market/academic sources, libraries (scikit-learn, XGBoost, pandas), dataset line (course materials, not redistributed), and **AI chat link placeholders** for Islam to fill. Re-open every URL; fix dead links.
- [ ] **T11.2 Cross-check:** slide-15 list == `references.txt`; all `[n]` tags resolve; no unused or missing items. Script it (`scripts/check_refs.py`).
- [ ] **T11.3 Draft AI-survey answers** in `docs/ai_disclosure_template.md` (PRD §13) with a reminder that Q4 must be answered honestly and **no transcripts or personal data** may be pasted.
- [ ] **T11.4 Export the Antigravity session log/artifacts** as `docs/agent_session_export.md` (so Islam can provide a link or file if organizers ask).

## Phase 12 — Human-Understanding Pack (Arabic)  *(Block C — but start drafting while working)*
- [ ] **T12.1 `docs/UNDERSTANDING_GUIDE_AR.md`:** for every phase: what · why · how (plain Arabic + a tiny example) · real result with number · what could go wrong · what to say if asked. Include the glossary from PRD §14.
- [ ] **T12.2 `docs/numbers_cheatsheet.md`:** every slide number → value · notebook cell/section · meaning · sensitivity.
- [ ] **T12.3 `docs/INTERVIEW_QA.md`:** ≥ 30 Q&As (technical, business, ethics, limitations, "why not a better model?", "why this threshold?", "why re-basing?", "how did you use AI?") + a 2-minute story.
- [ ] **T12.4 Self-test:** 20 questions with answers at the end; instruct Islam to take it before answering survey Q4.
- [ ] **T12.5 `docs/HOW_TO_RERUN.md`:** exact commands/clicks to re-run the notebook and rebuild the PDF (local and Colab).
*Done when:* every slide, notebook section, number, and assumption is explained in Arabic and simple words.

## Phase 13 — Final QA and packaging  *(Block C)*
- [ ] **T13.1 Requirements checklist (R1–R7)** with evidence pointers (slide numbers/cell numbers) in `docs/final_checklist.md`:
  - R1 recommendation slide title states the decision + impact slide has numbers;
  - R2 EDA charts specific to Company A (slides 5–6) + hypotheses;
  - R3 model name/metric/result as **text** (slide 9) + why chosen + how built + what learned;
  - R4 documented market analysis with verified sources (slide 3 + references);
  - R5 plain-language model diagram + jargon defined;
  - R6 multiple purposeful charts;
  - R7 titles-only story is coherent.
- [ ] **T13.2 Honesty audit:** search slides/notebook for causal language ("because", "causes", "drives") and revise to "indicator/hypothesis" unless tested; confirm "course project / estimated under assumptions" statements; confirm no real-client claims.
- [ ] **T13.3 Privacy audit:** no CSV in the submission folder; no keys; no personal data in the notebook; nothing published publicly.
- [ ] **T13.4 Package `submission/`:** `ACCOUNT_NAME.pdf`, `ACCOUNT_NAME.ipynb` (or `.zip` if multiple files), `references.txt`. Confirm names match the Omnicampus account name (after Islam answers); keep placeholders obvious if unanswered.
- [ ] **T13.5 Final clean run:** fresh environment/Colab test of the notebook; rebuild PDF; re-run `check_pdf.py`, `verify_numbers.py`, `check_refs.py` — all pass.
- [ ] **T13.6 Submission instructions for Islam** (`docs/SUBMIT_STEPS.md`): confirm the live Omnicampus course link (the README says the "170 course" page; tutorial images are from an older cohort), attach **all three** items every time, paste references (with AI chat links), answer the AI survey honestly, press the green **Submit**, reopen the page to verify status and attachments, **submit early (≥ 1 day before 28 Nov)**; re-submission before the deadline is allowed but each re-submission must re-attach everything; no changes after the deadline.
- [ ] **T13.7 Hand-off summary** (`docs/HANDOFF.md`): what was built, key numbers, decisions made, open items (account name, AI links, survey), and the exact first three things Islam should read in the Understanding Pack.
*Done when:* all checks pass and `submission/` is complete.

---

## Cross-cutting checklists

### A. Slide-quality checklist
- [ ] ≤ 15 pages, ≤ 10 MB, fonts embedded · [ ] titles are takeaway sentences · [ ] one idea per slide · [ ] body text ≥ 24 px, labels ≥ 18 px · [ ] consistent colors (coral = churn, blue = stayed) · [ ] axes/units/annotations on all charts · [ ] sources `[n]` on every slide with external facts · [ ] model name/metric/value are live text · [ ] every number matches `results.json`.

### B. Analytical-integrity checklist
- [ ] test set untouched except logged final evaluations · [ ] thresholds derived on training split · [ ] no feature uses post-outcome info · [ ] `ethnic` excluded from the final model (with AUC delta reported) · [ ] raw vs re-based impact shown side by side · [ ] hypotheses labelled as hypotheses · [ ] scenarios + sensitivity + break-even present.

### C. Reproducibility checklist
- [ ] seed 42 · [ ] pinned `requirements.txt` · [ ] relative paths + Colab fallback · [ ] `nbconvert --execute` passes · [ ] `results.json` regenerates identically · [ ] no keys/personal data.

### D. When blocked (decision rules)
- A source can't be verified → drop it; find another.
- Thresholds fail robustness → reframe Lane 2 as monitoring hypothesis; keep risk ranking + value-at-risk as the core (log it).
- A library is unavailable → use a fallback (e.g., `HistGradientBoostingClassifier`) and note it.
- Time is short → follow the **protect/cut** list at the top; ship a clean v1 first.
- Any rule conflict between sources → follow PRD §0.1 precedence and log it.
