"""Check the vectorised aggregate against a transcription of the original loop.

The original `aggregate_isic.aggregate` cannot be executed on this environment:
it builds its result with `DataFrame.append`, removed in pandas 2.0. So the
reference here is a line-by-line transcription of its loop with the appends
collected into a list instead - the control flow, the `continue` chain, the
zero tests, the divisors and the `source` tags are copied verbatim from
aggregate_isic.py. That is what is being compared against, and it is the only
executable statement of the original's intent.

Run directly (no pytest needed)::

    <fao_data-python> tests/test_aggregate_equivalence.py [n_countries]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(1, str(REPO / "working_hours"))

from working_hours.aggregate_isic_vectorised import (  # noqa: E402
    ORIGINAL_YEARS, aggregate,
)
from working_hours.clean_hour_list import clean_hour  # noqa: E402
from working_hours.combine_isic_3_4_vectorised import combine  # noqa: E402
from working_hours.isic3_to_isic4_vectorised import isic3_to_isic4  # noqa: E402

COLUMNS = ["ref_area", "sex", "classif1", "time", "obs_value", "source"]
KEYS = ["ref_area", "sex", "classif1", "time"]

DATA = Path("D:/indecol/data/labour/data")
HOURS_CSV = DATA / "HOW_TEMP_SEX_ECO_NB_A.csv"
WORKFORCE_CSV = Path("D:/indecol/data/labour/final_table/workforce.csv")
ISIC3_CSV = REPO / "isic3.csv"


def reference_aggregate(table: pd.DataFrame, years: range) -> pd.DataFrame:
    """Transcription of aggregate_isic.aggregate, appends collected in a list."""
    rows = []

    def value_of(code, sex, letter, year):
        slice_ = table.loc[(table['ref_area'] == code) & (table['sex'] == sex)
                           & (table['classif1'] == 'ECO_ISIC_' + letter)
                           & (table['time'] == year), ['obs_value']]
        if not slice_.isnull().values.all():
            return float(slice_.to_string(header=False, index=False))
        return 0

    for code in table.ref_area.unique():
        for sex in table.sex.unique():
            for year in years:
                value_d = value_of(code, sex, 'D', year)
                value_e = value_of(code, sex, 'E', year)
                if value_d == 0 and value_e == 0:
                    continue
                if value_d == 0 or value_e == 0:
                    rows.append([code, sex, 'ECO_ISIC_DE', year,
                                 value_d + value_e, 1])
                else:
                    rows.append([code, sex, 'ECO_ISIC_DE', year,
                                 (value_d + value_e) / 2, 2])

                value_h = value_of(code, sex, 'H', year)
                value_j = value_of(code, sex, 'J', year)
                if value_h == 0 and value_j == 0:
                    continue
                if value_h == 0 or value_j == 0:
                    rows.append([code, sex, 'ECO_ISIC_HJ', year,
                                 value_h + value_j, 1])
                else:
                    rows.append([code, sex, 'ECO_ISIC_HJ', year,
                                 (value_h + value_j) / 2, 2])

                lst = [value_of(code, sex, letter, year)
                       for letter in ('R', 'S', 'T', 'U')]
                total = sum(lst)
                if lst.count(0) == 4:
                    continue
                if lst.count(0) == 3:
                    rows.append([code, sex, 'ECO_ISIC_RSTU', year, total, 1])
                elif lst.count(0) == 2:
                    rows.append([code, sex, 'ECO_ISIC_RSTU', year, total / 2, 2])
                elif lst.count(0) == 1:
                    rows.append([code, sex, 'ECO_ISIC_RSTU', year, total / 3, 3])
                else:
                    rows.append([code, sex, 'ECO_ISIC_RSTU', year, total / 4, 3])

                lst = [value_of(code, sex, letter, year)
                       for letter in ('L', 'M', 'N')]
                total = sum(lst)
                if lst.count(0) == 3:
                    continue
                if lst.count(0) == 2:
                    rows.append([code, sex, 'ECO_ISIC_LMN', year, total, 1])
                elif lst.count(0) == 1:
                    rows.append([code, sex, 'ECO_ISIC_LMN', year, total / 2, 2])
                else:
                    rows.append([code, sex, 'ECO_ISIC_LMN', year, total / 3, 3])

    built = pd.DataFrame(rows, columns=COLUMNS)
    components = [f'ECO_ISIC_{letter}'
                  for letter in 'D E H J L M N R S T U'.split()]
    kept = table[~table.classif1.isin(components)]
    return pd.concat([kept, built], ignore_index=True)


def build_input(n_countries: int) -> pd.DataFrame:
    hour_list, without_zero = clean_hour(
        pd.read_csv(HOURS_CSV, encoding="utf-8-sig", low_memory=False))
    isic4 = without_zero[without_zero["classif1"].str.contains("ISIC4",
                                                              regex=True)].copy()
    converted = isic3_to_isic4(
        pd.read_csv(ISIC3_CSV),
        pd.read_csv(WORKFORCE_CSV, low_memory=False,
                    usecols=["ref_area", "sex", "time", "classif1", "obs_value"]),
        range(1995, 2023), verbose=False)

    both = set(converted.ref_area) & set(isic4.ref_area) & set(hour_list.ref_area)
    ranked = (converted[converted.ref_area.isin(both)]
              .groupby("ref_area").size().sort_values(ascending=False))
    countries = list(ranked.index[:n_countries])
    print(f"countries under test: {countries}")

    seed = pd.DataFrame(data=None, columns=COLUMNS)
    return combine(hour_list[hour_list.ref_area.isin(countries)],
                   converted[converted.ref_area.isin(countries)],
                   seed, seed.columns,
                   isic4[isic4.ref_area.isin(countries)], verbose=False)


def main(n_countries: int = 3) -> int:
    for path in (HOURS_CSV, WORKFORCE_CSV, ISIC3_CSV):
        if not path.exists():
            print(f"missing {path}; run stage 1 first")
            return 2

    combined = build_input(n_countries)
    print(f"combine output: {len(combined):,} rows, "
          f"{combined.classif1.nunique()} classifications")

    started = time.perf_counter()
    got = aggregate(combined, years=ORIGINAL_YEARS, cascade_skip=True,
                    verbose=False)
    fast_seconds = time.perf_counter() - started

    started = time.perf_counter()
    want = reference_aggregate(combined, ORIGINAL_YEARS)
    slow_seconds = time.perf_counter() - started

    print(f"vectorised: {len(got):,} rows in {fast_seconds:.2f}s")
    print(f"transcribed original: {len(want):,} rows in {slow_seconds:.1f}s "
          f"({slow_seconds / max(fast_seconds, 1e-9):,.0f}x slower)")

    for frame in (got, want):
        frame["obs_value"] = pd.to_numeric(frame["obs_value"])
        frame["source"] = pd.to_numeric(frame["source"])
        frame["time"] = pd.to_numeric(frame["time"])

    failures = 0
    merged = want.merge(got, on=KEYS, how="outer", suffixes=("_original", "_new"),
                        indicator=True)
    for side, label in (("left_only", "only the transcribed original produced"),
                        ("right_only", "only the rewrite produced")):
        rows = merged[merged["_merge"] == side]
        if len(rows):
            failures += len(rows)
            print(f"FAIL: {len(rows)} rows {label}")
            print(rows[KEYS].head(10).to_string(index=False))

    both_rows = merged[merged["_merge"] == "both"].copy()
    diff = (both_rows["obs_value_new"] - both_rows["obs_value_original"]).abs()

    # Rows carried through untouched must match bit for bit. Rows the stage
    # builds may differ by the precision the original threw away: it read each
    # component back with float(...to_string()), i.e. round(v, 6), before
    # averaging, so the mean carries at most 5e-7 of truncation error however
    # many components go into it.
    is_built = both_rows["classif1"].isin(
        ["ECO_ISIC_DE", "ECO_ISIC_HJ", "ECO_ISIC_LMN", "ECO_ISIC_RSTU"])
    tolerance = pd.Series(1e-12, index=both_rows.index).mask(is_built, 5.01e-7)
    bad_value = both_rows[diff > tolerance]
    bad_source = both_rows[both_rows["source_new"] != both_rows["source_original"]]
    if len(bad_value):
        failures += len(bad_value)
        print(f"FAIL: {len(bad_value)} values differ")
        print(bad_value.nlargest(10, "obs_value_new")[
            KEYS + ["obs_value_original", "obs_value_new"]].to_string(index=False))
    if len(bad_source):
        failures += len(bad_source)
        print(f"FAIL: {len(bad_source)} rows tagged with a different source")
        print(bad_source[KEYS + ["source_original", "source_new"]]
              .head(10).to_string(index=False))
    if not failures:
        aggregates = both_rows[is_built].groupby("classif1").size().to_dict()
        print(f"OK: {len(both_rows):,} rows agree in source; "
              f"{(~is_built).sum():,} carried-through rows match exactly, "
              f"{is_built.sum():,} built rows within "
              f"{diff[is_built].max():.2e} (limit 5.01e-07)")
        print(f"    aggregates built: {aggregates}")

    print("PASS" if failures == 0 else f"FAILURES: {failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 3))
