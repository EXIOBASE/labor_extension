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


if __name__ == "__main__":
    test_national_share_is_reproduced_and_bounded()
    test_country_without_modelled_share_takes_its_region()
    print("ok")
