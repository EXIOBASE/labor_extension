"""Supplementary countries (workforce_salary/from_cia_to_ilo.py).

3.12.0 release 2: the Channel Islands are not counted twice, the hand-compiled
territory totals (total population) are scaled to workforce, and entities whose
region has no ILO aggregate for their income group fall back to the World
aggregate instead of being skipped.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from workforce_salary import from_cia_to_ilo as fc  # noqa: E402

YEARS = list(range(1991, 2022))
SEXES = ["SEX_T", "SEX_M", "SEX_F"]
CLASSIF = ["ECO_SECTOR_TOTAL", "ECO_SECTOR_AGR"]

EUR = "Northern, Southern and Western Europe: High income"
WORLD_HI = "World: High income"
AFRICA_HI = "Africa: High income"  # deliberately not an ILO aggregate here
EMPLOYED = {EUR: 1000.0, WORLD_HI: 5000.0}
POPULATION = {EUR: 2000.0, WORLD_HI: 10000.0}  # participation 0.5


def _ilo_frame(with_chi=True):
    rows = []
    for label, emp in EMPLOYED.items():
        for sex in SEXES:
            for c in CLASSIF:
                for y in YEARS:
                    share = {"SEX_T": 1.0, "SEX_M": 0.6, "SEX_F": 0.4}[sex]
                    share *= 1.0 if c == "ECO_SECTOR_TOTAL" else 0.1
                    rows.append((label, label, sex, c, y, emp * share))
    if with_chi:
        for sex in SEXES:
            for c in CLASSIF:
                for y in YEARS:
                    rows.append(("CHI", "Channel Islands", sex, c, y, 80.0))
    d = pd.DataFrame(rows, columns=["ref_area", "ref_area.label", "sex",
                                    "classif1", "time", "obs_value"])
    d["source"] = "XA:1"
    d["indicator"] = "EMP"
    d["obs_status"] = np.nan
    d["EXIO3"] = "WE"
    return d


def _cia():
    def entry(n, date):
        return {"data": {"economy": {"labor_force": {"total_size": {
            "total_people": n, "date": date}}}}}
    return {"countries": {"jersey": entry(60000, "2020"),
                          "guernsey": entry(31000, "2020"),
                          "isle_of_man": entry(41000, "2020"),
                          "seychelles": entry(51000, "2020")}}


def _meta():
    rows = []
    for iso, income, sub, reg in [
            ("JEY", "High income", "Northern, Southern and Western Europe", "Europe and Central Asia"),
            ("GGY", "High income", "Northern, Southern and Western Europe", "Europe and Central Asia"),
            ("IMN", "High income", "Northern, Southern and Western Europe", "Europe and Central Asia"),
            ("SYC", "High income", "Sub-Saharan Africa", "Africa")]:
        rows.append({"ISO3 Code": iso, "World Bank Income Group": income,
                     "ILO Subregion - Broad": sub, "ILO Region": reg})
    return pd.DataFrame(rows)


def _xlsx_missing():
    cols = ["ISO3", "Name", "Label_short", "Remark", "Source"] + [float(y) for y in YEARS]
    return pd.DataFrame([
        ["GLP", "Guadeloupe", EUR, np.nan, "x"] + [0.4] * len(YEARS),
        ["REU", "Reunion", AFRICA_HI, np.nan, "x"] + [0.8] * len(YEARS),
    ], columns=cols)


def _run(with_chi, population_agg):
    data_list = _ilo_frame(with_chi)
    return fc.cia_to_ilo(data_list, _cia(), _meta(), _xlsx_missing(),
                         population_agg=population_agg)[0]


def _total(out, iso, year=2020):
    sel = out[(out["ref_area"] == iso) & (out["classif1"] == "ECO_SECTOR_TOTAL")
              & (out["sex"] == "SEX_T") & (out["time"] == year)]
    return float(sel["obs_value"].sum())


@pytest.fixture(scope="module")
def population_agg():
    return pd.DataFrame(
        {y: POPULATION for y in YEARS}).rename_axis("ref_area.label")


@pytest.fixture(scope="module")
def with_chi(population_agg):
    return _run(True, population_agg)


def test_drop_double_counted_unit():
    kept, dropped = fc.drop_double_counted(["JEY", "GGY", "IMN"], ["CHI", "FRA"])
    assert kept == ["IMN"] and sorted(dropped) == ["GGY", "JEY"]
    kept, dropped = fc.drop_double_counted(["JEY", "GGY", "IMN"], ["FRA"])
    assert kept == ["JEY", "GGY", "IMN"] and dropped == []


def test_channel_islands_counted_once_when_ilo_has_chi(with_chi):
    present = set(with_chi["ref_area"].unique())
    assert "JEY" not in present and "GGY" not in present


def test_channel_islands_parts_built_when_ilo_lacks_chi(population_agg):
    out = _run(False, population_agg)
    present = set(out["ref_area"].unique())
    assert {"JEY", "GGY"} <= present
    # constant share of the ILO aggregate, anchored on the Factbook figure
    assert _total(out, "JEY") == pytest.approx(60.0, rel=1e-9)
    assert _total(out, "GGY") == pytest.approx(31.0, rel=1e-9)


def test_no_island_counted_twice_in_the_combined_table(with_chi):
    """With CHI from ILO, the Channel Islands total is CHI alone."""
    combined = pd.concat([_ilo_frame(True), with_chi])
    islands = combined[combined["ref_area"].isin(["CHI", "JEY", "GGY"])
                       & (combined["classif1"] == "ECO_SECTOR_TOTAL")
                       & (combined["sex"] == "SEX_T") & (combined["time"] == 2020)]
    assert islands["obs_value"].sum() == pytest.approx(80.0)


def test_isle_of_man_and_seychelles_added(with_chi):
    # IMN: the Factbook name isle_of_man does not pass the regex converter.
    assert _total(with_chi, "IMN") == pytest.approx(41.0, rel=1e-9)
    # SYC: Sub-Saharan Africa and Africa have no high-income aggregate, so the
    # World aggregate of the same income group is used.
    assert _total(with_chi, "SYC") == pytest.approx(51.0, rel=1e-9)
    status = with_chi.loc[with_chi["ref_area"] == "SYC", "obs_status"].unique()
    assert list(status) == ["ILO_World_income"]


def test_territory_total_is_scaled_by_participation(with_chi):
    # GLP: 0.4 (thousand of people after the /1000 done by the caller is not
    # applied here, the helper takes the value as given) x 0.5 participation.
    assert _total(with_chi, "GLP") == pytest.approx(0.4 * 0.5, rel=1e-9)
    # REU has no aggregate for Africa: High income, so World: High income
    assert _total(with_chi, "REU") == pytest.approx(0.8 * 0.5, rel=1e-9)
    status = with_chi.loc[with_chi["ref_area"] == "REU", "obs_status"].unique()
    assert list(status) == ["ILO_World_income"]


def test_switch_off_keeps_total_population(population_agg):
    out = _run(True, None)
    assert _total(out, "GLP") == pytest.approx(0.4, rel=1e-9)
    assert _total(out, "REU") == pytest.approx(0.8, rel=1e-9)


def test_missing_population_file_is_loud(tmp_path):
    with pytest.raises(FileNotFoundError, match="LABOR_TERRITORY_PARTICIPATION"):
        fc.load_population_aggregates(tmp_path)


def test_resolve_aggregate_chain():
    agg = {"A: High income", "Africa: Low income", "World: High income"}
    assert fc.resolve_aggregate("A: High income", "R: High income", "High income", agg) == ("A: High income", "ILO_Subregion_Broad")
    assert fc.resolve_aggregate("x: High income", "A: High income", "High income", agg) == ("A: High income", "ILO_region")
    assert fc.resolve_aggregate("x: High income", "y: High income", "High income", agg) == ("World: High income", "ILO_World_income")
    assert fc.resolve_aggregate("x: Mid", "y: Mid", "Mid", agg) == (None, None)
