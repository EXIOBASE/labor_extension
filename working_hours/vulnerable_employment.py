"""Vulnerable employment share by region, sex, ILO section and year.

Vulnerable employment is own-account workers plus contributing family
workers (ICSE-93 groups 3 and 5), the ILO definition and the one behind the
two `Vulnerable employment` stressors EXIOBASE 3.8.2 shipped
(docs/improvement_plan_2026-11-06.md, Phase 2).

Sources, both ILOSTAT:

- `EMP_2EMP_SEX_STE_NB_A`, modelled employment by sex and status: the
  national share V(country, sex, year) for every country, no activity detail.
- `EMP_TEMP_SEX_STE_ECO_NB_A`, survey employment by sex, status and ISIC4
  section: the section profile. Pooled over all survey years of a country,
  since few countries report every year (113 in 2019, under 13 a year
  before 2008).

Method, for each country, sex and year:

1. Profile p_g: the pooled survey share of vulnerable workers in each of the
   14 ILO section groups g (A, B, C, DE, F, G, HJ, I, K, LMN, O, P, Q, RSTU)
   of the country; a group the country's survey does not cover takes the
   pooled profile of its UN region, then of the world.
2. Shift every group by the same amount on the logit scale until the
   employment-weighted mean equals V: v_g = logistic(logit(p_g) + k), with
   sum_g E_g v_g = V sum_g E_g. The shares stay inside (0, 1) and keep the
   survey's ranking of sections, and the national total is ILO's.
3. A region's share is the employment-weighted mean over its countries.
   A country without a modelled V (the hand-compiled supplementary entities)
   takes its UN region's employment-weighted V, then the world's.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

STATUS_MODELLED = "EMP_2EMP_SEX_STE_NB_A.csv"
STATUS_BY_ACTIVITY = "EMP_TEMP_SEX_STE_ECO_NB_A.csv"

VULNERABLE = ("STE_ICSE93_3", "STE_ICSE93_5")
TOTAL = "STE_ICSE93_TOTAL"
SEXES = ("SEX_M", "SEX_F")

#: ISIC4 section letter -> the ECO_DETAILS group the labour account uses.
SECTION_GROUP = {
    "A": "A", "B": "B", "C": "C", "D": "DE", "E": "DE", "F": "F", "G": "G",
    "H": "HJ", "J": "HJ", "I": "I", "K": "K", "L": "LMN", "M": "LMN",
    "N": "LMN", "O": "O", "P": "P", "Q": "Q", "R": "RSTU", "S": "RSTU",
    "T": "RSTU", "U": "RSTU",
}
GROUPS = [f"ECO_DETAILS_{g}" for g in
          ("A", "B", "C", "DE", "F", "G", "HJ", "I", "K", "LMN", "O", "P", "Q", "RSTU")]

_EPS = 1e-4


def _un_region(iso3):
    import country_converter as coco
    cc = coco.CountryConverter(include_obsolete=True)
    out = cc.convert(names=list(iso3), src="ISO3", to="UNregion", not_found=None)
    out = out if isinstance(out, list) else [out]
    return dict(zip(iso3, ["World" if o in (None, "not found") else o for o in out]))


def national_shares(modelled: pd.DataFrame) -> pd.Series:
    """V(country, sex, year) from the modelled status table."""
    m = modelled[modelled["sex"].isin(SEXES)
                 & modelled["classif1"].isin(VULNERABLE + (TOTAL,))]
    m = m.pivot_table(index=["ref_area", "sex", "time"], columns="classif1",
                      values="obs_value", aggfunc="sum")
    m = m[m[TOTAL] > 0]
    return (m[list(VULNERABLE)].sum(axis=1) / m[TOTAL]).rename("V")


def section_profiles(by_activity: pd.DataFrame, un_region: dict) -> pd.DataFrame:
    """Pooled vulnerable share p(country, sex, group), with region and world
    fallbacks filled in; index (ref_area, sex), one column per group."""
    t = by_activity[by_activity["sex"].isin(SEXES)
                    & by_activity["classif2"].str.startswith("ECO_ISIC4_")
                    & by_activity["classif1"].str.startswith("STE_ICSE93_")].copy()
    t["group"] = t["classif2"].str.removeprefix("ECO_ISIC4_").map(SECTION_GROUP)
    t = t.dropna(subset=["group"])
    t["group"] = "ECO_DETAILS_" + t["group"]
    t["kind"] = np.where(t["classif1"] == TOTAL, "tot",
                         np.where(t["classif1"].isin(VULNERABLE), "vul", "other"))
    # Pool over the survey cells (country, sex, year, section). A cell that
    # reports no ICSE 3 or 5 count is a zero if its other statuses (1, 2, 4,
    # 6) add up to its total, as in 4,535 of 5,139 such cells (2026-11-10;
    # e.g. employees only in public administration, or domestic workers),
    # and is left out otherwise: the gap may be suppressed vulnerable
    # workers, and counting it as none would pull the section down.
    cell = t.pivot_table(index=["ref_area", "sex", "time", "classif2", "group"],
                         columns="kind", values="obs_value", aggfunc="sum")
    cell = cell.reindex(columns=["vul", "tot", "other"])
    cell = cell[cell["tot"] > 0]
    closed = (cell["tot"] - cell["other"]).abs() <= 0.005 + 1e-6 * cell["tot"]
    cell["vul"] = cell["vul"].where(cell["vul"].notna() | ~closed, 0.0)
    cell = cell.dropna(subset=["vul"])
    pooled = cell.groupby(level=["ref_area", "sex", "group"])[["vul", "tot"]].sum()
    pooled = pooled[pooled["tot"] > 0]

    def shares(frame, keys):
        g = frame.groupby(keys)[["vul", "tot"]].sum()
        return (g["vul"] / g["tot"]).clip(0, 1)

    country = shares(pooled, ["ref_area", "sex", "group"]).unstack("group")
    pooled = pooled.reset_index()
    pooled["unregion"] = pooled["ref_area"].map(un_region).fillna("World")
    region = shares(pooled, ["unregion", "sex", "group"]).unstack("group")
    world = shares(pooled, ["sex", "group"]).unstack("group")
    return country.reindex(columns=GROUPS), region.reindex(columns=GROUPS), world.reindex(columns=GROUPS)


def _profile_for(iso3, sex, country, region, world, un_region):
    p = (country.loc[(iso3, sex)] if (iso3, sex) in country.index
         else pd.Series(np.nan, index=GROUPS))
    reg = un_region.get(iso3, "World")
    if (reg, sex) in region.index:
        p = p.fillna(region.loc[(reg, sex)])
    return p.fillna(world.loc[sex]).clip(_EPS, 1 - _EPS)


def _solve_shift(logit_p, weights, target, iters=60):
    """k with sum(w * logistic(logit_p + k)) / sum(w) = target, row-wise."""
    lo = np.full(len(target), -30.0)
    hi = np.full(len(target), 30.0)
    wsum = weights.sum(axis=1)
    for _ in range(iters):
        mid = (lo + hi) / 2
        mean = (weights / (1 + np.exp(-(logit_p + mid[:, None])))).sum(axis=1) / wsum
        too_high = mean > target
        hi = np.where(too_high, mid, hi)
        lo = np.where(too_high, lo, mid)
    return (lo + hi) / 2


def country_shares(employment: pd.DataFrame, V: pd.Series, profiles, un_region) -> pd.DataFrame:
    """v(country, sex, group, year), long, with the employment E alongside.

    `employment`: ref_area, sex, classif1 (ECO_DETAILS_*), time, obs_value.
    """
    country, region, world = profiles
    E = employment[employment["sex"].isin(SEXES)
                   & employment["classif1"].isin(GROUPS)]
    E = E.pivot_table(index=["ref_area", "sex", "time"], columns="classif1",
                      values="obs_value", aggfunc="sum").reindex(columns=GROUPS).fillna(0.0)
    E = E[E.sum(axis=1) > 0]

    # V for every (country, sex, year) in E; missing -> UN region, then world,
    # employment-weighted over the countries that have it.
    idx = E.index.to_frame(index=False)
    idx["V"] = V.reindex(E.index).to_numpy()
    idx["Etot"] = E.sum(axis=1).to_numpy()
    idx["unregion"] = idx["ref_area"].map(un_region).fillna("World")
    have = idx.dropna(subset=["V"])
    reg_v = (have.assign(w=have.V * have.Etot).groupby(["unregion", "sex", "time"])
             .apply(lambda g: g.w.sum() / g.Etot.sum(), include_groups=False))
    wld_v = (have.assign(w=have.V * have.Etot).groupby(["sex", "time"])
             .apply(lambda g: g.w.sum() / g.Etot.sum(), include_groups=False))
    miss = idx["V"].isna()
    idx.loc[miss, "V"] = [reg_v.get((r, s, t), np.nan) for r, s, t in
                          idx.loc[miss, ["unregion", "sex", "time"]].itertuples(index=False)]
    miss = idx["V"].isna()
    idx.loc[miss, "V"] = [wld_v.get((s, t), np.nan) for s, t in
                          idx.loc[miss, ["sex", "time"]].itertuples(index=False)]
    miss = idx["V"].isna()
    if miss.any():
        print(f"[WARN] vulnerable employment: {int(miss.sum())} country-sex-years with "
              f"people but no national, regional or world share set to 0, e.g. "
              f"{list(idx.loc[miss, ['ref_area', 'sex', 'time']].head(5).itertuples(index=False, name=None))}")
        idx.loc[miss, "V"] = 0.0
    target = idx["V"].clip(0, 1 - _EPS).to_numpy()

    prof = {}
    for iso3, sex in set(zip(idx["ref_area"], idx["sex"])):
        prof[(iso3, sex)] = _profile_for(iso3, sex, country, region, world, un_region).to_numpy()
    P = np.vstack([prof[(a, s)] for a, s in zip(idx["ref_area"], idx["sex"])])
    logit_p = np.log(P / (1 - P))
    W = E.to_numpy()
    k = _solve_shift(logit_p, W, target)
    v = 1 / (1 + np.exp(-(logit_p + k[:, None])))
    v[target <= 0] = 0.0

    out = pd.DataFrame(v, index=E.index, columns=GROUPS).stack().rename("share").to_frame()
    out["E"] = E.stack().to_numpy()
    return out.reset_index().rename(columns={"level_3": "classif1"})


def country_table(employment: pd.DataFrame, data_dir: Path) -> pd.DataFrame:
    """Vulnerable share by country: columns ref_area, region, sex, classif1
    (the activity group), time, share, E. Same inputs as `region_shares`."""
    data_dir = Path(data_dir)
    modelled = pd.read_csv(data_dir / STATUS_MODELLED,
                           usecols=["ref_area", "sex", "classif1", "time", "obs_value"])
    by_activity = pd.read_csv(data_dir / STATUS_BY_ACTIVITY,
                              usecols=["ref_area", "sex", "classif1", "classif2", "time", "obs_value"])
    emp = employment[employment["EXIO3"].notna()
                     & ~employment["EXIO3"].isin(["not found", ""])]
    countries = sorted(set(emp["ref_area"]) | set(by_activity["ref_area"]))
    un_region = _un_region(countries)
    V = national_shares(modelled)
    profiles = section_profiles(by_activity, un_region)
    cs = country_shares(emp[["ref_area", "sex", "classif1", "time", "obs_value"]],
                        V, profiles, un_region)
    region_of = emp.drop_duplicates("ref_area").set_index("ref_area")["EXIO3"]
    cs["region"] = cs["ref_area"].map(region_of)
    return cs


def region_shares(employment: pd.DataFrame, data_dir: Path) -> pd.DataFrame:
    """Share of vulnerable employment by axis region, sex, group and year.

    `employment` is the workforce table (workforce.csv): ref_area, EXIO3 (the
    axis region), sex, classif1, time, obs_value. Rows whose region is
    `not found` or blank (ILO aggregates) are ignored.
    """
    cs = country_table(employment, data_dir)
    cs["vul"] = cs["share"] * cs["E"]
    g = cs.groupby(["region", "sex", "classif1", "time"])[["vul", "E"]].sum()
    g["share"] = np.where(g["E"] > 0, g["vul"] / g["E"].where(g["E"] > 0, 1), 0.0)
    return g.reset_index()[["region", "sex", "classif1", "time", "share", "vul", "E"]]
