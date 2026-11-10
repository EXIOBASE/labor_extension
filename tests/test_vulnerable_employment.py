"""Vulnerable employment shares (working_hours/vulnerable_employment.py)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "working_hours"))

import vulnerable_employment as ve  # noqa: E402

UN = {"AAA": "Region1", "BBB": "Region1", "CCC": "Region1"}


def _employment(countries, year=2019):
    rows = []
    rng = np.random.default_rng(0)
    for c in countries:
        for s in ve.SEXES:
            for g in ve.GROUPS:
                rows.append((c, s, g, year, float(rng.uniform(1, 100))))
    return pd.DataFrame(rows, columns=["ref_area", "sex", "classif1", "time", "obs_value"])


def _profiles(countries_with_survey):
    by_activity = []
    for c in countries_with_survey:
        for s in ve.SEXES:
            for letter, group in ve.SECTION_GROUP.items():
                share = 0.9 if group == "A" else 0.1 if group in ("O", "P", "Q") else 0.4
                by_activity += [(c, s, "STE_ICSE93_TOTAL", f"ECO_ISIC4_{letter}", 2019, 100.0),
                                (c, s, "STE_ICSE93_3", f"ECO_ISIC4_{letter}", 2019, 100 * share)]
    df = pd.DataFrame(by_activity, columns=["ref_area", "sex", "classif1", "classif2", "time", "obs_value"])
    return ve.section_profiles(df, UN)


def test_national_share_is_reproduced_and_bounded():
    E = _employment(["AAA", "BBB"])
    V = pd.Series({("AAA", "SEX_M", 2019): 0.6, ("AAA", "SEX_F", 2019): 0.05,
                   ("BBB", "SEX_M", 2019): 0.3, ("BBB", "SEX_F", 2019): 0.3},
                  name="V")
    V.index.names = ["ref_area", "sex", "time"]
    out = ve.country_shares(E, V, _profiles(["AAA"]), UN)
    assert out["share"].between(0, 1).all()
    got = out.assign(w=out.share * out.E).groupby(["ref_area", "sex"]).apply(
        lambda g: g.w.sum() / g.E.sum(), include_groups=False)
    for (c, s, _), v in V.items():
        assert abs(got[(c, s)] - v) < 1e-9
    # BBB has no survey: it takes Region1's profile, so agriculture stays the
    # most vulnerable section and public administration the least.
    b = out[(out.ref_area == "BBB") & (out.sex == "SEX_M")].set_index("classif1").share
    assert b.idxmax() == "ECO_DETAILS_A"
    assert b["ECO_DETAILS_O"] < b["ECO_DETAILS_G"]


def test_country_without_modelled_share_takes_its_region():
    E = _employment(["AAA", "CCC"])
    V = pd.Series({("AAA", "SEX_M", 2019): 0.4, ("AAA", "SEX_F", 2019): 0.2}, name="V")
    V.index.names = ["ref_area", "sex", "time"]
    out = ve.country_shares(E, V, _profiles(["AAA"]), UN)
    c = out[(out.ref_area == "CCC") & (out.sex == "SEX_M")]
    assert abs((c.share * c.E).sum() / c.E.sum() - 0.4) < 1e-9


def test_suppressed_vulnerable_counts_are_not_pooled_as_zero():
    # Section A: 2018 has 60 own-account workers of 100; 2019 a total of 100
    # with no status detail (suppressed: left out); 2020 a total of 100, all
    # employees (no ICSE 3 or 5 row, but the statuses add up: a true zero).
    # The profile is 60 / 200, not 60 / 300 or 60 / 100.
    rows = [("AAA", s, y, c, "ECO_ISIC4_A", v) for s in ve.SEXES
            for y, c, v in ((2018, "STE_ICSE93_TOTAL", 100.0), (2018, "STE_ICSE93_3", 60.0),
                            (2018, "STE_ICSE93_1", 40.0),
                            (2019, "STE_ICSE93_TOTAL", 100.0),
                            (2020, "STE_ICSE93_TOTAL", 100.0), (2020, "STE_ICSE93_1", 100.0))]
    df = pd.DataFrame(rows, columns=["ref_area", "sex", "time", "classif1", "classif2", "obs_value"])
    country, _, _ = ve.section_profiles(df, UN)
    assert np.isclose(country.loc[("AAA", "SEX_M"), "ECO_DETAILS_A"], 0.3)


def test_region_shares_aggregate_countries_and_stay_below_people(tmp_path):
    # Modelled status: AAA 50% vulnerable, BBB 10%, both sexes, 2019.
    mod = [(c, s, k, 2019, v) for c, vul in (("AAA", 50.0), ("BBB", 10.0)) for s in ve.SEXES
           for k, v in (("STE_ICSE93_TOTAL", 100.0), ("STE_ICSE93_3", vul), ("STE_ICSE93_5", 0.0))]
    pd.DataFrame(mod, columns=["ref_area", "sex", "classif1", "time", "obs_value"]).to_csv(
        tmp_path / ve.STATUS_MODELLED, index=False)
    by = [(c, s, k, f"ECO_ISIC4_{letter}", 2019, v) for c in ("AAA", "BBB") for s in ve.SEXES
          for letter in ve.SECTION_GROUP for k, v in (("STE_ICSE93_TOTAL", 100.0), ("STE_ICSE93_3", 30.0))]
    pd.DataFrame(by, columns=["ref_area", "sex", "classif1", "classif2", "time", "obs_value"]).to_csv(
        tmp_path / ve.STATUS_BY_ACTIVITY, index=False)
    E = _employment(["AAA", "BBB", "X01"])
    E["EXIO3"] = E["ref_area"].map({"AAA": "R1", "BBB": "R1", "X01": ""})
    out = ve.region_shares(E, tmp_path)
    assert set(out["region"]) == {"R1"}  # the blank-region aggregate is dropped
    assert (out["vul"] <= out["E"] + 1e-9).all() and out["share"].between(0, 1).all()
    # The region total is the employment-weighted mean of the national shares.
    for s in ve.SEXES:
        o = out[out.sex == s]
        e = E[(E.sex == s) & (E.ref_area != "X01")].groupby("ref_area").obs_value.sum()
        assert np.isclose(o.vul.sum() / o.E.sum(), (0.5 * e["AAA"] + 0.1 * e["BBB"]) / e.sum())
        assert np.isclose(o.E.sum(), e.sum())


if __name__ == "__main__":
    import tempfile
    test_national_share_is_reproduced_and_bounded()
    test_country_without_modelled_share_takes_its_region()
    test_suppressed_vulnerable_counts_are_not_pooled_as_zero()
    with tempfile.TemporaryDirectory() as d:
        test_region_shares_aggregate_countries_and_stay_below_people(Path(d))
    print("ok")
