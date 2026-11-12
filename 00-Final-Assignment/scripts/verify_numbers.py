"""Task T10.8: Verify that every headline metric in outputs/results.json matches the rendered PDF slide deck."""
import json
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


def main() -> int:
    if not config.RESULTS_JSON.exists():
        print(f"ERROR: {config.RESULTS_JSON} not found.")
        return 1

    pdf_path = config.SLIDES_BUILD_DIR / f"{config.ACCOUNT_NAME}.pdf"
    if not pdf_path.exists():
        print(f"ERROR: {pdf_path} not found.")
        return 1

    with open(config.RESULTS_JSON, encoding="utf-8") as f:
        res = json.load(f)

    doc = fitz.open(pdf_path)
    full_pdf_text = "\n".join(page.get_text("text") for page in doc)

    fm = res["final_model"]
    tb = res["tutorial_baseline"]
    eda = res["eda"]
    topk10 = [r for r in res["topk"] if r["k_pct"] == 10][0]
    sc_map = {r["scenario"]: r for r in res["impact"]["scenarios_at_k10"]}

    checks = [
        ("Dataset total rows", f"{res['data']['n_rows']:,}"),
        ("Sample churn %", f"{res['data']['churn_rate']*100:.2f}%"),
        ("Tutorial Test Accuracy", f"{tb['test_acc']:.4f}"),
        ("Tutorial Test ROC-AUC", f"{tb['test_auc']:.4f}"),
        ("Final Model CV ROC-AUC", f"{fm['cv_auc_mean']:.4f}"),
        ("Final Model Test ROC-AUC", f"{fm['test_auc']:.4f}"),
        ("Final Model Test Accuracy", f"{fm['test_acc']:.4f}"),
        ("300-day jump pp", f"{eda['jump_300d']['train_diff_pp']:.2f}"),
        ("Month 9 train churn %", f"{eda['tenure_highlights']['month_9_train_churn']*100:.2f}%"),
        ("Month 11 peak train churn %", f"{eda['tenure_highlights']['month_11_train_churn']*100:.2f}%"),
        ("Zero-MOU churn %", f"{eda['usage_collapse'][0]['full_churn_rate']*100:.2f}%"),
        ("Top-10% Sample Precision %", f"{topk10['precision_sample']*100:.1f}%"),
        ("Top-10% Re-based (10% prior) Precision %", f"{topk10['precision_rebased_10pct']*100:.1f}%"),
        ("Base Case Net Impact at k=10%", f"{int(sc_map['Base Case']['net_impact_mu']):,}"),
        ("Conservative Net Impact at k=10%", f"{int(sc_map['Conservative']['net_impact_mu']):,}"),
        ("Optimistic Net Impact at k=10%", f"{int(sc_map['Optimistic']['net_impact_mu']):,}"),
    ]

    mismatches = 0
    for label, expected_str in checks:
        if expected_str in full_pdf_text:
            print(f"  [OK] {label}: '{expected_str}' found in PDF")
        else:
            print(f"  [MISMATCH] {label}: '{expected_str}' NOT found in PDF!")
            mismatches += 1

    if mismatches > 0:
        print(f"FAIL: {mismatches} number mismatches detected between results.json and PDF!")
        return 1

    print(f"PASS: 0 mismatches across {len(checks)} headline metrics between outputs/results.json and PDF.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
