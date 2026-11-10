"""People by skill from ILO occupation counts (docs/improvement_plan_2026-11-06.md, Phase 3).

Until 2026-11 the salary split gave each skill level a share of an
industry's *people* equal to its share of the industry's *wage bill* (the SUT
rows w03.a/b/c), which counts too many high-skilled and too few low-skilled
people, and applied the ILO section's sex ratio to every skill level alike.
Both reference methods (Simas, Wood, Hertwich 2015; Wood et al. 2019, JRC
report for the OECD ICIO, section 2.2) count people by skill from occupation
data and use compensation only to spread a sector over its industries.

This module rebalances the salary split's output, per region, year and sex:

- row margins: the people of each industry and sex, as the salary split
  already has them (ILO section totals spread by compensation of employees,
  section sex shares), unchanged;
- column margins: people by skill from ILO's modelled employment by sex and
  ISCO-08 major group (`EMP_2EMP_SEX_OCU_NB_A`), on the ISCO-08 skill
  levels: groups 1-3 high, 4-8 medium, 9 low; scaled to the region's people
  of that sex;
- structure inside each industry: the SUT wage bill by skill (w03.a/b/c),
  balanced to both margins by RAS. Dividing the wage bill by a national
  relative wage per skill level, which would turn it into a people prior,
  is a column scaling and RAS absorbs it, so it is not done separately. An
  industry with people but no wage bill starts from the region's skill mix.

The modelled table merges groups 6 (skilled agricultural, medium) and 9
(elementary, low) into one category, 96. It is split by the ratio 9 / (6 + 9)
in the country's survey data (`EMP_TEMP_SEX_OCU_NB_A`, ISCO-08 rows, pooled
over years); for a country without them, group 6 is set to the survey median
ratio of group 6 to agricultural employment times the country's agricultural
employment (capped at group 96), the rest of group 96 being elementary. The survey's own skill
levels are not used as the margin: many countries have one or two survey
years (China only the 2000 census, with almost no elementary occupations),
so carrying them would freeze the skill mix, while the modelled series is
annual for every country. A country with no modelled row (the hand-compiled
supplementary entities) takes its UN region's employment-weighted mix, then
the world's.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

OCCUPATION_MODELLED = "EMP_2EMP_SEX_OCU_NB_A.csv"
OCCUPATION_SURVEY = "EMP_TEMP_SEX_OCU_NB_A.csv"

SKILLS = ("low", "middle", "high")
SEXES = {"SEX_M": "male", "SEX_F": "female"}

SPLIT = {"low": "Split Low qualification employment",
         "middle": "Split Middle qualification employment",
         "high": "Split High qualification employment"}
WAGE = {"low": "Compensation of employees; wages, salaries, & employers social contributions: Low-skilled",
        "middle": "Compensation of employees; wages, salaries, & employers social contributions: Middle-skilled",
        "high": "Compensation of employees; wages, salaries, & employers social contributions: High-skilled"}


def _un_region(iso3):
    import country_converter as coco
    cc = coco.CountryConverter(include_obsolete=True)
    out = cc.convert(names=list(iso3), src="ISO3", to="UNregion", not_found=None)
    out = out if isinstance(out, list) else [out]
    return dict(zip(iso3, ["World" if o in (None, "not found") else o for o in out]))


def elementary_ratio(survey: pd.DataFrame, un_region: dict) -> pd.DataFrame:
    """r = ISCO-08 group 9 / (6 + 9) by (ref_area, sex), pooled over every
    survey year; also the UN region and world pools. Returns three Series."""
    s = survey[survey["classif1"].isin(["OCU_ISCO08_6", "OCU_ISCO08_9"])
               & survey["sex"].isin(SEXES)]
    p = s.pivot_table(index=["ref_area", "sex"], columns="classif1",
                      values="obs_value", aggfunc="sum").fillna(0.0)
    p = p[(p["OCU_ISCO08_6"] + p["OCU_ISCO08_9"]) > 0].reset_index()
    p["unregion"] = p["ref_area"].map(un_region).fillna("World")
    reg = p.groupby(["unregion", "sex"])[["OCU_ISCO08_6", "OCU_ISCO08_9"]].sum()
    wld = p.groupby("sex")[["OCU_ISCO08_6", "OCU_ISCO08_9"]].sum()
    ratio = lambda d: d["OCU_ISCO08_9"] / (d["OCU_ISCO08_6"] + d["OCU_ISCO08_9"])
    country = ratio(p.set_index(["ref_area", "sex"]))
    return country, ratio(reg), ratio(wld)


def agri_alpha(survey: pd.DataFrame, agri: pd.Series) -> pd.Series:
    """Median over survey country-years of ISCO-08 group 6 / agricultural
    employment, by sex (ratios outside (0, 2) dropped as mismatched)."""
    s = survey[(survey["classif1"] == "OCU_ISCO08_6") & survey["sex"].isin(SEXES)]
    g6 = s.groupby(["ref_area", "sex", "time"])["obs_value"].mean()
    ratio = (g6 / agri.reindex(g6.index)).dropna()
    ratio = ratio[(ratio > 0) & (ratio < 2)]
    return ratio.groupby(level="sex").median()


def country_skill_shares(modelled: pd.DataFrame, survey: pd.DataFrame,
                         un_region: dict, years, agri: pd.Series | None = None) -> pd.DataFrame:
    """Skill shares by (ref_area, sex, time): columns low, middle, high.

    From ILO's modelled employment by ISCO-08 major group (every country and
    year): high = groups 1-3, middle = 4, 5, 7, 8 and the skilled
    agricultural part of the merged group 96, low = its elementary part,
    split by `elementary_ratio` where the country has survey rows for
    groups 6 and 9, else by `agri` (agricultural employment by ref_area,
    sex, time): group 6 = alpha * agri, capped at group 96, with alpha the
    median survey ratio of group 6 to agricultural employment for that sex.
    """
    m = modelled[modelled["sex"].isin(SEXES) & modelled["time"].isin(years)
                 & (modelled["classif1"] != "OCU_ISCO08_TOTAL")]
    p = m.pivot_table(index=["ref_area", "sex", "time"], columns="classif1",
                      values="obs_value", aggfunc="sum").fillna(0.0)
    country, reg, wld = elementary_ratio(survey, un_region)
    idx = p.index.to_frame(index=False)
    r = pd.Series([country.get((a, s), np.nan) for a, s in zip(idx.ref_area, idx.sex)])
    g = lambda c: p[c].to_numpy() if c in p.columns else 0.0
    # No survey for groups 6 and 9: tie group 6 to the country's own farm
    # workforce. Skilled agricultural workers work in agriculture, so group 6
    # is at most agricultural employment; in survey country-years it is a
    # median 0.73 of it (both sexes, 1,518 country-years, 2026-11-10). For
    # China (394 million in group 96 in 2019 against 185 million in
    # agriculture) this gives about 34% low-skilled; a pooled 9/(6+9) ratio
    # cannot see that group 96 is twice the farm workforce (world pool 0.53:
    # 28%; Eastern Asia's pool, set by Japan and Korea, 0.81: 41%).
    miss = r.isna().to_numpy()
    if agri is not None and miss.any():
        alpha = agri_alpha(survey, agri)
        a = agri.reindex(p.index).to_numpy()
        g96 = g("OCU_ISCO08_96") * np.ones(len(p))
        g6 = np.minimum(np.array([alpha.get(s, np.nan) for s in idx.sex]) * a, g96)
        with np.errstate(invalid="ignore", divide="ignore"):
            r_agri = np.where(g96 > 0, 1 - g6 / g96, np.nan)
        use = miss & np.isfinite(r_agri)
        r[use] = r_agri[use]
    miss = r.isna()
    r[miss] = [wld.get(s, 0.5) for s in idx.sex[miss]]
    r = r.to_numpy()
    out = pd.DataFrame({
        "low": g("OCU_ISCO08_96") * r,
        "middle": g("OCU_ISCO08_4") + g("OCU_ISCO08_5") + g("OCU_ISCO08_7")
                  + g("OCU_ISCO08_8") + g("OCU_ISCO08_96") * (1 - r),
        "high": g("OCU_ISCO08_1") + g("OCU_ISCO08_2") + g("OCU_ISCO08_3"),
    }, index=p.index)
    out = out[out.sum(axis=1) > 0]
    return out.div(out.sum(axis=1), axis=0)


def region_skill_shares(modelled: pd.DataFrame, survey: pd.DataFrame,
                        employment: pd.DataFrame, years) -> pd.DataFrame:
    """Skill shares by (region, sex, time), employment-weighted over countries.

    `employment`: ref_area, EXIO3 (the axis region), sex, classif1, time,
    obs_value; the ECO_DETAILS_TOTAL rows of SEX_M and SEX_F are used.
    """
    e = employment[(employment["classif1"] == "ECO_DETAILS_TOTAL")
                   & employment["sex"].isin(SEXES)
                   & employment["time"].isin(years)
                   & employment["EXIO3"].notna() & (employment["EXIO3"] != "not found")]
    e = e.groupby(["ref_area", "EXIO3", "sex", "time"], as_index=False)["obs_value"].sum()
    un = _un_region(sorted(set(e["ref_area"]) | set(survey["ref_area"]) | set(modelled["ref_area"])))
    a = employment[(employment["classif1"] == "ECO_DETAILS_A") & employment["sex"].isin(SEXES)]
    agri = a.groupby(["ref_area", "sex", "time"])["obs_value"].sum()
    cs = country_skill_shares(modelled, survey, un, years, agri=agri)
    e["unregion"] = e["ref_area"].map(un).fillna("World")

    e = e.join(cs, on=["ref_area", "sex", "time"])
    have = e.dropna(subset=list(SKILLS))
    for k in SKILLS:
        have = have.assign(**{f"w_{k}": have[k] * have["obs_value"]})
    wcols = [f"w_{k}" for k in SKILLS]
    reg = have.groupby(["unregion", "sex", "time"])[wcols + ["obs_value"]].sum()
    wld = have.groupby(["sex", "time"])[wcols + ["obs_value"]].sum()
    reg_sh = reg[wcols].div(reg["obs_value"], axis=0).set_axis(list(SKILLS), axis=1)
    wld_sh = wld[wcols].div(wld["obs_value"], axis=0).set_axis(list(SKILLS), axis=1)

    miss = e[list(SKILLS)].isna().any(axis=1)
    fill = e.loc[miss, ["unregion", "sex", "time"]].join(reg_sh, on=["unregion", "sex", "time"])
    e.loc[miss, list(SKILLS)] = fill[list(SKILLS)].to_numpy()
    miss = e[list(SKILLS)].isna().any(axis=1)
    fill = e.loc[miss, ["sex", "time"]].join(wld_sh, on=["sex", "time"])
    e.loc[miss, list(SKILLS)] = fill[list(SKILLS)].to_numpy()

    for k in SKILLS:
        e[f"w_{k}"] = e[k] * e["obs_value"]
    r = e.groupby(["EXIO3", "sex", "time"])[wcols + ["obs_value"]].sum()
    shares = r[wcols].div(r["obs_value"].where(r["obs_value"] > 0), axis=0)
    shares.columns = list(SKILLS)
    shares.index = shares.index.set_names(["region", "sex", "time"])
    return shares.fillna(1 / 3)


def ras(prior: np.ndarray, rows: np.ndarray, cols: np.ndarray,
        iters: int = 500, tol: float = 1e-10) -> np.ndarray:
    """Scale `prior` (n x k, non-negative) to row sums `rows` and column sums
    `cols` (sum(rows) == sum(cols)). A row with a positive target and no prior
    starts from the column mix."""
    X = np.asarray(prior, dtype=float).copy()
    rows = np.asarray(rows, dtype=float)
    cols = np.asarray(cols, dtype=float)
    empty = (X.sum(axis=1) <= 0) & (rows > 0)
    X[empty] = cols / cols.sum() if cols.sum() > 0 else 1.0 / X.shape[1]
    X[rows <= 0] = 0.0
    # A skill level with a target but no prior anywhere: seed it thinly.
    dead = (X.sum(axis=0) <= 0) & (cols > 0)
    if dead.any():
        X[:, dead] = 1e-9 * rows[:, None]
    for _ in range(iters):
        rs = X.sum(axis=1)
        X *= np.divide(rows, rs, out=np.zeros_like(rows), where=rs > 0)[:, None]
        cs = X.sum(axis=0)
        X *= np.divide(cols, cs, out=np.zeros_like(cols), where=cs > 0)[None, :]
        if np.abs(X.sum(axis=1) - rows).max() <= tol * max(rows.max(), 1.0):
            break
    return X


def rebalance_year(frame: pd.DataFrame, shares: pd.DataFrame, year: int) -> pd.DataFrame:
    """Replace the nine `Split <skill> ... - <sex>/total` columns of one year
    of the salary split by the occupation-based split. Industry totals by sex
    are kept; regions with no people are left as they are."""
    out = frame.copy()
    split_cols = [f"{SPLIT[k]} - {sx}" for k in SKILLS for sx in ("male", "female", "total")]
    out[split_cols] = out[split_cols].astype(float)
    wages = out[[WAGE[k] for k in SKILLS]].to_numpy(dtype=float).clip(min=0)
    for code in pd.unique(out["Country"]):
        mask = (out["Country"] == code).to_numpy()
        for sex_code, sex in SEXES.items():
            cols = [f"{SPLIT[k]} - {sex}" for k in SKILLS]
            people = out.loc[mask, cols].to_numpy(dtype=float)
            rows = people.sum(axis=1)
            total = rows.sum()
            if total <= 0:
                continue
            key = (code, sex_code, year)
            target = (shares.loc[key].to_numpy(dtype=float) if key in shares.index
                      else people.sum(axis=0) / total) * total
            out.loc[mask, cols] = ras(wages[mask], rows, target)
    for k in SKILLS:
        out[f"{SPLIT[k]} - total"] = out[f"{SPLIT[k]} - male"] + out[f"{SPLIT[k]} - female"]
    return out


def rebalance(split: dict, employment: pd.DataFrame, data_dir: Path, final_path: Path | None = None) -> dict:
    """Apply `rebalance_year` to every year of the salary split."""
    cols = ["ref_area", "sex", "classif1", "time", "obs_value"]
    modelled = pd.read_csv(Path(data_dir) / OCCUPATION_MODELLED, usecols=cols)
    survey = pd.read_csv(Path(data_dir) / OCCUPATION_SURVEY, usecols=cols)
    years = sorted(split)
    shares = region_skill_shares(modelled, survey, employment, years)
    if final_path is not None:
        shares.reset_index().to_csv(Path(final_path) / "skill_shares_occupation.csv", index=False)
    return {y: rebalance_year(split[y], shares, y) for y in years}
