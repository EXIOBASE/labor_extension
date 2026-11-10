"""Labour-risk allocation helpers (labour_risk/common.py)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
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


def test_allocate_counts_year_without_counts_is_zero():
    acc = _account()
    counts = pd.Series({("AA", "AGR", 2019): 7.0})
    counts.index.names = ["region", "broad", "time"]
    out = common.allocate_counts(acc, counts, 2005, GROUP)
    assert (out == 0).all()


def _child_inputs():
    from labour_risk import child_forced as cf
    if not (cf.ILOSTAT / "CLD_2POP_SEX_AGE_NB_A.csv").exists():
        pytest.skip("ILOSTAT child labour downloads not available")
    pop = pd.read_csv(cf.ILOSTAT / "CLD_2POP_SEX_AGE_NB_A.csv", usecols=["ref_area"])
    areas = sorted(a for a in pop.ref_area.unique() if not a.startswith("X"))
    return cf, {a: a for a in areas}, common.un_region(areas)


def test_child_labour_single_year_equals_multi_year():
    """A year's count must not depend on the other years requested: the
    benchmark scale is interpolated over the full span either way."""
    cf, region_of, un = _child_inputs()
    one = cf.child_labour("child_labour", [2010], region_of, un)
    many = cf.child_labour("child_labour", list(range(1995, 2026)), region_of, un)
    pd.testing.assert_series_equal(one, many.xs(2010, level="time", drop_level=False))
    # 2008 and 2012 are world benchmarks (ILO 2017 trends); 2010 lies between.
    assert 150_000 < one.sum() < 260_000


def test_informal_spread_keeps_cell_rate():
    from labour_risk import indicators
    f = pd.DataFrame({"ref_area": "AA", "sex": "SEX_M", "cell": "MKT", "time": 2019,
                      "group": ["ECO_DETAILS_G", "ECO_DETAILS_I", "ECO_DETAILS_K"],
                      "vul": [0.4, 0.2, 0.0], "E": [50.0, 30.0, 20.0], "rate": 0.5})
    s = indicators._spread(f)
    assert np.isclose((s * f.E).sum() / f.E.sum(), 0.5, atol=1e-6)
    assert (np.diff(s) < 0).all() and (s >= 0).all() and (s <= 1).all()


def _vul_synthetic():
    from labour_risk import indicators
    rows = []
    for a, base in (("IND", 0.7), ("CHN", 0.4), ("BRA", 0.3), ("THA", 0.5), ("USA", 0.05)):
        for sex in common.SEXES:
            for i, g in enumerate(common.GROUPS):
                for t in range(1995, 2026):
                    rows.append((a, a, sex, g, t, base * (1.5 if g == "ECO_DETAILS_A" else 1.0) * (1 - 0.01 * i),
                                 100.0 + i))
    return indicators, pd.DataFrame(rows, columns=["ref_area", "region", "sex", "group", "time", "share", "E"])


def test_informal_single_year_equals_multi_year():
    indicators, vul = _vul_synthetic()
    risk = Path("d:/indecol/data/labour/data/risk/ilostat_2026-11-10")
    if not (risk / "SDG_0831_SEX_ECO_RT_A.csv").exists():
        pytest.skip("SDG 8.3.1 download not available")
    un = common.un_region(sorted(set(vul.ref_area)))
    one = indicators.informal(vul, risk, un, [2010]).set_index(["ref_area", "sex", "group", "time"])
    many = indicators.informal(vul, risk, un, common.SPAN).set_index(["ref_area", "sex", "group", "time"])
    pd.testing.assert_frame_equal(one, many.xs(2010, level="time", drop_level=False).reindex(one.index))
    assert (many["share"] <= 1).all() and (many["share"] >= 0).all()
    # China has no SDG 8.3.1 data: predicted, at least its vulnerable share.
    chn = many.loc["CHN"]
    assert chn["informal_source"].str.startswith("predicted").all()
    v = vul.set_index(["ref_area", "sex", "group", "time"])["share"].loc["CHN"]
    assert (chn["share"] >= v.reindex(chn.index) - 1e-9).groupby(level="sex").mean().min() > 0.5


def _build_module():
    import importlib.util
    f = Path(__file__).resolve().parents[1] / "scripts" / "build_labour_risk.py"
    spec = importlib.util.spec_from_file_location("build_labour_risk", f)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_no_stressor_joins_the_employment_totals():
    """Downstream composites sum `Employment people.*` and `Employment hours.*`."""
    m = _build_module()
    assert not [s for s in m.UNITS if s.startswith(("Employment people", "Employment hours"))]


def test_write_year_release_format(tmp_path):
    m = _build_module()
    cols = pd.MultiIndex.from_tuples([("AT", "Farming"), ("AT", "Steel")], names=["region", "sector"])
    fd = pd.MultiIndex.from_tuples([("AT", "Households")], names=["region", "category"])
    F = pd.DataFrame([[1.0, 2.0]], index=pd.Index(["Forced labour"], name="stressor"), columns=cols)
    m.write_year(tmp_path, F, fd)
    back = pd.read_csv(tmp_path / "F.txt", sep="\t", header=[0, 1], index_col=0)
    assert back.columns.equals(cols) and back.index.name == "stressor"
    fy = pd.read_csv(tmp_path / "F_Y.txt", sep="\t", header=[0, 1], index_col=0)
    assert fy.columns.equals(fd) and (fy == 0).all().all()
    import json
    assert json.loads((tmp_path / "file_parameters.json").read_text())["name"] == "labour_risk"
