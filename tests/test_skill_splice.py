"""Unit test for workforce_salary/skill_splice.py (the C7-3 fix).

Synthetic SUT frames, no data on disk. Runs under pytest or directly::

    <python> tests/test_skill_splice.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from workforce_salary.skill_splice import splice_skill_split, splice_year_for  # noqa: E402


def _sut(wages: dict[str, list[float]]) -> pd.DataFrame:
    """A legacy usebpdom-shaped frame: a product row, w03, then the three skill rows."""
    rows = {"p01.a": [5.0, 6.0, 7.0], "w03": [0.0, 0.0, 0.0]}
    rows.update(wages)
    df = pd.DataFrame(rows, index=["i01.a", "i15.a", "i75"]).T.reset_index()
    return df.rename(columns={"index": "Row"})


def test_splice_keeps_industry_totals_and_takes_reference_shares():
    year = _sut({"w03.a": [0.4, 10.0, 1.0], "w03.b": [99.2, 70.0, 5.0],
                 "w03.c": [0.4, 20.0, 94.0]})
    ref = _sut({"w03.a": [12.0, 1.0, 0.0], "w03.b": [85.0, 8.0, 0.0],
                "w03.c": [3.0, 1.0, 0.0]})
    out, n = splice_skill_split(year, ref)

    w = ["w03.a", "w03.b", "w03.c"]
    before = year.set_index("Row").loc[w]
    after = out.set_index("Row").loc[w]
    # Every industry keeps its own wage bill, so the employment split over
    # industries (which uses only the total) is unchanged.
    np.testing.assert_allclose(after.sum().to_numpy(), before.sum().to_numpy())
    # Industries where the reference has wages take the reference shares.
    np.testing.assert_allclose(after["i01.a"].to_numpy(), [12.0, 85.0, 3.0])
    np.testing.assert_allclose(after["i15.a"].to_numpy(), [10.0, 80.0, 10.0])
    # No reference wage: the industry keeps its own split.
    np.testing.assert_allclose(after["i75"].to_numpy(), before["i75"].to_numpy())
    assert n == 2
    # Rows other than the three wage rows are untouched.
    pd.testing.assert_frame_equal(out[~out["Row"].isin(w)], year[~year["Row"].isin(w)])


def test_zero_wage_industry_stays_zero():
    year = _sut({"w03.a": [0.0, 1.0, 1.0], "w03.b": [0.0, 1.0, 1.0],
                 "w03.c": [0.0, 1.0, 1.0]})
    ref = _sut({"w03.a": [1.0, 1.0, 1.0], "w03.b": [1.0, 1.0, 1.0],
                "w03.c": [1.0, 1.0, 1.0]})
    out, n = splice_skill_split(year, ref)
    assert (out.set_index("Row").loc[["w03.a", "w03.b", "w03.c"], "i01.a"] == 0).all()
    assert n == 2


def test_splice_year_for():
    splice = {"CN": 2007, "WF": 2008}
    assert splice_year_for("CN", 1995, splice) == 2007
    assert splice_year_for("CN", 2006, splice) == 2007
    assert splice_year_for("CN", 2007, splice) is None
    assert splice_year_for("WF", 2007, splice) == 2008
    assert splice_year_for("US", 2000, splice) is None
    assert splice_year_for("CN", 2006, {}) is None


if __name__ == "__main__":
    test_splice_keeps_industry_totals_and_takes_reference_shares()
    test_zero_wage_industry_stays_zero()
    test_splice_year_for()
    print("ok")
