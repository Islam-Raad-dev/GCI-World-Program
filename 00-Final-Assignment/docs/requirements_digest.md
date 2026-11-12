# Requirements Digest — GCI World 2026 Final Assignment (Company A Telecom Churn PoC)

> **Source-of-truth precedence (PRD §0.1):**
> 1. `README.docx` (official assignment rules)
> 2. `final_assignment_tutorial.pdf` & `tutorial.ipynb` (official walkthrough)
> 3. `ENG_Company _A_ Dataset Overview.docx` (column descriptions)
> 4. Actual CSV data (`telecom/Client.csv`, `telecom/Record.csv`)
> 5. `GCI_Final_Assignment_Guide.pdf` (prior calibration guide)
> 6. `prd.md` & `tasks.md` (operational execution rules)

---

## 1. The 7 Official Grading Requirements (`README.docx` §2)

| # | Requirement | Official Specification (`README.docx` / `tutorial.ipynb`) | How We Satisfy & Prove It (`prd.md` §2.2) |
|---|---|---|---|
| **R1** | **Clear Business Proposal** | Move beyond mere technical reporting; form a clear business proposal driven by insights from the data with quantified impact (revenue lift, cost savings, risk reduction). (`README.docx` §1, §2) | Executive Summary (Slide 2), Concrete Two-Lane Retention Recommendation with owner/action/timing/A-B pilot (Slide 12), and Quantified Financial Impact under conservative/base/optimistic scenarios & label-shift re-basing (Slide 13). |
| **R2** | **Actual EDA of Dataset** | Base proposal on actual EDA of the dataset, highlighting client-specific challenges. (`README.docx` §2) | Full data audit (missingness signal, doc-vs-data discrepancies, duplicates, negative values) + 4–6 purpose-built charts on Company A's specific patterns (~300-day device cliff with robustness checks, month 10–12 tenure spike, entanglement heatmap, usage collapse segments) + 3 testable hypotheses (Slides 4–6). |
| **R3** | **Appropriate ML Model(s) Reported as Live Text** | Build and report ≥1 appropriate ML/statistical model; **explicitly write model name, evaluation metric, and score as text on the slide** (screenshots/figures alone are insufficient); explain why chosen, how built, and insights gained. Comparing multiple models is preferable. (`README.docx` §2 Notes on R3, §6 FAQ) | Compare ≥5 models (Dummy baseline, Logistic Regression, Shallow Decision Tree, Tutorial XGBoost, Engineered XGBoost, Tuned XGBoost, LightGBM) via 5-fold stratified CV on the 70% train split. Report all names, metrics (ROC-AUC, Accuracy, Precision@k, Lift@k), and scores **as selectable live HTML text** on Slide 9, plus feature importance (gain + permutation) and partial dependence on Slide 10. |
| **R4** | **External Sources & Market Analysis** | Use external sources (data, reports, papers) and conduct market analysis. Cite sources clearly on slides and in the reference list. (`README.docx` §2, §2-1) | Grounded in Iraq's mobile telecom market (CMC, ITU, GSMA, DataReportal, Zain Iraq, Asiacell) + peer-reviewed telecom churn literature (≥8 verified sources). Explicit disclaimer that Company A is anonymous. Footnote tags `[n]` on slides matching `references.txt` and Slide 15 line-for-line. |
| **R5** | **Understandable to Non-ML Executives** | Make presentation understandable to client executives with no ML background, while translating essential technical methods via conceptual diagrams. (`README.docx` §2, §7-2) | Action/takeaway sentence titles on all slides; plain-language conceptual diagram on Slide 10 showing how decision trees vote to rank customer risk; plain definitions of AUC, Lift, Precision, and Value-at-Risk; clear explanation of confusion matrix costs on Slide 11. |
| **R6** | **Multiple Data Visualizations** | Use multiple data visualizations designed with purpose (clear colors, units, legends, annotations), not just raw numbers. (`README.docx` §2, §7-2) | Consistent colorblind-safe palette (Coral `#E4572E` = churn, Blue `#3B7DD8` = stayed, Navy `#0B1F3A`, Teal `#0F8B8D`) across 10+ high-DPI charts (missingness signal, device age jump & RD robustness, tenure curve, 2D entanglement heatmap, usage collapse, model comparison, feature importance, lift/gain curve, scenario net impact & sensitivity tornado). |
| **R7** | **Logical Consistency** | Ensure logical consistency from analysis through proposal. (`README.docx` §2) | Single cohesive thread: Market Need → Data Audit → EDA Patterns & Hypotheses → Problem Definition → Engineered Signals → Model Selection & Interpretation → Top-k Targeting Power → Two-Lane Recommendation → Re-based Financial Impact → Risks, Ethics & 90-Day Pilot. |

---

