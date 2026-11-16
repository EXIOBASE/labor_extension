"""People by skill from occupation (workforce_salary/skill_from_occupation.py)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from workforce_salary import skill_from_occupation as so  # noqa: E402


def test_ras_hits_both_margins_and_fills_empty_rows():
    prior = np.array([[1.0, 2.0, 3.0], [0.0, 0.0, 0.0], [5.0, 1.0, 0.5]])
    rows = np.array([10.0, 4.0, 6.0])
    cols = np.array([5.0, 9.0, 6.0])
    X = so.ras(prior, rows, cols)
    assert np.allclose(X.sum(axis=1), rows)
    assert np.allclose(X.sum(axis=0), cols)
    assert (X[1] > 0).all()  # no wage bill, but people: takes the column mix


def _frame():
    rows = []
    for sector, wages in (("i01", (8, 2, 0.5)), ("i24", (1, 5, 3)), ("i55", (0, 0, 0))):
        r = {"Country": "AA", "Sector": sector}
        for k, w in zip(so.SKILLS, wages):
            r[so.WAGE[k]] = w
        for k, m, f in zip(so.SKILLS, (5, 3, 2), (4, 2, 2)):
            r[f"{so.SPLIT[k]} - male"] = m
            r[f"{so.SPLIT[k]} - female"] = f
            r[f"{so.SPLIT[k]} - total"] = m + f
        rows.append(r)
    return pd.DataFrame(rows)


def test_rebalance_keeps_industry_totals_and_sets_skill_totals():
    f = _frame()
    shares = pd.DataFrame({"low": [0.5, 0.2], "middle": [0.3, 0.3], "high": [0.2, 0.5]},
                          index=pd.MultiIndex.from_tuples([("AA", "SEX_M", 2019), ("AA", "SEX_F", 2019)],
                                                          names=["region", "sex", "time"]))
    g = so.rebalance_year(f, shares, 2019)
    for sex, code in (("male", "SEX_M"), ("female", "SEX_F")):
        cols = [f"{so.SPLIT[k]} - {sex}" for k in so.SKILLS]
        assert np.allclose(g[cols].sum(axis=1), f[cols].sum(axis=1))
        tot = g[cols].sum()
        assert np.allclose(tot / tot.sum(), shares.loc[("AA", code, 2019)].to_numpy())
    for k in so.SKILLS:
        assert np.allclose(g[f"{so.SPLIT[k]} - total"],
                           g[f"{so.SPLIT[k]} - male"] + g[f"{so.SPLIT[k]} - female"])


def test_group_96_split_by_elementary_ratio():
    rows = [("AAA", s, 2019, c, v) for s in ("SEX_M", "SEX_F") for c, v in
            (("OCU_ISCO08_2", 20.0), ("OCU_ISCO08_5", 30.0), ("OCU_ISCO08_96", 50.0))]
    modelled = pd.DataFrame(rows, columns=["ref_area", "sex", "time", "classif1", "obs_value"])
    survey = pd.DataFrame([("AAA", s, 2015, c, v) for s in ("SEX_M", "SEX_F")
                           for c, v in (("OCU_ISCO08_6", 3.0), ("OCU_ISCO08_9", 1.0))],
                          columns=["ref_area", "sex", "time", "classif1", "obs_value"])
    out = so.country_skill_shares(modelled, survey, {"AAA": "R"}, [2019])
    row = out.loc[("AAA", "SEX_M", 2019)]
    assert np.isclose(row["low"], 0.125) and np.isclose(row["high"], 0.2)
    assert np.isclose(row["middle"], 0.675)


def test_no_survey_country_splits_96_by_its_agriculture():
    rows = [(c, s, 2019, k, v) for c in ("AAA", "BBB") for s in ("SEX_M", "SEX_F")
            for k, v in (("OCU_ISCO08_2", 20.0), ("OCU_ISCO08_96", 60.0))]
    modelled = pd.DataFrame(rows, columns=["ref_area", "sex", "time", "classif1", "obs_value"])
    # AAA has a survey: group 6 = 30, agriculture 40 -> alpha 0.75.
    survey = pd.DataFrame([("AAA", s, 2019, c, v) for s in ("SEX_M", "SEX_F")
                           for c, v in (("OCU_ISCO08_6", 30.0), ("OCU_ISCO08_9", 30.0))],
                          columns=["ref_area", "sex", "time", "classif1", "obs_value"])
    agri = pd.Series({(c, s, 2019): 40.0 for c in ("AAA", "BBB") for s in ("SEX_M", "SEX_F")})
    agri.index.names = ["ref_area", "sex", "time"]
    out = so.country_skill_shares(modelled, survey, {"AAA": "R", "BBB": "R"}, [2019], agri=agri)
    # BBB: group 6 = 0.75 * 40 = 30 of 60, so elementary 30 of 80 people.
    assert np.isclose(out.loc[("BBB", "SEX_M", 2019), "low"], 30 / 80)


def test_agriculture_above_group_96_falls_back_to_world_ratio():
    # CCC (no survey) has more farm workers than group 96: alpha * agri
    # would take all of group 96 and leave no elementary workers, so the
    # world pool 9 / (6 + 9) = 30 / 60 is used instead.
    rows = [(c, s, 2019, k, v) for c in ("AAA", "CCC") for s in ("SEX_M", "SEX_F")
            for k, v in (("OCU_ISCO08_2", 20.0), ("OCU_ISCO08_96", 60.0))]
    modelled = pd.DataFrame(rows, columns=["ref_area", "sex", "time", "classif1", "obs_value"])
    survey = pd.DataFrame([("AAA", s, 2019, c, v) for s in ("SEX_M", "SEX_F")
                           for c, v in (("OCU_ISCO08_6", 30.0), ("OCU_ISCO08_9", 30.0))],
                          columns=["ref_area", "sex", "time", "classif1", "obs_value"])
    agri = pd.Series({(c, s, 2019): a for c, a in (("AAA", 40.0), ("CCC", 100.0))
                      for s in ("SEX_M", "SEX_F")})
    agri.index.names = ["ref_area", "sex", "time"]
    out = so.country_skill_shares(modelled, survey, {"AAA": "R", "CCC": "R"}, [2019], agri=agri)
    for s in ("SEX_M", "SEX_F"):
        assert np.isclose(out.loc[("CCC", s, 2019), "low"], 0.5 * 60 / 80)


def test_survey_years_with_one_group_are_not_pooled():
    # 2015 reports both groups (6: 3, 9: 1); 2016 only group 6, which must
    # not count as zero elementary workers. DDD reports only group 9: no
    # survey ratio, so the world pool (AAA's 2015, 0.25) is used.
    rows = [(c, s, 2019, k, v) for c in ("AAA", "DDD") for s in ("SEX_M", "SEX_F")
            for k, v in (("OCU_ISCO08_2", 20.0), ("OCU_ISCO08_96", 80.0))]
    modelled = pd.DataFrame(rows, columns=["ref_area", "sex", "time", "classif1", "obs_value"])
    survey = pd.DataFrame([("AAA", s, y, c, v) for s in ("SEX_M", "SEX_F")
                           for y, c, v in ((2015, "OCU_ISCO08_6", 3.0), (2015, "OCU_ISCO08_9", 1.0),
                                           (2016, "OCU_ISCO08_6", 50.0))]
                          + [("DDD", s, 2015, "OCU_ISCO08_9", 7.0) for s in ("SEX_M", "SEX_F")],
                          columns=["ref_area", "sex", "time", "classif1", "obs_value"])
    country, _, wld = so.elementary_ratio(survey, {"AAA": "R", "DDD": "R"})
    assert np.isclose(country[("AAA", "SEX_M")], 0.25)
    assert ("DDD", "SEX_M") not in country.index
    assert np.isclose(wld["SEX_F"], 0.25)
    out = so.country_skill_shares(modelled, survey, {"AAA": "R", "DDD": "R"}, [2019])
    assert np.isclose(out.loc[("DDD", "SEX_M", 2019), "low"], 0.25 * 0.8)


def test_region_skill_shares_weight_countries_by_employment():
    rows = [(c, s, 2019, k, v) for c, low in (("AAA", 10.0), ("BBB", 50.0))
            for s in ("SEX_M", "SEX_F")
            for k, v in (("OCU_ISCO08_2", 100.0 - low), ("OCU_ISCO08_96", low))]
    modelled = pd.DataFrame(rows, columns=["ref_area", "sex", "time", "classif1", "obs_value"])
    survey = pd.DataFrame([(c, s, 2019, "OCU_ISCO08_9", 1.0) for c in ("AAA", "BBB")
                           for s in ("SEX_M", "SEX_F")]
                          + [(c, s, 2019, "OCU_ISCO08_6", 0.0) for c in ("AAA", "BBB")
                             for s in ("SEX_M", "SEX_F")],
                          columns=["ref_area", "sex", "time", "classif1", "obs_value"])
    # AAA and BBB form region R1 (3 and 1 people); an ILO aggregate with a
    # blank region and a `not found` row must not count.
    emp = pd.DataFrame([(c, reg, s, "ECO_DETAILS_TOTAL", 2019, e)
                        for c, reg, e in (("AAA", "R1", 3.0), ("BBB", "R1", 1.0),
                                          ("X01", "", 1000.0), ("X02", "not found", 1000.0))
                        for s in ("SEX_M", "SEX_F")],
                       columns=["ref_area", "EXIO3", "sex", "classif1", "time", "obs_value"])
    sh = so.region_skill_shares(modelled, survey, emp, [2019])
    assert list(sh.index.get_level_values("region").unique()) == ["R1"]
    assert np.isclose(sh.loc[("R1", "SEX_M", 2019), "low"], (3 * 0.1 + 1 * 0.5) / 4)
    assert np.allclose(sh.sum(axis=1), 1.0)


def test_country_keeps_its_own_mix_after_its_modelled_series_ends():
    # ILO's modelled occupation rows for Ukraine stop in 2021 while its
    # workforce is carried to 2025: the later years keep the country's last
    # mix, not its UN region's.
    rows = [(c, s, y, k, v) for c, low, years in (("UKR", 10.0, (2021,)), ("POL", 50.0, (2021, 2022)))
            for y in years for s in ("SEX_M", "SEX_F")
            for k, v in (("OCU_ISCO08_2", 100.0 - low), ("OCU_ISCO08_96", low))]
    modelled = pd.DataFrame(rows, columns=["ref_area", "sex", "time", "classif1", "obs_value"])
    survey = pd.DataFrame([(c, s, 2019, k, v) for c in ("UKR", "POL") for s in ("SEX_M", "SEX_F")
                           for k, v in (("OCU_ISCO08_9", 1.0), ("OCU_ISCO08_6", 0.0))],
                          columns=["ref_area", "sex", "time", "classif1", "obs_value"])
    emp = pd.DataFrame([(c, c, s, "ECO_DETAILS_TOTAL", y, 5.0) for c in ("UKR", "POL")
                        for y in (2021, 2022) for s in ("SEX_M", "SEX_F")],
                       columns=["ref_area", "EXIO3", "sex", "classif1", "time", "obs_value"])
    sh = so.region_skill_shares(modelled, survey, emp, [2021, 2022])
    assert np.isclose(sh.loc[("UKR", "SEX_M", 2021), "low"], 0.1)
    assert np.isclose(sh.loc[("UKR", "SEX_M", 2022), "low"], 0.1)
    assert np.isclose(sh.loc[("POL", "SEX_F", 2022), "low"], 0.5)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("ok")


def _long(rows):
    return pd.DataFrame(rows, columns=["ref_area", "sex", "time", "classif1", "obs_value"])


def test_merged_elementary_takes_low_skilled_out_of_groups_7_and_8():
    # TTT's survey has groups 1-6 and 8 and never 7 or 9 (Taiwan): group 96
    # is all farmers, and the elementary workers come out of group 8 by the
    # region's survey ratio 9 / (7 + 8 + 9) = 10 / 50, whatever group 96 does.
    modelled = _long([("TTT", s, y, k, v) for s in ("SEX_M", "SEX_F")
                      for y, g96 in ((2019, 10.0), (2025, 2.0))
                      for k, v in (("OCU_ISCO08_2", 30.0), ("OCU_ISCO08_8", 60.0),
                                   ("OCU_ISCO08_96", g96))])
    survey = _long([("TTT", s, 2019, f"OCU_ISCO88_{g}", 1.0)
                    for s in ("SEX_M", "SEX_F") for g in (1, 2, 3, 4, 5, 6, 8)]
                   + [("PPP", s, 2019, k, v) for s in ("SEX_M", "SEX_F")
                      for k, v in (("OCU_ISCO08_6", 5.0), ("OCU_ISCO08_7", 20.0),
                                   ("OCU_ISCO08_8", 20.0), ("OCU_ISCO08_9", 10.0))])
    assert so.merged_elementary(survey) == {"TTT"}
    out = so.country_skill_shares(modelled, survey, {"TTT": "R", "PPP": "R"}, [2019, 2025])
    assert np.isclose(out.loc[("TTT", "SEX_M", 2019), "low"], 0.2 * 60 / 100)
    assert np.isclose(out.loc[("TTT", "SEX_M", 2025), "low"], 0.2 * 60 / 92)
    assert np.isclose(out.loc[("TTT", "SEX_M", 2019), "high"], 0.3)


def test_ratio_break_pools_each_side_of_the_break(monkeypatch):
    # Group 6 drops from 30 to 10 in the survey and in the modelled group 96
    # at the break; group 9 stays at 30, and so must the low-skilled people.
    monkeypatch.setattr(so, "RATIO_BREAKS", {"AAA": (2021,)})
    modelled = _long([("AAA", s, y, k, v) for s in ("SEX_M", "SEX_F")
                      for y, g96 in ((2020, 60.0), (2021, 40.0))
                      for k, v in (("OCU_ISCO08_2", 40.0), ("OCU_ISCO08_96", g96))])
    survey = _long([("AAA", s, y, k, v) for s in ("SEX_M", "SEX_F")
                    for y, g6 in ((2019, 30.0), (2020, 30.0), (2021, 10.0), (2022, 10.0))
                    for k, v in (("OCU_ISCO08_6", g6), ("OCU_ISCO08_9", 30.0))])
    out = so.country_skill_shares(modelled, survey, {"AAA": "R"}, [2020, 2021])
    assert np.isclose(out.loc[("AAA", "SEX_M", 2020), "low"], 30 / 100)
    assert np.isclose(out.loc[("AAA", "SEX_M", 2021), "low"], 30 / 80)


def test_level_break_carries_the_new_level_back_and_ignores_years_asked(monkeypatch):
    # High-skilled share 40% on the old basis (to 2020), 20% on the new one
    # (from 2023): 2020-2022 take the 2023 shares, 2019 keeps its movement
    # against 2020, and a build of 2019 alone gives the same 2019.
    monkeypatch.setattr(so, "LEVEL_BREAKS", {"AAA": (2020, 2023)})
    high = {2019: 30.0, 2020: 40.0, 2021: 33.0, 2022: 27.0, 2023: 20.0}
    modelled = _long([("AAA", s, y, k, v) for s in ("SEX_M", "SEX_F") for y, h in high.items()
                      for k, v in (("OCU_ISCO08_2", h), ("OCU_ISCO08_5", 100.0 - h))])
    survey = _long([("AAA", s, 2019, k, 1.0) for s in ("SEX_M", "SEX_F")
                    for k in ("OCU_ISCO08_6", "OCU_ISCO08_9")])
    out = so.country_skill_shares(modelled, survey, {"AAA": "R"}, list(high))
    for y in (2020, 2021, 2022, 2023):
        assert np.isclose(out.loc[("AAA", "SEX_M", y), "high"], 0.2)
    h, m = 0.3 * 0.2 / 0.4, 0.7 * 0.8 / 0.6
    assert np.isclose(out.loc[("AAA", "SEX_M", 2019), "high"], h / (h + m))
    assert np.allclose(out.sum(axis=1), 1.0)
    one = so.country_skill_shares(modelled, survey, {"AAA": "R"}, [2019])
    assert list(one.index.get_level_values("time").unique()) == [2019]
    assert np.isclose(one.loc[("AAA", "SEX_M", 2019), "high"], h / (h + m))
