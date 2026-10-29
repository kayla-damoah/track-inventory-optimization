"""
Generate the illustrative athlete-level dataset used by the analysis.

The sizes, events and replacement dates are SIMULATED. Group totals are fixed to match the
84-athlete model (43 women, 41 men) so the CSV, the analysis script and the dashboard agree.
Athletes are identified by ID only. The random seed is fixed, so the output is reproducible.

Usage:
    python generate_sample_data.py
"""
import csv
import random
from pathlib import Path

SEED = 2026
AS_OF = (2026, 2)  # replacement dates are generated relative to this month (year, month)

WOMEN_SIZES = {"XS": 8, "S": 21, "M": 12, "L": 2}            # 43 athletes
MEN_SIZES = {"S": 10, "M": 19, "L": 9, "XL": 3}              # 41 athletes
EVENTS = {"Distance": 36, "Sprints": 18, "Jumps": 12, "Throws": 8,
          "Javelin": 4, "Pole Vault": 4, "Multi-Events": 2}  # 84 athletes
CLASS_YEARS = {"Freshman": 18, "Sophomore": 22, "Junior": 24, "Senior": 14, "Graduate": 6}  # 84

# Months since the last replacement are drawn from 0..lifecycle for each item.
LIFECYCLE_MONTHS = {
    "Competition_Spikes_Replaced": 7,
    "Training_Gear_Replaced": 12,
    "Warm_Up_Replaced": 21,
    "Uniform_Replaced": 24,
    "Travel_Bag_Replaced": 36,
}


def expand(counts):
    return [key for key, n in counts.items() for _ in range(n)]


def months_ago(n):
    year, month = AS_OF
    total = year * 12 + (month - 1) - n
    return f"{total // 12}-{total % 12 + 1:02d}"


def main():
    rng = random.Random(SEED)
    genders = ["Female"] * sum(WOMEN_SIZES.values()) + ["Male"] * sum(MEN_SIZES.values())
    sizes = expand(WOMEN_SIZES) + expand(MEN_SIZES)
    events = expand(EVENTS)
    years = expand(CLASS_YEARS)
    assert len(genders) == len(sizes) == len(events) == len(years) == 84

    rng.shuffle(events)
    rng.shuffle(years)

    fields = ["Athlete_ID", "Gender", "Event_Specialization", "Class_Year", "Size_Apparel", *LIFECYCLE_MONTHS]
    out = Path(__file__).with_name("rutgers_track_inventory_data.csv")
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for i in range(84):
            row = {
                "Athlete_ID": f"A{i + 1:03d}",
                "Gender": genders[i],
                "Event_Specialization": events[i],
                "Class_Year": years[i],
                "Size_Apparel": sizes[i],
            }
            for column, lifecycle in LIFECYCLE_MONTHS.items():
                row[column] = months_ago(rng.randint(0, lifecycle))
            writer.writerow(row)
    print(f"Wrote {out.name} (84 simulated athletes, seed {SEED})")


if __name__ == "__main__":
    main()
