# FE5105 Group Project — Southwest Airlines (LUV)

> **Status: complete.** The merged report is [`report/final_report.docx`](./report/final_report.docx) (11 pages; PDF preview: [`report/final_report_preview.pdf`](./report/final_report_preview.pdf)).
> The official guidelines and the Chinese task-split PDF are in [`Read it before you do!`](./Read%20it%20before%20you%20do!/).

- **Target firm:** Southwest Airlines (LUV)
- **Competitors (N = 4):** Delta (DAL), United (UAL), American (AAL), Alaska (ALK)
- **Data dates:** balance sheet at 30 September 2026; trailing twelve months (TTM) = FY2025 + 9M2026 − 9M2025; market data and valuation date 13 November 2026
- **Page limit:** fewer than 4 + 2×4 = 12 pages, everything included

---

## Group members and sections

| Member | Name | Report section | Main outputs |
|---|---|---|---|
| **A** | ZHOU Mo | 1 Introduction, 2 Financial Performance, 6 Conclusion; shared data; final editing | `data/processed/financials.csv`, `A_ratios/output/ratios_table.xlsx`, Figure 1 |
| **B** | ZHANG Jiaxin | 3 Financing and Cost of Capital | `B_financing_wacc/output/wacc_results.csv`, `shared/assumptions.md` |
| **C** | RUAN Yalin | 4 Valuation | `C_valuation/LUV_Valuation_Model.xlsx`, Figure 2 |
| **D** | JING Wanyi | 5 Financial Planning and Risk Management | `D_risk_management/output/*.csv`, Figures 3–4 |

## Key results

| Item | Result |
|---|---|
| TTM operating margin | LUV 4.4%, the only firm in the group whose margin rose year on year |
| WACC | LUV 7.97% (DAL 7.95%, UAL 7.96%, AAL 8.75%, ALK 7.88%) |
| DCF value per share | $50.22 (range $39.80–$70.73) vs $44.94 close on 13 November 2026 |
| Peer EV/EBITDAR median | $48.87 per share (range $37.11–$74.45) |
| 30% fuel-price shock | $1,095.8 million funding shortfall with no refinancing |
| 50% fuel collar | Improves stressed free cash flow by $705.6 million |

---

## How to rebuild

Run everything from the project root, in this order. Python packages needed: `pandas`, `openpyxl`, `matplotlib`, `beautifulsoup4`, `python-docx`, `Pillow`.

```bash
# A: shared dataset, ratios and Figure 1
python3 A_ratios/pipeline/build_financials.py   # reads data/raw/, writes data/processed/
python3 A_ratios/pipeline/comparability.py
python3 A_ratios/pipeline/compute_ratios.py
python3 A_ratios/pipeline/make_figures.py

# B: financing and WACC
python3 B_financing_wacc/pipeline/build_wacc.py

# C: valuation (also needs Node.js; see C_valuation/C_piepline/README.md)
python3 C_valuation/C_piepline/rebuild.py

# D: liquidity, stress test, hedging and Figures 3–4
python3 D_risk_management/liquidity_analysis.py
python3 D_risk_management/fuel_stress_test.py
python3 D_risk_management/fuel_hedging.py
python3 D_risk_management/generate_figures.py

# Final report: merges the four sections into report/final_report.docx
python3 report/build_final_report.py
```

`report/build_final_report.py` only renumbers tables and figures, fixes typos and applies one house style (`$` with million/billion in text, US spelling, day-month-year dates). It does not change any member's analysis. Shared formatting for tables and figures comes from `shared/config.py`.

---

## Repository structure

```
Group Project/
├── README.md
├── Read it before you do!/        # guidelines + task split (Chinese)
├── shared/
│   ├── assumptions.md             # common parameters (tax rate, Rf, ERP, dates)
│   └── config.py                  # shared figure and Word formatting
├── data/
│   ├── raw/                       # 10-K, 10-Q, 8-K filings and market data
│   └── processed/                 # financials.csv, DATA_DICTIONARY.md, validation_checks.csv
├── A_ratios/                      # pipeline/ + output/ (ratios, comparability adjustments)
├── B_financing_wacc/              # pipeline/, sources/, output/ (WACC, financing, Part B text)
├── C_valuation/                   # C_piepline/, valuation model, Part C text
├── D_risk_management/             # analysis scripts + output/
└── report/
    ├── sections/                  # A and D section files
    ├── figures/                   # Figures 1, 3, 4
    ├── build_final_report.py      # merge script
    ├── final_report.docx          # final submission
    └── final_report_preview.pdf
```

## Data sources and AI use
- Company filings from SEC EDGAR (Form 10-K FY2021–FY2025, Form 10-Q Q3 2026, Form 8-K earnings releases); U.S. Treasury yields; Damodaran; ICE BofA spreads via FRED.
- The group used Claude (Anthropic) and ChatGPT (OpenAI) for coding, data extraction, drafting and language editing, in line with NUS guidelines on AI use. All members checked the calculations and reviewed the final text.
