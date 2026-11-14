"""A two-observation hours series is extended with its plain mean.

3.12.0 release 2: `regression_ILO_region_with_minimum*.py` floored the mean of
two observed weekly-hours values to a whole hour (`valeur // 2`), so 41.0 and 42.0
gave 41, not 41.5.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

os.environ.pop("LABOR_RAY", None)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "working_hours"))

from regression_ILO_region_with_minimum import regression  # noqa: E402
from regression_ILO_region_with_minimum_ray import regression_r  # noqa: E402

YEARS = list(range(2000, 2006))


def _pivot(index):
    row = [np.nan, np.nan, 41.0, 42.0, np.nan, np.nan]
    return pd.DataFrame([row], index=index, columns=YEARS)


def test_serial_two_value_mean_is_not_floored():
    pivot = _pivot(["AAA"])
    out = regression(pivot, YEARS[0], YEARS[-1])
    out = pivot if out is None else out
    assert out.loc["AAA", 2000] == 41.5
    assert out.loc["AAA", 2005] == 41.5


def test_ray_module_two_value_mean_is_not_floored():
    index = pd.MultiIndex.from_tuples([("AAA", "SEX_M", "ECO_X")])
    pivot = _pivot(index)
    out = regression_r(pivot, YEARS[0], YEARS[-1])
    assert out.loc[("AAA", "SEX_M", "ECO_X"), 2000] == 41.5
    assert out.loc[("AAA", "SEX_M", "ECO_X"), 2005] == 41.5


def test_main_country_buckets_follow_the_ilo_region(monkeypatch):
    """A main country with no hours borrows from the bucket of its ILO region."""
    monkeypatch.chdir(Path(__file__).resolve().parents[1])
    import average_working_hours as awh  # noqa: E402

    frame = pd.DataFrame({"EXIO3": ["DE", "DE", "US", "CN", "ZA", "SA"],
                          "ref_area": ["DEU", "DEU", "USA", "CHN", "ZAF", "SAU"]})
    got = awh.main_country_buckets(frame)
    assert got == {"DE": "WE", "US": "WL", "CN": "WA", "ZA": "WF", "SA": "WM"}


def test_cell_without_hours_takes_the_bucket_average():
    """sector_hours_pair on a bucket frame gives the pair the infill uses."""
    import average_working_hours as awh

    av2 = pd.DataFrame({"EXIO3": ["WE", "WE"], "sex": ["SEX_M", "SEX_F"],
                        "classif1": ["ECO_A", "ECO_A"], "time": [2022, 2022],
                        "Weighted average working hours": [39.25, 35.5]})
    assert awh.sector_hours_pair(av2, "EXIO3", "WE", "ECO_A", 2022,
                                 "Weighted average working hours") == (39.25, 35.5)
    own = av2.iloc[0:0]
    assert awh.sector_hours_pair(own, "EXIO3", "DE", "ECO_A", 2022,
                                 "Weighted average working hours") == (None, None)
