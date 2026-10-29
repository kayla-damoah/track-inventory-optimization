"""
Rutgers Track & Field: apparel inventory optimization (projection model)

Reads the athlete-level CSV and prints:
  1. Size forecast by team, with a 10% buffer
  2. Annual equipment needs by item
  3. Cost model: baseline budget vs. projected budget with bulk ordering
  4. Seasonal demand pattern and the bulk-order window
  5. Recommendations

Every number printed is computed here. Inputs are split into two groups at the top of the
file so it is clear what came from the team and what is an assumption:

  BASELINE     figures from the team (roster size, annual apparel budget, emergency orders)
  ASSUMPTIONS  improvement rates the model applies (bulk discount, fewer emergency orders)

The savings are therefore a projection, not a measured result. The athlete-level data in the
CSV is simulated (see generate_sample_data.py). Output is deterministic: there is no randomness.

Usage:
    python inventory_analysis.py [path/to/athletes.csv]
"""
import sys
from pathlib import Path

import pandas as pd

DEFAULT_CSV = Path(__file__).with_name("rutgers_track_inventory_data.csv")

# ---- Inputs -----------------------------------------------------------------------------
BASELINE = {
    "annual_budget": 42000,     # dollars per year spent on apparel
    "emergency_orders": 32,     # rush orders per year
    "avg_item_cost": 52,        # dollars per item
}
ASSUMPTIONS = {
    "bulk_discount": 0.19,            # discount from one September bulk order
    "emergency_reduction": 0.40,      # share of emergency orders avoided with planned replacement
    "rush_fee_per_order": 25,         # dollars saved per avoided emergency order
    "size_buffer": 0.10,              # extra stock added on top of the forecasted size mix
}

# Replacement cycle, annual need per athlete and unit cost for each equipment category.
EQUIPMENT = {
    "Competition Spikes":   {"lifecycle_months": 7,  "annual_need_per_athlete": 1.5,  "unit_cost": 120},
    "Training Gear":        {"lifecycle_months": 12, "annual_need_per_athlete": 1.0,  "unit_cost": 45},
    "Warm-Up Suits":        {"lifecycle_months": 21, "annual_need_per_athlete": 0.6,  "unit_cost": 85},
    "Competition Uniforms": {"lifecycle_months": 24, "annual_need_per_athlete": 0.3,  "unit_cost": 95},
    "Travel Bags":          {"lifecycle_months": 36, "annual_need_per_athlete": 0.25, "unit_cost": 65},
}

# Relative monthly demand (100 = peak). Modeled from the competition calendar, not purchase history.
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DEMAND_INDEX = [75, 85, 90, 95, 100, 40, 35, 50, 85, 80, 45, 40]
SEASONS = ["Indoor"] * 3 + ["Outdoor"] * 2 + ["Summer"] * 3 + ["Fall prep"] * 2 + ["Off-season"] * 2

SIZE_ORDER = ["XS", "S", "M", "L", "XL"]


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"Athlete_ID", "Gender", "Event_Specialization", "Size_Apparel"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"{path.name} is missing columns: {sorted(missing)}")
    return df


def size_forecast(df: pd.DataFrame) -> dict:
    """Units to stock per size for each team: the roster's size counts plus a buffer."""
    forecast = {}
    for gender, team in (("Female", "Women"), ("Male", "Men")):
        counts = df[df["Gender"] == gender]["Size_Apparel"].value_counts()
        forecast[team] = {
            "athletes": int(counts.sum()),
            "counts": {s: int(counts.get(s, 0)) for s in SIZE_ORDER if counts.get(s, 0)},
            "stock": {s: int(counts.get(s, 0) * (1 + ASSUMPTIONS["size_buffer"]))
                      for s in SIZE_ORDER if counts.get(s, 0)},
        }
    return forecast


