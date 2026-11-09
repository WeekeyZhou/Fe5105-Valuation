# FE5105 Group Project — Southwest Airlines (LUV)

> 📌 **First, read everything in [`Read it before you do!`](./Read%20it%20before%20you%20do!/)**: the official project guidelines plus the Chinese task-split PDF (`分工说明.pdf`).

- **Target firm:** Southwest Airlines (LUV)
- **Competitors (N = 4):** Delta (DAL), United (UAL), American (AAL), Alaska (ALK)
- **Page limit:** fewer than 4 + 2×4 = **12 pages**, including everything (no separate cover page). Shorter is better at equal quality.
- **Format:** 1.5 line spacing, 12pt font. Submit on Canvas before the final exam (date TBC).

---

## Task split at a glance

| Member | Module | Firms covered | Report pages | Key deliverables |
|---|---|---|---|---|
| **A** | Financial ratios + shared data + intro/conclusion + final editing | All 5 | ~2.5 | `data/processed/financials.csv`, ratio comparison table |
| **B** | Financing sources + hidden leverage + WACC + capital-structure advice | All 5 | ~2.5 | WACC table for all 5 firms, `shared/assumptions.md` |
| **C** | Valuation: DCF + multiples cross-check + sensitivity analysis | LUV only | ~3 | DCF model, valuation range chart, sensitivity tables |
| **D** | Liquidity + adverse scenario + risk management & hedge proposal | LUV only | ~3 | Stress-test table, hedge proposal analysis |

> **Why this is balanced:** A and B work across all five firms, so their load is breadth. C and D work on LUV only, so their load is depth. A also owns the shared data and the final edit, to offset the lighter analysis.

---

## Detailed tasks

### 👤 A — Financial ratios (Part I, first half) + data + final edit
- [ ] Download the latest 10-K and most recent 10-Q for all 5 firms from SEC EDGAR → `data/raw/`
- [ ] Build one clean shared dataset → `data/processed/financials.csv` (everyone uses it)
- [ ] Choose a small set of ratios and explain the *economically important* differences, not just the numbers:
  - Profitability: operating margin, ROA, ROE
  - Efficiency: asset turnover; airline metrics CASM-ex, RASM, load factor
  - Leverage: Debt/EBITDAR, Debt/Equity
  - Liquidity: current ratio, cash/revenue
- [ ] Write the introduction (why these 5 firms, selection criteria) and the conclusion
- [ ] Final edit: consistent formatting, page count under the limit

### 👤 B — Financing & cost of capital (Part I, second half)
- [ ] Identify each firm's major financing sources (bonds, term loans, aircraft financing / EETCs, etc.)
- [ ] Identify material hidden leverage: operating leases, pension obligations, loyalty-program deferred revenue (air traffic liability)
- [ ] Estimate cost of debt from rating spreads or bond yields-to-maturity
- [ ] Estimate cost of equity with CAPM (regression beta, or industry beta unlevered and relevered)
- [ ] Compute the after-tax WACC for all 5 firms
- [ ] Should LUV change its capital structure? Cover the tax benefits, financial-distress costs, and financing needs from growth
- [ ] **Do this first:** create and maintain `shared/assumptions.md` (risk-free rate, market risk premium, tax rate, valuation date)

### 👤 C — Valuation (Part II)
- [ ] Forecast LUV's free cash flow to the firm (FCFF) for about 5 years, with each assumption justified
- [ ] Run the DCF with B's WACC → intrinsic enterprise value and value per share
- [ ] Cross-check with a competitor valuation multiple (EV/EBITDAR or EV/EBITDA)
- [ ] Compare the valuation range with the current market value
- [ ] Sensitivity analysis: WACC × long-run growth, plus one key operating assumption (suggested: **jet fuel price** or CASM-ex)
- [ ] Discuss how confident we are that the stock is mispriced, given market efficiency and forecast uncertainty

### 👤 D — Financial planning & risk management (Part III)
- [ ] Assess near-term cash ability: cash conversion cycle, current and quick ratios, interest coverage, cash reserves, debt maturity schedule
- [ ] Design one plausible adverse scenario (suggested: **jet fuel price shock**, e.g. the 2026 Strait of Hormuz episode) and test LUV under it
- [ ] Identify the major risks (fuel, demand cycle, interest rates, Boeing deliveries, labor) and decide which to bear and which to hedge
- [ ] Evaluate LUV's existing policy: it ended its fuel-hedging program in 2025
- [ ] Propose one specific hedge (e.g. crude or heating-oil call options, a collar) and explain how it protects cash flows and affects firm value

---

## Dependencies & timeline

```
Phase 1 ──► A: shared dataset      B: assumptions.md (rf, MRP, tax rate)
              │                      │
Phase 2 ──► A: ratio analysis      B: WACC ───────► C: DCF + sensitivity
              │
              └────────────────────────────────────► D: liquidity + stress test + hedge
Phase 3 ──► Everyone writes their section → A merges → peer review → submit on Canvas
```

- **C depends on B's WACC.** B should publish a first-draft WACC early so C can build the model, then update it later.
- **D depends on A's data.** Liquidity ratios read directly from `financials.csv`.
- **Everyone uses the same parameters from `shared/assumptions.md`**, so the numbers in the report stay consistent.

---

## Repository structure

```
Group Project/
├── README.md
├── Read it before you do!/
│   ├── Group Project Guidelines.pdf   # official guidelines
│   └── 分工说明.pdf                    # task split (Chinese)
├── shared/
│   └── assumptions.md                 # common assumptions (B maintains)
├── data/
│   ├── raw/                           # original 10-K / 10-Q files
│   └── processed/                     # financials.csv (A maintains)
├── A_ratios/
├── B_financing_wacc/
├── C_valuation/
├── D_risk_management/
└── report/
    ├── sections/                      # one section per member
    ├── figures/
    └── final_report.docx              # merged by A
```

## Collaboration rules
1. Work on your own branch (`A-ratios`, `B-wacc`, `C-valuation`, `D-risk`) and merge into `main` through a Pull Request that at least one teammate has reviewed.
2. Only edit your own folder. Tell the group before you change anything in `shared/` or `data/processed/`.
3. Record the source and date of every data point. The results in the report must be up to date.
4. All text, figures, and tables must be our own work. Any use of AI tools must follow NUS's AI guidelines.
