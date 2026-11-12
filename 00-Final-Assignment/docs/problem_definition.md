# Problem Definition — Company A Telecom Churn PoC

> **Task T4.3 & T4.4 (Feeds Slide 7 and Notebook Section 5):**

## 1. Executive Problem Statement (One Sentence)
> **"Company A is losing revenue-generating subscribers at predictable lifecycle cliffs and usage-decline moments, so we use machine learning to rank every customer's 31–60 day churn probability and focus finite retention budgets on the highest-risk, saveable customers before they leave."**

## 2. Full Problem Paragraph (4 Sentences for Non-Technical Executives)
Company A operates in a saturated wireless telecom market where acquiring a replacement subscriber costs several times more than keeping an existing one, yet churners and stayers have nearly identical average monthly bills ($58.21\text{ MU}$ vs. $59.22\text{ MU}$)—meaning untargeted retention discounts waste money on loyal customers. Exploratory analysis of Company A's 100,000 customer records reveals that churn risk concentrates around a sharp first-year contract/handset cliff (`eqpdays` crossing ~300 days and `months` 10–12, where sample churn jumps from ~37% to >60%) and multi-signal usage drops (`change_mou`, overage friction), while 1.6% of zero-usage subscribers (`mou_Mean == 0`) have already silently abandoned their SIMs. We formulate this as a **supervised binary classification and probability-ranking task** predicting `churn` (whether an active subscriber leaves within 31–60 days after observation),excluding sensitive demographic attributes (`ethnic`). The **Retention & CRM Team** acts on these monthly risk scores via a **Two-Lane Program**: (Lane 1) contacting only the riskiest top-$k^*$% active revenue-generating subscribers with targeted plan/loyalty saves, and (Lane 2) launching a randomized A/B pilot offering proactive handset upgrades at days 240–290 (months 8–9) before the 300-day cliff.

## 3. Operational Governance (`T4.4`)
- **Decision Owner:** Head of Customer Value Management (CVM) / Retention & CRM Operations at Company A.
- **Primary ML Metrics:** Out-of-sample **ROC-AUC** (overall ranking power across thresholds) and **Precision@k / Lift@k** (concentration of true churners in the targeted top-$k$% decile, evaluated both in-sample and re-based to 5%–10% real-world churn).
- **Primary Business KPI:** **Net Incremental Retained Value (in Monetary Units, MU)** and **Incremental Retention Lift (%)** measured against a randomized 20% holdout control group over a 90-day pilot.
