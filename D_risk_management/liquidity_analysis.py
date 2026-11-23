
import pandas as pd

# 1. Read the shared financial dataset
df = pd.read_csv("data/processed/financials.csv")

# 2. Select Southwest Airlines
luv = df[df["ticker"] == "LUV"]

# 3. Select the latest balance sheet
bs = luv[luv["period"] == "BS_2026-09-30"]

# 4. Display the key liquidity items
items = [
    "cash",
    "st_investments",
    "cash_and_sti",
    "receivables",
    "current_assets",
    "accounts_payable",
    "current_liabilities",
    "debt_current"
]

result = bs[bs["item"].isin(items)]

print("Southwest Airlines — Liquidity Data")
print("As of September 30, 2026")
print(result[["item", "value", "unit"]].to_string(index=False))


# 5. Calculate liquidity ratios
data = dict(zip(bs["item"], bs["value"]))

current_ratio = (
    data["current_assets"] / data["current_liabilities"]
)

quick_ratio = (
    data["cash_and_sti"] + data["receivables"]
) / data["current_liabilities"]

working_capital = (
    data["current_assets"] - data["current_liabilities"]
)

print("\n--- Liquidity Ratios ---")
print(f"Current Ratio: {current_ratio:.3f}")
print(f"Quick Ratio: {quick_ratio:.3f}")
print(f"Net Working Capital: {working_capital:,.0f} USD mn")


# 6. Cash conversion cycle analysis

fin = dict(zip(
    luv["period"] + "|" + luv["item"],
    luv["value"]
))

ar_2025 = fin["BS_2025-12-31|receivables"]
ar_2026 = fin["BS_2026-09-30|receivables"]

ap_2025 = fin["BS_2025-12-31|accounts_payable"]
ap_2026 = fin["BS_2026-09-30|accounts_payable"]

revenue = fin["TTM_2026Q3|revenue"]
opex = fin["TTM_2026Q3|total_opex"]

avg_ar = (ar_2025 + ar_2026) / 2
avg_ap = (ap_2025 + ap_2026) / 2

dso = avg_ar / revenue * 365
dpo_proxy = avg_ap / opex * 365

print("\n--- Cash Conversion Cycle Analysis ---")
print(f"DSO: {dso:.2f} days")
print(f"DPO Proxy: {dpo_proxy:.2f} days")
print(f"DSO - DPO Proxy: {dso - dpo_proxy:.2f} days")
print("Note: This is NOT a complete CCC.")


# 7. Air Traffic Liability Analysis

atl = luv[
    luv["item"] == "air_traffic_liability_total"
][["period", "value", "unit"]]

print("\n--- Air Traffic Liability ---")
print(atl.to_string(index=False))

atl_latest = fin.get(
    "BS_2026-09-30|air_traffic_liability_total"
)

if atl_latest is not None:
    atl_to_cash = atl_latest / data["cash_and_sti"]

    print(f"\nATL / Cash: {atl_to_cash:.2f}x")


# 8. Debt and Cash Flow Coverage

cash = data["cash_and_sti"]
current_debt = data["debt_current"]

total_liquidity = 5624.0  # From A's liquidity table

cfo = fin["TTM_2026Q3|cfo"]
capex = fin["TTM_2026Q3|capex"]
interest_paid = fin["TTM_2026Q3|interest_paid"]

fcf = cfo - capex

cash_coverage = cash / current_debt
liquidity_coverage = total_liquidity / current_debt

print("\n--- Debt and Cash Flow Coverage ---")
print(f"Cash / Current Debt: {cash_coverage:.2f}x")
print(f"Total Liquidity / Current Debt: {liquidity_coverage:.2f}x")
print(f"Operating Cash Flow: {cfo:,.0f} USD mn")
print(f"Capital Expenditure: {capex:,.0f} USD mn")
print(f"Free Cash Flow: {fcf:,.0f} USD mn")
print(f"Interest Paid: {interest_paid:,.0f} USD mn")


# 9. Cash Conversion Cycle Proxy

# Inventory figures from LUV Q3 2026 10-Q
inventory_2025 = 775.0
inventory_2026 = 997.0

avg_inventory = (
    inventory_2025 + inventory_2026
) / 2

# Operating expenses used as a proxy for COGS
dio_proxy = avg_inventory / opex * 365

ccc_proxy = dio_proxy + dso - dpo_proxy

print("\n--- Cash Conversion Cycle Proxy ---")
print(f"Average Inventory: {avg_inventory:,.0f} USD mn")
print(f"DIO Proxy: {dio_proxy:.2f} days")
print(f"DSO: {dso:.2f} days")
print(f"DPO Proxy: {dpo_proxy:.2f} days")
print(f"CCC Proxy: {ccc_proxy:.2f} days")
