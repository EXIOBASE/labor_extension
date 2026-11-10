"""Labour-risk indicators built from ILOSTAT (docs/improvement_plan_2026-11-06.md, Phase 4).

Each function returns country-level values with the ILO employment E
alongside (columns ref_area, region, sex, group, time, share, E), ready for
`common.region_share`.

- `informal`: informal employment share, ILO's harmonised SDG 8.3.1
  (`SDG_0831_SEX_ECO_RT_A`, national data only, ILO's modelled aggregates
  dropped) by sex and the six ECO_AGGREGATE cells (agriculture; mining and
  utilities; manufacturing; construction; market services; public and other
  services), falling back to the broad sector, then the national total, and
  to both sexes where a sex is missing. Interpolated between observed years
  and carried outside them (data start in 2004 for most countries, so
  1995-2003 hold the first observation). Within a cell the rate is spread
  over the labour account's activity groups by their vulnerable share with
  one logit shift that keeps the cell's employment-weighted rate (as in
  working_hours/vulnerable_employment). Countries without any SDG 8.3.1
  data (China, the US, Japan, Canada, Australia and small territories) are
  predicted from their vulnerable share: informal = r * vulnerable bounded
  to [vulnerable, 1], with r the ratio of informal to vulnerable workers
  summed over the observed country-years of the UN region, else the World
  Bank income group, else the world, by sex and cell. In the 3.12 e3 build
  146 countries have data (62% of 2019 employment) and the world total is
  96%, 99% and 99% of ILO's modelled world informal employment
  (`EMP_2IFL_SEX_NB_A`, X01) in 2005, 2019 and 2024.
- `working_poverty`: employed people below US$3 a day (2021 PPP), SDG 1.1.1
  (`SDG_0111_SEX_AGE_RT_A`, age 15+, ILO modelled, 2000-2025, every low- and
  middle-income country). High-income countries are not estimated by ILO
  and are set to zero; other gaps take the UN region's employment-weighted
  rate. The national rate is spread over activity groups in proportion to
  the vulnerable share (working poverty is concentrated in own-account and
  family work), capped at 1 and rescaled to keep the national rate.
- `long_hours`: share of employed people usually working 49 hours a week or
  more (ILO's "excessive hours" band, `EMP_TEMP_SEX_HOW_NB_A`); national by
  sex, no activity detail, so uniform over groups; gaps take the UN region,
  then the world.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from labour_risk.common import REPO, SEXES, fill_years, income_group


#: ILO ECO_AGGREGATE cell of each labour-account activity group, and the broad
#: sector (ECO_SECTOR) of each cell, for SDG 8.3.1.
CELL = {"ECO_DETAILS_A": "AGR", "ECO_DETAILS_B": "MEL", "ECO_DETAILS_DE": "MEL",
        "ECO_DETAILS_C": "MAN", "ECO_DETAILS_F": "CON",
        **{f"ECO_DETAILS_{g}": "MKT" for g in ("G", "HJ", "I", "K", "LMN")},
        **{f"ECO_DETAILS_{g}": "PUB" for g in ("O", "P", "Q", "RSTU")}}
CELL_SECTOR = {"AGR": "AGR", "MEL": "IND", "MAN": "IND", "CON": "IND", "MKT": "SER", "PUB": "SER"}
_EPS = 1e-4


def informal_rates(risk_dir: Path, years) -> tuple[pd.Series, set]:
    """SDG 8.3.1 informal share (0-1) by ref_area, sex, cell, time from
    national data. Each (country, sex, classification) series is interpolated
    between observed years and carried outside them, then each cell takes
    its ECO_AGGREGATE value, else its broad sector's, else the national
    total; a sex without data takes the both-sexes value. Returns the rates
    and the set of (ref_area, time) actually observed."""
    d = pd.read_csv(risk_dir / "SDG_0831_SEX_ECO_RT_A.csv", low_memory=False,
                    usecols=["ref_area", "source", "sex", "classif1", "time", "obs_value"])
    # ILO's regional aggregates (X01...) are modelled (source XA); keep countries.
    d = d[~d["source"].astype(str).str.startswith("XA") & ~d["ref_area"].str.match(r"^X\d\d$")]
    d = d[d["sex"].isin(["SEX_M", "SEX_F", "SEX_T"]) & d["obs_value"].notna()]
    observed = set(zip(d["ref_area"], d["time"]))
    r = fill_years((d.groupby(["ref_area", "sex", "classif1", "time"])["obs_value"].mean() / 100).clip(0, 1),
                   ["ref_area", "sex", "classif1"], years)
    w = r.unstack("classif1")
    out = {}
    for cell, sector in CELL_SECTOR.items():
        v = w.get(f"ECO_AGGREGATE_{cell}", pd.Series(np.nan, index=w.index))
        v = v.fillna(w.get(f"ECO_SECTOR_{sector}", np.nan))
        v = v.fillna(w.get("ECO_SECTOR_TOTAL", np.nan)).fillna(w.get("ECO_AGGREGATE_TOTAL", np.nan))
        out[cell] = v
    c = pd.DataFrame(out)
    c.columns.name = "cell"
    c = c.stack(future_stack=True).rename("rate").reset_index()
    tot = c[c.sex == "SEX_T"].set_index(["ref_area", "cell", "time"])["rate"]
    c = c[c.sex.isin(SEXES)].set_index(["ref_area", "sex", "cell", "time"])["rate"]
    # Every (country, sex) with any data, both sexes filled from SEX_T.
    keys = c.index.to_frame(index=False)[["ref_area", "cell", "time"]]
    keys = pd.concat([keys, tot.index.to_frame(index=False)]).drop_duplicates()
    full = pd.concat([keys.assign(sex=s) for s in SEXES]).set_index(["ref_area", "sex", "cell", "time"]).index
    c = c.reindex(full)
    t = tot.reindex(pd.MultiIndex.from_arrays([full.get_level_values(i) for i in (0, 2, 3)]))
    c = c.fillna(pd.Series(t.to_numpy(), index=full)).dropna()
    return c, observed


def _spread(frame: pd.DataFrame) -> np.ndarray:
    """Within each (ref_area, sex, cell, time), informal share per group:
    logistic(logit(vulnerable) + k) with k chosen so the employment-weighted
    mean is the cell rate (working_hours/vulnerable_employment._solve_shift).
    `frame`: columns ref_area, sex, cell, time, group, vul, E, rate."""
    if str(REPO / "working_hours") not in sys.path:
        sys.path.insert(0, str(REPO / "working_hours"))
    from vulnerable_employment import _solve_shift
    f = frame.reset_index(drop=True)
    f["slot"] = f.groupby(["ref_area", "sex", "cell", "time"]).cumcount()
    key = ["ref_area", "sex", "cell", "time"]
    P = f.pivot_table(index=key, columns="slot", values="vul", aggfunc="first")
    W = f.pivot_table(index=key, columns="slot", values="E", aggfunc="first").reindex_like(P)
    T = f.groupby(key)["rate"].first().reindex(P.index).to_numpy()
    present = P.notna().to_numpy()
    p = np.clip(P.fillna(0.5).to_numpy(), _EPS, 1 - _EPS)
    w = np.where(present, W.fillna(0.0).to_numpy(), 0.0)
    # A cell without employment: equal weights, so every group gets the rate.
    w = np.where((w.sum(axis=1, keepdims=True) > 0), w, present.astype(float))
    lp = np.log(p / (1 - p))
    k = _solve_shift(lp, w, np.clip(T, 0, 1))
    v = 1 / (1 + np.exp(-(lp + k[:, None])))
    v[T <= 0] = 0.0
    v[T >= 1] = 1.0
    res = pd.DataFrame(v, index=P.index, columns=P.columns).stack().rename("share")
    look = f.set_index(key + ["slot"]).index
    return res.reindex(look).to_numpy()


def informal(vul_country: pd.DataFrame, risk_dir: Path, un: dict, years) -> pd.DataFrame:
    """Informal employment share by country, sex, activity group and year.
    `vul_country`: vulnerable share by ref_area, region, sex, group, time
    (columns share, E), every year available (the fit pools observed years)."""
    years = sorted(set(int(y) for y in years))
    rates, observed = informal_rates(risk_dir, sorted(set(years) | set(vul_country["time"])))
    v = vul_country.copy()
    v["cell"] = v["group"].map(CELL)
    v["unregion"] = v["ref_area"].map(un).fillna("World")
    v["income"] = v["ref_area"].map(income_group()).fillna("unknown")
    v["vw"] = v["share"] * v["E"]
    cell = v.groupby(["ref_area", "unregion", "income", "sex", "cell", "time"])[["vw", "E"]].sum().reset_index()
    cell["V"] = (cell["vw"] / cell["E"].where(cell["E"] > 0)).fillna(0.0)
    cell["rate"] = rates.reindex(pd.MultiIndex.from_frame(cell[["ref_area", "sex", "cell", "time"]])).to_numpy()

    # Countries without any SDG 8.3.1 data: informal = r * vulnerable within
    # [vulnerable, 1], with r the ratio of informal to vulnerable workers
    # summed over the observed country-years of the UN region, else the
    # income group, else the world (by sex and cell).
    seen = np.array([(a, t) in observed for a, t in zip(cell.ref_area, cell.time)], dtype=bool)
    obs = cell[seen & cell["rate"].notna().to_numpy()]
    obs = obs.assign(iw=obs["rate"] * obs["E"])
    fits = []
    for keys in (["unregion"], ["income"], []):
        g = obs.groupby(keys + ["sex", "cell"])[["iw", "vw"]].sum()
        g = g[g["vw"] > 0]
        fits.append((keys, (g["iw"] / g["vw"]).clip(lower=1.0)))
    have = cell["ref_area"].isin(set(rates.index.get_level_values("ref_area")))
    cell["informal_source"] = np.where(have, "ILO SDG 8.3.1", "")
    for keys, r in fits:
        miss = cell["informal_source"].eq("")
        if not miss.any():
            break
        idx = pd.MultiIndex.from_frame(cell.loc[miss, keys + ["sex", "cell"]])
        rr = r.reindex(idx).to_numpy()
        ok = ~np.isnan(rr)
        rows = cell.index[miss][ok]
        V = cell.loc[rows, "V"].to_numpy()
        cell.loc[rows, "rate"] = np.clip(rr[ok] * V, V, 1.0)
        cell.loc[rows, "informal_source"] = "predicted from vulnerable share: " + (
            "UN region" if keys == ["unregion"] else "income group" if keys == ["income"] else "world")
    cell["rate"] = cell["rate"].fillna(cell["V"])

    v = v[v["time"].isin(years)]
    v = v.merge(cell[["ref_area", "sex", "cell", "time", "rate", "informal_source"]],
                on=["ref_area", "sex", "cell", "time"], how="left")
    v = v.rename(columns={"share": "vul"})
    v["share"] = _spread(v)
    return v[["ref_area", "region", "sex", "group", "time", "share", "E", "informal_source"]]


def working_poverty(vul_country: pd.DataFrame, risk_dir: Path, un: dict, years) -> pd.DataFrame:
    d = pd.read_csv(risk_dir / "SDG_0111_SEX_AGE_RT_A.csv",
                    usecols=["ref_area", "sex", "classif1", "time", "obs_value"])
    d = d[(d["classif1"] == "AGE_YTHADULT_YGE15") & d["sex"].isin(SEXES)]
    rate = fill_years(d.groupby(["ref_area", "sex", "time"])["obs_value"].mean() / 100,
                      ["ref_area", "sex"], years)
    out = vul_country.copy()
    E_nat = out.groupby(["ref_area", "sex", "time"])["E"].transform("sum")
    V_nat = (out["share"] * out["E"]).groupby([out.ref_area, out.sex, out.time]).transform("sum") / E_nat
    out["rate"] = rate.reindex(pd.MultiIndex.from_frame(out[["ref_area", "sex", "time"]])).to_numpy()
    inc = income_group()
    out.loc[out["rate"].isna() & out["ref_area"].map(inc).eq("High income"), "rate"] = 0.0
    out["unregion"] = out["ref_area"].map(un).fillna("World")
    have = out.dropna(subset=["rate"])
    nat = have.groupby(["ref_area", "unregion", "sex", "time"]).agg(rate=("rate", "first"), E=("E", "sum")).reset_index()
    reg = nat.assign(w=nat.rate * nat.E).groupby(["unregion", "sex", "time"]).apply(
        lambda g: g.w.sum() / g.E.sum(), include_groups=False)
    miss = out["rate"].isna()
    out.loc[miss, "rate"] = [reg.get((r, s, t), 0.0) for r, s, t in
                             zip(out.unregion[miss], out.sex[miss], out.time[miss])]
    out["rate_source"] = np.where(out.ref_area.isin(set(d.ref_area)), "ILO",
                                  np.where(out.ref_area.map(inc).eq("High income"), "high income, 0", "UN region"))
    # Spread over groups by the vulnerable profile, keep the national rate.
    prof = np.where(V_nat > 0, out["share"] / V_nat, 1.0)
    s = (out["rate"] * prof).clip(upper=1.0)
    scale = (out["rate"] * E_nat) / (s * out["E"]).groupby([out.ref_area, out.sex, out.time]).transform("sum")
    out["share"] = (s * scale.where(np.isfinite(scale), 0.0)).clip(upper=1.0)
    return out.drop(columns=["rate", "unregion"])


def long_hours(vul_country: pd.DataFrame, risk_dir: Path, un: dict, years) -> pd.DataFrame:
    d = pd.read_csv(risk_dir / "EMP_TEMP_SEX_HOW_NB_A.csv",
                    usecols=["ref_area", "sex", "classif1", "time", "obs_value"])
    d = d[d["sex"].isin(SEXES) & d["classif1"].isin(["HOW_BANDS_HGE49", "HOW_BANDS_TOTAL"])]
    p = d.pivot_table(index=["ref_area", "sex", "time"], columns="classif1", values="obs_value", aggfunc="mean")
    p = p[(p["HOW_BANDS_TOTAL"] > 0)].dropna()
    rate = fill_years((p["HOW_BANDS_HGE49"] / p["HOW_BANDS_TOTAL"]).clip(0, 1), ["ref_area", "sex"], years)
    out = vul_country[["ref_area", "region", "sex", "group", "time", "E"]].copy()
    out["share"] = rate.reindex(pd.MultiIndex.from_frame(out[["ref_area", "sex", "time"]])).to_numpy()
    out["unregion"] = out["ref_area"].map(un).fillna("World")
    have = out.dropna(subset=["share"])
    w = have.assign(w=have.share * have.E)
    reg = w.groupby(["unregion", "sex", "time"])[["w", "E"]].sum()
    reg = reg["w"] / reg["E"]
    wld = w.groupby(["sex", "time"])[["w", "E"]].sum()
    wld = wld["w"] / wld["E"]
    miss = out["share"].isna()
    out.loc[miss, "share"] = [reg.get((r, s, t), np.nan) for r, s, t in
                              zip(out.unregion[miss], out.sex[miss], out.time[miss])]
    miss = out["share"].isna()
    out.loc[miss, "share"] = [wld.get((s, t), 0.0) for s, t in zip(out.sex[miss], out.time[miss])]
    return out.drop(columns=["unregion"])


def who_long_hours(employment: pd.DataFrame, risk_dir: Path, years) -> dict:
    """Deaths and DALYs (thousands) attributable to exposure to long working hours
    (ischaemic heart disease and stroke, both sexes, age 15+, point
    estimates), WHO/ILO joint estimates 2023, 183 countries, 2000, 2010 and
    2016. Per employed person, interpolated between those years and held
    outside them, times the country's employment; summed to (region, time).
    `employment`: common.employment_by_country."""
    import country_converter as coco
    f = Path(risk_dir).parent / "who_ilo_joint_estimates" / "WHO_ILO_BOD_2023_05.csv"
    w = pd.read_csv(f)
    w.columns = ["risk", "year", "region", "country", "sex", "age", "cause", "measure",
                 "estimate", "number", "rate"]
    w = w[(w.risk == "Exposure to long working hours") & (w.sex == "Both") & (w.estimate == "Point")
          & w.age.astype(str).str.endswith("15 years") & w.age.astype(str).str.startswith("≥")
          & w.country.notna() & (w.country != "NA")]
    names = sorted(w.country.unique())
    iso = dict(zip(names, coco.convert(names, to="ISO3", not_found=None)))
    w["ref_area"] = w.country.map(iso)
    E = employment.groupby(["ref_area", "region", "time"])["E"].sum().reset_index()
    out = {}
    for measure, label in (("Deaths", "deaths"), ("Disability-adjusted life years", "dalys")):
        m = w[w.measure == measure].groupby(["ref_area", "year"])["number"].sum()
        # To thousands. The file's column is headed "Number (for DALYs in
        # 1000s)" but holds plain counts for both measures: the 2016 country
        # rows sum to 744,924 deaths and 23.3 million DALYs, the published
        # scale (WHO/ILO 2021 monitoring report).
        m = m / 1000.0
        m.index.names = ["ref_area", "time"]
        e = E.set_index(["ref_area", "time"])["E"]
        per = (m / e.groupby(level=["ref_area", "time"]).sum().reindex(m.index)).dropna()
        per = fill_years(per, ["ref_area"], years)
        j = E[E.time.isin(years)].copy()
        j["v"] = per.reindex(pd.MultiIndex.from_frame(j[["ref_area", "time"]])).fillna(0.0).to_numpy() * j["E"]
        out[label] = j.groupby(["region", "time"])["v"].sum()
    return out