def equipment_needs(athletes: int) -> pd.DataFrame:
    rows = []
    for item, spec in EQUIPMENT.items():
        units = int(spec["annual_need_per_athlete"] * athletes)
        rows.append({
            "Item": item,
            "Lifecycle (months)": spec["lifecycle_months"],
            "Annual units": units,
            "Unit cost": f"${spec['unit_cost']}",
            "Annual cost": f"${units * spec['unit_cost']:,}",
        })
    return pd.DataFrame(rows)


def cost_model() -> dict:
    """Project the budget with bulk pricing and fewer emergency orders (same number of items)."""
    budget = BASELINE["annual_budget"]
    orders = BASELINE["emergency_orders"]
    projected_budget = round(budget * (1 - ASSUMPTIONS["bulk_discount"]))
    projected_orders = round(orders * (1 - ASSUMPTIONS["emergency_reduction"]))
    bulk_savings = budget - projected_budget
    rush_savings = (orders - projected_orders) * ASSUMPTIONS["rush_fee_per_order"]
    return {
        "baseline_budget": budget,
        "projected_budget": projected_budget,
        "baseline_emergency_orders": orders,
        "projected_emergency_orders": projected_orders,
        "bulk_savings": bulk_savings,
        "rush_fee_savings": rush_savings,
        "total_savings": bulk_savings + rush_savings,
        "total_savings_pct": (bulk_savings + rush_savings) / budget * 100,
    }


def seasonal_demand() -> pd.DataFrame:
    return pd.DataFrame({"Month": MONTHS, "Demand index": DEMAND_INDEX, "Season": SEASONS})


def bulk_order_window() -> list:
    """Months with high demand coming off the summer low: where a single bulk order lands."""
    return ["Sep", "Oct"]


def heading(text: str) -> None:
    print(f"\n{text}\n" + "-" * 70)


def main(csv_path: Path) -> None:
    df = load(csv_path)

    print("=" * 70)
    print("RUTGERS TRACK & FIELD: APPAREL INVENTORY PROJECTION MODEL")
    print("=" * 70)
    print(f"Data: {csv_path.name} ({len(df)} athletes, simulated athlete-level values)")

    heading("1. SIZE FORECAST (roster size mix plus {:.0%} buffer)".format(ASSUMPTIONS["size_buffer"]))
    forecast = size_forecast(df)
    for team, info in forecast.items():
        print(f"{team}'s team (n={info['athletes']}):")
        for size, units in info["stock"].items():
            print(f"  {size:<3} {info['counts'][size]:>3} athletes -> stock {units}")

    heading("2. ANNUAL EQUIPMENT NEEDS")
    print(equipment_needs(len(df)).to_string(index=False))

    heading("3. COST MODEL (projection; inputs below are assumptions)")
    print(f"Assumed bulk discount:            {ASSUMPTIONS['bulk_discount']:.0%}")
    print(f"Assumed emergency-order cut:      {ASSUMPTIONS['emergency_reduction']:.0%}")
    c = cost_model()
    print(f"Annual budget:                    ${c['baseline_budget']:,} -> ${c['projected_budget']:,}")
    print(f"Emergency orders per year:        {c['baseline_emergency_orders']} -> {c['projected_emergency_orders']}")
    print(f"Savings from bulk pricing:        ${c['bulk_savings']:,}")
    print(f"Savings from fewer rush fees:     ${c['rush_fee_savings']:,}")
    print(f"Total projected annual savings:   ${c['total_savings']:,} ({c['total_savings_pct']:.1f}% of budget)")

    heading("4. SEASONAL DEMAND")
    print(seasonal_demand().to_string(index=False))
    print(f"\nBulk order window: {' to '.join(bulk_order_window())}")

    heading("5. RECOMMENDATIONS")
    print("1. Order once, in September, to earn the bulk discount (confirm the rate with the vendor).")
    print("2. Stock by the roster's size mix plus a buffer, not equal quantities of every size.")
    print("3. Track issue dates and replace on a schedule (competition spikes about every 7 months).")
    print("\nNote: savings are projections based on the assumptions above, not measured results.\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV)
