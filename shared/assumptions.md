# Shared assumptions — FE5105 Group Project

**Every number in the report must use these values.** If you need to change one, tell the group first and then update this file in a PR.
Owner: **B** (maintains cost-of-capital assumptions). Conventions agreed by A on 2026-11-15.

---

## 1. Dates

| Item | Value | Notes |
|---|---|---|
| Valuation date | **2026-11-13** (Friday) | Share prices are closing prices on this day |
| Latest financial data | **2026-09-30** | Q3 2026 10-Q |
| "Current" income statement / cash flow | **TTM to 2026-09-30** (`TTM_2026Q3`) | TTM = FY2025 + 9M2026 − 9M2025 |
| "Current" balance sheet | **2026-09-30** (`BS_2026-09-30`) | |
| Historical comparison | FY2023, FY2024, FY2025 | FY2021–22 not used (COVID distortion, PSP grants) |

## 2. Data source

- Use **`data/processed/financials.csv`**. Do not copy numbers from the filings by hand.
- Definitions are in `data/processed/DATA_DICTIONARY.md`.
- Units are **USD millions** unless the `unit` column says otherwise.

## 3. Market data (2026-11-13)

| Ticker | Close (USD) | Shares (mn) | Market cap (USD mn) |
|---|---|---|---|
| LUV | 44.94 | 489.60 | 22,002.7 |
| DAL | 86.25 | 657.91 | 56,744.9 |
| UAL | 109.31 | 324.89 | 35,514.2 |
| AAL | 13.17 | 662.62 | 8,726.7 |
| ALK | 38.48 | 112.78 | 4,339.6 |

Source: `data/raw/market_data_2026-11-13.csv`.

## 4. Debt and leverage definitions

| Item | Definition |
|---|---|
| **Adjusted debt** | Debt (current + noncurrent, **including finance leases**) + **operating lease liabilities** (ASC 842 balance-sheet amount, **not** the old "rent × 7" rule) |
| **Adjusted net debt** | Adjusted debt − (cash + short-term investments) |
| **Pension / postretirement deficit** | **Not** in adjusted debt. B discusses it separately as hidden leverage (supplementary after-tax figure OK). |
| **Air traffic liability & loyalty deferred revenue** | **Not** debt (settled by providing service). Qualitative discussion only. |
| **Leverage multiple** | Adjusted net debt / **EBITDAR** (EBITDAR = operating income + D&A + aircraft rent) |
| **Enterprise value** | Market cap (2026-11-13) + adjusted net debt (2026-09-30) |
| **Debt weight in WACC** | Book value of adjusted debt (market value of debt ≈ book; state this assumption) |

## 5. Cost of capital

Maintained by B. Base case communicated to the group on 2026-11-17.
This records B's selected assumptions, not unanimous group approval.

| Item | Value | Source / method |
|---|---|---|
| Risk-free proxy | **5.15%** | [US Treasury, 10 Yr, 2026-11-13](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value_month=202611&type=daily_treasury_yield_curve) |
| Equity risk premium | **4.41%** | [Damodaran, 2026-11-01](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/home.htm); trailing 12 months with adjusted payout |
| Industry unlevered beta | **0.70** | [Damodaran US Air Transport, January 2026](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/Betas.html); not cash-corrected |
| Equity beta | See company table | Industry beta relevered using market D/E |
| Pre-tax cost of debt | See company table | Treasury proxy plus broad rating-group OAS |
| Cost of operating leases | Same as pre-tax cost of debt | Same tax treatment under the group convention |
| **Normalised marginal tax rate** | **24% for all five firms** | B-selected assumption: 21% federal + 3 percentage points net state/local effect; A uses the same rate for ROIC |

The tax rate is a modelling assumption, not a common reported effective tax rate.
Tax-note evidence is retained in `B_financing_wacc/sources/tax/`.

| Firm | D / E | Equity beta | Ke | Kd before tax | WACC |
|---|---:|---:|---:|---:|---:|
| LUV | 0.31 | 0.8661 | 8.97% | 6.26% | 7.97% |
| DAL | 0.33 | 0.8766 | 9.02% | 6.26% | 7.95% |
| UAL | 0.97 | 1.2137 | 10.50% | 7.01% | 7.96% |
| AAL | 4.16 | 2.9114 | 17.99% | 8.59% | 8.75% |
| ALK | 1.73 | 1.6218 | 12.30% | 7.01% | 7.88% |

