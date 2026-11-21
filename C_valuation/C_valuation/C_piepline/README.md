# Rebuild Part C

Run this command from the project root.

```bash
python3 C_valuation/C_piepline/rebuild.py
```

The script reads Part A's `data/processed/financials.csv`, Part B's `B_financing_wacc/output/wacc_results.csv`, and `assumptions.json` in this directory. It writes the Excel valuation model, valuation range chart, and Word report to a new `C_valuation/rebuilt/` directory. The existing deliverables in `C_valuation/` remain unchanged. For a subsequent run, use a new output directory such as `--output C_valuation/rebuilt_v2`.

| File | Purpose |
|---|---|
| `rebuild.py` | Reads and validates the inputs, runs the model and report builders in a temporary directory, and publishes the three deliverables after both builders succeed. |
| `assumptions.json` | Stores Part C's forecast assumptions and sensitivity parameters. Edit this file to change the base-case assumptions. |
| `build_model.mjs` | Builds and recalculates the Excel workbook, then passes the calculated results to the report builder. |
| `build_report.py` | Uses those results to generate the PNG chart and Word report, including the figures, tables, and conclusions based on the valuation ranges. |

The pipeline requires Node.js with access to `@oai/artifact-tool` and Python with `python-docx` and `Pillow`. Use `--node`, `--node-modules`, and `--python` to specify their locations. Run the command with `--help` for the full list of options. To use alternate inputs, pass their paths with `--financials`, `--wacc`, and `--assumptions`.

The pipeline matches Part A's data to the valuation and balance sheet dates in Part B's results. Keep the original CSV field names and units. When rebuilding for a new annual report or valuation date, review the operating assumptions and filing references. The rebuild uses the input files listed above. Manual edits to Excel cells or formatting do not carry over to the rebuilt workbook.
