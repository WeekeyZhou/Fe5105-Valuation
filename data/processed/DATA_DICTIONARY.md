# Processed financial data — data dictionary

Maintained by Member A. Rebuild with `python A_ratios/pipeline/build_financials.py` (needs `beautifulsoup4`, `lxml`, `openpyxl`).

## Files

| File | What it is | Who uses it |
|---|---|---|
| `financials.csv` | **Main dataset, long format.** One row per ticker × period × item, with source and notes. Use this in code. | Everyone |
| `financials_wide.xlsx` | The same data laid out for reading: one sheet per company plus `Compare_latest` (all five side by side) and `Checks`. | Everyone, for quick reading |
| `validation_checks.csv` | 95 accounting-identity checks (all pass). | A (quality control) |

Inputs are in `data/raw/`: `html/` (FY2025 10-K and Q3 2026 10-Q, inline XBRL, saved from SEC EDGAR) and `market_data_2026-11-13.csv`.

## Conventions

- **Units:** USD millions unless the `unit` column says otherwise. ASM/RPM are in millions; fuel is in million gallons; the share price is in USD; shares are in millions.
- **Signs:** costs, taxes, capex, dividends and buybacks are **positive**. `cfi` and `cff` keep their cash-flow signs. Losses are negative.
- **Entity:** parent-company consolidated figures only. UAL and AAL file combined reports with their airline subsidiaries, and the subsidiary figures are excluded.
- **Valuation date:** 2026-11-13. **Latest financial data:** 2026-09-30.

## Periods

| Code | Meaning |
|---|---|
| `FY2023`, `FY2024`, `FY2025` | Fiscal years (all five companies end on Dec 31). Source: FY2025 10-K. |
| `9M2025`, `9M2026` | Nine months to Sep 30. Source: Q3 2026 10-Q. |
| `Q3_2025`, `Q3_2026` | Single third quarter. Source: Q3 2026 10-Q. |
| `TTM_2026Q3` | Trailing twelve months to 2026-09-30 = FY2025 + 9M2026 − 9M2025. **Use this for "current" ratios.** |
| `BS_2024-12-31`, `BS_2025-12-31`, `BS_2026-09-30` | Balance-sheet dates. **Use `BS_2026-09-30` for the latest position.** |
| `VAL_2026-11-13` | Market data at the valuation date. |

## Items

### Income statement
| Item | Definition |
|---|---|
| `revenue` | Total operating revenue |
| `refinery_sales_third_party` | **DAL only.** Third-party sales by Delta's Monroe refinery |
| `revenue_airline` | revenue − refinery_sales_third_party (equals revenue for the other four). **Use for TRASM and margins.** |
| `fuel_expense` | Aircraft fuel and related taxes |
| `labor_expense` | Salaries, wages and benefits |
| `aircraft_rent` | Aircraft rent (operating leases). LUV: aircraft operating lease cost from the lease note. |
| `da` | Depreciation and amortization |
| `total_opex` / `total_opex_airline` | Total operating expenses; the airline version excludes DAL's third-party refinery cost |
| `operating_income` | GAAP operating income (special items **not** removed) |
| `ebitda` | operating_income + da |
| `ebitdar` | ebitda + aircraft_rent |
| `interest_expense` | Gross interest expense. **Not available for DAL** (Delta reports only the net figure). |
| `interest_income` | Interest income |
| `interest_expense_net` | interest_expense − interest_income; DAL as reported |
| `pretax_income`, `income_tax`, `net_income` | As reported |

### Cash flow
| Item | Definition |
|---|---|
| `cfo` | Net cash from operating activities |
| `capex` | Capital expenditures (DAL/ALK 10-Q: flight equipment + other property, summed) |
| `free_cash_flow` | cfo − capex |
| `cfi`, `cff` | Investing and financing cash flows (signed) |
| `dividends_paid`, `buybacks` | Set to 0 when the company reports none |
| `interest_paid` | Cash interest paid (not every filing reports it quarterly) |

### Operating statistics
| Item | Definition |
|---|---|
| `asm` | Available seat miles (capacity) |
| `rpm` | Revenue passenger miles (traffic) |
| `fuel_gallons` | Fuel consumed |

Unit metrics are computed in the ratio step, not stored: load factor = rpm/asm; TRASM = revenue_airline/asm; CASM = total_opex_airline/asm; CASM ex-fuel = (total_opex_airline − fuel_expense)/asm; fuel price = fuel_expense/fuel_gallons.

### Balance sheet
| Item | Definition |
|---|---|
| `cash`, `st_investments`, `cash_and_sti` | Cash and equivalents, short-term investments, and their sum. AAL keeps most cash equivalents inside short-term investments, so compare `cash_and_sti`, not `cash`. |
| `receivables`, `current_assets`, `total_assets`, `accounts_payable`, `current_liabilities` | As reported |
| `air_traffic_liability_total` | Air traffic liability + loyalty deferred revenue (current + noncurrent). **Operating liability, not debt.** |
| `debt_current`, `debt_noncurrent`, `total_debt` | Debt **including finance leases** as presented on the balance sheet (UAL also includes "other financial liabilities") |
| `finance_lease_liab` | Finance lease liability (10-K only; already inside total_debt) |
| `oplease_liab_current`, `oplease_liab_noncurrent`, `oplease_liab_total` | Operating lease liabilities (ASC 842) |
| `adjusted_debt` | **Group definition:** total_debt + oplease_liab_total |
| `adjusted_net_debt` | adjusted_debt − cash_and_sti |
| `pension_liab` | Pension and postretirement liability on the balance sheet. **Not in adjusted_debt**; B treats it separately as hidden leverage. |
| `total_liabilities`, `equity`, `liab_and_equity` | Total liabilities are derived as liab_and_equity − equity. AAL equity is **negative** (stockholders' deficit). |

### Market data (`VAL_2026-11-13`)
| Item | Definition |
|---|---|
| `share_price` | Closing price on 2026-11-13 |
| `shares_outstanding` | From the Q3 2026 10-Q cover page |
| `market_cap` | share_price × shares_outstanding |
| `enterprise_value` | market_cap + adjusted_net_debt at 2026-09-30 |

## Caveats to mention in the report

1. **DAL refinery.** Always use `revenue_airline` and `total_opex_airline` for unit revenue, unit cost and margins.
2. **ALK–Hawaiian.** Hawaiian was consolidated from 2024-09-18, so ALK's FY2024 figures (financials and ASM/RPM) are not comparable with FY2025.
3. **LUV aircraft rent** is not disclosed quarterly, so the TTM value equals FY2025 (USD 291 mn).
4. **DAL gross interest expense** is not reported. Use `interest_expense_net` for every company when comparing coverage, or flag DAL.
5. **Special items** are not removed from operating income. Each company defines its own adjustments; if you use adjusted figures, take them from the non-GAAP tables in `data/raw` and cite them.
6. **AAL negative equity.** ROE and Debt/Equity are meaningless for AAL; use EBITDAR-based leverage instead.
7. **ALK and AAL losses.** ALK has a TTM net loss (−395) and AAL has a TTM net loss (−481); both reflect the 2026 fuel shock.
