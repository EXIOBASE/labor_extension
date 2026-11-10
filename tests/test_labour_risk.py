"""Labour-risk allocation helpers (labour_risk/common.py)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from labour_risk import common  # noqa: E402

GROUP = {"Farming": "ECO_DETAILS_A", "Steel": "ECO_DETAILS_C", "Shops": "ECO_DETAILS_G"}


def _account():
    idx = pd.MultiIndex.from_product([["AA"], list(GROUP)], names=["region", "sector"])
    cols = {}
    for sex in ("male", "female"):
        for i, c in enumerate(common.PEOPLE[sex]):
            cols[c] = [10.0 * (i + 1), 5.0, 2.0]
        for c in common.HOURS[sex]:
            cols[c] = [20.0, 10.0, 4.0]
    return pd.DataFrame(cols, index=idx)


def test_apply_shares_uses_sex_and_group():
    acc = _account()
    keys = [("AA", s, g, 2019) for s in common.SEXES for g in GROUP.values()]
    shares = pd.Series([0.5 if g == "ECO_DETAILS_A" else 0.1 for _, _, g, _ in keys],
                       index=pd.MultiIndex.from_tuples(keys))
    people, hours = common.apply_shares(acc, shares, 2019, GROUP)
    farm = sum(acc.loc[("AA", "Farming"), common.PEOPLE[s]].sum() for s in ("male", "female"))
    assert np.isclose(people[("AA", "Farming")], 0.5 * farm)
    assert np.isclose(hours[("AA", "Steel")], 0.1 * 2 * 30.0)


def test_allocate_counts_by_low_skilled_within_broad_sector():
    acc = _account()
    counts = pd.Series({("AA", "AGR", 2019): 7.0, ("AA", "IND", 2019): 3.0, ("AA", "SER", 2019): 1.0})
    counts.index.names = ["region", "broad", "time"]
    out = common.allocate_counts(acc, counts, 2019, GROUP)
    assert np.isclose(out.sum(), 11.0)
    assert np.isclose(out[("AA", "Farming")], 7.0)