**Calculation and debt treatment**

- βL = βU × [1 + (1 − T) × D/E]; Ke = Rf + βL × ERP.
- Kd = Rf + credit spread; WACC = E/(D+E) × Ke + D/(D+E) × Kd × (1−T).
- D is adjusted book debt at 2026-09-30, including finance and operating leases once. Book debt approximates market debt; cash is not netted from WACC weights.
- E is market capitalisation at 2026-11-13. AAL's negative book equity does not invalidate this market D/E; the accounting-ratio restriction in Section 6 applies to book equity.
- Benefit liabilities and traffic/loyalty obligations remain outside D. Usable interest tax shields and negligible debt beta are modelling assumptions.

**Credit-spread sources and interpretation**

LUV and DAL use the BBB group, UAL and ALK the BB group, and AAL the B group.
ICE BofA spreads via FRED for 2026-11-13: [BBB 1.11%](https://fred.stlouisfed.org/series/BAMLC0A4CBBB),
[BB 1.86%](https://fred.stlouisfed.org/series/BAMLH0A1HYBB) and [B 3.44%](https://fred.stlouisfed.org/series/BAMLH0A2HYB).
These observations were published on November 16; this is a retrospective estimate.
Index OAS plus a 10-year Treasury yield is a maturity approximation, not a company bond yield.
Rating evidence differs in date and type and is not continuously verified through the valuation date.

**Handoff to C**

Use LUV base WACC **7.97%**, with approximately **6.97%–8.97%** sensitivity alongside
terminal growth. This is a modelling range, not a confidence interval. For lease-consistent
FCFF, apply the after-tax lease-interest addback and leased-asset reinvestment treatment;
subtract lease liabilities once in the enterprise-to-equity bridge.

Full-precision results: `B_financing_wacc/output/wacc_results.csv`.
Sources and rating evidence: `B_financing_wacc/sources/source_register.csv`.
Final Part B report: `B_financing_wacc/output/FE5105_Part_B_2p5pages_Corrected.docx`.
Reproduce with `python3 B_financing_wacc/pipeline/build_wacc.py` from the repository root.

## 6. Accounting adjustments (all members)

1. **Delta refinery.** Use `revenue_airline` and `total_opex_airline`, which exclude third-party refinery sales, for margins, TRASM and CASM.
2. **Special items.** Use GAAP operating income by default. If you use a company's "adjusted" figures, cite the non-GAAP table.
3. **Interest coverage.** Use **net** interest expense for every firm, because Delta does not report gross interest expense.
4. **Southwest aircraft rent.** The TTM figure equals the FY2025 figure (USD 291 mn) because it is not disclosed quarterly.
5. **Alaska–Hawaiian.** Hawaiian was consolidated from 2024-09-18, so ALK's FY2024 figures are not comparable with FY2025.
6. **American's negative equity.** Do not use ROE or Debt/Equity for AAL; use EBITDAR-based ratios.

## 7. Valuation conventions (C)

- **DCF consistency with leases:** because operating leases are treated as debt, forecast cash flows **before lease financing**: add back the interest component of operating lease cost. Subtract lease liabilities when moving from enterprise value to equity value.
- **Multiples:** EV/EBITDAR (primary) or EV/EBITDA, using peer TTM figures from `financials_wide.xlsx` → `Compare_latest`.

## 8. Ratio responsibilities (avoid double counting)

| Ratio | Calculated by | Used by |
|---|---|---|
| Current ratio, interest coverage, EBITDAR/(interest + rent), total liquidity / revenue (all 5 firms) | **A** | D quotes LUV's figures |
| Cash conversion cycle, debt maturity profile, stress test (LUV) | D | — |
| WACC, cost of debt and equity (all 5 firms) | B | C, A (ROIC hurdle) |
| EV/EBITDAR multiples | A (inputs) / C (valuation) | — |

**Total liquidity** = cash + short-term investments + undrawn revolving credit facilities.
