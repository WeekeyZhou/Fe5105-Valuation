
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "shared"))

import config as cfg

# ----------------------------------------
# 1. Load existing analysis
# ----------------------------------------

out = ROOT / "D_risk_management" / "output"

stress = pd.read_csv(out / "stress_test.csv")
refinancing = pd.read_csv(
    out / "refinancing_sensitivity.csv"
)
hedging = pd.read_csv(
    out / "hedging_comparison.csv"
)

doc = cfg.new_report_doc()

from docx.shared import Cm, Pt

# Adjust Part D figure size only
cfg.REPORT["figure_width_cm"] = 10.0

# Reduce paragraph spacing without changing font size
normal = doc.styles["Normal"]
normal.paragraph_format.space_after = Pt(3)
for style_name in ["Heading 1", "Heading 2", "Heading 3"]:
    if style_name in doc.styles:
        style = doc.styles[style_name]
        style.paragraph_format.space_before = Pt(6)
        style.paragraph_format.space_after = Pt(3)


# ----------------------------------------
# 2. D.1 Liquidity and Financial Planning
# ----------------------------------------

cfg.add_heading(
    doc,
    "Part III. Financial Planning and Risk Management"
)


cfg.add_paragraph(
    doc,
    "This section evaluates Southwest Airlines' liquidity, "
    "financial risks, and hedging alternatives using "
    "September 2026 financial data and TTM cash flows."
)


cfg.add_heading(
    doc,
    "3.1 Liquidity and Near-Term Cash Requirements"
)

cfg.add_table(
    doc,
    caption="Table D1. Southwest liquidity indicators",
    header=["Indicator", "Value"],
    rows=[
        ["Current ratio", "0.474x"],
        ["Quick ratio", "0.359x"],
        ["Net working capital", "USD -7,232 mn"],
        ["CCC proxy", "1.74 days"],
        ["Cash and equivalents", "USD 3,624 mn"],
        ["Total liquidity", "USD 5,624 mn"],
        ["Current debt", "USD 2,153 mn"],
        ["TTM free cash flow", "USD -450 mn"],
    ],
    note=(
        "Source: Southwest FY2025 10-K and Q3 2026 10-Q; "
        "group calculations. Total liquidity includes USD "
        "2,000 mn of undrawn committed revolving credit."
    ),
    first_col_cm=9.0,
    highlight_col=None
)


cfg.add_paragraph(
    doc,
    "Liquidity. Current and quick ratios of 0.474x and "
    "0.359x indicate weak conventional liquidity. However, "
    "USD 8,277 million of air traffic and loyalty liabilities "
    "are largely fulfilled through future services rather "
    "than cash repayment. Total liquidity of USD 5,624 "
    "million covers reported current debt 2.61 times."
)



cfg.add_paragraph(
    doc,
    "Cash conversion. Southwest's estimated CCC proxy is "
    "1.74 days (DIO 10.72 + DSO 14.24 - DPO 23.22). "
    "Unlike manufacturing firms, Southwest primarily holds "
    "maintenance parts and supplies rather than goods for "
    "resale, while advance ticket payments provide cash "
    "before services are delivered. Operating expenses are "
    "therefore used as an imperfect proxy for COGS. "
    "Moreover, average working-capital balances are based "
    "on available year-end and Q3 observations rather than "
    "the exact TTM endpoints. Consequently, this CCC "
    "estimate should be interpreted cautiously, with "
    "greater emphasis placed on cash reserves, operating "
    "cash flow, and debt maturities."
)



cfg.add_paragraph(
    doc,
    "Debt and investment needs. Current debt rose from "
    "USD 324 million in 2025 to USD 2,153 million in "
    "September 2026. Debt instruments with USD 2,128 "
    "million of carrying value mature in calendar 2027, "
    "while aircraft commitments total USD 14.5 billion "
    "through 2031. TTM operating cash flow of USD 2,755 "
    "million fell short of USD 3,205 million in capital "
    "expenditure, resulting in negative USD 450 million "
    "of free cash flow. The maturity figures are not "
    "a complete contractual payment schedule."
)


# ----------------------------------------
# 3. D.2 Adverse Scenario
# ----------------------------------------

cfg.add_heading(
    doc,
    "3.2 Adverse Scenario: Jet Fuel Price Shock"
)

cfg.add_paragraph(
    doc,
    "We model illustrative 20% and 30% increases in fuel "
    "prices over one year, holding consumption, ticket prices, "
    "and capital expenditure constant. Starting from TTM "
    "fuel expense of USD 7,056 million, a 30% shock adds "
    "USD 2,116.8 million of fuel costs. Under the assumption "
    "that this cost increase is paid in cash without an "
    "offsetting tax benefit, operating cash flow falls from "
    "USD 2,755 million to USD 638.2 million, while free "
    "cash flow declines from negative USD 450 million to "
    "negative USD 2,566.8 million."
)


