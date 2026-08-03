"""ISIC Rev.3 -> Rev.4 conversion of average working hours, vectorised.

Replaces the 22 hand-written `task_A` ... `task_X` functions in
`isic3_to_isic4.py` (3,476 lines) with one concordance table and one
computation. The arithmetic is unchanged; see "Equivalence" below.

What the original did
---------------------
Every ISIC4 letter got its own function, and inside it every combination of
"which ISIC3 sources are non-zero this year" was written out as a separate
if-branch: `task_C` has five sources, so 31 branches. Each branch was the same
formula with the missing terms deleted by hand.

That is one formula. For ISIC4 target `t` built from sources `s`, each with a
concordance share `w_s` and a workforce category `p_s`:

    hours_t = sum_s [h_s != 0] * w_s * pop_{p_s} * h_s
              -----------------------------------------
              sum_s [h_s != 0] * w_s * pop_{p_s}

A source that is zero drops out of both sums, which is exactly what deleting
its term by hand did. The single-source branches (`eco_isic4_c = eco_isic3_d`)
are the same formula too: with one term the weights cancel. So all 22 targets
and all their branches collapse into the table below.

Why the rewrite was needed
--------------------------
The original was not merely long, it was quadratic. The value lookup

    isic3.loc[(isic3['ref_area'] == code) & (isic3['sex'] == sex)
              & (isic3['time'] == year) & (isic3['classif1'] == classif),
              ['obs_value']]

sat five loops deep (country, year, sex, classif, letter) and rescanned all
24,599 isic3 rows on every pass, roughly 2.3 billion row comparisons per task.
The population lookups did the same against the 937,251-row workforce frame.
And each of the 22 tasks was handed its own pickled copy of that frame by a
ProcessPoolExecutor, which is where the memory went.

Equivalence
-----------
`tests/test_isic3_to_isic4_equivalence.py` runs the original task functions and
this module over the same subset and compares every value. Two deliberate
differences:

1. Precision. The original read each value out with
   `float(df.to_string(index=False, header=False))`, i.e. it formatted the
   number as display text and parsed it back, which rounds to 6 decimal places.
   This module keeps full float precision. Differences are ~1e-6 relative.
2. `var_holder` was never cleared between iterations, so a letter absent from
   the whole frame raised KeyError while a letter absent for one country
   silently reused the previous country's value. Here absent means zero
   everywhere, which is what the code meant.

Two defects in the original, corrected (decided 2026-08-03; see STATUS.md)
-------------------------------------------------------------------------
1. `task_S` weighted two of its four sources by the LMN population instead of
   HJ and G. See `CONCORDANCE_S_ORIGINAL`.
2. Kosovo rewrote `code = 'XKX'` *before* looking up its ISIC3 rows, which are
   filed under `KOS`, so nothing matched and Kosovo contributed no converted
   hours at all. The relabel belongs after the lookup, which is what happens
   now: 35 rows, all in 2000. Only XKX maps to an EXIOBASE region (WE).

Set `REPRODUCE_ORIGINAL_DEFECTS` (or pass `reproduce_original_defects=True`) to
get the original behaviour back; the equivalence test does exactly that, so it
still compares like for like.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# ISIC4 target -> [(ISIC3 source letter, concordance share, workforce category)]
#
# Recovered mechanically from the all-sources-present branch of each task_* in
# isic3_to_isic4.py, which is the only branch carrying the complete formula.
# `None` as the workforce category marks a one-to-one target: the original had
# no population term there at all, and with a single source the weights cancel.
CONCORDANCE: dict[str, list[tuple[str, float, str | None]]] = {
    "A": [("a", 1.0, "A"), ("b", 1.0, "B")],
    "B": [("c", 1.0, None)],
    "C": [("d", 1.0, "DE"), ("f", 0.05, "F"), ("g", 0.018, "G"),
          ("i", 0.029, "I"), ("k", 0.014, "K")],
    "D": [("e", 1.0, None)],
    "E": [("e", 0.25, "DE"), ("f", 0.05, "F"), ("o", 0.113, "O")],
    "F": [("f", 0.85, "F"), ("k", 0.014, "K")],
    "G": [("g", 1.0, None)],
    "H": [("g", 0.018, "G"), ("i", 0.706, "I"), ("o", 0.019, "O")],
    "I": [("h", 1.0, None)],
    "J": [("k", 0.233, "K"), ("i", 0.088, "I"), ("o", 0.208, "O")],
    "K": [("i", 0.029, "I"), ("j", 0.926, "HJ")],
    "L": [("k", 0.027, "K"), ("l", 0.143, "LMN")],
    "M": [("k", 0.26, "K"), ("l", 0.071, "LMN"), ("n", 0.077, "LMN"),
          ("o", 0.038, "O")],
    "N": [("j", 0.037, "HJ"), ("l", 0.071, "LMN"), ("g", 0.018, "G"),
          ("i", 0.147, "I"), ("k", 0.384, "K"), ("o", 0.094, "O")],
    "O": [("l", 1.0, None)],
    "P": [("k", 0.027, "K"), ("m", 1.0, "LMN"), ("n", 0.077, "LMN"),
          ("o", 0.075, "O")],
    "Q": [("n", 0.846, "LMN"), ("l", 0.071, "LMN")],
    "R": [("k", 0.014, "K"), ("l", 0.071, "LMN"), ("o", 0.264, "O")],
    # See CONCORDANCE_S_ORIGINAL below: S is the one entry the original got
    # wrong, and this is the corrected form.
    "S": [("k", 0.014, "K"), ("j", 0.037, "HJ"), ("g", 0.109, "G"),
          ("o", 0.189, "O")],
    "T": [("p", 1.0, None)],
    "U": [("k", 0.014, "K"), ("f", 0.05, "F"), ("q", 1.0, "Q")],
    "X": [("x", 1.0, None)],
}

#: `task_S`'s normal-year branch weights j and g by the LMN population instead
#: of HJ and G. It disagrees with `task_S`'s own Ukraine-2022 branch, and it is
#: the only one of the 22 conversions where the two branches disagree, so it
#: reads as a copy-paste slip. Corrected above for the 3.11.2 build (decided
#: 2026-08-03): 1,372 values, 4.8% of all converted rows, mean absolute change
#: 2.7%, ECO_ISIC4_S mean 39.52 -> 40.45 h/week. Only years before 2009 reach
#: the published accounts, since combine takes native ISIC4 from 2009 on.
CONCORDANCE_S_ORIGINAL = [("k", 0.014, "K"), ("j", 0.037, "LMN"),
                          ("g", 0.109, "LMN"), ("o", 0.189, "O")]

#: Set True to reproduce the original's two defects (task_S above, and dropping
#: Kosovo). The equivalence test uses it to compare like for like; the build
#: leaves it False.
REPRODUCE_ORIGINAL_DEFECTS = False

# Ukraine 2022: the original scaled the 2021 workforce by this factor rather
# than reading 2022, in every task that uses a population term. The branch is
# dead - Ukraine reports ISIC3 hours only for 2009-2012, so no task ever
# reaches it - but it is kept so behaviour does not change if that alters.
_UKR_YEAR, _UKR_SOURCE_YEAR, _UKR_FACTOR = 2022, 2021, 0.845

_KEYS = ["ref_area", "sex", "time"]
_OUT_COLUMNS = ["ref_area", "sex", "classif1", "time", "obs_value"]


def _hours_matrix(isic3: pd.DataFrame, years: range) -> pd.DataFrame:
    """(ref_area, sex, time) x ISIC3 letter matrix of average hours.

    Null and absent both become 0, which is how the original read them: its
    `.isnull().values.all()` test returns True for an empty slice, so a missing
    row took the `else` branch and set the value to 0.
    """
    df = isic3[isic3["time"].isin(years)].copy()
    df["letter"] = (df["classif1"].str.removeprefix("ECO_ISIC3_")
                    .str.lower())
    df = df[df["letter"].str.len() == 1]  # drops ECO_ISIC3_TOTAL
    df["obs_value"] = pd.to_numeric(df["obs_value"], errors="coerce")

    dupes = df.duplicated(_KEYS + ["letter"]).sum()
    if dupes:
        raise ValueError(
            f"isic3 has {dupes} duplicate (ref_area, sex, time, classif1) rows; "
            "the original read each with float(...to_string()) and would have "
            "raised. Deduplicate upstream."
        )
    return (df.pivot(index=_KEYS, columns="letter", values="obs_value")
              .fillna(0.0))


def _population_matrix(workforce: pd.DataFrame, index: pd.MultiIndex,
                       categories: set[str]) -> pd.DataFrame:
    """(ref_area, sex, time) x ECO_DETAILS category matrix, aligned to `index`."""
    wanted = {f"ECO_DETAILS_{c}" for c in categories}
    df = workforce[workforce["classif1"].isin(wanted)].copy()
    df["obs_value"] = pd.to_numeric(df["obs_value"], errors="coerce")
    df["category"] = df["classif1"].str.removeprefix("ECO_DETAILS_")

    df = df.drop_duplicates(_KEYS + ["category"], keep="first")
    pop = df.pivot(index=_KEYS, columns="category", values="obs_value")

    # Ukraine 2022 takes 0.845 x its 2021 population.
    ukr_2021 = pop[(pop.index.get_level_values("ref_area") == "UKR")
                   & (pop.index.get_level_values("time") == _UKR_SOURCE_YEAR)]
    if not ukr_2021.empty:
        scaled = ukr_2021 * _UKR_FACTOR
        scaled.index = pd.MultiIndex.from_arrays(
            [scaled.index.get_level_values("ref_area"),
             scaled.index.get_level_values("sex"),
             np.full(len(scaled), _UKR_YEAR)],
            names=_KEYS,
        )
        pop = pd.concat([pop.drop(index=scaled.index, errors="ignore"), scaled])

    return pop.reindex(index)


def isic3_to_isic4(isic3: pd.DataFrame, workforce: pd.DataFrame,
                   years: range, verbose: bool = True,
                   reproduce_original_defects: bool | None = None) -> pd.DataFrame:
    """Convert ISIC Rev.3 average working hours to Rev.4 categories.

    Returns the same long frame the 22 task functions produced between them:
    columns ref_area, sex, classif1 (ECO_ISIC4_*), time, obs_value. A
    (country, sex, year, target) row is emitted only where at least one of the
    target's ISIC3 sources is non-zero, matching the original.
    """
    if reproduce_original_defects is None:
        reproduce_original_defects = REPRODUCE_ORIGINAL_DEFECTS
    concordance = dict(CONCORDANCE)
    if reproduce_original_defects:
        concordance["S"] = CONCORDANCE_S_ORIGINAL

    # Kosovo files its ISIC3 rows under KOS, but only XKX maps to an EXIOBASE
    # region (WE). The original rewrote the code to XKX *before* the lookup, so
    # nothing matched and Kosovo contributed no converted hours at all. Relabel
    # after, which is what was meant. 35 rows, all in 2000; Kosovo's post-2009
    # hours were never affected, since they come from native ISIC4.
    isic3 = isic3.copy()
    kosovo = int((isic3["ref_area"] == "KOS").sum())
    if reproduce_original_defects:
        if kosovo and verbose:
            print(f"[isic3->isic4] dropping {kosovo} Kosovo rows "
                  "(reproduce_original_defects=True)")
        isic3 = isic3[isic3["ref_area"] != "KOS"]
    elif kosovo and verbose:
        print(f"[isic3->isic4] {kosovo} Kosovo rows kept, relabelled KOS -> XKX")

    hours = _hours_matrix(isic3, years)
    categories = {p for sources in concordance.values()
                  for _, _, p in sources if p is not None}
    pop = _population_matrix(workforce, hours.index, categories)

    if verbose:
        print(f"[isic3->isic4] {len(hours):,} (country, sex, year) cells x "
              f"{len(concordance)} targets, years {years[0]}-{years[-1]}")

    missing_pop = 0
    frames = []
    for target, sources in concordance.items():
        numerator = pd.Series(0.0, index=hours.index)
        denominator = pd.Series(0.0, index=hours.index)
        any_source = pd.Series(False, index=hours.index)

        for letter, share, category in sources:
            if letter not in hours.columns:
                continue
            h = hours[letter]
            present = h != 0
            if category is None:
                weight = pd.Series(1.0, index=hours.index)
            else:
                weight = share * pop[category]
                missing_pop += int((present & weight.isna()).sum())
                weight = weight.fillna(0.0)

            contribution = (weight * present).astype(float)
            numerator += contribution * h
            denominator += contribution
            any_source |= present

        keep = any_source & (denominator != 0)
        if not keep.any():
            continue

        values = (numerator[keep] / denominator[keep]).rename("obs_value")
        frame = values.reset_index()
        frame["classif1"] = f"ECO_ISIC4_{target}"
        frames.append(frame[_OUT_COLUMNS])

    if missing_pop and verbose:
        print(f"[isic3->isic4] WARNING: {missing_pop} source terms had no "
              "workforce population and were given zero weight. The original "
              "would have raised ValueError here.")

    if not frames:
        return pd.DataFrame(columns=_OUT_COLUMNS)

    out = pd.concat(frames, ignore_index=True)
    if not reproduce_original_defects:
        out["ref_area"] = out["ref_area"].replace({"KOS": "XKX"})
    out = out.sort_values(["classif1", "ref_area", "sex", "time"],
                          ignore_index=True)
    if verbose:
        print(f"[isic3->isic4] {len(out):,} converted rows")
    return out
