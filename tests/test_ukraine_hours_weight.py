"""Ukraine's 2022 weight in the hours average follows the employment account
(register R-LAB-07, 3.12.0 release 2).

The hours stage weighted Ukraine's 2022 row by a fixed 0.845 of its 2021
workforce while the workforce stage holds Ukraine flat at its 2021 value, so
the two stages disagreed on how many people Ukraine has in 2022. The weight
is now the account's own 2022 over 2021 ratio (`ukraine_carry_factor`): 1.0
against this branch's flat carry, the population ratio against main's.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "working_hours"))


@pytest.fixture(scope="module")
def awh():
    # Imported here, not at collection: importing the hours module starts a
    # Ray instance (substitute.py), and a later ray.init in another test file
    # (test_hours_two_value_mean) would then raise. Shut it down afterwards.
    import ray
    import average_working_hours as module
    yield module
    ray.shutdown()


def _workforce(factor_2022, time_type=int):
    rows = [("UKR", s, c, time_type(y), v * f)
            for y, f in ((2021, 1.0), (2022, factor_2022))
            for c in ("ECO_DETAILS_A", "ECO_DETAILS_C")
            for s, v in (("SEX_M", 20.0), ("SEX_F", 10.0), ("SEX_T", 30.0))]
    other = [("POL", s, "ECO_DETAILS_A", time_type(y), 500.0)
             for y in (2021, 2022) for s in ("SEX_M", "SEX_F")]
    return pd.DataFrame(rows + other,
                        columns=["ref_area", "sex", "classif1", "time", "obs_value"])


def test_flat_carry_gives_weight_one(awh):
    # The release 2 workforce stage holds Ukraine flat from 2021.
    assert awh.ukraine_carry_factor(_workforce(1.0)) == 1.0


def test_weight_is_the_accounts_ratio(awh):
    assert np.isclose(awh.ukraine_carry_factor(_workforce(0.9)), 0.9)
    # Read back from CSV, time and value can arrive as strings.
    wf = _workforce(0.9, time_type=str)
    wf["obs_value"] = wf["obs_value"].astype(str)
    assert np.isclose(awh.ukraine_carry_factor(wf), 0.9)


def test_no_ukraine_2022_gives_weight_one(awh):
    wf = _workforce(0.9)
    assert awh.ukraine_carry_factor(wf[wf["time"] == 2021]) == 1.0
    assert awh.ukraine_carry_factor(wf[wf["ref_area"] != "UKR"]) == 1.0


def test_fixed_war_factor_is_gone(awh):
    assert not hasattr(awh, "UKRAINE_WAR_FACTOR")
    source = (ROOT / "working_hours" / "average_working_hours.py").read_text(
        encoding="utf-8")
    assert "0.845 *" not in source
