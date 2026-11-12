# How to Re-Run the Entire Project From Scratch (`docs/HOW_TO_RERUN.md`)

Everything in this repository is 100% deterministic (`SEED = 42`) and runs end-to-end using the Python 3.12 virtual environment at `/home/islam-raad/ai_workspace/bin/python`.

---

## 1. Quick Single-Command Verification (Check All Numbers, PDF, and References)

From `/home/islam-raad/Projects/Final Assignment`:

```bash
/home/islam-raad/ai_workspace/bin/python scripts/verify_numbers.py && \
/home/islam-raad/ai_workspace/bin/python scripts/check_pdf.py && \
/home/islam-raad/ai_workspace/bin/python scripts/check_refs.py
```

All three scripts must exit with code `0` (`0 mismatches`).

---

## 2. Re-Run the Reproducible Jupyter Notebook (`notebooks/ACCOUNT_NAME.ipynb`)

### Local Execution (Headless CLI)
```bash
/home/islam-raad/ai_workspace/bin/jupyter nbconvert \
  --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=600 \
  notebooks/ACCOUNT_NAME.ipynb
```
- **Expected runtime:** ~2.5 to 4 minutes on 4 CPU cores.
- **What it produces:** Regenerates `outputs/results.json`, all CSV tables in `outputs/tables/`, and all charts in `outputs/figures/`.

### Google Colab Execution
1. Upload the `telecom/` folder (`Client.csv` and `Record.csv`) to your Google Drive at:
   `MyDrive/Final Assignment/telecom/`
2. Open `submission/ACCOUNT_NAME.ipynb` in Google Colab.
3. In Cell 1, the notebook automatically detects whether `./telecom/Client.csv` exists locally; if not, it mounts Google Drive and loads `/content/drive/MyDrive/Final Assignment/telecom/`.
4. Click **Runtime $\to$ Run all**.

---

## 3. Re-Build the 15-Slide PDF Deck (`slides/build/ACCOUNT_NAME.pdf`)

 Whenever you update [`config.py`](file:///home/islam-raad/Projects/Final%20Assignment/config.py) (for example, changing `ACCOUNT_NAME = "ACCOUNT_NAME"` to your actual OmniCamp account name) or update [`references.txt`](file:///home/islam-raad/Projects/Final%20Assignment/references.txt) (pasting your shared AI chat URL):

```bash
/home/islam-raad/ai_workspace/bin/python scripts/build_slides.py
```

This script:
1. Reads `outputs/results.json` and `references.txt`.
2. Renders `slides/src/slides.html` (15 slides, 1920×1080 16:9 layout).
3. Calls Google Chrome headless (`/usr/bin/google-chrome --headless --print-to-pdf`) to generate `slides/build/<ACCOUNT_NAME>.pdf`.
4. Copies the verified PDF, notebook, and `references.txt` into `submission/`.
5. Runs `scripts/check_pdf.py`, `scripts/verify_numbers.py`, and `scripts/check_refs.py`.

---

## 4. Re-Run Individual Pipeline Phases (Optional)

If you want to re-run the modular Python scripts step-by-step:

```bash
# Phase 0 & Phase 1: Data Merge, Tutorial Baseline & Full 100-Column Audit
/home/islam-raad/ai_workspace/bin/python scripts/run_phase0_1.py

# Phase 2: Exploratory Data Analysis & 300-Day Robustness Checks
/home/islam-raad/ai_workspace/bin/python scripts/run_phase2_eda.py

# Phases 5–8: Feature Engineering, 5-Fold CV Modeling, Evaluation & Impact Model
/home/islam-raad/ai_workspace/bin/python scripts/run_phases5_8.py

# Phase 10 & 11: Build Slide Deck & Run Automated Verification Suite
/home/islam-raad/ai_workspace/bin/python scripts/build_slides.py
```
