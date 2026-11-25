
import pandas as pd

# Baseline figures (USD million)
fuel_expense = 7056.0
base_cfo = 2755.0
capex = 3205.0

# Illustrative collar assumptions
hedge_ratio = 0.50
call_strike = 1.10
put_strike = 0.90
net_premium = 0.0

# Include falling and rising fuel prices
price_scenarios = [-0.30, -0.20, 0.0, 0.20, 0.30]

results = []

for shock in price_scenarios:

    price_ratio = 1 + shock

    # Additional fuel expense relative to baseline
    fuel_cost_change = fuel_expense * shock

    # Payoff of long call and short put
    call_payoff = (
        fuel_expense
        * hedge_ratio
        * max(price_ratio - call_strike, 0)
    )

    put_payoff = (
        -fuel_expense
        * hedge_ratio
        * max(put_strike - price_ratio, 0)
    )

    hedge_payoff = call_payoff + put_payoff

    # Compare unhedged and hedged cash flows
    unhedged_fcf = base_cfo - capex - fuel_cost_change

    hedged_fcf = (
        unhedged_fcf
        + hedge_payoff
        - net_premium
    )

    results.append({
        "Fuel Shock": f"{shock:+.0%}",
        "Unhedged FCF": unhedged_fcf,
        "Hedge Payoff": hedge_payoff,
        "Hedged FCF": hedged_fcf
    })

result_df = pd.DataFrame(results)

print("\n--- Fuel Collar Hedging Analysis ---")
print(result_df.to_string(index=False, float_format="%.1f"))


# 5. Compare Unhedged, Call, and Collar

call_premium_rate = 0.03
call_premium = (
    fuel_expense * hedge_ratio * call_premium_rate
)

comparison = []

for shock in price_scenarios:

    price_ratio = 1 + shock
    fuel_cost_change = fuel_expense * shock

    unhedged_fcf = (
        base_cfo - capex - fuel_cost_change
    )

    call_payoff = (
        fuel_expense
        * hedge_ratio
        * max(price_ratio - call_strike, 0)
    )

    put_payoff = (
        -fuel_expense
        * hedge_ratio
        * max(put_strike - price_ratio, 0)
    )

    call_fcf = (
        unhedged_fcf
        + call_payoff
        - call_premium
    )

    collar_fcf = (
        unhedged_fcf
        + call_payoff
        + put_payoff
        - net_premium
    )

    comparison.append({
        "Fuel Shock": f"{shock:+.0%}",
        "Unhedged": unhedged_fcf,
        "Call Option": call_fcf,
        "Collar": collar_fcf
    })

comparison_df = pd.DataFrame(comparison)

print("\n--- Hedging Strategy Comparison ---")
print(
    comparison_df.to_string(
        index=False,
        float_format="%.1f"
    )
)


from pathlib import Path

output_dir = Path("D_risk_management/output")
output_dir.mkdir(parents=True, exist_ok=True)

comparison_df.to_csv(
    output_dir / "hedging_comparison.csv",
    index=False
)

print("\nHedging comparison exported successfully.")