## 2. Deliverable Rules & Constraints (`README.docx` §3)

1. **Slides PDF (`<ACCOUNT_NAME>.pdf`):**
   - Maximum **15 slides total** (including title page, executive summary, section dividers if any, and references). Slides beyond 15 may be disregarded.
   - Maximum file size: **≤ 10 MB**.
   - Must contain **selectable live text** (especially for R3 model name, metric, and score) and embedded fonts.
2. **References (`references.txt` & Omnicampus References field):**
   - One reference/URL per line, numbered to match on-slide footnote tags `[1]..[N]` and Slide 15 identically.
   - Direct quotation must be well below 40% (target ≈ 0%; paraphrase and synthesize).
   - **Mandatory AI disclosure:** Paste URLs to generative AI chat histories / session exports in the reference list.
3. **Notebook (`<ACCOUNT_NAME>.ipynb`):**
   - Reproducible end-to-end analysis (`Restart & Run All` completes cleanly in <10 minutes with `random_state=42`).
   - Auto-detects local `telecom/` path vs. Google Colab `/content/drive/MyDrive/Final Assignment/telecom/` path.
   - Must **not** redistribute `Client.csv` or `Record.csv`, and must contain no API keys or personal data.
4. **Hard Deadline:**
   - **Saturday, 28 November 2026, 11:30 UTC (14:30 Iraq time, UTC+3)**.
   - No late submissions or post-deadline edits accepted. Resubmissions before the deadline require re-attaching **all three** items every time.

---

## 3. Conflicts & Discrepancies Across Source Files (Traced & Resolved)

| Topic | Source A | Source B | Resolution (per PRD §0.1 Precedence) |
|---|---|---|---|
| **Dataset Overview file name** | `prd.md` §3.1 writes `ENG_Company_A_Dataset Overview.docx` (no spaces around `_A_`). | Actual filesystem has `ENG_Company _A_ Dataset Overview.docx` (spaces around `_A_`). | Use actual filesystem path when reading; document in `decision_log.md`. |
| **Cohort label in headers** | `README.docx` and `final_assignment_tutorial.pdf` state **GCI World 2026 September**. | `tutorial.ipynb` and `ENG_Company _A_ Dataset Overview.docx` state **GCI World 2026 Winter**; tutorial screenshots show **GCI World 2026 April** dates. | Follow `README.docx` (#1 source of truth): cohort is **GCI World 2026 September**, deadline is **28 Nov 2026 11:30 UTC**, portal is course 170 (`https://edu.omnicamp.us/en/courses/170/`). |
| **Location of `months` column** | `tutorial.ipynb` §2.3 table says `Client.csv` contains "tenure, plan, demographics, equipment". | Actual CSV headers show `months` is in `Record.csv`, while `Client.csv` has lifetime totals (`tot*`, `avg*`). | Actual CSV data wins (#4 over #2 for data structure, and noted in `GCI_Final_Assignment_Guide.pdf` p.8). Always verify against merged `df.columns`. |
| **Definition of `change_mou` and `change_rev`** | `ENG_Company _A_ Dataset Overview.docx` defines them as *"Percentage change in monthly minutes of use / revenue vs previous three month average"*. | Actual CSV data has ~22.6% of `change_mou` values `< -100` (impossible for a percentage drop) and correlates ~0.90–0.94 with `mou_Mean - avg3mou` and `rev_Mean - avg3rev`. | Actual CSV data wins (#4 over #3). Treat and label on slides as **absolute change in minutes/revenue vs. 3-month average** (or explicitly note the documentation discrepancy). |
| **handset price column name** | `prd.md` §5.3 mentions `price_hnd` in one bullet and `hnd_price` in §5.2. | `ENG_Company _A_ Dataset Overview.docx` and `Client.csv` use `hnd_price`. | Use actual column name `hnd_price` from `Client.csv`. |
| **Call feature `_Mean` suffixes** | `prd.md` §5.2 lists shorthand `callwait, callfwdv, threeway, inonemin`. | `ENG_Company _A_ Dataset Overview.docx` and `Record.csv` use `callwait_Mean, callfwdv_Mean, threeway_Mean, inonemin_Mean`. | Use exact column names from `Record.csv`. |
| **PRD-only operational rules** | `README.docx` requires a business proposal with ≥1 model, EDA, market analysis, citations, and ≤15 slides. | `prd.md` adds strict engineering guardrails: `outputs/results.json` single source of truth, `verify_numbers.py`, label-shift re-basing for the 49.56% sample churn rate, fairness exclusion of `ethnic`, and the Arabic Human-Understanding Pack (`docs/UNDERSTANDING_GUIDE_AR.md`, `INTERVIEW_QA.md`, etc.). | Adopt all `prd.md` guardrails as they directly strengthen R1–R7 and ensure Islam can defend every slide and cell. |
