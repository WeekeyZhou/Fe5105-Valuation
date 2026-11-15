# Shared assumptions — FE5105 Group Project

**Every number in the report must use these values.** If you need to change one, tell the group first and then update this file in a PR.
Owner: **B** (fills in the TBD items). Conventions agreed by A on 2026-11-15.

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

## 5. Cost of capital (B to fill in)

| Item | Value | Source / method |
|---|---|---|
| Risk-free rate | **TBD** | e.g. 10-year US Treasury yield on 2026-11-13 |
| Market risk premium | **TBD** | State the source (e.g. Damodaran implied ERP) |
| Equity beta | **TBD per firm** | Regression (weekly returns, 2–5 yrs vs S&P 500) and/or industry beta unlevered and relevered |
| Pre-tax cost of debt | **TBD per firm** | Credit rating spread or bond YTM |
| Cost of operating leases | Same as pre-tax cost of debt | |
| **Marginal tax rate** | **TBD (≈ 21% federal + state)** | Use the same rate for every firm, set from the 10-K tax notes; A also uses it for ROIC |
| WACC (first draft) | **TBD** | **Publish a first draft early: C needs it** |

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
