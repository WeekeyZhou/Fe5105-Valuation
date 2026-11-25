
import pandas as pd

# 1. Load financial data
df = pd.read_csv("data/processed/financials.csv")

luv = df[
    (df["ticker"] == "LUV") &
    (df["period"] == "TTM_2026Q3")
]

data = dict(zip(luv["item"], luv["value"]))

# 2. Baseline financial figures (USD million)
fuel_expense = data["fuel_expense"]
cfo = data["cfo"]
capex = data["capex"]

base_fcf = cfo - capex

# 3. Stress-test assumptions
shocks = [0.00, 0.20, 0.30]

results = []

for shock in shocks:

    additional_fuel_cost = fuel_expense * shock

    stressed_cfo = cfo - additional_fuel_cost
    stressed_fcf = stressed_cfo - capex

    results.append({
        "Fuel Price Shock": f"{shock:.0%}",
        "Additional Fuel Cost": additional_fuel_cost,
        "Operating Cash Flow": stressed_cfo,
        "Free Cash Flow": stressed_fcf
    })

# 4. Display results
result_df = pd.DataFrame(results)

print("\n--- Jet Fuel Price Stress Test ---")
print(result_df.to_string(index=False, float_format="%.1f"))


# 5. Liquidity stress test

beginning_cash = 3624.0
current_debt = 2153.0
undrawn_revolver = 2000.0

liquidity_results = []

for shock in shocks:

    additional_fuel_cost = fuel_expense * shock

    stressed_fcf = base_fcf - additional_fuel_cost

    ending_cash = (
        beginning_cash
        + stressed_fcf
        - current_debt
    )

    liquidity_after_revolver = (
        ending_cash + undrawn_revolver
    )

    liquidity_results.append({
        "Fuel Shock": f"{shock:.0%}",
        "Stressed FCF": stressed_fcf,
        "Ending Cash": ending_cash,
        "Liquidity incl. Revolver": liquidity_after_revolver
    })

liquidity_df = pd.DataFrame(liquidity_results)

print("\n--- Liquidity Stress Test ---")
print(
    liquidity_df.to_string(
        index=False,
        float_format="%.1f"
    )
)


# 6. Refinancing sensitivity analysis

refinancing_rates = [0.0, 0.5, 1.0]
refinancing_results = []

for shock in shocks:
    stressed_fcf = base_fcf - fuel_expense * shock

    for rate in refinancing_rates:
        cash_debt_repayment = current_debt * (1 - rate)

        ending_cash = (
            beginning_cash
            + stressed_fcf
            - cash_debt_repayment
        )

        refinancing_results.append({
            "Fuel Shock": f"{shock:.0%}",
            "Refinancing Rate": f"{rate:.0%}",
            "Ending Cash": ending_cash,
            "Liquidity incl. Revolver":
                ending_cash + undrawn_revolver
        })

refinancing_df = pd.DataFrame(refinancing_results)

print("\n--- Refinancing Sensitivity ---")
print(
    refinancing_df.to_string(
        index=False,
        float_format="%.1f"
    )
)


from pathlib import Path

output_dir = Path("D_risk_management/output")
output_dir.mkdir(parents=True, exist_ok=True)

result_df.to_csv(
    output_dir / "stress_test.csv",
    index=False
)

liquidity_df.to_csv(
    output_dir / "liquidity_stress.csv",
    index=False
)

refinancing_df.to_csv(
    output_dir / "refinancing_sensitivity.csv",
    index=False
)

print("\nStress-test results exported successfully.")
