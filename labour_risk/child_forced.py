"""Child labour and forced labour counts by axis region, broad sector and year.

Both are an explicitly modelled layer (Richard, 2026-11-10): the totals are
ILO's global estimates, the country and industry detail is allocation.

Child labour and hazardous child work (children 5-17, 1000 p)
--------------------------------------------------------------
- Country rate: ILOSTAT survey (`CLD_XCHL_` / `CLD_XHAZ_SEX_AGE_ECO_NB_A` over
  `CLD_TPOP_SEX_AGE_NB_A`, ages 5-17, 68 countries with a survey since 2001),
  interpolated between survey years and carried outside them; a country
  without a survey takes its SDG region's 2024 rate (ILO-UNICEF 2024 annex).
- Children 5-17: ILO's UN-based child population (`CLD_2POP`), which stops
  at age 14, so 15-17 is taken as 0.6 x the 10-14 band.
- Benchmarks: per SDG region the raw counts are scaled to the ILO-UNICEF
  regional totals of 2020 and 2024, and all regions together to the world
  totals of 2000, 2004, 2008, 2012 and 2016 (ILO 2017 report, Figure 2;
  those rounds have no SDG-region split); the scale factor is interpolated
  between benchmark years and held before 2000 and after 2024.
- Broad sector (agriculture, industry, services): the country's survey
  split, else its SDG region's (2024 report, Fig. 17, five regions), else the
  world split (2024 annex).

Forced labour (all ages, 1000 p)
--------------------------------
- ILO/Walk Free/IOM 2021 totals for the five ILO regions, spread over the
  region's countries in 2021 by the Walk Free Global Slavery Index 2023
  country estimates (people in modern slavery, which also counts forced
  marriage, used only as the key; its regional sums reproduce the ILO
  totals), countries outside the index by the region's index number per
  worker; other years move with each country's employment (a constant rate
  per worker).
- Broad sector, world composition applied to every region: forced labour
  exploitation by the sector shares of Fig. 8 ("other" spread pro rata),
  forced commercial sexual exploitation to services, state-imposed forced
  labour by the region's employment.

Within a region and broad sector, `common.allocate_counts` spreads the count
over industries by their low-skilled people.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from labour_risk.common import BROAD, GROUPS, REPO, SPAN

RISK = Path("d:/indecol/data/labour/data/risk")
ILOSTAT = RISK / "ilostat_2026-11-10"
CHILD = RISK / "ilo_unicef_child_labour_2024" / "derived"
FORCED = RISK / "ilo_forced_labour_2021" / "derived"
EARLY = RISK / "ilo_child_labour_2017_trends" / "derived" / "world_child_labour_2000_2016.csv"
SECTOR_CODE = {"ECO_SECTOR_AGR": "AGR", "ECO_SECTOR_IND": "IND", "ECO_SECTOR_SER": "SER"}
REPORT_SECTOR = {"Agriculture": "AGR", "Industry": "IND", "Services": "SER"}

#: ILO region of the workforce codes auxdata/countries_en.csv lacks (it has
#: Kosovo as KOS; the workforce uses XKX). Kept here rather than editing the
#: shared auxdata file; by geography, ILO's five-region split.
ILO_REGION_EXTRA = {
    "XKX": "Europe and Central Asia",
    "CHI": "Europe and Central Asia",  # Channel Islands
    "SJM": "Europe and Central Asia",  # Svalbard and Jan Mayen
    "VAT": "Europe and Central Asia",  # Holy See
    "BES": "Americas",                 # Bonaire, Sint Eustatius and Saba
    "CXR": "Asia and the Pacific",     # Christmas Island
    "CCK": "Asia and the Pacific",     # Cocos (Keeling) Islands
}

#: UN M49 sub-region (country_converter `UNregion`) -> SDG region.
SDG_REGION = {
    **{r: "Sub-Saharan Africa" for r in ("Eastern Africa", "Middle Africa", "Southern Africa", "Western Africa")},
    **{r: "Northern Africa and Western Asia" for r in ("Northern Africa", "Western Asia")},
    **{r: "Central and Southern Asia" for r in ("Central Asia", "Southern Asia")},
    **{r: "Eastern and South-Eastern Asia" for r in ("Eastern Asia", "South-eastern Asia", "South-Eastern Asia")},
    **{r: "Latin America and the Caribbean" for r in ("Caribbean", "Central America", "South America")},
    **{r: "Europe and Northern America" for r in ("Eastern Europe", "Northern Europe", "Southern Europe",
                                                  "Western Europe", "Northern America")},
    **{r: "Oceania" for r in ("Australia and New Zealand", "Melanesia", "Micronesia", "Polynesia")},
}


def _child_population(years) -> pd.Series:
    p = pd.read_csv(ILOSTAT / "CLD_2POP_SEX_AGE_NB_A.csv", usecols=["ref_area", "sex", "classif1", "time", "obs_value"])
    p = p[(p["sex"] == "SEX_T") & p["classif1"].isin(["AGE_CLDVERSION_Y05-09", "AGE_CLDVERSION_Y10-14"])]
    w = p.pivot_table(index=["ref_area", "time"], columns="classif1", values="obs_value")
    pop = w["AGE_CLDVERSION_Y05-09"] + 1.6 * w["AGE_CLDVERSION_Y10-14"]
    return pop[pop.index.get_level_values("time").isin(years)]


def _survey(indicator: str):
    c = pd.read_csv(ILOSTAT / f"{indicator}.csv", usecols=["ref_area", "sex", "classif1", "classif2", "time", "obs_value"])
    c = c[(c["sex"] == "SEX_T") & (c["classif1"] == "AGE_CLDVERSION_Y05-17")]
    tot = c[c["classif2"] == "ECO_SECTOR_TOTAL"].groupby(["ref_area", "time"])["obs_value"].mean()
    sec = c[c["classif2"].isin(SECTOR_CODE)].assign(b=lambda d: d["classif2"].map(SECTOR_CODE))
    sec = sec.pivot_table(index=["ref_area", "time"], columns="b", values="obs_value", aggfunc="mean")
    pop = pd.read_csv(ILOSTAT / "CLD_TPOP_SEX_AGE_NB_A.csv", usecols=["ref_area", "sex", "classif1", "time", "obs_value"])
    pop = pop[(pop["sex"] == "SEX_T") & (pop["classif1"] == "AGE_CLDVERSION_Y05-17")].groupby(["ref_area", "time"])["obs_value"].mean()
    rate = (tot / pop).dropna()
    rate = rate[(rate >= 0) & (rate < 1)]
    split = sec.div(sec.sum(axis=1), axis=0).dropna()
    split = split.groupby(level="ref_area").mean()  # pooled over survey years
    return rate, split


def _interp(rate: pd.Series, years) -> pd.Series:
    out = {}
    for a, g in rate.groupby(level="ref_area"):
        g = g.droplevel("ref_area")
        full = g.reindex(sorted(set(g.index) | set(years))).interpolate(
            method="index", limit_area="inside").ffill().bfill()
        for y in years:
            out[(a, y)] = full.loc[y]
    s = pd.Series(out)
    s.index.names = ["ref_area", "time"]
    return s


def child_labour(indicator: str, years, region_of: dict, un: dict) -> pd.Series:
    """Counts (1000 children) by (region, broad, time). `indicator` is
    'child_labour' or 'hazardous_work'."""
    ilo_id = {"child_labour": "CLD_XCHL_SEX_AGE_ECO_NB_A", "hazardous_work": "CLD_XHAZ_SEX_AGE_ECO_NB_A"}[indicator]
    rate, split = _survey(ilo_id)
    reg = pd.read_csv(CHILD / "child_labour_by_region_sex_age.csv")
    reg = reg[(reg.indicator == indicator) & (reg.region_classification == "SDG")
              & (reg.sex == "total") & (reg.age_group == "5-17")].set_index("region")
    trend = pd.read_csv(CHILD / "child_labour_trends_2016_2020_2024.csv")
    trend = trend[trend.indicator == indicator]
    w16 = trend[(trend.breakdown == "World") & (trend.year == 2016)]["number_thousands"]
    world_bench = {2016: float(w16.iloc[0])} if len(w16) else {}
    early = pd.read_csv(EARLY)
    early = early[early.indicator == indicator]
    world_bench.update({int(y): n / 1000 for y, n in zip(early.year, early.number) if y < 2016})
    sdg_bench = trend[trend.breakdown == "SDG"].dropna(subset=["number_thousands"])

    # Compute over the full span and every benchmark year, keep the requested
    # years at the end: the scale of a year must not depend on which other
    # years were asked for.
    want = sorted(set(int(y) for y in years))
    years = sorted(set(want) | set(SPAN) | set(world_bench) | set(int(y) for y in sdg_bench.year))
    rate = _interp(rate, years)
    pop = _child_population(years)
    df = pop.rename("pop").reset_index()
    df["sdg"] = df["ref_area"].map(lambda a: SDG_REGION.get(un.get(a, ""), None))
    df = df.dropna(subset=["sdg"])
    df["rate"] = rate.reindex(pd.MultiIndex.from_frame(df[["ref_area", "time"]])).to_numpy()
    df["survey"] = df["rate"].notna()
    df.loc[~df["survey"], "rate"] = df.loc[~df["survey"], "sdg"].map(reg["prevalence_pct_of_children"] / 100)
    df["raw"] = df["rate"].fillna(0.0) * df["pop"]

    # Benchmark scale per SDG region and year.
    raw_r = df.groupby(["sdg", "time"])["raw"].sum()
    scale = {}
    for sdg in df["sdg"].unique():
        pts = {}
        b = sdg_bench[sdg_bench.category == sdg]
        for _, row in b.iterrows():
            if (sdg, row.year) in raw_r.index and raw_r[(sdg, row.year)] > 0:
                pts[int(row.year)] = row.number_thousands / raw_r[(sdg, row.year)]
        # World benchmarks for the rounds without a regional split.
        for yb, W in world_bench.items():
            if yb not in pts:
                wraw = df[df.time == yb]["raw"].sum()
                if wraw > 0:
                    pts[yb] = W / wraw
        if not pts:
            for y in years:
                scale[(sdg, y)] = 1.0
            continue
        s = pd.Series(pts, dtype=float).sort_index()
        full = s.reindex(sorted(set(s.index) | set(years))).interpolate(
            method="index", limit_area="inside").ffill().bfill()
        for y in years:
            scale[(sdg, y)] = full.loc[y]
    df["count"] = df["raw"] * [scale[(s, t)] for s, t in zip(df.sdg, df.time)]

    # Broad sector split: country survey, SDG region, world.
    fig17 = pd.read_csv(CHILD / "child_labour_sector_share_by_sdg_region.csv")
    fig17 = fig17.assign(b=fig17.sector.map(REPORT_SECTOR)).pivot_table(
        index="region", columns="b", values="pct_of_children_in_child_labour")
    fig17 = fig17.div(fig17.sum(axis=1), axis=0)
    world = pd.read_csv(CHILD / "child_labour_by_sector_sex_age.csv")
    world = world[(world.indicator == indicator) & (world.sex == "total") & (world.age_group == "5-17")]
    world = world.assign(b=world.sector.map(REPORT_SECTOR)).set_index("b")["pct_of_children_in_indicator"]
    world = world / world.sum()
    rows = []
    for a, sdg, t, n in zip(df.ref_area, df.sdg, df.time, df["count"]):
        if a in split.index:
            sh = split.loc[a]
        elif indicator == "child_labour" and sdg in fig17.index:
            sh = fig17.loc[sdg]
        else:
            sh = world
        region = region_of.get(a)
        if region is None:
            continue
        for b in ("AGR", "IND", "SER"):
            rows.append((region, b, t, n * float(sh.get(b, 0.0))))
    out = pd.DataFrame(rows, columns=["region", "broad", "time", "v"])
    out = out[out.time.isin(want)]
    return out.groupby(["region", "broad", "time"])["v"].sum()


def forced_labour(employment: pd.DataFrame, years, region_of: dict) -> pd.Series:
    """Counts (1000 p) by (region, broad, time). `employment`: E by ref_area,
    region, sex, group, time (common.employment_by_country)."""
    tot = pd.read_csv(FORCED / "forced_labour_by_region.csv")
    tot = tot[(tot.category == "total_forced_labour") & (tot.region != "World")].set_index("region")["number_thousands"]
    cat = pd.read_csv(FORCED / "modern_slavery_by_category_sex_age_income.csv")
    cat = cat[cat.breakdown == "World"].set_index("category")["number_thousands"]
    fle = cat["privately_imposed_forced_labour_excl_FCSE"]
    fcse = cat["forced_commercial_sexual_exploitation_FCSE"]
    total_world = tot.sum()
    state = total_world - fle - fcse
    fig8 = pd.read_csv(FORCED / "forced_labour_exploitation_adults_by_sector_sex.csv")
    fig8 = fig8[fig8.sex == "total"].set_index("sector")["pct_of_adults_in_FLE"]
    to_broad = {"Agriculture": "AGR", "Manufacturing": "IND", "Construction": "IND",
                "Mining and quarrying": "IND", "Services excluding domestic work": "SER",
                "Domestic work": "SER"}
    named = fig8[[s for s in fig8.index if s in to_broad]]
    fle_b = named.groupby(named.index.map(to_broad)).sum()
    fle_b = fle_b / fle_b.sum()

    ilo_region = pd.read_csv(REPO / "auxdata" / "countries_en.csv", encoding="utf-8-sig")
    ilo_region = {**dict(zip(ilo_region["ISO3 Code"], ilo_region["ILO Region"])), **ILO_REGION_EXTRA}
    e = employment.groupby(["ref_area", "group", "time"])["E"].sum().reset_index()
    e["broad"] = e["group"].map(BROAD)
    e["ilo"] = e["ref_area"].map(ilo_region)
    e = e.dropna(subset=["ilo"])
    nat = e.groupby(["ref_area", "ilo", "time"])["E"].sum().reset_index()
    base = nat[nat.time == 2021].set_index("ref_area")
    # Country key in 2021: the Global Slavery Index number of people in
    # modern slavery where the country is covered (160 countries), else the
    # region's GSI number per worker times the country's employment.
    gsi = gsi_numbers()
    base["key"] = gsi.reindex(base.index)
    cov = base.dropna(subset=["key"])
    per_worker = cov.groupby("ilo")["key"].sum() / cov.groupby("ilo")["E"].sum()
    miss = base["key"].isna()
    base.loc[miss, "key"] = base.loc[miss, "E"] * base.loc[miss, "ilo"].map(per_worker).fillna(0.0)
    base_r = base.groupby("ilo")["key"].sum()
    rows = []
    for ilo, g in e.groupby("ilo"):
        if ilo not in tot.index:
            continue
        T = tot[ilo]
        eb = g[g.time == 2021].groupby("broad")["E"].sum()
        eb = eb / eb.sum()
        comp = (fle * fle_b.reindex(["AGR", "IND", "SER"]).fillna(0)
                + fcse * pd.Series({"AGR": 0.0, "IND": 0.0, "SER": 1.0})
                + state * eb.reindex(["AGR", "IND", "SER"]).fillna(0)) / total_world
        comp = comp / comp.sum()
        for (a, t), E_ct in g.groupby(["ref_area", "time"])["E"].sum().items():
            if t not in years or a not in base.index:
                continue
            # 2021 share of the region by the key, moved with employment.
            n = T * base.at[a, "key"] / base_r[ilo] * E_ct / base.at[a, "E"]
            region = region_of.get(a)
            if region is None:
                continue
            for b, sh in comp.items():
                rows.append((region, b, t, n * sh))
    out = pd.DataFrame(rows, columns=["region", "broad", "time", "v"])
    return out.groupby(["region", "broad", "time"])["v"].sum()


def gsi_numbers() -> pd.Series:
    """Walk Free Global Slavery Index 2023: estimated number of people in
    modern slavery (forced labour and forced marriage, 2021) by ISO3."""
    import country_converter as coco
    f = RISK / "walkfree_gsi_2023" / "2023-Global-Slavery-Index-Data.xlsx"
    if not f.exists():
        return pd.Series(dtype=float)
    g = pd.read_excel(f, "GSI 2023 summary data", header=2).iloc[:, :5]
    g.columns = ["country", "population", "region", "prevalence", "number"]
    g = g.dropna(subset=["country", "number"])
    g["iso"] = coco.convert(list(g["country"]), to="ISO3", not_found=None)
    return g.dropna(subset=["iso"]).groupby("iso")["number"].sum()


def region_counts(workforce: pd.DataFrame, years, un: dict) -> dict:
    from labour_risk.common import employment_by_country
    emp = employment_by_country(workforce)
    region_of = emp.drop_duplicates("ref_area").set_index("ref_area")["region"].to_dict()
    return {
        "Child labour": child_labour("child_labour", years, region_of, un),
        "Child labour: hazardous work": child_labour("hazardous_work", years, region_of, un),
        "Forced labour": forced_labour(emp, years, region_of),
    }
