# Part C Southwest Airlines Valuation Assumptions

The base valuation date is **November 13, 2026**. All monetary amounts are in USD millions unless otherwise stated. The assumptions below describe the base case. Each rebuild reads the current CSV inputs from Parts A and B. Part C's editable model inputs are in [assumptions.json](C_piepline/assumptions.json).

## Data and Valuation Timing

| Input | Base case | Source and use |
|---|---:|---|
| Latest operating period | TTM ended September 30, 2026 | Part A financial data. TTM equals FY2025 plus the first nine months of 2026, less the first nine months of 2025. |
| Balance sheet date | September 30, 2026 | Part A balances for cash, debt and operating lease liabilities. |
| Closing price and shares outstanding | $44.94 per share and approximately 489.60 million shares | Part A's valuation-date market data. The original workbook uses the share count from the original market snapshot. A rebuild uses the precision available in Part A's CSV. |
| WACC and marginal tax rate | 7.97% and 24% | Part B's WACC results. Calculations retain the full precision of WACC and round it for display. |
| Adjusted net debt | $3,247 million | Debt of $5,887 million, including finance leases, plus operating lease liabilities of $984 million, less cash and short-term investments of $3,624 million. |
| Forecast timing | November 13 of each year from 2027 through 2031 | The model starts from the TTM operating run rate and discounts five full twelve-month periods using end-of-period timing. |

Sources include [Part A financial data](../data/processed/financials.csv), [Part B WACC results](../B_financing_wacc/output/wacc_results.csv) and the [group's shared assumptions](../shared/assumptions.md).

## Five-Year Operating Forecast

| Assumption | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 |
|---|---:|---:|---:|---:|---:|
| Available seat mile (ASM) growth | 2.50% | 2.50% | 2.25% | 2.00% | 2.00% |
| Revenue per available seat mile (TRASM) growth | 2.50% | 2.25% | 2.00% | 1.80% | 1.50% |
| Available seat miles per gallon growth | 0.80% | 0.80% | 0.80% | 0.80% | 0.80% |
| Jet fuel price (USD per gallon) | 3.10 | 2.95 | 2.85 | 2.80 | 2.80 |
| Nonfuel cost per ASM growth | 2.50% | 2.50% | 2.50% | 2.50% | 2.50% |
| Depreciation and amortization as a share of revenue | 5.00% | 5.00% | 5.00% | 5.10% | 5.20% |
| Gross cash capital expenditures as a share of revenue | 10.00% | 9.00% | 8.00% | 7.10% | 6.50% |

- **Revenue** equals available seat miles multiplied by revenue per available seat mile. Southwest's FY2025 capacity grew approximately 1.6% year over year. The forecast assumes moderate capacity expansion and early revenue gains from assigned seating, extra-legroom seats and bag fees. The contribution of these changes tapers over time.
- **Fuel expense** equals projected gallons consumed multiplied by the price per gallon. The forecast assumes the 2026 fuel price shock gradually eases. Jet fuel cost approximately $2.42 per gallon in FY2025 and $3.92 in Q3 2026. The fuel efficiency forecast draws on the approximately 0.7% year-over-year improvement reported for Q3 2026.
- **Nonfuel costs** rise with capacity and cost per available seat mile. The assumed 2.5% annual increase in unit cost allows for wages and other operating cost pressures.
- **Depreciation and capital expenditures** are based on historical ratios. Gross cash capital expenditures start near the TTM share of revenue and decline as fleet investment is assumed to moderate. Management's 2026 net capital spending guidance includes proceeds from asset sales and sale-leasebacks. The model uses gross cash capital expenditures.
- **Incremental operating working capital** is set at 0% of incremental revenue. The base case takes a neutral position because advance ticket payments, accounts payable and seasonality can cause short-term swings.

The forecast paths are Part C assumptions informed by the [Southwest FY2025 Form 10-K](../data/raw/html/LUV_10K_FY2025.htm) and [Southwest Q3 2026 Form 10-Q](../data/raw/html/LUV_10Q_Q3_2026.htm).

## Leases, Terminal Value and Peer Multiples

- **Operating leases.** The model uses the 4.2% weighted-average operating lease discount rate in Note 7 of the FY2025 10-K to estimate lease interest. Base fixed lease expense is $363 million, comprising $291 million for aircraft leases and $72 million for other fixed leases. Fixed lease expense and closing lease liabilities scale with capacity. Fixed lease expense less estimated lease interest approximates leased-asset amortization. Investment in new leased assets equals that amortization plus the increase in the lease liability balance. FCFF adds back after-tax lease interest and leased-asset amortization, then deducts investment in new leased assets. The enterprise-to-equity bridge deducts operating lease liabilities once through adjusted net debt.
- **Terminal value.** A nominal long-run growth rate of 2.25% and a 10% marginal return on invested capital imply a 22.5% terminal reinvestment rate. Year 6 FCFF equals after-tax operating profit less required reinvestment. Dividing Year 6 FCFF by WACC less long-run growth gives terminal value at the end of Year 5. The model discounts that value to the valuation date.
- **Peer valuation.** The cross-check uses market EV divided by TTM EBITDAR for DAL, UAL, AAL and ALK. EV equals market capitalization plus adjusted net debt. Part A's EBITDAR adds back aircraft rent. The median multiple provides the central estimate, and the lowest and highest multiples define the range. Southwest's TTM aircraft rent uses the FY2025 figure as a proxy.
- **Sensitivity analysis.** The WACC and long-run growth grid has two steps below and two above the base case, at 0.50 percentage points per step. The fuel scenarios shift the price by plus or minus $0.50 per gallon in each of the first two years. Other operating drivers and terminal fuel prices stay at their base-case values.
