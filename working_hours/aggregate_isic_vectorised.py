"""Build the ISIC4 aggregate categories (DE, HJ, LMN, RSTU), vectorised.

Drop-in replacement for `aggregate_isic.aggregate`. Each aggregate is the mean
of whichever of its components carry a value; `source` records how many were
averaged. The component rows are then dropped, leaving the aggregates alongside
the letters that need no aggregation.

This stage has never run
------------------------
`aggregate_isic.py` looks up `ECO_ISIC_D`, `ECO_ISIC_E` and 42 more names that
nothing in the repo produces: `combine` was supposed to strip the revision digit
(`ECO_ISIC4_D` -> `ECO_ISIC_D`) and had stopped doing so. Every lookup missed,
every year hit `continue`, and the function returned its input unchanged. With
the rename restored in `combine_isic_3_4_vectorised`, it does something for the
first time - and the original would immediately have raised `AttributeError`,
because it builds its output with `DataFrame.append`, removed in pandas 2.0
(this environment runs 2.3.3).

So there is no output from this stage to be faithful to on this machine. The
two switches below preserve what the code says anyway, because the 3.10 labour
release predates pandas 2 and was probably built with these semantics.

`cascade_skip` (set False for the 3.11.2 build; True reproduces the original)
    The original's four blocks are chained by `continue`, not `pass`: if D and E
    are both absent for a (country, sex, year), the `continue` skips the rest of
    that year, so HJ, RSTU and LMN are never built either - even where their own
    components are present. Almost certainly meant to be `pass`. Setting False
    builds each aggregate on its own merits.

`years` (set to the config range for the 3.11.2 build; 1995-2019 is the original)
    The original loops `range(1995, 2020)`. The component rows are dropped for
    *all* years regardless, so from 2020 on, eleven ISIC letters disappear and
    no aggregate replaces them. With the data now running to 2025 that leaves a
    six-year hole in D, E, H, J, L, M, N, R, S, T and U. Pass the config year
    range to close it.

The owner chose to correct both for the 3.11.2 respin r2 build (2026-08-01);
see `AGGREGATE_YEARS` / `AGGREGATE_CASCADE_SKIP` below and STATUS.md. Both
changes only ever add rows: no value the original produced is altered.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
import config as _cfg

# Order matters: `cascade_skip` chains them in exactly this sequence, because
# that is the order the original's `continue` statements run in.
AGGREGATES: list[tuple[str, list[str]]] = [
    ("DE", ["D", "E"]),
    ("HJ", ["H", "J"]),
    ("RSTU", ["R", "S", "T", "U"]),
    ("LMN", ["L", "M", "N"]),
]

ORIGINAL_YEARS = range(1995, 2020)

# ---------------------------------------------------------------------------
# The two settings the pipeline runs with. Both were changed away from the code
# as written on 2026-08-01, by the owner, for the 3.11.2 respin r2 build. Set
# them back to ORIGINAL_YEARS / True to reproduce 3.10 semantics exactly.
#
#   AGGREGATE_YEARS: the original's range(1995, 2020) left a six-year hole,
#   because the component rows are dropped for every year regardless. Now the
#   config range, so DE/HJ/LMN/RSTU exist wherever their components do.
#
#   AGGREGATE_CASCADE_SKIP: the original chained its four blocks with
#   `continue`, so an absent D and E suppressed HJ, RSTU and LMN for that
#   (country, sex, year) too. Now False, so each aggregate stands on its own
#   components.
#
# Both changes ADD rows; neither alters a value that the original produced.
# ---------------------------------------------------------------------------
AGGREGATE_YEARS = _cfg.year_range()
AGGREGATE_CASCADE_SKIP = False

_PREFIX = "ECO_ISIC_"
_GROUP_KEYS = ["ref_area", "sex", "time"]
_OUT_COLUMNS = ["ref_area", "sex", "classif1", "time", "obs_value", "source"]

# The original tags a 4-component RSTU mean with source 3, not 4. Preserved.
MAX_SOURCE = 3


def aggregate(new_table_150222: pd.DataFrame, new_table_150222_columns=None, *,
              years: range = ORIGINAL_YEARS, cascade_skip: bool = True,
              verbose: bool = True) -> pd.DataFrame:
    """Add DE/HJ/LMN/RSTU and drop the components they replace."""
    table = new_table_150222.copy()
    table["obs_value"] = pd.to_numeric(table["obs_value"], errors="coerce")
    table["time"] = pd.to_numeric(table["time"], errors="coerce")

    components = [f"{_PREFIX}{letter}"
                  for _, letters in AGGREGATES for letter in letters]

    in_scope = table[table["time"].isin(years)]
    wide = (in_scope[in_scope["classif1"].isin(components)]
            .pivot_table(index=_GROUP_KEYS, columns="classif1",
                         values="obs_value", aggfunc="first"))

    built = []
    eligible = None  # None means "every cell", i.e. nothing skipped yet
    for name, letters in AGGREGATES:
        present = [f"{_PREFIX}{letter}" for letter in letters
                   if f"{_PREFIX}{letter}" in wide.columns]
        if not present:
            if cascade_skip:
                break  # this group is empty everywhere, so nothing after it runs
            continue

        # The original counted a component present with `lst.count(0)`, so an
        # absent row and a literal 0.0 are both "absent". Matched here.
        block = wide[present]
        block = block.where(block.notna() & (block != 0))
        count = block.notna().sum(axis=1)
        has_any = count > 0
        rows = has_any if eligible is None else (has_any & eligible)

        if cascade_skip:
            # The original's `continue` skips the remainder of the year, so a
            # cell that fails here is unavailable to every later group.
            eligible = rows

        if not rows.any():
            continue

        values = block.sum(axis=1, min_count=1)[rows] / count[rows]
        frame = values.rename("obs_value").reset_index()
        frame["classif1"] = f"{_PREFIX}{name}"
        frame["source"] = count[rows].clip(upper=MAX_SOURCE).to_numpy()
        built.append(frame[_OUT_COLUMNS])

    kept = table[~table["classif1"].isin(components)]
    out = pd.concat([kept] + built, ignore_index=True) if built else kept

    if verbose:
        made = {f.loc[0, "classif1"]: len(f) for f in built}
        print(f"[aggregate] years {years[0]}-{years[-1]}, "
              f"cascade_skip={cascade_skip}: built {made}; dropped "
              f"{len(table) - len(kept):,} component rows")
    return out.reset_index(drop=True)
