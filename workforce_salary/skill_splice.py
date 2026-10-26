"""Splice the SUT compensation skill split across a source break.

The salary split (``salary_split_ray.py``) spreads each ILO ISIC employment
total over EXIOBASE industries by the industry's compensation of employees
(SUT value-added rows ``w03.a`` / ``w03.b`` / ``w03.c``, low / medium / high
skilled), and over skill levels by the same rows' shares. Industry totals
therefore depend only on ``w03.a + w03.b + w03.c``; the skill split depends
only on each industry's shares across the three rows.

Those shares come from 06-SUT_balance, which splits the balanced COE row
with the legacy socioeconomic extension ``coe-shares.mat``. For CN, IN, ID
and WA that file changes structure between 2006 and 2007: agriculture goes
from about 0.2-0.4% low skilled to 7-12%, public administration from about
93% high skilled to 44-55%, and so on. Every other region moves smoothly. In
the labour account this showed as world low-skilled people and hours
jumping +42% to +50% at 2006-2007 (to-do C7-3), with no matching move in
total employment, which ILO sets.

The fix keeps each industry's wage bill of the year (so the industry split
of employment, and every ILO control total, is unchanged) and replaces the
skill shares of the years before the break with the shares of the first
year after it, for the regions listed in ``config.yaml``
``skill_split_splice``. That is a backcast of the 2007 skill structure, the
same carry the SUT uses forward of 2012. WF has the same kind of break one
year later (2007-2008: agriculture 31% to 47% low skilled), which made world
low-skilled people rise about 11% at 2007-2008; it is spliced at 2008.
"""
from __future__ import annotations

import pandas as pd

WAGE_ROWS = ("w03.a", "w03.b", "w03.c")


def _wage_block(df: pd.DataFrame, row_col: str) -> pd.DataFrame:
    """The three wage rows as a (3, industry) float frame, in WAGE_ROWS order."""
    idx = []
    for r in WAGE_ROWS:
        hit = df.index[df[row_col] == r]
        if len(hit) != 1:
            raise ValueError(f"SUT frame has {len(hit)} rows named {r!r}, expected 1")
        idx.append(hit[0])
    cols = [c for c in df.columns if c != row_col]
    return df.loc[idx, cols].apply(pd.to_numeric, errors="coerce").fillna(0.0), idx, cols


def splice_skill_split(df: pd.DataFrame, ref: pd.DataFrame,
                       row_col: str = "Row") -> tuple[pd.DataFrame, int]:
    """Return ``df`` with each industry's skill split taken from ``ref``.

    For every industry column with a nonzero wage bill in ``df`` and a
    positive one in ``ref``, the three wage rows become ``ref``'s shares times
    ``df``'s own total, so the column total is unchanged to rounding. Columns
    where ``ref`` has no wage keep their own split. Only the three wage rows
    are touched. Returns the new frame and the number of columns respliced.
    """
    blk, idx, cols = _wage_block(df, row_col)
    rblk, _, rcols = _wage_block(ref, row_col)
    rblk = rblk.reindex(columns=cols, fill_value=0.0)

    tot = blk.sum(axis=0).to_numpy()
    rtot = rblk.sum(axis=0).to_numpy()
    use = (rtot > 0) & (tot != 0)

    new = blk.to_numpy().copy()
    new[:, use] = rblk.to_numpy()[:, use] / rtot[use] * tot[use]

    out = df.copy()
    for k, i in enumerate(idx):
        out.loc[i, cols] = new[k]
    return out, int(use.sum())


def splice_year_for(code: str, year: int, splice: dict[str, int]) -> int | None:
    """The year whose skill shares (code, year) should take, or None.

    ``splice`` maps a region code to the first year of its later skill
    structure (config.yaml ``skill_split_splice``); years before it take that
    year's shares, the break year and later are left alone.
    """
    brk = splice.get(code)
    if brk is None or int(year) >= int(brk):
        return None
    return int(brk)
