# Topic Note 3 — Retention Economics & Profit-Driven Churn Modeling (`research/notes/retention_economics.md`)

## Key Verified Facts
1. **Retention vs. Acquisition Asymmetry (`[6]`):**
   - **Reichheld & Sasser (1990), *Harvard Business Review*** (`[6]`): Reducing customer defection rates by just **5 percentage points** increases service-company profits by **25% to 85%**, because customer acquisition costs (commissions, SIM provisioning, onboarding subsidies, marketing) are amortized over a longer relationship and retained subscribers generate predictable recurring margin.
2. **Defection Detection & Top-Decile Lift (`[7]`):**
   - **Neslin, Gupta, Kamakura, Lu, & Mason (2006), *Journal of Marketing Research*** (`[7]`): In their landmark tournament on wireless telecom churn, differences in predictive ranking accuracy (top-decile lift and AUC) directly translated into **hundreds of thousands of dollars in incremental campaign profit**, and gradient-boosted/tree-ensemble approaches exhibited strong temporal "staying power" across validation periods.
3. **Profit-Driven Top-$k\%$ Targeting vs. Threshold-0.5 Classification (`[8]`):**
   - **Verbeke, Dejaeger, Martens, Hur, & Baesens (2012), *European Journal of Operational Research*** (`[8]`): Across 11 real-world telecom operator datasets, evaluating models by profit maximization at an optimal top-$k\%$ contact fraction consistently outperforms naive 0.5-threshold accuracy classification because contacting false positives wastes retention incentives ($c$ per targeted customer).
4. **Prior-Shift Correction for Case-Control Samples (`[9]`):**
   - **Saerens, Latinne, & Decaestecker (2002), *Neural Computation*** (`[9]`): When a classifier is evaluated on a balanced sample with prior $\pi_s = 0.4956$ and deployed in a production population with prior $\pi_r \in \{0.05, 0.10\}$, the true production precision at top-$k\%$ is given by:
     $$P_r = \frac{P_s \cdot \frac{\pi_r}{\pi_s}}{P_s \cdot \frac{\pi_r}{\pi_s} + (1 - P_s) \cdot \frac{1 - \pi_r}{1 - \pi_s}}$$

## Strategic Implication ("So What" for Slides 7, 8, 11, and 13)
This literature provides the exact theoretical backbone for our PoC:
- Why we rank customers by churn probability $\hat{p}_i$ and target the **top-$k\%$** instead of applying a flat `0.5` cutoff (`[8]`).
- Why we evaluate both **raw sample economics** ($\pi_s = 49.56\%$) and **label-shift re-based economics** ($\pi_r = 10\%$ and $\pi_r = 5\%$) (`[9]`).
