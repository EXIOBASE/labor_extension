"""Check the vectorised ISIC3 -> ISIC4 conversion against the original tasks.

The original `task_A` ... `task_X` in working_hours/isic3_to_isic4.py are far
too slow to run over the full country set (that is why they were replaced), so
this compares them on a subset: the N countries with the most ISIC3
observations, which between them exercise every source letter and every target.

Run directly (no pytest needed)::

    <fao_data-python> tests/test_isic3_to_isic4_equivalence.py [n_countries]

Reads isic3.csv from the repo root and workforce.csv from the labour
final_table directory, both written by the stage-1 workforce build.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(1, str(REPO / "working_hours"))

from working_hours import isic3_to_isic4 as original  # noqa: E402
from working_hours.isic3_to_isic4_vectorised import (  # noqa: E402
    CONCORDANCE, isic3_to_isic4,
)

# The original hardcodes range(1995, 2023) in every task, so the comparison is
# pinned to that span. Downstream, combine_isic_3_4 keeps ISIC3-derived values
# only for years < 2009, so the span never mattered.
YEARS = range(1995, 2023)

# float(df.to_string(...)) in the original rounds to 6 decimal places.
TOLERANCE = 2e-6

WORKFORCE_CSV = Path("D:/indecol/data/labour/final_table/workforce.csv")
ISIC3_CSV = REPO / "isic3.csv"


def run_original(isic3: pd.DataFrame, workforce: pd.DataFrame) -> pd.DataFrame:
    empty = pd.DataFrame(columns=["ref_area", "sex", "classif1", "time",
                                  "obs_value"])
    frames = []
    for target in CONCORDANCE:
        task = getattr(original, f"task_{target}")
        frames.append(task(empty.iloc[0:0], isic3, workforce))
    return pd.concat(frames, ignore_index=True)


def main(n_countries: int = 3) -> int:
    if not WORKFORCE_CSV.exists():
        print(f"missing {WORKFORCE_CSV}; run stage 1 first")
        return 2

    isic3 = pd.read_csv(ISIC3_CSV)
    counts = (isic3[isic3.obs_value.notna()]
              .groupby("ref_area").size().sort_values(ascending=False))
    countries = [c for c in counts.index if c != "KOS"][:n_countries]
    print(f"countries under test: {countries}")

    isic3_subset = isic3[isic3["ref_area"].isin(countries)].copy()
    letters = set(isic3_subset["classif1"].str.removeprefix("ECO_ISIC3_")
                  .str.lower())
    needed = {s for sources in CONCORDANCE.values() for s, _, _ in sources}
    if missing := needed - letters:
        print(f"WARNING: source letters absent from the subset: "
              f"{sorted(missing)}; those paths are untested")

    workforce = pd.read_csv(
        WORKFORCE_CSV, usecols=["ref_area", "sex", "time", "classif1",
                                "obs_value"])
    workforce_subset = workforce[workforce["ref_area"].isin(countries)].copy()

    # The rewrite corrects two defects in the original (task_S's population
    # weights, and Kosovo being dropped). Turn them back on so this compares
    # the vectorisation, not the corrections - those are quantified separately
    # in the module docstring.
    started = time.perf_counter()
    got = isic3_to_isic4(isic3_subset, workforce_subset, YEARS, verbose=False,
                         reproduce_original_defects=True)
    fast_seconds = time.perf_counter() - started
    print(f"vectorised: {len(got):,} rows in {fast_seconds:.2f}s")

    started = time.perf_counter()
    want = run_original(isic3_subset, workforce_subset)
    slow_seconds = time.perf_counter() - started
    print(f"original:   {len(want):,} rows in {slow_seconds:.1f}s "
          f"({slow_seconds / max(fast_seconds, 1e-9):,.0f}x slower on "
          f"{n_countries} of {isic3.ref_area.nunique()} countries)")

    keys = ["ref_area", "sex", "classif1", "time"]
    want["obs_value"] = pd.to_numeric(want["obs_value"])
    merged = want.merge(got, on=keys, how="outer", suffixes=("_original", "_new"),
                        indicator=True)

    failures = 0
    only_original = merged[merged["_merge"] == "left_only"]
    only_new = merged[merged["_merge"] == "right_only"]
    if len(only_original):
        failures += len(only_original)
        print(f"FAIL: {len(only_original)} rows only the original produced")
        print(only_original[keys].head(10).to_string(index=False))
    if len(only_new):
        failures += len(only_new)
        print(f"FAIL: {len(only_new)} rows only the rewrite produced")
        print(only_new[keys].head(10).to_string(index=False))

    both = merged[merged["_merge"] == "both"].copy()
    both["delta"] = (both["obs_value_new"] - both["obs_value_original"]).abs()
    both["relative"] = both["delta"] / both["obs_value_original"].abs().clip(lower=1e-12)
    bad = both[both["relative"] > TOLERANCE]
    if len(bad):
        failures += len(bad)
        print(f"FAIL: {len(bad)} of {len(both):,} shared values differ by more "
              f"than {TOLERANCE:g} relative")
        print(bad.nlargest(10, "relative")[
            keys + ["obs_value_original", "obs_value_new", "relative"]
        ].to_string(index=False))
    else:
        print(f"OK: {len(both):,} shared values agree within {TOLERANCE:g} "
              f"relative (max seen {both['relative'].max():.2e})")

    per_target = both.groupby("classif1").size()
    untested = sorted({f"ECO_ISIC4_{t}" for t in CONCORDANCE} - set(per_target.index))
    if untested:
        print(f"note: no rows compared for {untested}")

    print("PASS" if failures == 0 else f"FAILURES: {failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 3))
