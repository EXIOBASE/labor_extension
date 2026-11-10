"""Labour-risk indicators built from ILOSTAT (docs/improvement_plan_2026-11-06.md, Phase 4).

Each function returns country-level values with the ILO employment E
alongside (columns ref_area, region, sex, group, time, share, E), ready for
`common.region_share`.

- `informal`: informal employment share. Survey data (`EMP_NIFL_SEX_ECO_NB_A`
  over `EMP_TEMP_SEX_ECO_NB_A`, ISIC4 sections) cover 122 countries around
  2019, 55% of world employment, without China or the US, and few years per
  country. The ratio of the informal share to the vulnerable share of the
  same country, sex and group (pooled over the survey years) is stable where
  both are known, so informal = min(1, k * vulnerable), with k from the
  country, else its UN region, else the world; the year profile then comes
  from ILO's complete modelled status series.
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

from pathlib import Path

import numpy as np
import pandas as pd

from labour_risk.common import GROUPS, SECTION_GROUP, SEXES, fill_years, income_group, un_region


def _survey_by_group(path: Path) -> pd.DataFrame:
    d = pd.read_csv(path, usecols=["ref_area", "sex", "classif1", "time", "obs_value"], low_memory=False)
    d = d[d["sex"].isin(SEXES) & d["classif1"].str.startswith("ECO_ISIC4_")]
    d["group"] = d["classif1"].str.removeprefix("ECO_ISIC4_").map(SECTION_GROUP)
    d = d.dropna(subset=["group"])
    d["group"] = "ECO_DETAILS_" + d["group"]
    return d.groupby(["ref_area", "sex", "group", "time"])["obs_value"].sum()


def informal(vul_country: pd.DataFrame, risk_dir: Path, un: dict) -> pd.DataFrame:
    """`vul_country`: vulnerable share by ref_area, region, sex, group, time
    (columns share, E)."""
    inf = _survey_by_group(risk_dir / "EMP_NIFL_SEX_ECO_NB_A.csv")
    tot = _survey_by_group(risk_dir / "EMP_TEMP_SEX_ECO_NB_A.csv")
    j = pd.DataFrame({"inf": inf, "tot": tot}).dropna()
    j = j[j["tot"] > 0]
    v = vul_country.set_index(["ref_area", "sex", "group", "time"])["share"]
    j["vul"] = v.reindex(j.index).to_numpy()
    j = j.dropna()
    j = j[j["vul"] > 0].reset_index()
    j["unregion"] = j["ref_area"].map(un).fillna("World")
    # k = pooled informal share / mean vulnerable share over the same years.
    def k_of(frame, keys):
        g = frame.groupby(keys).agg(inf=("inf", "sum"), tot=("tot", "sum"), vul=("vul", "mean"))
        return ((g["inf"] / g["tot"]) / g["vul"]).clip(lower=0)
    k_c = k_of(j, ["ref_area", "sex", "group"])
    k_r = k_of(j, ["unregion", "sex", "group"])
    k_w = k_of(j, ["sex", "group"])
    out = vul_country.copy()
    out["unregion"] = out["ref_area"].map(un).fillna("World")
    k = pd.Series([k_c.get((a, s, g), np.nan) for a, s, g in zip(out.ref_area, out.sex, out.group)],
                  index=out.index)
    miss = k.isna()
    k[miss] = [k_r.get((r, s, g), np.nan) for r, s, g in
               zip(out.unregion[miss], out.sex[miss], out.group[miss])]
    miss = k.isna()
    k[miss] = [k_w.get((s, g), 1.0) for s, g in zip(out.sex[miss], out.group[miss])]
    out["k"] = k
    out["k_source"] = np.where(out.ref_area.isin(set(j.ref_area)), "country", "region/world")
    out["share"] = (out["k"] * out["share"]).clip(upper=1.0)
    return out.drop(columns=["unregion"])


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
