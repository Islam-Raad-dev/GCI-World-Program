"""Economic & label-shift re-basing functions for Company A Telecom PoC (PRD §9)."""
import numpy as np
import pandas as pd


def compute_topk_metrics(y_true: np.ndarray, y_prob: np.ndarray, k_pcts=(1, 2, 5, 10, 15, 20, 30, 50), pi_reals=(0.05, 0.10)):
    """
    Compute top-k% targeting table both in-sample (pi_s = y_true.mean()) and re-based
    under prior probability shift (label shift) to realistic priors pi_r in pi_reals.

    Under label shift where P(score | y) is invariant:
       Positive test rows receive weight w_1 = pi_r / pi_s
       Negative test rows receive weight w_0 = (1 - pi_r) / (1 - pi_s)
    Weighted precision in the top-k% of the test set (or top-k% of weighted population)
    estimates real-world precision. We compute both:
      - `precision_rebased_{int(pi_r*100)}`: Bayes/prior-shifted precision for the top-k% riskiest cohort
      - `lift_rebased_{int(pi_r*100)}`: precision_rebased / pi_r
    """
    y_true = np.asarray(y_true, dtype=float)
    y_prob = np.asarray(y_prob, dtype=float)
    n_total = len(y_true)
    pi_s = float(y_true.mean())

    order = np.argsort(-y_prob)
    y_sorted = y_true[order]
    p_sorted = y_prob[order]

    total_pos = float(y_sorted.sum())
    rows = []

    for k in k_pcts:
        n_k = max(1, int(round(n_total * (k / 100.0))))
        yk = y_sorted[:n_k]
        pk = p_sorted[:n_k]

        prec_sample = float(yk.mean())
        rec_sample = float(yk.sum() / total_pos) if total_pos > 0 else 0.0
        lift_sample = prec_sample / pi_s if pi_s > 0 else 0.0

        row = {
            "k_pct": k,
            "n_test_targeted": n_k,
            "n_base_100k_targeted": int(round(100000 * (k / 100.0))),
            "score_threshold": round(float(pk[-1]), 4),
            "precision_sample": round(prec_sample, 4),
            "recall_sample": round(rec_sample, 4),
            "lift_sample": round(lift_sample, 3),
        }

        for pi_r in pi_reals:
            w1 = pi_r / pi_s
            w0 = (1.0 - pi_r) / (1.0 - pi_s)
            weights_k = np.where(yk == 1, w1, w0)
            prec_reb = float((yk * weights_k).sum() / weights_k.sum())
            lift_reb = prec_reb / pi_r if pi_r > 0 else 0.0
            tag = int(round(pi_r * 100))
            row[f"precision_rebased_{tag}pct"] = round(prec_reb, 4)
            row[f"lift_rebased_{tag}pct"] = round(lift_reb, 3)

        rows.append(row)

    return rows


def compute_net_impact(
    n_base: int,
    k_pct: float,
    p_adj: float,
    s: float,
    arpu: float,
    margin: float,
    horizon_months: float,
    cost_per_target: float,
) -> dict:
    """
    PRD §9.1 Net impact formula:
      V = ARPU * margin * H
      n = (k_pct / 100) * n_base
      Gross Retained Value = n * p_adj * s * V
      Campaign Cost = n * c  (paid on ALL targeted customers, including false positives)
      Net Impact = Gross Retained Value - Campaign Cost
      Break-even success rate s* = c / (p_adj * V)
    """
    n_targeted = int(round(n_base * (k_pct / 100.0)))
    v_customer = float(arpu * margin * horizon_months)
    true_churners_in_target = float(n_targeted * p_adj)
    retained_customers = float(true_churners_in_target * s)
    gross_saved_mu = float(retained_customers * v_customer)
    total_cost_mu = float(n_targeted * cost_per_target)
    net_impact_mu = float(gross_saved_mu - total_cost_mu)
    roi_pct = float((net_impact_mu / total_cost_mu) * 100.0) if total_cost_mu > 0 else 0.0
    breakeven_s = float(cost_per_target / (p_adj * v_customer)) if (p_adj * v_customer) > 0 else 1.0

    return {
        "k_pct": k_pct,
        "n_targeted": n_targeted,
        "p_adj": round(p_adj, 4),
        "s": round(s, 4),
        "arpu_mu": round(arpu, 2),
        "margin": round(margin, 2),
        "horizon_months": horizon_months,
        "v_customer_mu": round(v_customer, 2),
        "cost_per_target_mu": round(cost_per_target, 2),
        "true_churners_targeted": round(true_churners_in_target, 1),
        "retained_customers": round(retained_customers, 1),
        "gross_saved_mu": round(gross_saved_mu, 0),
        "total_cost_mu": round(total_cost_mu, 0),
        "net_impact_mu": round(net_impact_mu, 0),
        "roi_pct": round(roi_pct, 1),
        "breakeven_s": round(breakeven_s, 4),
    }
