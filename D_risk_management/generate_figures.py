
import sys
from pathlib import Path
import pandas as pd

# Add shared configuration to Python path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "shared"))

import config as cfg

# Read refinancing sensitivity results
df = pd.read_csv(
    ROOT / "D_risk_management/output/refinancing_sensitivity.csv"
)


fig, ax = cfg.new_figure()

rates = ["0%", "50%", "100%"]
colors = [
    cfg.SEQUENTIAL[6],
    cfg.SEQUENTIAL[4],
    cfg.SEQUENTIAL[2]
]

for rate, color in zip(rates, colors):
    subset = df[df["Refinancing Rate"] == rate]

    ax.plot(
        subset["Fuel Shock"],
        subset["Ending Cash"],
        marker="o",
        linewidth=2,
        color=color,
        label=f"{rate} refinancing"
    )

ax.axhline(
    0,
    color=cfg.MUTED,
    linestyle="--",
    linewidth=1
)

ax.legend()

cfg.finish_figure(
    fig,
    ax,
    title="Refinancing assumptions affect liquidity under fuel shocks",
    subtitle="Illustrative ending cash, USD mn; TTM cash flows and book current debt",
    filename="fig_D_liquidity_stress",
    ylabel="Ending cash (USD mn)"
)


# Figure D2: Fuel Hedging Strategy Comparison

hedge_df = pd.read_csv(
    ROOT / "D_risk_management/output/hedging_comparison.csv"
)

fig2, ax2 = cfg.new_figure()


strategies = {
    "Unhedged": {
        "color": cfg.PEER,
        "linestyle": "-"
    },
    "Call Option": {
        "color": cfg.SEQUENTIAL[2],
        "linestyle": "--"
    },
    "Collar": {
        "color": cfg.ACCENT,
        "linestyle": "-."
    }
}

for strategy, style in strategies.items():
    ax2.plot(
        hedge_df["Fuel Shock"],
        hedge_df[strategy],
        marker="o",
        linewidth=2,
        color=style["color"],
        linestyle=style["linestyle"],
        label=strategy
    )

ax2.axhline(
    0,
    color=cfg.MUTED,
    linestyle=":",
    linewidth=1
)

ax2.legend()

cfg.finish_figure(
    fig2,
    ax2,
    title="A collar limits fuel shocks but sacrifices price-decline benefits",
    subtitle="Illustrative 50% fuel hedge; USD million",
    filename="fig_D_hedging_comparison",
    ylabel="Free cash flow (USD mn)"
)


