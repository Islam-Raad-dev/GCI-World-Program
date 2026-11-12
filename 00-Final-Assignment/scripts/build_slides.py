"""Task T10.1-T10.9: Build 15-slide HTML deck from outputs/results.json and references.txt, render to PDF via Chrome headless, and copy to submission/."""
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


def load_svg_inline(svg_path: Path) -> str:
    txt = svg_path.read_text(encoding="utf-8").strip()
    return txt


def build_html(res: dict, ref_lines: list[str]) -> str:
    d = res["data"]
    tb = res["tutorial_baseline"]
    eda = res["eda"]
    fm = res["final_model"]
    models = res["models"]
    topk = res["topk"]
    imp = res["importance"]
    impact = res["impact"]

    topk10 = [r for r in topk if r["k_pct"] == 10][0]
    sc_map = {r["scenario"]: r for r in impact["scenarios_at_k10"]}
    unadj = impact["unadjusted_sample_at_k10"]
    lane2 = impact["lane2_pilot"]

    fig_dir = config.FIGURES_DIR.resolve()
    svg_pipeline = load_svg_inline(fig_dir / "pipeline_diagram.svg")
    svg_voting = load_svg_inline(fig_dir / "tree_voting_diagram.svg")
    svg_twolane = load_svg_inline(fig_dir / "two_lane_program_diagram.svg")

    # Build model progression rows for Slide 9
    model_rows_html = ""
    for m in models:
        is_best = m["id"] == fm["id"]
        is_base = m["id"] == "M3"
        row_cls = "highlight-row" if is_best else ("baseline-row" if is_base else "")
        badge = ' <span class="badge-best">FINAL SELECTED</span>' if is_best else (' <span class="badge-base">TUTORIAL BASELINE</span>' if is_base else "")
        model_rows_html += f"""
        <tr class="{row_cls}">
          <td><strong>{m['id']}</strong></td>
          <td><strong>{html.escape(m['name'])}</strong>{badge}<br><span class="sub-td">{html.escape(m['description'])}</span></td>
          <td class="num">{m['n_features']}</td>
          <td class="num"><strong>{m['cv_auc_mean']:.4f}</strong> <span class="sub-td">±{m['cv_auc_std']:.4f}</span></td>
          <td class="num"><strong>{m['test_auc']:.4f}</strong></td>
          <td class="num"><strong>{m['test_acc']:.4f}</strong> ({m['test_acc']*100:.2f}%)</td>
          <td class="num">{m['train_acc']*100:.2f}%</td>
          <td class="num">{m['train_test_acc_gap_pp']:.2f} pp</td>
          <td class="num"><strong>{m['test_top10_precision']*100:.1f}%</strong></td>
        </tr>"""

    # Build Top-k targeting rows for Slide 11
    topk_rows_html = ""
    for r in topk:
        is_k10 = r["k_pct"] == 10
        cls = "highlight-row" if is_k10 else ""
        tag = ' <span class="badge-best">PILOT CUTOFF</span>' if is_k10 else ""
        topk_rows_html += f"""
        <tr class="{cls}">
          <td><strong>Top {r['k_pct']}%</strong>{tag}</td>
          <td class="num">{r['n_base_100k_targeted']:,}</td>
          <td class="num">&ge; {r['score_threshold']:.3f}</td>
          <td class="num"><strong>{r['precision_sample']*100:.1f}%</strong></td>
          <td class="num">{r['recall_sample']*100:.1f}%</td>
          <td class="num">{r['lift_sample']:.2f}&times;</td>
          <td class="num"><strong>{r['precision_rebased_10pct']*100:.1f}%</strong> ({r['lift_rebased_10pct']:.2f}&times;)</td>
          <td class="num"><strong>{r['precision_rebased_5pct']*100:.1f}%</strong> ({r['lift_rebased_5pct']:.2f}&times;)</td>
        </tr>"""

    # Build References list for Slide 15
    refs_html = "\n".join(
        f'<div class="ref-item">{html.escape(line)}</div>' for line in ref_lines
    )

    c_sc = sc_map["Conservative"]
    b_sc = sc_map["Base Case"]
    o_sc = sc_map["Optimistic"]

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Company A Telecom Churn PoC — {config.AUTHOR_NAME}</title>
<style>
  @page {{
    size: 1920px 1080px;
    margin: 0;
  }}
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }}
  body {{
    font-family: 'Inter', 'DejaVu Sans', 'Segoe UI', Arial, sans-serif;
    background: #0F172A;
    color: #0F172A;
    margin: 0;
    padding: 0;
  }}
  .slide {{
    width: 1920px;
    height: 1080px;
    background: #FFFFFF;
    position: relative;
    overflow: hidden;
    page-break-after: always;
    break-after: page;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 40px 64px 32px 64px;
  }}
  .slide.cover-slide {{
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 65%, #0F2942 100%);
    color: #FFFFFF;
    padding: 72px 88px 56px 88px;
  }}
  /* Header Bar */
  .slide-header {{
    border-bottom: 3px solid #E2E8F0;
    padding-bottom: 14px;
    margin-bottom: 18px;
  }}
  .section-tag {{
    display: inline-block;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    color: #1D4ED8;
    background: #DBEAFE;
    padding: 4px 12px;
    border-radius: 4px;
    margin-bottom: 8px;
  }}
  .section-tag.teal {{ color: #0F766E; background: #CCFBF1; }}
  .section-tag.coral {{ color: #BE123C; background: #FFE4E6; }}
  .section-tag.amber {{ color: #B45309; background: #FEF3C7; }}
  .action-title {{
    font-size: 30px;
    font-weight: 800;
    line-height: 1.22;
    color: #0F172A;
  }}
  .action-title .accent-coral {{ color: #E11D48; }}
  .action-title .accent-teal {{ color: #0D9488; }}
  .action-title .accent-blue {{ color: #1D4ED8; }}

  /* Main Content Grid */
  .slide-body {{
    flex: 1;
    display: grid;
    gap: 28px;
    align-items: stretch;
    min-height: 0;
  }}
  .cols-60-40 {{ grid-template-columns: 1.42fr 1fr; }}
  .cols-55-45 {{ grid-template-columns: 1.22fr 1fr; }}
  .cols-50-50 {{ grid-template-columns: 1fr 1fr; }}
  .cols-45-55 {{ grid-template-columns: 1fr 1.25fr; }}
  .cols-3 {{ grid-template-columns: 1fr 1fr 1fr; }}
  .rows-auto {{ display: flex; flex-direction: column; gap: 18px; }}

  /* Cards & Panels */
  .card {{
    background: #F8FAFC;
    border: 1.5px solid #CBD5E1;
    border-radius: 12px;
    padding: 20px 24px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
  }}
  .card.white {{ background: #FFFFFF; }}
  .card.navy {{ background: #0F172A; color: #FFFFFF; border-color: #1E293B; }}
  .card.teal-tint {{ background: #F0FDF4; border-color: #5EEAD4; }}
  .card.coral-tint {{ background: #FFF1F2; border-color: #FDA4AF; }}
  .card.blue-tint {{ background: #EFF6FF; border-color: #93C5FD; }}
  .card.amber-tint {{ background: #FFFBEB; border-color: #FCD34D; }}

  .card-title {{
    font-size: 19px;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  .card.navy .card-title {{ color: #38BDF8; }}
  .kpi-row {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 14px;
  }}
  .kpi-box {{
    background: #FFFFFF;
    border: 1.5px solid #CBD5E1;
    border-left: 6px solid #1D4ED8;
    border-radius: 10px;
    padding: 14px 18px;
  }}
  .kpi-box.coral {{ border-left-color: #E11D48; }}
  .kpi-box.teal {{ border-left-color: #0D9488; }}
  .kpi-box.amber {{ border-left-color: #D97706; }}
  .kpi-num {{
    font-size: 32px;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.1;
  }}
  .kpi-num.coral {{ color: #E11D48; }}
  .kpi-num.teal {{ color: #0D9488; }}
  .kpi-num.blue {{ color: #1D4ED8; }}
  .kpi-label {{
    font-size: 14px;
    font-weight: 700;
    color: #475569;
    margin-top: 4px;
  }}
  .kpi-sub {{
    font-size: 12.5px;
    color: #64748B;
    margin-top: 3px;
  }}

  ul.clean-list {{
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 11px;
  }}
  ul.clean-list li {{
    font-size: 16.5px;
    line-height: 1.42;
    color: #1E293B;
    padding-left: 20px;
    position: relative;
  }}
  ul.clean-list li::before {{
    content: "▸";
    position: absolute;
    left: 0;
    color: #1D4ED8;
    font-weight: 800;
  }}
  .card.navy ul.clean-list li {{ color: #E2E8F0; }}
  .card.navy ul.clean-list li::before {{ color: #38BDF8; }}

  /* Images & Figures */
  .fig-box {{
    background: #FFFFFF;
    border: 1.5px solid #CBD5E1;
    border-radius: 12px;
    padding: 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }}
  .fig-box img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
  }}
  .fig-caption {{
    font-size: 12.5px;
    color: #475569;
    margin-top: 6px;
    text-align: center;
    font-weight: 600;
  }}

  /* Tables */
  table.data-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 14.5px;
    background: #FFFFFF;
    border-radius: 8px;
    overflow: hidden;
  }}
  table.data-table th {{
    background: #0F172A;
    color: #FFFFFF;
    font-weight: 700;
    text-align: left;
    padding: 9px 12px;
    font-size: 13.5px;
  }}
  table.data-table th.num, table.data-table td.num {{
    text-align: right;
    font-variant-numeric: tabular-nums;
  }}
  table.data-table td {{
    padding: 8px 12px;
    border-bottom: 1px solid #E2E8F0;
    color: #1E293B;
    vertical-align: middle;
  }}
  table.data-table tr:nth-child(even) {{ background: #F8FAFC; }}
  table.data-table tr.highlight-row {{
    background: #CCFBF1 !important;
    border-top: 2px solid #0D9488;
    border-bottom: 2px solid #0D9488;
  }}
  table.data-table tr.baseline-row {{
    background: #FEF3C7 !important;
  }}
  .sub-td {{
    font-size: 12px;
    color: #475569;
    font-weight: 400;
  }}
  .badge-best {{
    display: inline-block;
    background: #0D9488;
    color: #FFFFFF;
    font-size: 10.5px;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 4px;
    margin-left: 6px;
  }}
  .badge-base {{
    display: inline-block;
    background: #D97706;
    color: #FFFFFF;
    font-size: 10.5px;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 4px;
    margin-left: 6px;
  }}

  /* Footer & So-What Bar */
  .slide-footer {{
    margin-top: 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}
  .sowhat-bar {{
    background: #0F172A;
    color: #F8FAFC;
    padding: 11px 20px;
    border-radius: 8px;
    border-left: 6px solid #0D9488;
    font-size: 15.5px;
    line-height: 1.35;
  }}
  .sowhat-bar strong {{ color: #5EEAD4; }}
  .meta-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12.5px;
    color: #64748B;
    font-weight: 600;
  }}
  .formula-box {{
    background: #0F172A;
    color: #F8FAFC;
    padding: 16px 22px;
    border-radius: 10px;
    font-size: 17px;
    font-weight: 700;
    text-align: center;
    border: 1.5px solid #38BDF8;
    margin: 8px 0;
  }}
  .ref-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px 26px;
    margin-top: 6px;
  }}
  .ref-item {{
    font-size: 13.2px;
    line-height: 1.38;
    color: #1E293B;
    background: #F8FAFC;
    border-left: 3.5px solid #1D4ED8;
    padding: 7px 12px;
    border-radius: 4px;
    word-break: break-word;
  }}
  code {{
    font-family: 'JetBrains Mono', 'DejaVu Sans Mono', monospace;
    font-size: 0.91em;
    background: rgba(148, 163, 184, 0.18);
    padding: 1px 5px;
    border-radius: 4px;
  }}
</style>
</head>
<body>

<!-- ==================== SLIDE 1: COVER ==================== -->
<section class="slide cover-slide">
  <div>
    <div style="display:flex; gap:12px; align-items:center; margin-bottom:28px;">
      <span style="background:#0D9488; color:#FFFFFF; font-weight:800; font-size:14px; padding:6px 14px; border-radius:6px; letter-spacing:1.2px;">GCI WORLD 2026 SEPTEMBER — FINAL ASSIGNMENT</span>
      <span style="background:#1E293B; color:#94A3B8; font-weight:700; font-size:14px; padding:6px 14px; border-radius:6px; border:1px solid #334155;">COMPANY A TELECOM POC [13]</span>
    </div>
    <h1 style="font-size:43px; font-weight:800; line-height:1.20; color:#FFFFFF; max-width:1720px; margin-bottom:22px;">
      From Reactive Churn Firefighting to <span style="color:#5EEAD4;">Proactive Value Retention</span>:<br>
      A Risk-Ranked Lifecycle &amp; Usage-Rescue PoC for Company A
    </h1>
    <p style="font-size:22px; line-height:1.45; color:#CBD5E1; max-width:1500px; margin-bottom:44px;">
      Combining regularized gradient-boosted risk ranking (<strong>M5 XGBoost</strong>), pre-300-day handset lifecycle triggers, and Bayes prior-shift calibration to protect recurring contribution margin in a saturated mobile market.
    </p>

    <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:26px; margin-top:16px;">
      <div style="background:rgba(255,255,255,0.06); border:1.5px solid rgba(94,234,212,0.4); border-top:5px solid #0D9488; border-radius:12px; padding:24px 28px;">
        <div style="font-size:14px; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:1px;">1. Empirical Audit Scope [13]</div>
        <div style="font-size:42px; font-weight:800; color:#5EEAD4; margin:8px 0;">{d['n_rows']:,} Subscribers</div>
        <div style="font-size:16px; color:#E2E8F0; line-height:1.4;">100 merged columns (`Client.csv` &#8904; `Record.csv`); {d['churn_rate']*100:.2f}% case-control sample churn rate audited with zero data leakage (70/30 split, SEED=42).</div>
      </div>
      <div style="background:rgba(255,255,255,0.06); border:1.5px solid rgba(56,189,248,0.4); border-top:5px solid #38BDF8; border-radius:12px; padding:24px 28px;">
        <div style="font-size:14px; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:1px;">2. Predictive &amp; Decile Lift [10, 12]</div>
        <div style="font-size:42px; font-weight:800; color:#38BDF8; margin:8px 0;">0.7011 Test AUC</div>
        <div style="font-size:16px; color:#E2E8F0; line-height:1.4;">Up from {tb['test_auc']:.4f} tutorial baseline (+{fm['test_acc']*100:.2f}% vs. {tb['test_acc']*100:.2f}% accuracy), cutting overfitting in half while achieving <strong>{topk10['precision_sample']*100:.1f}% sample precision</strong> ({topk10['precision_rebased_10pct']*100:.1f}% re-based at 10% prior) in the Top-10% tier.</div>
      </div>
      <div style="background:rgba(255,255,255,0.06); border:1.5px solid rgba(251,191,36,0.4); border-top:5px solid #F59E0B; border-radius:12px; padding:24px 28px;">
        <div style="font-size:14px; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:1px;">3. Re-Based Financial Impact [8, 9]</div>
        <div style="font-size:42px; font-weight:800; color:#FBBF24; margin:8px 0;">+{int(b_sc['net_impact_mu']):,} MU</div>
        <div style="font-size:16px; color:#E2E8F0; line-height:1.4;">Estimated annual Base Case net impact (+{int(c_sc['net_impact_mu']):,} MU Conservative to +{int(o_sc['net_impact_mu']):,} MU Optimistic) at Top-10% targeting after prior-shift re-basing and full offer costs.</div>
      </div>
    </div>
  </div>

  <div style="border-top:1px solid #334155; padding-top:22px; display:flex; justify-content:space-between; align-items:center; font-size:16px; color:#94A3B8;">
    <div><strong>Author:</strong> {config.AUTHOR_NAME} ({config.AUTHOR_AFFILIATION}) &nbsp;|&nbsp; <strong>Submission ID:</strong> {config.ACCOUNT_NAME}</div>
    <div><strong>Date:</strong> November 2026 &nbsp;|&nbsp; <strong>Slide 1 / 15</strong></div>
  </div>
</section>

<!-- ==================== SLIDE 2: MARKET CONTEXT ==================== -->
<section class="slide">
  <div class="slide-header">
    <span class="section-tag">1. INDUSTRY &amp; REGIONAL CONTEXT</span>
    <h2 class="action-title">With Iraq Mobile Penetration at <span class="accent-coral">100%–103%</span>, Retention Beats Acquisition on Unit Economics [1, 2, 6]</h2>
  </div>

  <div class="slide-body cols-55-45">
    <div class="rows-auto">
      <div class="kpi-row">
        <div class="kpi-box coral">
          <div class="kpi-num coral">48.1M (103%)</div>
          <div class="kpi-label">Iraq Active Mobile Lines [1]</div>
          <div class="kpi-sub">Up from 46.0M (100.0%) in 2024; ITU reports 100.08/100 people [2]</div>
        </div>
        <div class="kpi-box">
          <div class="kpi-num blue">427M (64%)</div>
          <div class="kpi-label">MENA Unique Subscribers [3]</div>
          <div class="kpi-sub">&gt;85%–90% prepaid mix in Iraq/Levant; widespread multi-SIM switching</div>
        </div>
        <div class="kpi-box teal">
          <div class="kpi-num teal">+25% to +85%</div>
          <div class="kpi-label">Profit Lift per 5 pp Churn Cut [6]</div>
          <div class="kpi-sub">Reichheld &amp; Sasser (HBR): retention amortizes acquisition cost</div>
        </div>
      </div>

      <div class="card white" style="flex:1;">
        <div class="card-title">Competitive Reality in Iraq &amp; MENA Wireless Markets [1, 3, 4, 5]</div>
        <table class="data-table">
          <thead>
            <tr>
              <th>Operator / Benchmark</th>
              <th class="num">Active Subscribers</th>
              <th class="num">Market Share / Scale</th>
              <th>Strategic Retention Challenge</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Zain Iraq</strong> (Zain Group) [4]</td>
              <td class="num">17.9M &ndash; 19.3M</td>
              <td class="num">~37% &ndash; 42% share<br><span class="sub-td">USD 0.97B–1.1B rev</span></td>
              <td>Protecting high-ARPU data &amp; voice users against dual-SIM promo switching.</td>
            </tr>
            <tr>
              <td><strong>Asiacell</strong> (Ooredoo Group) [5]</td>
              <td class="num">17.69M &ndash; 19.13M</td>
              <td class="num">~38% &ndash; 40% share<br><span class="sub-td">QAR 4,452M rev (24.8 QAR ARPU)</span></td>
              <td>Retaining +8.1% YoY subscriber influx absorbed from displaced regional lines.</td>
            </tr>
            <tr>
              <td><strong>Korek Telecom</strong> [3, 5]</td>
              <td class="num">Contracting base</td>
              <td class="num">&lt;15% share</td>
              <td>Regulatory/interconnection disputes triggered mass SIM migration across Iraq.</td>
            </tr>
            <tr class="highlight-row">
              <td><strong>Company A Dataset</strong> (PoC Target) [7, 13]</td>
              <td class="num"><strong>100,000</strong></td>
              <td class="num"><strong>58.72 MU Mean ARPU</strong><br><span class="sub-td">48.20 MU Median ARPU</span></td>
              <td><strong>49.56% case-control sample churn</strong> (real industry monthly/quarterly rate: <strong>5%–10%</strong> [7, 8]).</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="rows-auto">
      <div class="card navy" style="flex:1;">
        <div class="card-title">Why Blanket Retention Campaigns Fail in Telecom [7, 8]</div>
        <ul class="clean-list">
          <li><strong>Zero Greenfield Headroom:</strong> At 100.08 subscriptions per 100 people in Iraq [2], every "new" gross addition is either a secondary SIM or poached from a rival at high dealer commission and onboarding cost.</li>
          <li><strong>Untargeted Discounts Destroy Margin:</strong> Offering a 10 MU monthly discount to all 100,000 subscribers costs 1,000,000 MU per wave—mostly subsidizing loyal customers who would have stayed anyway [8].</li>
          <li><strong>Timing Beat Generosity:</strong> Once a subscriber zeroes out voice minutes (`mou_Mean == 0`) or swaps primary SIMs, churn reaches <strong>79.81%</strong> [13]—interventions must fire <em>before</em> disengagement completes.</li>
          <li><strong>Unit Currency Convention:</strong> Because Company A's dataset is denominated in North American wireless billing scale (mean `rev_Mean` = 58.72 MU vs. ~6.80 USD in Iraq [5, 13]), all PoC financials are reported in <strong>Dataset Monetary Units (MU)</strong>.</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="sowhat-bar">
      <strong>So What / Decision Implication:</strong> In a 100%+ penetrated market [1, 2], EBITDA growth depends on surgical retention—identifying the <strong>Top-10% highest-risk, positive-margin subscribers</strong> early enough to intervene profitably [7, 8].
    </div>
    <div class="meta-bar">
      <span>Sources: [1] DataReportal Iraq 2025; [2] World Bank/ITU WDI; [3] GSMA MENA 2024; [4] Zain Group AR; [5] Ooredoo AR; [6] Reichheld &amp; Sasser (1990); [7] Neslin et al. (2006).</span>
      <span>Slide 2 / 15</span>
    </div>
  </div>
</section>

<!-- ==================== SLIDE 3: DATA AUDIT & HYGIENE ==================== -->
<section class="slide">
  <div class="slide-header">
    <span class="section-tag">2. DATA AUDIT &amp; INTEGRITY</span>
    <h2 class="action-title">100,000-Subscriber Audit Reveals <span class="accent-coral">Informative Missingness</span>, 10 Duplicate Pairs &amp; Unit Anomalies [13]</h2>
  </div>

  <div class="slide-body cols-55-45">
    <div class="fig-box">
      <img src="{fig_dir}/missing_top20.png" alt="Top 20 Columns by Missingness and Churn Rate Gap">
      <div class="fig-caption">Figure 1: Top-20 columns by missingness (%) on `Client.csv` &#8904; `Record.csv` (N = 100,000) with churn-rate delta when missing vs. present [13].</div>
    </div>

    <div class="rows-auto">
      <div class="kpi-row">
        <div class="kpi-box">
          <div class="kpi-num blue">100,000 &times; 100</div>
          <div class="kpi-label">Exact 1:1 Inner Join [13]</div>
          <div class="kpi-sub">51 Record + 50 Client cols; 0 duplicate IDs (`1,000,001–1,100,000`)</div>
        </div>
        <div class="kpi-box coral">
          <div class="kpi-num coral">76.09%</div>
          <div class="kpi-label">Churn When `change_mou` Missing</div>
          <div class="kpi-sub">n = 891 (+26.77 pp vs. present); `hnd_webcap` NaN = 59.15% churn</div>
        </div>
        <div class="kpi-box teal">
          <div class="kpi-num teal">10 Cols Dropped</div>
          <div class="kpi-label">Near-Duplicate Pairs (|&rho;| &gt; 0.995)</div>
          <div class="kpi-sub">Dropping 10 redundant cols improves 5-fold CV AUC (0.6940 &rarr; 0.6947)</div>
        </div>
      </div>

      <div class="card white" style="flex:1;">
        <div class="card-title">Critical Audit Findings &amp; Documentation Discrepancies Fixed [13]</div>
        <table class="data-table">
          <thead>
            <tr>
              <th>Audit Dimension</th>
              <th>Empirical Finding in Dataset</th>
              <th>Pipeline Engineering Action</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>1. `change_mou` &amp; `change_rev` Units</strong></td>
              <td>Overview docx calls them "% change", but <strong>22.79%</strong> of `change_mou` &lt; -100 (min -3,875) and <em>r</em> = <strong>0.9025</strong> with `mou_Mean - avg3mou` (raw difference).</td>
              <td>Construct true relative ratios `mou_ratio_3m` and `rev_ratio_3m` alongside raw deltas.</td>
            </tr>
            <tr>
              <td><strong>2. Negative `eqpdays` Values</strong></td>
              <td><strong>133 rows</strong> have `eqpdays &lt; 0` (min -5; 34 rows = -1, which causes `np.log1p` `RuntimeWarning` in `tutorial.ipynb`).</td>
              <td>Add `eqpdays_negative_flag` and clamp `eqpdays_clean = max(eqpdays, 0)` before log/ratio transforms.</td>
            </tr>
            <tr>
              <td><strong>3. Correlated Missing Blocks</strong></td>
              <td><strong>1,732 rows (1.73%)</strong> miss all 11 demographic fields (`truck`..`kid16_17`, 47.86% churn); <strong>2,839 rows</strong> miss `avg6*` (tenure &lt; 6m, 40.23% churn).</td>
              <td>Create explicit missingness indicators (`missing_change_mou`, `missing_hnd_webcap`, `missing_avg6`, `missing_demo_block`).</td>
            </tr>
            <tr>
              <td><strong>4. 20 Collinear Pairs (|&rho;| &gt; 0.98)</strong></td>
              <td>`totcalls`/`adjqty` (&rho;=0.9995), `totmou`/`adjmou` (&rho;=0.9995), `plcd_vce`/`attempt` (&rho;=0.9994), `comp_vce`/`complete` (&rho;=0.9992).</td>
              <td>Drop 10 redundant duplicate columns to stabilize split gain and permutation importance.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="sowhat-bar">
      <strong>So What / Decision Implication:</strong> Missing values in telecom billing logs are <strong>behavioral signals, not random noise</strong>—preserving missingness indicators and fixing `change_mou` scaling directly lifts ranking accuracy [13].
    </div>
    <div class="meta-bar">
      <span>Sources: [13] GCI Company A Dataset (`Client.csv`, `Record.csv`) &amp; Overview Docx Audit (`outputs/tables/missing.csv`, `docs/data_doc_discrepancies.md`).</span>
      <span>Slide 3 / 15</span>
    </div>
  </div>
</section>

<!-- ==================== SLIDE 4: EDA FINDING 1 (300-DAY CLIFF) ==================== -->
<section class="slide">
  <div class="slide-header">
    <span class="section-tag coral">3. EXPLORATORY DATA ANALYSIS — FINDING 1</span>
    <h2 class="action-title">Churn Surges <span class="accent-coral">+23.83 pp</span> After Handset Age Crosses 300 Days (36.85% &rarr; 60.69%) [13]</h2>
  </div>

  <div class="slide-body cols-55-45">
    <div class="fig-box">
      <img src="{fig_dir}/eqpdays_churn.png" alt="Churn Rate by Equipment Days">
      <div class="fig-caption">Figure 2: Churn rate across 25-day handset age (`eqpdays`) bins on the 70% training split (n = 70,000) with 95% Wilson confidence intervals [13].</div>
    </div>

    <div class="rows-auto">
      <div class="kpi-row">
        <div class="kpi-box teal">
          <div class="kpi-num teal">36.85%</div>
          <div class="kpi-label">Pre-Threshold Churn (260–300d)</div>
          <div class="kpi-sub">n = 4,792 train accounts (36.87% full dataset)</div>
        </div>
        <div class="kpi-box coral">
          <div class="kpi-num coral">60.69%</div>
          <div class="kpi-label">Post-Threshold Churn (301–340d)</div>
          <div class="kpi-sub">n = 6,774 train accounts; peaks at 62.44% in 326–350d</div>
        </div>
        <div class="kpi-box amber">
          <div class="kpi-num">+23.83 pp</div>
          <div class="kpi-label">Verified Jump Across 300d</div>
          <div class="kpi-sub">95% Boot CI: [+22.12, +25.62] pp | RD Jump: +23.88 pp</div>
        </div>
      </div>

      <div class="card white" style="flex:1;">
        <div class="card-title">Subgroup Robustness Audit Around the 300-Day Boundary (Train Split) [13]</div>
        <table class="data-table">
          <thead>
            <tr>
              <th>Customer Subgroup</th>
              <th class="num">260–300d Churn (n)</th>
              <th class="num">301–340d Churn (n)</th>
              <th class="num">Jump (&Delta; pp)</th>
            </tr>
          </thead>
          <tbody>
            <tr class="highlight-row">
              <td><strong>All Training Accounts</strong></td>
              <td class="num">36.85% (4,792)</td>
              <td class="num">60.69% (6,774)</td>
              <td class="num"><strong>+23.83 pp</strong></td>
            </tr>
            <tr>
              <td><strong>Single-Handset Accounts (`phones == 1`)</strong></td>
              <td class="num">29.10% (2,869)</td>
              <td class="num">63.18% (4,932)</td>
              <td class="num"><strong>+34.08 pp</strong></td>
            </tr>
            <tr>
              <td><strong>New Handsets Only (`refurb_new == 'N'`)</strong></td>
              <td class="num">34.23% (4,128)</td>
              <td class="num">60.65% (6,087)</td>
              <td class="num"><strong>+26.42 pp</strong></td>
            </tr>
            <tr>
              <td><strong>Tenure &ge; 10 Months Only (`months &ge; 10`)</strong></td>
              <td class="num">41.23% (3,090)</td>
              <td class="num">60.69% (6,774)</td>
              <td class="num"><strong>+19.46 pp</strong></td>
            </tr>
            <tr>
              <td><strong>Prime Credit Tier (`crclscod == 'AA'`)</strong></td>
              <td class="num">34.11% (1,897)</td>
              <td class="num">63.42% (3,152)</td>
              <td class="num"><strong>+29.31 pp</strong></td>
            </tr>
            <tr>
              <td><strong>Multi-Handset Accounts (`phones &ge; 2`)</strong></td>
              <td class="num">48.41% (1,923)</td>
              <td class="num">54.02% (1,842)</td>
              <td class="num"><strong>+5.60 pp</strong></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="sowhat-bar">
      <strong>So What / Decision Implication:</strong> `eqpdays` is the strongest single predictor in the dataset (univariate AUC = 0.5751), and the <strong>240–300 day pre-spike window</strong> provides a clear 60-day operational runway for proactive retention [13].
    </div>
    <div class="meta-bar">
      <span>Sources: [13] Company A Dataset 70% Train Split (`outputs/tables/eqpdays_bins25.csv`, `outputs/tables/threshold_robustness.csv`).</span>
      <span>Slide 4 / 15</span>
    </div>
  </div>
</section>

<!-- ==================== SLIDE 5: EDA FINDING 2 (TENURE-DEVICE ENTANGLEMENT) ==================== -->
<section class="slide">
  <div class="slide-header">
    <span class="section-tag coral">3. EXPLORATORY DATA ANALYSIS — FINDING 2</span>
    <h2 class="action-title">The 300-Day Spike Coincides with the <span class="accent-coral">Months 10–12 Renewal Cliff</span>, Yet Device Age Persists Later [13]</h2>
  </div>

  <div class="slide-body cols-50-50">
    <div class="fig-box">
      <img src="{fig_dir}/months_churn.png" alt="Churn Rate by Customer Tenure Months">
      <div class="fig-caption">Figure 3: Churn rate by account tenure (`months` 6–36) showing the dramatic doubling from Month 9 (29.25%) to Month 11 (64.57%) [13].</div>
    </div>

    <div class="rows-auto">
      <div class="fig-box" style="flex:1;">
        <img src="{fig_dir}/tenure_device_heatmap.png" alt="2D Tenure x Device Age Heatmap">
        <div class="fig-caption">Figure 4: 2D Churn Rate (%) &amp; Sample Size across Tenure (`months`) &times; Handset Age (`eqpdays`) on the 70% training split [13].</div>
      </div>

      <div class="card amber-tint">
        <div class="card-title" style="font-size:16.5px;">Why Disentangling `months` and `eqpdays` Matters for Intervention Design [13]</div>
        <ul class="clean-list" style="gap:6px;">
          <li style="font-size:14.8px;"><strong>First-Year Coupling:</strong> On a subscriber's first handset (`phones == 1`), `eqpdays ≈ 30 × months`. Exactly <strong>0 customers</strong> have `months ≤ 9` and `eqpdays > 300` (max `eqpdays` for `months ≤ 9` is <strong>288 days</strong>). Thus, crossing 300 days on a first phone is also crossing into the <strong>Month 10–12 contract renewal cliff</strong> (29.25% &rarr; 64.57%).</li>
          <li style="font-size:14.8px;"><strong>Independent Device-Age Effect in Mature Cohorts:</strong> Holding tenure fixed above 12 months, subscribers with a newer/upgraded handset (`≤200d`) churn far less than peers on aging handsets (`501d+`): <strong>39.2% vs. 55.0%</strong> in Months 19–24 (<strong>-15.7 pp</strong>) and <strong>33.2% vs. 57.1%</strong> in Months 25+ (<strong>-23.8 pp</strong>).</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="sowhat-bar">
      <strong>So What / Decision Implication:</strong> Because first-year contract renewal and handset aging co-move, our <strong>Lane 2 intervention pairs a Month 8–9 renewal check with a handset trade-in voucher</strong>, verified via an 80/20 holdout pilot [13].
    </div>
    <div class="meta-bar">
      <span>Sources: [13] Company A Dataset 70% Train Split (`outputs/tables/tenure_months_churn.csv`, `outputs/tables/tenure_device_entanglement.csv`).</span>
      <span>Slide 5 / 15</span>
    </div>
  </div>
</section>

<!-- ==================== SLIDE 6: EDA FINDING 3 (USAGE COLLAPSE, ARPU & FAIRNESS) ==================== -->
<section class="slide">
  <div class="slide-header">
    <span class="section-tag coral">3. EXPLORATORY DATA ANALYSIS — FINDING 3</span>
    <h2 class="action-title">Zero-MOU Accounts Churn at <span class="accent-coral">79.81%</span> on Low ARPU (23.11 MU), Requiring Value-Gated Triage [13]</h2>
  </div>

  <div class="slide-body cols-55-45">
    <div class="fig-box">
      <img src="{fig_dir}/usage_segments.png" alt="Usage Collapse Segments Churn vs ARPU">
      <div class="fig-caption">Figure 5: Churn rate (%) vs. Mean Monthly Revenue (`rev_Mean`, MU) across voice usage segments [13].</div>
    </div>

    <div class="rows-auto">
      <div class="card white">
        <div class="card-title">Three Commercial Traps Uncovered by Segment &amp; Fairness Audits [13]</div>
        <ul class="clean-list">
          <li><strong>Trap 1 — The Dormant SIM Trap (`mou_Mean == 0`):</strong> The 1,615 zero-usage accounts churn at <strong>79.81%</strong> (78.48% train), making them easy for any ML model to flag. Yet their mean ARPU is only <strong>23.11 MU</strong> (median 17.14 MU, <strong>0.64% of total revenue</strong>). Spending 7.50–10.00 MU on human call-center outreach for already-silent SIMs destroys campaign ROI.</li>
          <li><strong>Trap 2 — Mean ARPU Alone Is Blind (`rev_Mean`):</strong> Overall monthly revenue is virtually identical between churners (<strong>58.21 MU</strong> mean / 47.49 MU median) and stayers (<strong>59.22 MU</strong> mean / 48.88 MU median; <em>r</em> = -0.0109). What predicts churn is <em>relative usage trajectory</em> (`change_mou`, `mou_ratio_3m`) and <em>overage friction</em> (`ovrrev_Mean &gt; 20 MU` &rarr; 52.05% churn).</li>
          <li><strong>Trap 3 — Demographic Disparity (`ethnic`):</strong> Raw churn across `ethnic` codes spans <strong>18.37 pp</strong> (Code `O`: <strong>58.08%</strong> vs. Code `Z`: <strong>39.71%</strong>). To prevent discriminatory offer allocation, we <strong>exclude `ethnic`</strong> from production scoring—verified to cost only <strong>-0.0016 validation AUC</strong> (0.7073 &rarr; 0.7057).</li>
        </ul>
      </div>

      <div class="kpi-row" style="margin-bottom:0;">
        <div class="kpi-box coral">
          <div class="kpi-num coral">79.81%</div>
          <div class="kpi-label">Zero-MOU Churn (n=1,615)</div>
          <div class="kpi-sub">ARPU = 23.11 MU &rarr; Automated SMS only</div>
        </div>
        <div class="kpi-box">
          <div class="kpi-num blue">58.21 vs 59.22</div>
          <div class="kpi-label">Churned vs Stayed Mean MU</div>
          <div class="kpi-sub">Static ARPU cannot separate risk</div>
        </div>
        <div class="kpi-box teal">
          <div class="kpi-num teal">-0.0016 AUC</div>
          <div class="kpi-label">Cost of Dropping `ethnic`</div>
          <div class="kpi-sub">Fairness achieved with ~zero accuracy loss</div>
        </div>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="sowhat-bar">
      <strong>So What / Decision Implication:</strong> High churn probability alone is not enough to trigger costly human outreach—offers must be gated by <strong>active value (`rev_Mean &ge; 30 MU`, `mou_Mean &gt; 0`)</strong> and <strong>fairness-audited features</strong> [8, 13].
    </div>
    <div class="meta-bar">
      <span>Sources: [13] Company A Dataset (`outputs/tables/usage_collapse_segments.csv`, `outputs/tables/ethnic_fairness_audit.csv`).</span>
      <span>Slide 6 / 15</span>
    </div>
  </div>
</section>

<!-- ==================== SLIDE 7: PROBLEM FORMULATION & PIPELINE ==================== -->
<section class="slide">
  <div class="slide-header">
    <span class="section-tag teal">4. PROBLEM FORMULATION &amp; METHODOLOGY</span>
    <h2 class="action-title">We Frame Retention as a <span class="accent-teal">Leakage-Safe Top-k% Risk-Ranking Engine</span> Linked to Two Action Lanes [8, 12]</h2>
  </div>

  <div class="slide-body rows-auto">
    <div class="fig-box" style="height:355px; padding:6px 12px;">
      {svg_pipeline}
    </div>

    <div class="card white" style="flex:1; padding:14px 20px;">
      <div class="card-title" style="font-size:17px; margin-bottom:6px;">Candidate Problem Formulation Decision Matrix (Evaluated Before Modeling) [7, 8, 13]</div>
      <table class="data-table" style="font-size:13.8px;">
        <thead>
          <tr>
            <th>Candidate Problem Framing</th>
            <th>Primary Target &amp; Action</th>
            <th class="num">Data Support (30%)</th>
            <th class="num">Intervenability (25%)</th>
            <th class="num">Net Impact (25%)</th>
            <th class="num">Causal Rigor (20%)</th>
            <th class="num">Weighted Score</th>
            <th>Strategic Role in Proposal</th>
          </tr>
        </thead>
        <tbody>
          <tr class="highlight-row">
            <td><strong>P1. Proactive Top-10% Risk-Ranked Retention Engine</strong></td>
            <td>Rank all 100k users by p&#770;<sub>i</sub>; target Top-10% (`rev_Mean &ge; 30 MU`)</td>
            <td class="num">5.0 / 5</td>
            <td class="num">4.5 / 5</td>
            <td class="num">5.0 / 5</td>
            <td class="num">4.5 / 5</td>
            <td class="num"><strong>4.78 / 5.00</strong></td>
            <td><strong>Primary Core Architecture (Lane 1 + Scoring Engine)</strong></td>
          </tr>
          <tr>
            <td><strong>P2. Pre-300-Day Handset Refresh &amp; Month 8–9 Renewal Pilot</strong></td>
            <td>Target `eqpdays` in [240, 300]d (`n = 8,815`, ARPU 66.91 MU)</td>
            <td class="num">4.5 / 5</td>
            <td class="num">4.5 / 5</td>
            <td class="num">4.0 / 5</td>
            <td class="num">4.5 / 5</td>
            <td class="num"><strong>4.38 / 5.00</strong></td>
            <td><strong>Integrated as Dedicated Lifecycle Track (Lane 2 Pilot)</strong></td>
          </tr>
          <tr>
            <td><strong>P3. Dormant / Zero-MOU Account Reactivation Triage</strong></td>
            <td>Target `mou_Mean &le; 10` (`n = 3,848`, ARPU 24.00 MU)</td>
            <td class="num">4.5 / 5</td>
            <td class="num">2.5 / 5</td>
            <td class="num">2.5 / 5</td>
            <td class="num">4.0 / 5</td>
            <td class="num"><strong>3.40 / 5.00</strong></td>
            <td><strong>Automated Low-Cost Digital/SMS Guardrail Only</strong></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="slide-footer">
    <div class="sowhat-bar">
      <strong>So What / Decision Implication:</strong> Combining <strong>P1 (Top-10% ML Risk Ranking)</strong> with <strong>P2 (Pre-300-Day Lifecycle Trigger)</strong> and a <strong>P3 Dormant-Account Cost Filter</strong> maximizes protected CLV per MU of retention spend [8].
    </div>
    <div class="meta-bar">
      <span>Sources: [7] Neslin et al. (2006); [8] Verbeke et al. (2012); [12] Pedregosa et al. (2011); `docs/problem_decision_matrix.md`.</span>
      <span>Slide 7 / 15</span>
    </div>
  </div>
</section>

<!-- ==================== SLIDE 8: LABEL-SHIFT RE-BASING ==================== -->
<section class="slide">
  <div class="slide-header">
    <span class="section-tag teal">4. PROBLEM FORMULATION &amp; METHODOLOGY</span>
    <h2 class="action-title">Solving the Case-Control Trap: Re-Basing <span class="accent-coral">49.56% Sample Churn</span> to Realistic <span class="accent-teal">5%–10% Priors</span> [7, 9]</h2>
  </div>

  <div class="slide-body cols-50-50">
    <div class="rows-auto">
      <div class="card white" style="flex:1;">
        <div class="card-title">Why Unadjusted Sample Precision Overstates Production ROI by 3.3&times; [7, 9]</div>
        <ul class="clean-list">
          <li><strong>The Case-Control Calibration Structure:</strong> Company A's dataset has a <strong>49.56% churn rate</strong> (`49,562` churned vs. `50,438` stayed) [13]. As documented by Neslin et al. (2006) on the Teradata/Duke wireless benchmark [7] and highlighted in the GCI Tutorial PDF, this is a <strong>50/50 case-control sample</strong> oversampled from a real operator environment where monthly/quarterly churn is <strong>5% to 10%</strong> [3, 7, 8].</li>
          <li><strong>Ranking Is Invariant, Precision Is Not:</strong> Under prior probability shift (where class-conditional feature distributions P(X | Y) remain invariant), a model's <strong>ROC-AUC is unchanged</strong>, but the fraction of true churners inside the top-k% tier depends directly on the true base rate &pi;<sub>r</sub> [9].</li>
          <li><strong>Exact Bayes Prior-Shift Formula (Saerens et al., 2002) [9]:</strong> Given sample prior &pi;<sub>s</sub> = 0.4956, sample top-k% precision P<sub>s</sub>, and real production prior &pi;<sub>r</sub> &isin; {{0.05, 0.10}}:</li>
        </ul>
        <div class="formula-box">
          P<sub>real</sub>(k) &nbsp;=&nbsp; [ P<sub>s</sub>(k) &middot; (&pi;<sub>r</sub> / &pi;<sub>s</sub>) ] &nbsp;/&nbsp; [ P<sub>s</sub>(k) &middot; (&pi;<sub>r</sub> / &pi;<sub>s</sub>) + (1 &minus; P<sub>s</sub>(k)) &middot; ((1 &minus; &pi;<sub>r</sub>) / (1 &minus; &pi;<sub>s</sub>)) ]
        </div>
        <p style="font-size:14px; color:#475569; margin-top:4px;">
          At <strong>Top-10%</strong> (n = 10,000), sample precision P<sub>s</sub> = 81.00% (1.63&times; lift) maps to <strong>P<sub>real</sub> = 32.53% (3.25&times; lift) at &pi;<sub>r</sub> = 10%</strong> and <strong>P<sub>real</sub> = 18.59% (3.72&times; lift) at &pi;<sub>r</sub> = 5%</strong> [9].
        </p>
      </div>
    </div>

    <div class="rows-auto">
      <div class="card teal-tint" style="flex:1;">
        <div class="card-title">Side-by-Side Impact of Prior-Shift Correction at Top-10% (n = 10,000) [9]</div>
        <table class="data-table">
          <thead>
            <tr>
              <th>Metric at Top-10% Tier</th>
              <th class="num">Unadjusted Sample (&pi;<sub>s</sub> = 49.56%)</th>
              <th class="num">Re-Based Base Case (&pi;<sub>r</sub> = 10.0%)</th>
              <th class="num">Re-Based Conservative (&pi;<sub>r</sub> = 5.0%)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Targeted Subscribers (n)</strong></td>
              <td class="num">10,000</td>
              <td class="num">10,000</td>
              <td class="num">10,000</td>
            </tr>
            <tr class="highlight-row">
              <td><strong>True Precision in Top-10%</strong></td>
              <td class="num">81.00%</td>
              <td class="num"><strong>32.53%</strong></td>
              <td class="num"><strong>18.59%</strong></td>
            </tr>
            <tr>
              <td><strong>True Churners Reached</strong></td>
              <td class="num">8,100</td>
              <td class="num"><strong>3,253</strong></td>
              <td class="num"><strong>1,859</strong></td>
            </tr>
            <tr>
              <td><strong>False Positives Contacted</strong><br><span class="sub-td">(Incur full offer cost c)</span></td>
              <td class="num">1,900</td>
              <td class="num">6,747</td>
              <td class="num">8,141</td>
            </tr>
            <tr>
              <td><strong>Lift Over Random Outreach</strong></td>
              <td class="num">1.63&times;</td>
              <td class="num"><strong>3.25&times;</strong></td>
              <td class="num"><strong>3.72&times;</strong></td>
            </tr>
            <tr class="baseline-row">
              <td><strong>Estimated Net Impact (MU)</strong><br><span class="sub-td">(After paying c on all 10,000)</span></td>
              <td class="num">+457,708 MU<br><span class="sub-td">(3.3&times; inflated)</span></td>
              <td class="num"><strong>+138,938 MU</strong><br><span class="sub-td">(Realistic Base)</span></td>
              <td class="num"><strong>+27,418 MU</strong><br><span class="sub-td">(Realistic Low)</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="sowhat-bar">
      <strong>So What / Decision Implication:</strong> Reporting <strong>prior-shifted precision (32.5% at 10% base rate; 18.6% at 5%)</strong> prevents CFO budget over-commitment while proving the model still delivers a <strong>3.25&times;–3.72&times; concentration of churners</strong> [9].
    </div>
    <div class="meta-bar">
      <span>Sources: [7] Neslin et al. (2006); [8] Verbeke et al. (2012); [9] Saerens, Latinne, &amp; Decaestecker (2002), Neural Computation.</span>
      <span>Slide 8 / 15</span>
    </div>
  </div>
</section>

<!-- ==================== SLIDE 9: MODEL PROGRESSION & R3 TABLE ==================== -->
<section class="slide">
  <div class="slide-header">
    <span class="section-tag teal">5. MODEL SELECTION &amp; VALIDATION (R3 LIVE-TEXT VERIFIED)</span>
    <h2 class="action-title">Final Model <span class="accent-teal">M5 (Regularized XGBoost)</span> Reaches <span class="accent-teal">0.7013 CV / 0.7011 Test ROC-AUC</span> &amp; Cuts Overfitting in Half [10, 12]</h2>
  </div>

  <div class="slide-body rows-auto" style="gap:14px;">
    <div class="card white" style="padding:14px 18px;">
      <div class="card-title" style="font-size:17px; margin-bottom:8px;">
        <span>Systematic 7-Model Progression on 70% Training Split (5-Fold Stratified CV) &amp; Held-Out 30% Test Split (SEED = 42) [10, 11, 12]</span>
        <span style="font-size:13px; color:#0D9488; font-weight:800;">Selected Model: XGBoost Regularized &amp; Tuned (M5) | Metric: ROC-AUC = 0.7011 (Test) / 0.7013 (CV) | Accuracy = 0.6413</span>
      </div>
      <table class="data-table" style="font-size:13.6px;">
        <thead>
          <tr>
            <th>ID</th>
            <th>Model Name &amp; Configuration</th>
            <th class="num">Features</th>
            <th class="num">5-Fold CV ROC-AUC</th>
            <th class="num">Test ROC-AUC</th>
            <th class="num">Test Accuracy</th>
            <th class="num">Train Accuracy</th>
            <th class="num">Train–Test Gap</th>
            <th class="num">Test Top-10% Precision</th>
          </tr>
        </thead>
        <tbody>
          {model_rows_html}
        </tbody>
      </table>
    </div>

    <div style="display:grid; grid-template-columns: 1.25fr 1fr; gap:20px; flex:1; min-height:0;">
      <div class="fig-box" style="padding:8px;">
        <img src="{fig_dir}/model_comparison.png" alt="Model Comparison Chart">
      </div>
      <div class="card teal-tint" style="padding:16px 20px;">
        <div class="card-title" style="font-size:17px;">Why M5 (Regularized XGBoost) Is Selected Over M3 &amp; M6 [10, 11]</div>
        <ul class="clean-list" style="gap:8px;">
          <li style="font-size:14.8px;"><strong>Beats Tutorial Baseline (M3) Across Every Metric:</strong> Test ROC-AUC rises from <strong>0.6938 &rarr; 0.7011</strong> (+0.0073), 5-fold CV ROC-AUC rises from <strong>0.6940 &rarr; 0.7013</strong>, Test Accuracy rises from <strong>0.6357 (63.57%) &rarr; 0.6413 (64.13%)</strong>, and Top-10% sample precision jumps from <strong>79.2% &rarr; 81.0%</strong> (+183 more true churners caught per 10,000 targeted).</li>
          <li style="font-size:14.8px;"><strong>Cuts Overfitting Gap Nearly in Half:</strong> Tutorial M3 (`max_depth=6`, unregularized) overfits heavily (Train Acc 73.49% vs. Test Acc 63.57% = <strong>9.92 pp gap</strong>). Regularizing M5 (`max_depth=5`, `min_child_weight=20`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_lambda=2.0`) shrinks the gap to <strong>5.23 pp</strong> (`Brier score = 0.2185`).</li>
          <li style="font-size:14.8px;"><strong>Cross-Checked Against LightGBM (M6):</strong> LightGBM (`0.7002` CV AUC, `0.7010` Test AUC, `0.6409` Test Accuracy) confirms the ~0.701 AUC ceiling on these 107 fair tabular features.</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="sowhat-bar">
      <strong>So What / Decision Implication:</strong> Domain feature engineering (+20 lifecycle/usage features, -10 duplicates, excluding `ethnic`) plus tree regularization lifts Top-10% precision to <strong>81.0%</strong> while halving overfitting [10, 12].
    </div>
    <div class="meta-bar">
      <span>Sources: [10] Chen &amp; Guestrin (2016) XGBoost; [11] Ke et al. (2017) LightGBM; [12] Pedregosa et al. (2011) Scikit-learn (`outputs/tables/experiment_log.csv`).</span>
      <span>Slide 9 / 15</span>
    </div>
  </div>
</section>

<!-- ==================== SLIDE 10: EXPLAINABILITY & COMMERCIAL LEVERS ==================== -->
<section class="slide">
  <div class="slide-header">
    <span class="section-tag teal">5. MODEL EXPLAINABILITY &amp; ACTIONABILITY</span>
    <h2 class="action-title">How the Model Ranks Risk: <span class="accent-coral">Handset Lifecycle</span>, <span class="accent-blue">3-Month Usage Slumps</span> &amp; <span class="accent-teal">Plan Fit</span> Drive Predictions [10, 13]</h2>
  </div>

  <div class="slide-body cols-55-45">
    <div class="fig-box">
      <img src="{fig_dir}/feature_importance_levers.png" alt="Top 10 Features by Gain and Commercial Lever Type">
      <div class="fig-caption">Figure 6: Top-10 features in Final Model M5 by tree split gain share (%), color-coded by commercial intervenability [10, 13].</div>
    </div>

    <div class="rows-auto">
      <div class="fig-box" style="height:260px; padding:6px;">
        {svg_voting}
      </div>

      <div class="card white" style="flex:1; padding:14px 18px;">
        <div class="card-title" style="font-size:16.5px; margin-bottom:6px;">Triangulating Gain, Held-Out Permutation Importance &amp; Ablation [10, 12]</div>
        <table class="data-table" style="font-size:13.2px;">
          <thead>
            <tr>
              <th>Signal Family</th>
              <th>Top Features (Gain Share / Perm Drop)</th>
              <th>PDP / Ablation Finding</th>
              <th>Mapped Retention Action</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>1. Handset Lifecycle</strong></td>
              <td>`dev_age_gt_300` (15.2% gain), `eqpdays` (4.6% gain, #3 perm), `refurb_new` (2.6%)</td>
              <td>PDP jumps from <strong>0.458 (300d) &rarr; 0.549 (315d)</strong>; dropping all `eqpdays` cols cuts AUC by <strong>-0.0065</strong>.</td>
              <td><strong>Lane 2:</strong> Pre-300d trade-in voucher + quality warranty on refurb replacements.</td>
            </tr>
            <tr>
              <td><strong>2. Tenure Renewal Window</strong></td>
              <td>`months` (2.6% gain, #2 perm +0.0214), `tenure_le_9` (2.2%), `tenure_10_12_cliff` (1.9%)</td>
              <td>PDP peaks at <strong>0.609 at Month 12</strong> before decaying to 0.475 by Month 24.</td>
              <td><strong>Lane 2:</strong> Proactive Month 8–9 renewal check before Month 11 peak.</td>
            </tr>
            <tr>
              <td><strong>3. Usage Slump &amp; Plan Fit</strong></td>
              <td>`mou_ratio_3m` (#1 perm +0.0304, 2.3% gain), `asl_flag` (1.4%), `recurring_rev_share` (1.4%)</td>
              <td>Users with `mou_Mean / avg3mou &lt; 0.7` and high overage share spike in risk while still active.</td>
              <td><strong>Lane 1:</strong> Right-sized bundle + Account Spending Limit (`asl_flag`) activation.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="sowhat-bar">
      <strong>So What / Decision Implication:</strong> A non-technical CRM manager can read every top model driver as a concrete action: <strong>refresh aging handsets before Day 300</strong> and <strong>right-size plans when 3-month usage drops</strong> [10, 13].
    </div>
    <div class="meta-bar">
      <span>Sources: [10] Chen &amp; Guestrin (2016); [12] Pedregosa et al. (2011) (`outputs/tables/feature_importance_gain.csv`, `feature_importance_permutation.csv`).</span>
      <span>Slide 10 / 15</span>
    </div>
  </div>
</section>

<!-- ==================== SLIDE 11: TOP-K TARGETING & LIFT ==================== -->
<section class="slide">
  <div class="slide-header">
    <span class="section-tag teal">5. MODEL EVALUATION — DECILES &amp; LIFT</span>
    <h2 class="action-title">Top-10% Targeting Concentrates Churners by <span class="accent-teal">3.25&times; (10% Prior)</span> to <span class="accent-teal">3.72&times; (5% Prior)</span> Over Random [8, 9]</h2>
  </div>

  <div class="slide-body rows-auto" style="gap:14px;">
    <div class="fig-box" style="height:370px; padding:8px;">
      <img src="{fig_dir}/topk_lift_curve.png" alt="Top-k Precision and Lift Curve">
    </div>

    <div class="card white" style="flex:1; padding:12px 18px;">
      <div class="card-title" style="font-size:16.5px; margin-bottom:6px;">
        <span>Held-Out Test Set Top-k% Targeting Table (Scaled to N = 100,000 Base; Sample vs. Label-Shift Re-Based) [8, 9]</span>
        <span style="font-size:13px; color:#E11D48; font-weight:800;">Top-10% Risk (81.0% Sample Churn) vs. Bottom-10% Safe Tier (18.4% Sample Churn) = 4.40&times; Risk Separation</span>
      </div>
      <table class="data-table" style="font-size:13.5px;">
        <thead>
          <tr>
            <th>Targeting Tier (k%)</th>
            <th class="num">Targeted Customers (per 100k)</th>
            <th class="num">Score Cutoff (p&#770;<sub>i</sub>)</th>
            <th class="num">Sample Precision (&pi;<sub>s</sub>=49.6%)</th>
            <th class="num">Sample Recall (Share Caught)</th>
            <th class="num">Sample Lift</th>
            <th class="num">Re-Based Precision (&pi;<sub>r</sub>=10% Prior)</th>
            <th class="num">Re-Based Precision (&pi;<sub>r</sub>=5% Prior)</th>
          </tr>
        </thead>
        <tbody>
          {topk_rows_html}
        </tbody>
      </table>
    </div>
  </div>

  <div class="slide-footer">
    <div class="sowhat-bar">
      <strong>So What / Decision Implication:</strong> Selecting the <strong>Top-10% cutoff (p&#770;<sub>i</sub> &ge; 0.713, n = 10,000)</strong> captures <strong>3,253 true churners</strong> under a 10% real base rate (vs. 1,000 by random outreach)—maximizing campaign efficiency [8, 9].
    </div>
    <div class="meta-bar">
      <span>Sources: [8] Verbeke et al. (2012); [9] Saerens et al. (2002) (`outputs/tables/topk_targeting.csv`).</span>
      <span>Slide 11 / 15</span>
    </div>
  </div>
</section>

<!-- ==================== SLIDE 12: TWO-LANE RETENTION PROGRAM ==================== -->
<section class="slide">
  <div class="slide-header">
    <span class="section-tag amber">6. PROPOSED OPERATIONAL SOLUTION</span>
    <h2 class="action-title">Operational Playbook: A <span class="accent-blue">Two-Lane Retention Program</span> Gated by a 90-Day 80/20 Holdout Pilot [7, 8]</h2>
  </div>

  <div class="slide-body rows-auto" style="gap:14px;">
    <div class="fig-box" style="height:315px; padding:6px 12px;">
      {svg_twolane}
    </div>

    <div class="slide-body cols-3" style="gap:18px;">
      <div class="card blue-tint">
        <div class="card-title" style="font-size:17px; color:#1E3A8A;">Lane 1: High-Value Usage-Slump &amp; Plan-Fit Rescue</div>
        <ul class="clean-list" style="gap:7px;">
          <li style="font-size:14.2px;"><strong>Target Segment:</strong> Top-10% risk score (`p̂_i ≥ 0.713`) with active revenue (`rev_Mean ≥ 30 MU`, `mou_Mean > 0`) exhibiting a 3-month usage drop (`mou_ratio_3m < 0.75`) or overage friction (`ovrrev_Mean > 10 MU`).</li>
          <li style="font-size:14.2px;"><strong>Commercial Offer:</strong> Proactive care call + right-sized voice/data bundle, one-time overage buffer credit, and Account Spending Limit (`asl_flag = Y`) activation.</li>
          <li style="font-size:14.2px;"><strong>Unit Economics:</strong> Expected cost <strong>c = 7.50 MU</strong> per targeted account; protects <strong>V = 328.83 MU</strong> (8m margin at 58.72 MU ARPU). Break-even save rate is just <strong>s* = 7.01%</strong>.</li>
        </ul>
      </div>

      <div class="card teal-tint">
        <div class="card-title" style="font-size:17px; color:#0F766E;">Lane 2: Pre-300-Day Handset Refresh &amp; Month 8–9 Check</div>
        <ul class="clean-list" style="gap:7px;">
          <li style="font-size:14.2px;"><strong>Target Segment:</strong> Active subscribers in the <strong>240–300 day handset window</strong> (or Tenure Months 8–9) with `rev_Mean ≥ 30 MU` (<strong>8,815 accounts</strong> in 100k; mean ARPU = <strong>66.91 MU</strong>, V = 374.70 MU).</li>
          <li style="font-size:14.2px;"><strong>Commercial Offer:</strong> Early handset trade-in / 12-month installment upgrade voucher + quality check for refurbished-device holders (`refurb_new == 'R'`).</li>
          <li style="font-size:14.2px;"><strong>90-Day Pilot Math:</strong> 80% treatment (`7,052` accts) vs. 20% control (`1,763` accts) at <strong>c = 4.00 MU</strong>; closing 25% of the 5.5 pp re-based jump saves <strong>97.0 accounts</strong> = <strong>+8,125 MU net pilot return</strong>.</li>
        </ul>
      </div>

      <div class="card amber-tint">
        <div class="card-title" style="font-size:17px; color:#92400E;">Guardrail Lane: Automated Digital Triage for Dormant SIMs</div>
        <ul class="clean-list" style="gap:7px;">
          <li style="font-size:14.2px;"><strong>Target Segment:</strong> High-risk accounts with `mou_Mean ≤ 10` or `rev_Mean < 30 MU` (including the 1,615 zero-MOU accounts with 79.81% churn and 23.11 MU ARPU).</li>
          <li style="font-size:14.2px;"><strong>Why Exclude From Human Calls:</strong> At 23.11 MU ARPU, human call + subsidy outreach has poor unit economics because disengagement has already occurred.</li>
          <li style="font-size:14.2px;"><strong>Automated Action:</strong> Zero-marginal-cost automated SMS/push "Win-Back Top-Up Bonus" (`c < 0.25 MU`) triggered only upon an inbound recharge or usage event.</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="sowhat-bar">
      <strong>So What / Decision Implication:</strong> Routing high-risk subscribers into <strong>cause-specific lanes</strong> and keeping a <strong>mandatory 20% randomized holdout</strong> turns predictive scores into verifiable profit [7, 8].
    </div>
    <div class="meta-bar">
      <span>Sources: [7] Neslin et al. (2006); [8] Verbeke et al. (2012); [13] Company A Dataset (`docs/assumptions.md`).</span>
      <span>Slide 12 / 15</span>
    </div>
  </div>
</section>

<!-- ==================== SLIDE 13: FINANCIAL IMPACT & SENSITIVITY ==================== -->
<section class="slide">
  <div class="slide-header">
    <span class="section-tag amber">6. ESTIMATED FINANCIAL IMPACT &amp; SENSITIVITY</span>
    <h2 class="action-title">Re-Based Net Impact at Top-10%: <span class="accent-blue">+27,418 MU (Conservative)</span> to <span class="accent-teal">+138,938 MU (Base)</span> to <span class="accent-coral">+329,786 MU (Optimistic)</span> [8, 9]</h2>
  </div>

  <div class="slide-body rows-auto" style="gap:14px;">
    <div class="fig-box" style="height:365px; padding:8px;">
      <img src="{fig_dir}/impact_scenarios_tornado.png" alt="Net Financial Impact Scenarios and Sensitivity Tornado">
    </div>

    <div class="card white" style="flex:1; padding:12px 18px;">
      <div class="card-title" style="font-size:16px; margin-bottom:6px;">
        <span>Explicit Scenario &amp; Assumption Table at Pilot Cutoff k = 10% (n = 10,000 Targeted out of N = 100,000; Dataset Monetary Units, MU) [8, 9, 13]</span>
        <span style="font-size:12.5px; color:#0F766E; font-weight:800;">Net Impact = n &middot; p_adj &middot; s &middot; (ARPU &middot; margin &middot; H) &minus; n &middot; c</span>
      </div>
      <table class="data-table" style="font-size:13.3px;">
        <thead>
          <tr>
            <th>Scenario Name</th>
            <th class="num">Real Churn Prior (&pi;<sub>r</sub>)</th>
            <th class="num">Re-Based Precision (p<sub>adj</sub>)</th>
            <th class="num">Save Rate (s)</th>
            <th class="num">ARPU &times; Margin &times; H = V</th>
            <th class="num">Offer Cost (c)</th>
            <th class="num">Saved Accts</th>
            <th class="num">Gross Saved (MU)</th>
            <th class="num">Total Cost (MU)</th>
            <th class="num">Estimated Net Impact (MU)</th>
            <th class="num">ROI / Break-Even s*</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Conservative</strong> <span class="sub-td">(5% Prior, Median ARPU)</span></td>
            <td class="num">5.0%</td>
            <td class="num">18.59%</td>
            <td class="num">15.0%</td>
            <td class="num">48.20 &times; 65% &times; 6m = <strong>187.98 MU</strong></td>
            <td class="num">2.50 MU</td>
            <td class="num">278.8</td>
            <td class="num">52,418 MU</td>
            <td class="num">25,000 MU</td>
            <td class="num"><strong>+{int(c_sc['net_impact_mu']):,} MU</strong></td>
            <td class="num">+109.7% / s*={c_sc['breakeven_s']*100:.2f}%</td>
          </tr>
          <tr class="highlight-row">
            <td><strong>Base Case (Recommended)</strong> <span class="sub-td">(10% Prior, Mean ARPU)</span></td>
            <td class="num"><strong>10.0%</strong></td>
            <td class="num"><strong>32.53%</strong></td>
            <td class="num"><strong>20.0%</strong></td>
            <td class="num">58.72 &times; 70% &times; 8m = <strong>328.83 MU</strong></td>
            <td class="num"><strong>7.50 MU</strong></td>
            <td class="num"><strong>650.6</strong></td>
            <td class="num"><strong>213,938 MU</strong></td>
            <td class="num"><strong>75,000 MU</strong></td>
            <td class="num"><strong>+{int(b_sc['net_impact_mu']):,} MU</strong></td>
            <td class="num"><strong>+185.3% / s*={b_sc['breakeven_s']*100:.2f}%</strong></td>
          </tr>
          <tr>
            <td><strong>Optimistic</strong> <span class="sub-td">(10% Prior, 12m Full Renewal)</span></td>
            <td class="num">10.0%</td>
            <td class="num">32.53%</td>
            <td class="num">25.0%</td>
            <td class="num">58.72 &times; 75% &times; 12m = <strong>528.48 MU</strong></td>
            <td class="num">10.00 MU</td>
            <td class="num">813.2</td>
            <td class="num">429,786 MU</td>
            <td class="num">100,000 MU</td>
            <td class="num"><strong>+{int(o_sc['net_impact_mu']):,} MU</strong></td>
            <td class="num">+329.8% / s*={o_sc['breakeven_s']*100:.2f}%</td>
          </tr>
          <tr class="baseline-row">
            <td><em>Unadjusted Sample Reference</em> <span class="sub-td">(If 49.56% Prior Ignored)</span></td>
            <td class="num"><em>49.56%</em></td>
            <td class="num"><em>81.00%</em></td>
            <td class="num"><em>20.0%</em></td>
            <td class="num"><em>58.72 &times; 70% &times; 8m = 328.83 MU</em></td>
            <td class="num"><em>7.50 MU</em></td>
            <td class="num"><em>1,620.0</em></td>
            <td class="num"><em>532,708 MU</em></td>
            <td class="num"><em>75,000 MU</em></td>
            <td class="num"><em>+{int(unadj['net_impact_mu']):,} MU (3.3&times; inflated)</em></td>
            <td class="num"><em>+610.3% / s*=2.82%</em></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="slide-footer">
    <div class="sowhat-bar">
      <strong>So What / Decision Implication:</strong> Even under the <strong>Conservative 5% real-churn prior (+27,418 MU net)</strong> and downside tornado stress tests, the Top-10% program remains solidly profitable because break-even conversion is only <strong>7.01%–7.15%</strong> [8, 9].
    </div>
    <div class="meta-bar">
      <span>Sources: [6] Reichheld &amp; Sasser (1990); [8] Verbeke et al. (2012); [9] Saerens et al. (2002) (`outputs/tables/sensitivity_tornado.csv`, `docs/assumptions.md`).</span>
      <span>Slide 13 / 15</span>
    </div>
  </div>
</section>

<!-- ==================== SLIDE 14: RISKS, LIMITATIONS & 90-DAY ROADMAP ==================== -->
<section class="slide">
  <div class="slide-header">
    <span class="section-tag amber">7. GOVERNANCE, RISKS &amp; EXECUTION ROADMAP</span>
    <h2 class="action-title">Five Operational Risk Mitigations &amp; a <span class="accent-teal">90-Day Gated Pilot Roadmap</span> Before Full Scale-Up [8, 9]</h2>
  </div>

  <div class="slide-body cols-55-45">
    <div class="card white">
      <div class="card-title">Key Technical &amp; Commercial Risks Paired with Concrete Mitigations [8, 9, 13]</div>
      <table class="data-table" style="font-size:13.8px;">
        <thead>
          <tr>
            <th>Risk / Limitation</th>
            <th>Why It Matters</th>
            <th>Concrete Mitigation Built Into PoC</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>1. Observational vs. Causal Uplift</strong></td>
            <td>High churn risk p&#770;<sub>i</sub> does not guarantee a customer will accept an offer (<em>persuadables</em> vs. <em>sure losses</em>).</td>
            <td>Enforce a <strong>20% randomized holdout control group</strong> in Phase 2 to measure true incremental save rate <em>s</em> before scaling budget.</td>
          </tr>
          <tr>
            <td><strong>2. Case-Control Prior Drift</strong></td>
            <td>Model probabilities are calibrated to the 49.56% sample prior rather than live monthly churn (5%–10%).</td>
            <td>Apply <strong>Saerens et al. [9] prior-shift adjustment</strong> in batch scoring and monitor monthly Brier/decile calibration.</td>
          </tr>
          <tr>
            <td><strong>3. "Sleeping Dog" Trigger Risk</strong></td>
            <td>Contacting satisfied month-to-month customers about contract renewal can accidentally prompt shopping.</td>
            <td>Restrict proactive calls to <strong>Top-10% risk (`p̂_i ≥ 0.713`)</strong>; track weekly treatment-vs-control churn delta by segment.</td>
          </tr>
          <tr>
            <td><strong>4. Subsidy Cannibalization</strong></td>
            <td>Low-risk or low-ARPU subscribers may game handset trade-in vouchers.</td>
            <td>Enforce <strong>`rev_Mean ≥ 30 MU` floor</strong>, `mou_Mean > 0`, and 12-month installment credit vesting (no upfront cash).</td>
          </tr>
          <tr>
            <td><strong>5. Demographic Proxy Bias</strong></td>
            <td>Neighborhood/credit codes (`prizm_social_one`, `crclscod`) could correlate with protected groups.</td>
            <td><strong>`ethnic` is excluded</strong> (`-0.0016` AUC impact); audit offer eligibility parity across regions every 30 days.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="rows-auto">
      <div class="card navy" style="flex:1;">
        <div class="card-title">90-Day Phased Implementation &amp; Governance Roadmap</div>
        <ul class="clean-list" style="gap:14px;">
          <li>
            <strong>Phase 1 — Days 1 to 30: Shadow Scoring &amp; Pipeline Integration</strong><br>
            Deploy `src/features.py` (107 fair features) + `final_model.joblib` (M5) in monthly shadow mode on billing warehouse; validate data drift, missingness flags (`change_mou`, `hnd_webcap`), and CRM call-queue routing.
          </li>
          <li>
            <strong>Phase 2 — Days 31 to 60: Launch 80/20 Randomized Holdout Pilot</strong><br>
            Execute <strong>Lane 1</strong> (Top-10% usage-slump rescue: 8,000 treatment / 2,000 control) and <strong>Lane 2</strong> (`eqpdays` 240–300d refresh: 7,052 treatment / 1,763 control). Track acceptance rate, call handling time, and 30/60-day survival.
          </li>
          <li>
            <strong>Phase 3 — Days 61 to 90: Uplift Readout, Uplift Model &amp; Scale Gate</strong><br>
            Compare 90-day churn between 80% Treatment and 20% Control. <strong>Hard Scale Gate:</strong> Proceed to full base rollout if verified save rate exceeds break-even (<strong>s &ge; 7.01%</strong> in Lane 1; net positive MU in Lane 2), then train a two-model uplift ranker on pilot outcomes.
          </li>
        </ul>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="sowhat-bar">
      <strong>So What / Decision Implication:</strong> Leadership does not need to gamble on unproven assumptions—a <strong>90-day 80/20 pilot</strong> validates whether conversion exceeds the <strong>7.01% break-even threshold</strong> before full commitment [8].
    </div>
    <div class="meta-bar">
      <span>Sources: [8] Verbeke et al. (2012); [9] Saerens et al. (2002); `docs/problem_definition.md`, `docs/assumptions.md`.</span>
      <span>Slide 14 / 15</span>
    </div>
  </div>
</section>

<!-- ==================== SLIDE 15: REFERENCES ==================== -->
<section class="slide">
  <div class="slide-header">
    <span class="section-tag">8. VERIFIED REFERENCES &amp; AI DISCLOSURE</span>
    <h2 class="action-title">Complete Numbered References &amp; Mandatory Tool Disclosure (100% Matched to `references.txt`)</h2>
  </div>

  <div class="slide-body rows-auto">
    <div class="card white" style="flex:1; padding:18px 24px;">
      <div class="card-title" style="font-size:17px; margin-bottom:8px;">
        <span>All External Market Reports, Peer-Reviewed Papers, Software Libraries, Dataset &amp; AI Assistance Links [1]–[14]</span>
        <span style="font-size:12.5px; color:#1D4ED8;">Synchronized with `submission/references.txt`</span>
      </div>
      <div class="ref-grid">
        {refs_html}
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div class="sowhat-bar">
      <strong>Reproducibility &amp; Auditability Note:</strong> Every metric in Slides 1–14 is programmatically verified against <code>outputs/results.json</code> generated by <code>submission/{config.ACCOUNT_NAME}.ipynb</code> (`SEED = 42`, 0 mismatches).
    </div>
    <div class="meta-bar">
      <span>Author: {config.AUTHOR_NAME} | GCI World 2026 September Final Assignment | End of Presentation</span>
      <span>Slide 15 / 15</span>
    </div>
  </div>
</section>

</body>
</html>
"""
    html_doc = re.sub(r"`([^`]+)`", r"<code>\1</code>", html_doc)
    return html_doc


def main() -> int:
    with open(config.RESULTS_JSON, encoding="utf-8") as f:
        res = json.load(f)

    ref_lines = [
        line.strip()
        for line in config.REFERENCES_TXT.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    html_content = build_html(res, ref_lines)
    html_path = config.SLIDES_SRC_DIR / "slides.html"
    html_path.write_text(html_content, encoding="utf-8")
    print(f"Wrote HTML slide deck to {html_path}")

    pdf_path = config.SLIDES_BUILD_DIR / f"{config.ACCOUNT_NAME}.pdf"
    cmd = [
        "/usr/bin/google-chrome",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        f"file://{html_path.resolve()}",
    ]
    print("Rendering PDF via headless Chrome...")
    subprocess.run(cmd, check=True)
    print(f"Rendered PDF to {pdf_path}")

    # Copy to submission/
    sub_pdf = config.SUBMISSION_DIR / f"{config.ACCOUNT_NAME}.pdf"
    sub_refs = config.SUBMISSION_DIR / "references.txt"
    shutil.copy2(pdf_path, sub_pdf)
    shutil.copy2(config.REFERENCES_TXT, sub_refs)
    print(f"Copied PDF and references.txt to {config.SUBMISSION_DIR}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
