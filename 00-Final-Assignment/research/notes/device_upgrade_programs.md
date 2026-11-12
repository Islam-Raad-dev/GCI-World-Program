# Topic Note 4 — Device Upgrade Programs & Lifecycle Retention (`research/notes/device_upgrade_programs.md`)

## Key Verified Facts
1. **First-Year Contract Renewal & Device Aging Dynamics (`[7]`, `[8]`, `[13]`):**
   - In wireless telecommunications, subscriber contracts and promotional bundles commonly follow 12-month or 24-month cycles (`[7]`, `[13]`).
   - In the Company A dataset (`[13]`), `eqpdays` (days on current handset) and `months` (total account tenure) are linked on a subscriber's first device (`eqpdays ≈ 30 × months`), producing a dual spike:
     - **Tenure Month 10–12 Renewal Cliff:** Churn doubles from **29.25%** at Month 9 to **64.57%** at Month 11 (training split).
     - **Handset Age >300 Days Persistent Elevation:** Even among mature subscribers past their first year (`months` in 13–18m, 19–24m, 25m+), subscribers who upgraded their handset (`eqpdays ≤ 200d`) churn at **15 to 24 percentage points lower rates** than same-tenure peers still using an aging handset (`eqpdays > 300d`).
2. **Two-Lane Retention Intervention Design (`[7]`, `[8]`):**
   - Telecom CRM literature (`[7]`, `[8]`) distinguishes between:
     - **Proactive lifecycle / device-trade-in interventions** timed *before* the renewal decision window (Month 8–9 / `eqpdays` 240–270 days), when customer satisfaction is still intact and a small loyalty bundle or trade-in voucher locks in another 12-month cycle.
     - **Behavioral usage-rescue interventions** triggered when a high-value subscriber's recent 3-month minutes (`change_mou < 0`, `mou_to_avg3_ratio < 0.7`) drop sharply relative to their 3-month baseline — catching "silent disengagement" *before* the account reaches zero usage (`mou_Mean == 0`, where churn hits 79.81% and ARPU has already collapsed to 23.11 MU).

## Strategic Implication ("So What" for Slides 4, 5, and 12)
Separating the **Month 8–9 First-Year Renewal & Device-Refresh Lane (Lane 1)** from the **High-Value Usage-Slump Rescue Lane (Lane 2)** directly addresses the tenure-device entanglement discovered in our EDA and avoids wasting handset subsidies on dormant low-ARPU SIMs.
