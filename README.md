# Apparel Inventory Optimization: Rutgers Track & Field

A projection model for how an 84-athlete track & field program could buy apparel more efficiently: one bulk order, size-matched stock, and planned replacement cycles instead of rush orders.

**[View the live dashboard](https://kayla-damoah.github.io/track-inventory-optimization/)** or open `index.html` in a browser.

## The problem

Apparel for the team was bought in small, reactive batches. Sizes were guessed, items wore out at different rates, and gaps were filled with expensive emergency orders.

## What the model projects

| Metric | Today | Projected | How |
|---|---|---|---|
| Annual apparel spend | $42,000 | $34,020 | 19% bulk-order discount on the same number of items |
| Emergency orders per year | 32 | 19 | 40% fewer, from planned replacement |
| Rush fees | $800 | $475 | $25 per emergency order |
| **Total annual savings** | | **about $8,300** | $7,980 from bulk pricing plus $325 in rush fees |

These are **projections**, not measured results. See the next section.

## What is real, assumed and simulated

| Input | Value | Status |
|---|---|---|
| Roster | 84 athletes (43 women, 41 men) | Team baseline |
| Annual apparel budget | $42,000 | Team baseline |
| Emergency orders per year | 32 | Team baseline |
| Bulk-order discount | 19% | Assumption, to be confirmed with the vendor |
| Reduction in emergency orders | 40% | Assumption |
| Rush fee per emergency order | $25 | Assumption |
| Athlete sizes and replacement dates | Per-athlete values | Simulated |
| Seasonal demand index | Monthly values | Modeled |

The savings come from applying the assumed discount and reduction to the team's baseline. Real savings would depend on the vendor's actual pricing and on the team following the plan.

## Approach

1. **Size forecasting.** Model the size mix for each team (women's skews S and M, men's skews M and L) and add a 10% buffer when ordering.
2. **Lifecycle modeling.** Estimate replacement cycles per item type, from about 7 months for competition spikes to 36 months for travel bags.
3. **Seasonal demand.** Map monthly demand to find the cheapest time to order. Demand falls in summer and rebuilds in September.
4. **Cost model.** Apply the bulk discount and fewer rush orders to the baseline budget.
5. **Recommendations.** Order once in September, stock by forecasted size, and replace on a schedule.

## Recommendations

1. **Order once, in September.** Consolidate purchasing before the season builds to earn the volume discount.
2. **Stock by forecasted size.** Use the roster's size mix plus a 10% buffer instead of equal quantities of every size.
3. **Replace on a schedule.** Track issue dates and keep buffer stock so replacements are planned.

## Files

| File | What it is |
|---|---|
| `index.html` | Interactive dashboard (Plotly) |
| `inventory_analysis.py` | Python analysis: reads the CSV and computes every figure (no randomness) |
| `rutgers_track_inventory_data.csv` | Simulated athlete-level dataset: 84 athletes, anonymized IDs |
| `generate_sample_data.py` | Regenerates the CSV from a fixed seed so it is reproducible |

## Run it

```bash
pip install pandas
python inventory_analysis.py
```

The script prints the size forecast, equipment needs, cost model, seasonal pattern and recommendations. It reads `rutgers_track_inventory_data.csv` and is deterministic, so every run gives the same output. The baseline figures and the assumed rates sit in two labeled blocks at the top of the file (`BASELINE` and `ASSUMPTIONS`), so you can change an assumption and see the projection move.

To regenerate the sample data: `python generate_sample_data.py`.

## Limitations

- The savings are projections that rest on an assumed discount and an assumed reduction in emergency orders. The first step in a real rollout is to confirm vendor pricing.
- Athlete-level sizes, events and replacement dates are simulated, so the charts show the modeling approach, not the actual roster. Group totals are set to match the 84-athlete baseline.
- Seasonal demand values and equipment replacement cycles are modeled estimates, not purchasing history.
- The equipment-needs table (about $26,900 a year) covers five item types and does not reconcile to the $42,000 total budget, which also includes other apparel and merchandise.

## Tools

Python (pandas), Plotly.

---

Kayla Damoah | Rutgers University, Business Analytics & Information Technology
