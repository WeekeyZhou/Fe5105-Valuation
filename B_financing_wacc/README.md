# Part B — Financing and Cost of Capital

Five airlines: LUV, DAL, UAL, AAL and ALK. Valuation date: 13 November 2026.

## Read the results

- `output/report.md`: report section for A to incorporate into the group report.
- `output/wacc_results.csv`: full-precision WACC results for C and A.
- `output/wacc_table.xlsx`: editable formula workbook using the delivered input snapshot.
- `output/financing_leverage.csv`: financing sources and supplementary obligations.
- `output/wacc_sensitivity.csv`: spread and debt-tax-shield sensitivity.
- `output/shared_assumptions.md`: Part B handoff text for the shared assumptions file.
- `sources/source_register.csv`: market inputs, ratings and filing locators.
- `sources/financial_inputs.csv`: exact A-data rows used, including original source notes.
- `sources/market/` and `sources/tax/`: supporting screenshots.

## Reproduce

From the repository root:

```bash
python3 B_financing_wacc/pipeline/build_wacc.py
```

Python 3 and its standard library are sufficient. The program reads
`data/processed/financials.csv` and `B_financing_wacc/wacc_inputs.json`.
It rebuilds the CSV and Markdown outputs and the input provenance manifest.
It does not download mutable web data. Source dates and URLs are saved in the JSON.
Rates are decimals; monetary figures are USD millions.

The Excel companion contains live formulas and editable blue input cells. It is
not automatically refreshed by the Python command. After changing JSON or A's
data, use regenerated CSV results as authoritative and update the workbook's
input cells to match. Its original input fingerprints are recorded on Inputs.

## Basis

The 24% marginal tax rate is B's selected modelling assumption. Debt costs are
broad rating-group estimates, not observed company yields. Detailed basis and
material limitations appear once in `output/report.md`; individual evidence
dates and rating types are in the source register. The workbook and report are
analysis deliverables, not a claim of group approval.

The shared-file handoff is supplied inside B. Notify the group before integrating
it into `shared/assumptions.md`, as required by the repository collaboration rule.
Keep other existing shared conventions. No changes to A's source data are needed.
