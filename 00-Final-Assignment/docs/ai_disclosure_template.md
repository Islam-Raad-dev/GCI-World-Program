# AI Usage Disclosure & Citation Guide (`docs/ai_disclosure_template.md`)

Per **GCI Final Assignment Guide §03 (Important Guidelines on Submitting Assignments — Citing AI Usage)**, any use of generative AI or coding agents for ideation, literature search, code verification, or presentation structuring must be disclosed on the **References slide (Slide 15)** and in **`references.txt`** with a **shareable link to the AI conversation(s)**.

---

## 1. Exact Citation Line Currently Included in `references.txt` & Slide 15

```text
[14] AI Assistance Disclosure (Google Antigravity / Gemini). (2026). AI Ideation, Literature Search, Code Verification & Slide Layout Assistance Log — Shared Conversation Link: [REPLACE_WITH_SHARED_AI_CHAT_URL_BEFORE_SUBMISSION]
```

---

## 2. Step-by-Step Instructions for Islam Before Submitting (Takes 2 Minutes)

1. **If you used ChatGPT / Claude / Gemini Web UI alongside this workspace:**
   - Open the conversation in your browser.
   - Click **Share** $\to$ **Create public/shareable link** (ensure "Anyone with the link can view" is enabled so the GCI grading team can open it).
   - Copy the shareable URL (e.g., `https://chatgpt.com/share/...` or `https://g.co/gemini/share/...`).
2. **If you want to share the Antigravity Agent Session:**
   - Follow [`docs/agent_session_export.md`](file:///home/islam-raad/Projects/Final%20Assignment/docs/agent_session_export.md) to export or upload the session summary to a public GitHub Gist or Google Doc with "Anyone with link can view", and paste that URL.
3. **Where to Paste Your Link:**
   - Replace `[REPLACE_WITH_SHARED_AI_CHAT_URL_BEFORE_SUBMISSION]` in [`references.txt`](file:///home/islam-raad/Projects/Final%20Assignment/references.txt) (line 14).
   - Re-run:
     ```bash
     /home/islam-raad/ai_workspace/bin/python scripts/build_slides.py
     /home/islam-raad/ai_workspace/bin/python scripts/check_refs.py
     ```
   - This automatically updates **Slide 15** in `slides/build/ACCOUNT_NAME.pdf` and `submission/ACCOUNT_NAME.pdf` and verifies 100% consistency between `references.txt` and Slide 15.

---

## 3. Summary of How AI Was Used (For Interview / Grader Transparency)

- **Data Audit & Verification Scripting:** Assisted in writing reproducible Python scripts (`scripts/run_phase0_1.py`, `scripts/run_phase2_eda.py`, `scripts/run_phases5_8.py`) to audit all 100 columns of `Client.csv` and `Record.csv`, verify 300-day handset-age robustness (`eqpdays`), and quantify tenure-device entanglement (`months` vs. `eqpdays`).
- **Literature & Market Research:** Assisted in locating peer-reviewed churn modeling papers (Neslin et al., *JMR* 2006; Verbeke et al., *EJOR* 2012; Saerens et al., *Neural Computation* 2002) and Iraq/MENA telecom benchmarks (DataReportal 2025, ITU/World Bank, GSMA MENA 2024, Zain Group & Ooredoo Group annual reports).
- **Slide Layout & Automated QA:** Assisted in building an HTML/CSS-to-PDF slide pipeline (`scripts/build_slides.py`) and automated verification checks (`scripts/verify_numbers.py`, `scripts/check_pdf.py`, `scripts/check_refs.py`) ensuring every number in the 15-slide deck matches `outputs/results.json`.
