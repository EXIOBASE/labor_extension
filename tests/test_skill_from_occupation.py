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


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("ok")
