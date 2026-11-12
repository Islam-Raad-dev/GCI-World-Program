# How to Export & Share This Antigravity Agent Session (`docs/agent_session_export.md`)

Because the GCI Final Assignment Guide (§03) requires a **shared link** when citing AI tools on Slide 15 and in `references.txt`, here is how to create a permanent, grader-accessible link for this session in under 3 minutes:

---

## Option A — Share via GitHub Gist or Google Drive Document (Recommended)

1. Open Google Docs or [GitHub Gist](https://gist.github.com/).
2. Create a new public document titled:
   `GCI World 2026 September Final Assignment — AI Assistance & Verification Log (Islam Raad)`
3. Copy and paste:
   - The contents of [`docs/work_log.md`](file:///home/islam-raad/Projects/Final%20Assignment/docs/work_log.md) (chronological log of all phases executed).
   - The contents of [`docs/decision_log.md`](file:///home/islam-raad/Projects/Final%20Assignment/docs/decision_log.md) (analytical and modeling decisions).
   - Or export the conversation transcript from `/home/islam-raad/.gemini/antigravity/brain/a6ab8d6c-67c1-4408-a05e-01f033d9e318/.system_generated/logs/transcript.jsonl`.
4. Set visibility to **Public / Anyone with the link can view**.
5. Copy the URL and replace `[REPLACE_WITH_SHARED_AI_CHAT_URL_BEFORE_SUBMISSION]` in [`references.txt`](file:///home/islam-raad/Projects/Final%20Assignment/references.txt).

---

## Option B — Share a Gemini / ChatGPT Web Conversation Link

1. Open [Gemini](https://gemini.google.com/) or [ChatGPT](https://chatgpt.com/).
2. Paste your prompt summarizing how you structured the EDA, feature engineering, label-shift prior correction, and two-lane retention strategy for Company A, and review the model's verification response.
3. Click **Share** $\to$ **Create public link**.
4. Paste that public URL into `[14]` of [`references.txt`](file:///home/islam-raad/Projects/Final%20Assignment/references.txt) and re-run `scripts/build_slides.py`.
