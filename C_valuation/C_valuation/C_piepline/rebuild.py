"""Build Part C from the two upstream CSVs into a new output directory."""

import argparse
import csv
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import date

PIPELINE = Path(__file__).resolve().parent
ROOT = PIPELINE.parents[1]
RUNTIME = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies"
FILES = ("LUV_Valuation_Model.xlsx", "LUV_Valuation_Range.png", "Part_C_Valuation.docx")


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--financials", type=Path, default=ROOT / "data/processed/financials.csv")
    parser.add_argument("--wacc", type=Path, default=ROOT / "B_financing_wacc/output/wacc_results.csv")
    parser.add_argument("--assumptions", type=Path, default=PIPELINE / "assumptions.json")
    parser.add_argument("--output", type=Path, default=PIPELINE.parent / "rebuilt")
    parser.add_argument("--node", default=os.environ.get("C_NODE", str(RUNTIME / "node/bin/node") if (RUNTIME / "node/bin/node").is_file() else "node"))
    parser.add_argument("--python", default=os.environ.get("C_PYTHON", str(RUNTIME / "python/bin/python3") if (RUNTIME / "python/bin/python3").is_file() else sys.executable))
    parser.add_argument("--node-modules", type=Path, default=Path(os.environ.get("C_NODE_MODULES", RUNTIME / "node/node_modules")))
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        parser.error(f"{output} already exists. Choose a new --output directory.")
    financials, wacc = read_csv(args.financials), read_csv(args.wacc)
    luv = [row for row in wacc if row["ticker"] == "LUV"]
    if len(luv) != 1:
        parser.error("WACC CSV must contain exactly one LUV row.")
    assumptions = json.loads(args.assumptions.read_text(encoding="utf-8"))
    for key, values in assumptions["forecast"].items():
        if len(values) != 5 or any(not math.isfinite(value) for value in values):
            parser.error(f"{key} must contain five finite values.")
    valuation_date = date.fromisoformat(luv[0]["valuation_date"])
    debt_date = date.fromisoformat(luv[0]["debt_date"])
    if debt_date > valuation_date:
        parser.error("The balance sheet date exceeds the valuation date.")
    g, roic = assumptions["terminal_growth"], assumptions["terminal_roic"]
    wacc_step, growth_step = assumptions["wacc_grid_step"], assumptions["growth_grid_step"]
    lo_g, hi_g = g - 2 * growth_step, g + 2 * growth_step
    lo_wacc = float(luv[0]["wacc"]) - 2 * wacc_step
    shock = assumptions["fuel_shock_usd_per_gallon"]
    if not (wacc_step > 0 and growth_step > 0 and shock > 0 and lo_g >= 0
            and hi_g < min(lo_wacc, roic)
            and shock < min(assumptions["forecast"]["fuel_price"][:2])):
        parser.error("Check grid ranges, terminal ROIC and fuel shock.")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".c-build-", dir=output.parent) as folder:
        work = Path(folder)
        (work / "inputs.json").write_text(json.dumps({
            "financials": financials, "wacc": luv[0], "assumptions": assumptions
        }), encoding="utf-8")
        if not (args.node_modules / "@oai/artifact-tool").exists():
            parser.error("Set --node-modules to a directory containing @oai/artifact-tool.")
        (work / "node_modules").symlink_to(args.node_modules.resolve(), target_is_directory=True)
        shutil.copyfile(PIPELINE / "build_model.mjs", work / "build_model.mjs")
        subprocess.run([args.node, str(work / "build_model.mjs"), str(work)], check=True)
        subprocess.run([args.python, str(PIPELINE / "build_report.py"), str(work)], check=True)
        deliverables = work / "deliverables"
        deliverables.mkdir()
        for name in FILES:
            (work / name).rename(deliverables / name)
        output.mkdir(exist_ok=False)
        for name in FILES:
            (deliverables / name).rename(output / name)
    print(f"Part C rebuilt in {output}")


if __name__ == "__main__":
    main()
