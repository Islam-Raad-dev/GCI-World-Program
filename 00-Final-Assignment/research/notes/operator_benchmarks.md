# Topic Note 2 — Operator Benchmarks in Iraq & MENA (`research/notes/operator_benchmarks.md`)

## Key Verified Facts
1. **Zain Iraq (`[4]`):**
   - Reported **17.9 million** active subscribers and **USD 974 million** in revenue in FY2023 (+20% YoY), expanding to **~19.3M–20.0M** subscribers and **USD 1.1B–1.2B** in FY2024 (`[4]`).
   - Holds roughly **37%–42%** of Iraq's mobile subscriber market.
2. **Asiacell (Ooredoo Group subsidiary) (`[5]`):**
   - Reported **17.69 million** subscribers and **QAR 4,452 million** revenue in FY2023 with blended ARPU of **24.8 QAR** (~USD 6.80/month), growing to **19.13 million** subscribers in FY2024 (+8.1% YoY) (`[5]`).
   - Holds roughly **38%–40%** of Iraq's mobile market.
3. **Korek Telecom & Market Dynamics (`[4]`, `[5]`):**
   - Regulatory and interconnection disputes between Korek Telecom and Iraq's Communications and Media Commission (CMC) triggered large subscriber migrations toward Zain Iraq and Asiacell, making retention of newly acquired and existing subscribers a top priority in 2024–2026.
4. **Industry Churn & ARPU Context (`[3]`, `[7]`, `[8]`):**
   - In real-world telecom operations, **monthly churn rates typically range from 1.5% to 3.0% per month** (or roughly **5% to 10% over a quarterly/campaign evaluation window**) (`[7]`, `[8]`).
   - By contrast, the GCI "Company A" dataset (`[13]`) is a **50/50 case-control sample** ($49.56\%$ churn, mean `rev_Mean` = $58.72\text{ MU/month}$), identical in structure to the Teradata Center at Duke University wireless churn benchmark documented by Neslin et al. (2006) (`[7]`).

## Strategic Implication ("So What" for Slides 2, 8, and 13)
Because Company A's dataset is a 50/50 case-control sample ($49.56\%$ churn) and uses US/North American wireless billing scale ($\text{ARPU} = 58.72\text{ MU}$), presenting raw sample profit calculations without adjustment would overstate campaign precision in an Iraqi/MENA production environment. Therefore, we report all financial figures in **Dataset Monetary Units (MU)** and explicitly **re-base top-$k\%$ precision to realistic $5\%$ and $10\%$ production churn priors** using Bayes' theorem (`[9]`).
