"""Merge native ISIC4 hours with ISIC3-derived hours, vectorised.

Drop-in replacement for `combine_isic_3_4.combine`. Same signature, same
result, no ray.

What it does
------------
One priority merge over (ref_area, sex, classif1, time):

    year <  2009  ->  ISIC3-derived value only              (source 3)
    year >= 2009  ->  native ISIC4 if present               (source 4)
                      otherwise the ISIC3-derived value     (source 3)

Native ISIC4 values before 2009 are discarded, which is what the original did:
its `year < 2009` branch never consulted `isic4` at all.

The key set comes from `hour_list`: a row is emitted only where its ref_area,
sex, classif1 and time each appear in `hour_list`, matching the original's four
nested loops over `hour_list.<column>.unique()`.

Why it was rewritten
--------------------
The original ran those four loops (roughly 180 countries x 2 sexes x ~38
classifications x ~30 years) and did a four-condition full-frame boolean scan
per cell, then appended one row at a time with
`new_table_150222.loc[len(new_table_150222)] = new_line`, which reallocates the
frame on every append. It fanned the countries out over ray to hide the cost.
Roughly half those cells could never match anything: `classif1` iterates the
`ECO_ISIC3_*` codes too, and neither input frame carries them.

The digit-stripping defect
--------------------------
`combine` is where `ECO_ISIC3_A` / `ECO_ISIC4_A` become `ECO_ISIC_A`, the
namespace everything downstream expects: `aggregate_isic.py` looks up
`ECO_ISIC_D`, `ECO_ISIC_E`, `ECO_ISIC_H` and 41 more, and those strings appear
nowhere else in the repo.

That rename was lost. The original line

    new_table_150222.append(pd.Series([code, sex,
        classi.translate({ord(k): None for k in digits}), ...

was replaced at some point by `new_table_150222.loc[len(...)] = new_line`
carrying a plain `classi`, and `from string import digits` was commented out to
match. So `combine` emitted `ECO_ISIC4_A`, every lookup in `aggregate` missed,
every year hit `continue`, and `aggregate` became an expensive no-op. Nothing
downstream of it can have been correct.

Restored here, controlled by `strip_classification_digits` so the equivalence
test can turn it off and compare against the original byte for byte. It cannot
introduce duplicate keys: only `ECO_ISIC4_*` rows are ever emitted (neither
input frame holds `ECO_ISIC3_*` values), so there is nothing for the stripped
names to collide with.
"""
from __future__ import annotations

import pandas as pd

_KEYS = ["ref_area", "sex", "classif1", "time"]
_OUT_COLUMNS = ["ref_area", "sex", "classif1", "time", "obs_value", "source"]

# The year native ISIC4 reporting takes over from the converted ISIC3 series.
NATIVE_ISIC4_FROM = 2009

SOURCE_CONVERTED_FROM_ISIC3 = 3
SOURCE_NATIVE_ISIC4 = 4


def _usable(frame: pd.DataFrame, hour_list: pd.DataFrame,
            label: str) -> pd.DataFrame:
    """Rows with a value, restricted to keys `hour_list` actually iterates."""
    out = frame[_KEYS + ["obs_value"]].copy()
    out["obs_value"] = pd.to_numeric(out["obs_value"], errors="coerce")
    out = out[out["obs_value"].notna()]

    for column in _KEYS:
        out = out[out[column].isin(set(hour_list[column].unique()))]

    duplicated = out.duplicated(_KEYS).sum()
    if duplicated:
        raise ValueError(
            f"{label} has {duplicated} duplicate (ref_area, sex, classif1, "
            "time) rows carrying values. The original read each match with "
            "float(...to_string()) and would have raised on more than one."
        )
    return out


def combine(hour_list: pd.DataFrame, isic4_from_isic3_data: pd.DataFrame,
            new_table_150222: pd.DataFrame, new_table_150222_columns,
            isic4: pd.DataFrame, *,
            strip_classification_digits: bool = True,
            verbose: bool = True) -> pd.DataFrame:
    """Combine the converted and native ISIC4 hours into one series.

    `new_table_150222` and `new_table_150222_columns` are accepted and ignored;
    they are the empty frame and column list the original was seeded with, kept
    so this stays a drop-in replacement.
    """
    converted = _usable(isic4_from_isic3_data, hour_list, "isic4_from_isic3_data")
    native = _usable(isic4, hour_list, "isic4")

    native = native[native["time"] >= NATIVE_ISIC4_FROM]
    native = native.assign(source=SOURCE_NATIVE_ISIC4)

    # Converted values fill both the pre-2009 span and any post-2009 gap.
    covered = pd.MultiIndex.from_frame(native[_KEYS])
    converted_index = pd.MultiIndex.from_frame(converted[_KEYS])
    fills_gap = ((converted["time"] < NATIVE_ISIC4_FROM).to_numpy()
                 | ~converted_index.isin(covered))
    converted = converted[fills_gap].assign(source=SOURCE_CONVERTED_FROM_ISIC3)

    out = pd.concat([native, converted], ignore_index=True)

    if strip_classification_digits:
        out["classif1"] = out["classif1"].str.replace(r"^ECO_ISIC\d_", "ECO_ISIC_",
                                                      regex=True)

    out = out[_OUT_COLUMNS].sort_values(_KEYS, ignore_index=True)
    if verbose:
        counts = out["source"].value_counts()
        print(f"[combine] {len(out):,} rows: "
              f"{counts.get(SOURCE_NATIVE_ISIC4, 0):,} native ISIC4, "
              f"{counts.get(SOURCE_CONVERTED_FROM_ISIC3, 0):,} converted from "
              f"ISIC3")
    return out