cfg.add_paragraph(
    doc,
    "Funding stress. We estimate ending cash as beginning "
    "cash plus stressed free cash flow minus debt repaid. "
    "Reported current debt of USD 2,153 million is used "
    "as an approximate repayment exposure, rather than "
    "a verified contractual maturity schedule. Under a "
    "30% fuel-price shock and no refinancing, the model "
    "implies a USD 1,095.8 million funding shortfall. "
    "Assuming 50% refinancing reduces this shortfall to "
    "USD 19.3 million. These are illustrative assumptions, "
    "not announced financing plans or cash-flow forecasts. "
    "The model excludes incremental financing costs, "
    "demand responses, and changes in capital expenditure."
)

cfg.add_figure(
    doc,
    "fig_D_liquidity_stress.png",
    caption=(
        "Figure D1. Liquidity sensitivity to fuel prices "
        "and refinancing assumptions"
    )
)

# ----------------------------------------
# 4. D.3 Risk Management
# ----------------------------------------

cfg.add_heading(
    doc,
    "3.3 Major Risks and Existing Risk Management"
)

cfg.add_paragraph(
    doc,
    "Fuel-price volatility is a major hedgeable financial "
    "exposure because jet fuel represents a substantial "
    "operating cost. Demand cyclicality, labor costs, and "
    "Boeing aircraft delivery delays are primarily operating "
    "risks better managed through capacity planning, "
    "contracting, and liquidity reserves. Interest-rate "
    "exposure can be managed selectively with swaps, "
    "subject to the firm's debt structure."
)

cfg.add_paragraph(
    doc,
    "Southwest discontinued its fuel-hedging program in "
    "2025, citing higher hedge premium costs and other "
    "factors, and stated that it did not intend to add "
    "fuel derivatives. Previously terminated hedges still "
    "affect accounting results through accumulated other "
    "comprehensive income. Separately, the company "
    "uses interest-rate swaps as fair-value hedges of "
    "fixed-rate notes due in 2035. These swaps convert "
    "the hedged fixed-rate exposure to floating-rate "
    "exposure and do not eliminate cash-flow sensitivity "
    "to rising interest rates."
)

# ----------------------------------------
# 5. D.4 Hedge Proposal
# ----------------------------------------

cfg.add_heading(
    doc,
    "3.4 Proposed Hedge and Implications for Firm Value"
)

cfg.add_paragraph(
    doc,
    "We evaluate a selective, one-year fuel collar covering "
    "50% of estimated fuel expenditure. The illustrative "
    "strategy buys calls with a strike at 110% of the "
    "baseline fuel price and sells puts with a strike at "
    "90%. We assume zero net premium solely for scenario "
    "comparison; actual market prices would be needed "
    "to establish whether these strikes can form a "
    "cost-neutral collar. The strategy limits fuel-price "
    "increases above the call strike on the hedged "
    "exposure but sacrifices some savings when prices "
    "fall below the put strike."
)

cfg.add_paragraph(
    doc,
    "Under a 30% fuel-price shock, unhedged free cash flow "
    "falls to negative USD 2,566.8 million. The illustrative "
    "collar improves it to negative USD 1,861.2 million, "
    "a USD 705.6 million cash-flow improvement. A standalone "
    "call with an assumed premium of 3% of hedged notional "
    "produces free cash flow of negative USD 1,967.0 million. "
    "However, at a 30% fuel-price decline, the collar "
    "reduces free cash flow from USD 1,666.8 million "
    "unhedged to USD 961.2 million."
)


cfg.add_paragraph(
    doc,
    "Recommendation and firm value. A limited collar "
    "may stabilize Southwest's cash flows during fuel "
    "price spikes, reducing costly refinancing, expected "
    "financial-distress costs, and the risk of forgoing "
    "positive-NPV investments. Such benefits could "
    "support firm value only if they exceed hedge costs, "
    "including basis risk, counterparty exposure, and "
    "foregone savings when fuel prices fall. Hedge payoffs "
    "must not be added directly to DCF value."
)


cfg.add_note(
    doc,
    "Sources: Southwest Airlines FY2025 10-K and Q3 2026 "
    "10-Q; group calculations. Financial data as of "
    "September 30, 2026. Fuel shocks, refinancing rates, "
    "hedge ratios, strikes and premiums are illustrative "
    "assumptions, not market quotes or company forecasts. "
    "The hedge model excludes basis risk, fuel-volume "
    "changes and ticket-price pass-through."
)


cfg.add_figure(
    doc,
    "fig_D_hedging_comparison.png",
    caption=(
        "Figure D2. Illustrative free cash flow under "
        "alternative fuel hedging strategies"
    )
)




# ----------------------------------------
# 6. Sources and assumptions
# ----------------------------------------


# ----------------------------------------
# 7. Save Word document
# ----------------------------------------

output_path = cfg.section_path(
    "D_Risk_Management.docx"
)

doc.save(output_path)

print("\nWord report generated successfully!")
print("Saved to:", output_path)
