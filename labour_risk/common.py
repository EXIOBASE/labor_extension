"""Shared plumbing for the labour-risk account (docs/improvement_plan_2026-11-06.md, Phase 4).

Every indicator is built the same way:

1. a value per country (ISO3), sex, ILO activity group and year, either a
   share of that country's employment in the group or a count;
2. aggregated to the axis region with the ILO employment of each country as
   weight (shares) or summed (counts);
3. applied to the labour account's people (and hours) of each EXIOBASE
   industry in that region, through the industry's ILO activity group.

The labour account's people per region, industry and sex come from the
handoff workbook (`final_labor_SUTs_*.xlsx`), so the labour-risk rows always
sum consistently with the published labour rows.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
SEXES = {"SEX_M": "male", "SEX_F": "female"}
GROUPS = [f"ECO_DETAILS_{g}" for g in
          ("A", "B", "C", "DE", "F", "G", "HJ", "I", "K", "LMN", "O", "P", "Q", "RSTU")]
#: ISIC4 section letter -> labour-account activity group.
SECTION_GROUP = {
    "A": "A", "B": "B", "C": "C", "D": "DE", "E": "DE", "F": "F", "G": "G",
    "H": "HJ", "J": "HJ", "I": "I", "K": "K", "L": "LMN", "M": "LMN",
    "N": "LMN", "O": "O", "P": "P", "Q": "Q", "R": "RSTU", "S": "RSTU",
    "T": "RSTU", "U": "RSTU",
}
#: Broad sector (ILO ECO_SECTOR) of each activity group.
BROAD = {g: ("AGR" if g == "ECO_DETAILS_A" else
             "IND" if g in ("ECO_DETAILS_B", "ECO_DETAILS_C", "ECO_DETAILS_DE", "ECO_DETAILS_F")
             else "SER") for g in GROUPS}

PEOPLE = {sex: [f"Employment people: {k}-skilled {sex}" for k in ("Low", "Medium", "High")]
          for sex in ("male", "female")}
HOURS = {sex: [f"Employment hours: {k}-skilled {sex}" for k in ("Low", "Medium", "High")]
         for sex in ("male", "female")}
LOW_PEOPLE = ["Employment people: Low-skilled male", "Employment people: Low-skilled female"]


def un_region(iso3) -> dict:
    import country_converter as coco
    cc = coco.CountryConverter(include_obsolete=True)
    iso3 = list(iso3)
    out = cc.convert(names=iso3, src="ISO3", to="UNregion", not_found=None)
    out = out if isinstance(out, list) else [out]
    return dict(zip(iso3, ["World" if o in (None, "not found") else o for o in out]))


def income_group() -> dict:
    t = pd.read_csv(REPO / "auxdata" / "countries_en.csv", encoding="utf-8-sig")
    return dict(zip(t["ISO3 Code"], t["World Bank Income Group"]))


def sector_groups() -> dict:
    """EXIOBASE industry name -> labour-account activity group."""
    c = pd.read_excel(REPO / "auxdata" / "Exiobase_ISIC_Rev-4.xlsx")
    c = c.dropna(subset=["Name", "ISIC REV 4_ILO_Alteryx"])
    return dict(zip(c["Name"], c["ISIC REV 4_ILO_Alteryx"].astype(str).str.strip()))


def read_account(workbook: Path, year: int) -> pd.DataFrame:
    """One year of the labour handoff workbook as rows (region, sector) with
    the stressors as columns. e3 sheets are wide (stressor rows, (region,
    sector) columns), other axes long."""
    raw = pd.read_excel(workbook, sheet_name=str(year), header=None, nrows=3)
    if str(raw.iloc[0, 0]).strip().lower() in ("region", "nan") and str(raw.iloc[1, 0]).strip().lower() == "sector":
        d = pd.read_excel(workbook, sheet_name=str(year), header=[0, 1], index_col=0)
        d = d.T
        d.index = d.index.set_names(["region", "sector"])
    else:
        d = pd.read_excel(workbook, sheet_name=str(year), index_col=[0, 1])
        d.index = d.index.set_names(["region", "sector"])
    return d.astype(float)


def employment_by_country(workforce: pd.DataFrame) -> pd.DataFrame:
    """ILO employment E by ref_area, region, sex, group, time from workforce.csv
    (country rows only)."""
    w = workforce[workforce["sex"].isin(SEXES) & workforce["classif1"].isin(GROUPS)
                  & workforce["EXIO3"].notna() & (workforce["EXIO3"] != "not found")]
    return (w.groupby(["ref_area", "EXIO3", "sex", "classif1", "time"], as_index=False)["obs_value"]
            .sum().rename(columns={"EXIO3": "region", "classif1": "group", "obs_value": "E"}))


def fill_years(series: pd.Series, keys: list, years) -> pd.Series:
    """Per key, linear interpolation between observed years and the nearest
    observation carried outside them. Index: keys + ['time']."""
    years = sorted(set(years))
    out = []
    for k, g in series.groupby(level=keys):
        g = g.droplevel(keys)
        full = g.reindex(sorted(set(g.index) | set(years))).interpolate(
            method="index", limit_area="inside").ffill().bfill().loc[years]
        k = k if isinstance(k, tuple) else (k,)
        full.index = pd.MultiIndex.from_tuples([k + (y,) for y in years], names=keys + ["time"])
        out.append(full)
    return pd.concat(out) if out else series.iloc[0:0]


def region_share(country: pd.DataFrame, value: str = "share") -> pd.Series:
    """Employment-weighted mean of `value` by (region, sex, group, time)."""
    c = country.assign(_w=country[value] * country["E"])
    g = c.groupby(["region", "sex", "group", "time"])[["_w", "E"]].sum()
    return (g["_w"] / g["E"].where(g["E"] > 0)).fillna(0.0)


def apply_shares(account: pd.DataFrame, shares: pd.Series, year: int, sector_group: dict,
                 hours: bool = True) -> tuple[pd.Series, pd.Series | None]:
    """People (and hours) of each (region, sector) times the share of its
    region, sex and activity group."""
    regions = account.index.get_level_values("region")
    groups = account.index.get_level_values("sector").map(sector_group)
    people = pd.Series(0.0, index=account.index)
    worked = pd.Series(0.0, index=account.index) if hours else None
    for sex_code, sex in SEXES.items():
        keys = pd.MultiIndex.from_arrays([regions, [sex_code] * len(account), groups,
                                          [year] * len(account)])
        s = shares.reindex(keys).fillna(0.0).to_numpy()
        people += account[PEOPLE[sex]].sum(axis=1).to_numpy() * s
        if hours:
            worked += account[HOURS[sex]].sum(axis=1).to_numpy() * s
    return people, worked


def allocate_counts(account: pd.DataFrame, counts: pd.Series, year: int, sector_group: dict,
                    key: str = "broad") -> pd.Series:
    """Spread counts by (region, broad sector or group, time) over the region's
    industries in proportion to their low-skilled people."""
    low = account[LOW_PEOPLE].sum(axis=1)
    grp = account.index.get_level_values("sector").map(sector_group)
    cell = grp.map(BROAD) if key == "broad" else grp
    frame = pd.DataFrame({"region": np.asarray(account.index.get_level_values("region")),
                          "cell": np.asarray(cell), "low": low.to_numpy()})
    tot = frame.groupby(["region", "cell"])["low"].transform("sum")
    c = counts.xs(year, level="time") if "time" in counts.index.names else counts
    target = np.array([c.get((r, k), 0.0) for r, k in zip(frame.region, frame.cell)])
    out = np.where(tot > 0, target * frame["low"] / tot.where(tot > 0, 1.0), 0.0)
    return pd.Series(out, index=account.index)
