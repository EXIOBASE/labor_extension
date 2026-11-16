"""Countries ILO stops reporting are carried by their population (2026-11-17).

Until then each cell was held flat at its last reported value (Ukraine at its
2021 workforce through 2025), and the hours average weighted Ukraine's 2022
row by a fixed 0.845 of its 2021 workforce.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "working_hours"))

from workforce_salary import from_cia_to_ilo as fc  # noqa: E402

CLASSIFS = ["ECO_SECTOR_TOTAL", "ECO_DETAILS_A"]
SEXES = ["SEX_T", "SEX_M", "SEX_F"]
COLUMNS = ["ref_area", "ref_area.label", "sex", "classif1", "time", "obs_value", "obs_status"]
VALUE = {("ECO_SECTOR_TOTAL", "SEX_T"): 100.0, ("ECO_SECTOR_TOTAL", "SEX_M"): 60.0,
         ("ECO_SECTOR_TOTAL", "SEX_F"): 40.0, ("ECO_DETAILS_A", "SEX_T"): 30.0,
         ("ECO_DETAILS_A", "SEX_M"): 20.0, ("ECO_DETAILS_A", "SEX_F"): 10.0}


def _ilo():
    # AAA reports to 2021, BBB to 2023 (the build's last year).
    rows = [(a, a, s, c, y, v) for a, last in (("AAA", 2021), ("BBB", 2023))
            for y in range(2020, last + 1) for (c, s), v in VALUE.items()]
    return pd.DataFrame(rows, columns=["ref_area", "ref_area.label", "sex", "classif1",
                                       "time", "obs_value"])


def _carry(population_area):
    return fc._build_dropouts(_ilo(), None, CLASSIFS, SEXES, [2020, 2021, 2022, 2023],
                              COLUMNS, set(), population_area=population_area)


def _cell(out, year, classif="ECO_SECTOR_TOTAL", sex="SEX_T"):
    sel = out[(out["time"] == year) & (out["classif1"] == classif) & (out["sex"] == sex)]
    return float(sel["obs_value"].iloc[0])


def test_carried_country_follows_its_population():
    pop = pd.DataFrame({2021: [1000.0], 2022: [900.0], 2023: [850.0]},
                       index=pd.Index(["AAA"], name="ref_area"))
    out = _carry(pop)
    assert set(out["ref_area"]) == {"AAA"} and set(out["time"]) == {2022, 2023}
    assert set(out["obs_status"]) == {"ILO_dropout_carried"}
    assert np.isclose(_cell(out, 2022), 90.0) and np.isclose(_cell(out, 2023), 85.0)
    # One ratio for every cell: the sexes still sum to the total.
    for y in (2022, 2023):
        for c in CLASSIFS:
            assert np.isclose(_cell(out, y, c, "SEX_M") + _cell(out, y, c, "SEX_F"),
                              _cell(out, y, c, "SEX_T"))


def test_carry_is_flat_without_population():
    for pop in (None,
                pd.DataFrame({2021: [1000.0]}, index=pd.Index(["ZZZ"], name="ref_area")),
                pd.DataFrame({2021: [1000.0], 2022: [np.nan]},
                             index=pd.Index(["AAA"], name="ref_area"))):
        out = _carry(pop)
        assert np.isclose(_cell(out, 2022), 100.0) and np.isclose(_cell(out, 2023), 100.0)


def test_hours_weight_for_ukraine_is_the_carried_workforce():
    import average_working_hours as awh

    rows = [("UKR", s, "ECO_DETAILS_A", y, v * f) for y, f in ((2021, 1.0), (2022, 0.9))
            for s, v in (("SEX_M", 20.0), ("SEX_F", 10.0), ("SEX_T", 30.0))]
    wf = pd.DataFrame(rows, columns=["ref_area", "sex", "classif1", "time", "obs_value"])
    assert np.isclose(awh.ukraine_carry_factor(wf), 0.9)
    assert awh.ukraine_carry_factor(wf[wf["time"] == 2021]) == 1.0
    assert not hasattr(awh, "UKRAINE_WAR_FACTOR")
