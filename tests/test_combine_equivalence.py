"""Check the vectorised combine against the original ray implementation.

Compared with digit-stripping switched off, since the original lost that rename
(see combine_isic_3_4_vectorised for the detail). What is being verified is the
merge itself: which value wins for each key, and which source it is tagged with.

Run directly (no pytest needed)::

    <fao_data-python> tests/test_combine_equivalence.py [n_countries]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(1, str(REPO / "working_hours"))

from working_hours.clean_hour_list import clean_hour  # noqa: E402
from working_hours.isic3_to_isic4_vectorised import isic3_to_isic4  # noqa: E402

DATA = Path("D:/indecol/data/labour/data")
HOURS_CSV = DATA / "HOW_TEMP_SEX_ECO_NB_A.csv"
WORKFORCE_CSV = Path("D:/indecol/data/labour/final_table/workforce.csv")
ISIC3_CSV = REPO / "isic3.csv"

COLUMNS = ["ref_area", "sex", "classif1", "time", "obs_value", "source"]
KEYS = ["ref_area", "sex", "classif1", "time"]


def main(n_countries: int = 3) -> int:
    for path in (HOURS_CSV, WORKFORCE_CSV, ISIC3_CSV):
        if not path.exists():
            print(f"missing {path}; run stage 1 first")
            return 2

    hour_list, hour_list_without_zero = clean_hour(
        pd.read_csv(HOURS_CSV, encoding="utf-8-sig", low_memory=False))
    isic4 = hour_list_without_zero[
        hour_list_without_zero["classif1"].str.contains("ISIC4", regex=True)].copy()

    isic3 = pd.read_csv(ISIC3_CSV)
    workforce = pd.read_csv(WORKFORCE_CSV, low_memory=False,
                            usecols=["ref_area", "sex", "time", "classif1",
                                     "obs_value"])
    converted = isic3_to_isic4(isic3, workforce, range(1995, 2023), verbose=False)

    # Countries that exercise both arms of the merge: native ISIC4 and
    # converted ISIC3.
    both = set(converted.ref_area) & set(isic4.ref_area) & set(hour_list.ref_area)
    ranked = (converted[converted.ref_area.isin(both)]
              .groupby("ref_area").size().sort_values(ascending=False))
    countries = list(ranked.index[:n_countries])
    print(f"countries under test: {countries}")

    hour_list_subset = hour_list[hour_list.ref_area.isin(countries)].copy()
    isic4_subset = isic4[isic4.ref_area.isin(countries)].copy()
    converted_subset = converted[converted.ref_area.isin(countries)].copy()
    print(f"hour_list {len(hour_list_subset):,} rows | "
          f"{hour_list_subset.classif1.nunique()} classifications | "
          f"{hour_list_subset.time.nunique()} years")

    seed = pd.DataFrame(data=None, columns=COLUMNS)

    from working_hours.combine_isic_3_4_vectorised import combine as fast
    started = time.perf_counter()
    got = fast(hour_list_subset, converted_subset, seed, seed.columns,
               isic4_subset, strip_classification_digits=False, verbose=False)
    fast_seconds = time.perf_counter() - started
    print(f"vectorised: {len(got):,} rows in {fast_seconds:.2f}s")

    from working_hours.combine_isic_3_4 import combine as original
    started = time.perf_counter()
    want = original(hour_list_subset, converted_subset, seed, seed.columns,
                    isic4_subset)
    slow_seconds = time.perf_counter() - started
    print(f"original:   {len(want):,} rows in {slow_seconds:.1f}s "
          f"({slow_seconds / max(fast_seconds, 1e-9):,.0f}x slower on "
          f"{n_countries} of {hour_list.ref_area.nunique()} countries)")

    want["obs_value"] = pd.to_numeric(want["obs_value"])
    want["source"] = pd.to_numeric(want["source"])
    want["time"] = pd.to_numeric(want["time"])

    failures = 0
    merged = want.merge(got, on=KEYS, how="outer", suffixes=("_original", "_new"),
                        indicator=True)
    for side, label in (("left_only", "only the original produced"),
                        ("right_only", "only the rewrite produced")):
        rows = merged[merged["_merge"] == side]
        if len(rows):
            failures += len(rows)
            print(f"FAIL: {len(rows)} rows {label}")
            print(rows[KEYS].head(10).to_string(index=False))

    # The original read every value back with float(df.to_string(...)), which is
    # exactly round(value, 6) - verified against the formatter, not assumed. So
    # the rewrite is correct iff the original equals the rewrite rounded to 6
    # decimal places; anything else is a real difference.
    both_rows = merged[merged["_merge"] == "both"].copy()
    value_diff = (both_rows["obs_value_new"].round(6)
                  - both_rows["obs_value_original"]).abs()
    bad_value = both_rows[value_diff > 1e-9]
    bad_source = both_rows[both_rows["source_new"] != both_rows["source_original"]]
    if len(bad_value):
        failures += len(bad_value)
        print(f"FAIL: {len(bad_value)} values differ")
        print(bad_value.head(10).to_string(index=False))
    if len(bad_source):
        failures += len(bad_source)
        print(f"FAIL: {len(bad_source)} rows tagged with a different source")
        print(bad_source[KEYS + ["source_original", "source_new"]]
              .head(10).to_string(index=False))
    if not failures:
        counts = both_rows["source_original"].value_counts().to_dict()
        raw = (both_rows["obs_value_new"] - both_rows["obs_value_original"]).abs()
        print(f"OK: {len(both_rows):,} rows identical in source and in value to "
              f"the original's 6-decimal read-back (by source: {counts}; "
              f"largest raw difference {raw.max():.2e}, the precision the "
              f"original discarded)")

    print("PASS" if failures == 0 else f"FAILURES: {failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 3))
