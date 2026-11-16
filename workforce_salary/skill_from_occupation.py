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
over the years that report both groups); for a country without them, group 6
is set to the survey median ratio of group 6 to agricultural employment times
the country's agricultural employment, the rest of group 96 being elementary.
Where that would take all of group 96 (Oman's and Syria's women in the
1990s), agriculture says nothing about the split and the world's pooled ratio
is used instead. The survey's own skill
levels are not used as the margin: many countries have one or two survey
years (China only the 2000 census, with almost no elementary occupations),
so carrying them would freeze the skill mix, while the modelled series is
annual for every country. A country with no modelled row (the hand-compiled
supplementary entities) takes its UN region's employment-weighted mix, then
the world's.

Three country cases the rules above get wrong (2026-11-17):

- Taiwan's national classification reports craft workers, machine operators
  and elementary labourers as one group, which ILO files under group 8: its
  survey rows (2001-2020) have groups 1-6 and 8, never 7 or 9, and the
  modelled group 96 is the farmers alone (509 thousand in 2019 against 507
  in survey group 6), extrapolated down to 210 thousand by 2025. Splitting
  group 96 left Taiwan 2.4% low-skilled in 2019 and 0.6% in 2025. For a
  country whose survey has groups 6 and 8 and never 7 or 9
  (`merged_elementary`), all of group 96 is skilled agricultural and the
  elementary workers are taken out of groups 7 + 8 by the pooled survey
  ratio 9 / (7 + 8 + 9) of its UN region (`elementary_of_manual`).
- Portugal's labour force survey breaks in 2021: group 6 falls from 254 to
  113 thousand while group 9 goes from 392 to 363, and the modelled group 96
  follows (649 to 478). One ratio pooled over all years passed the farmers'
  break on to the elementary workers (low-skilled people -25.6% in 2021).
  For the countries in `RATIO_BREAKS` the ratio is pooled separately before
  and from the break year.
- India's survey changes from ISCO-88 (to 2020) to ISCO-08 (from 2022) and
  group 1 falls from 35.2 million (2020, ISCO-88) to 17.1 million (2023)
  while group 5 rises from 33.5 to 59.0 million; the modelled series bridges
  the two (high-skilled share 17.0% in 2020, 11.7% in 2023). For the
  countries in `LEVEL_BREAKS` the shares of the years up to the last year of
  the old basis are scaled, skill by skill, by the ratio of the first new
  year to that last old year and renormalised, and the years between take
  the first new year's shares: the level of ISCO-08 with the year-to-year
  movement of the old series, on the assumption of no real change across
  the gap.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

OCCUPATION_MODELLED = "EMP_2EMP_SEX_OCU_NB_A.csv"
OCCUPATION_SURVEY = "EMP_TEMP_SEX_OCU_NB_A.csv"

# ref_area: first years of a new basis for the survey ratio 9 / (6 + 9).
RATIO_BREAKS = {"PRT": (2021,)}
# ref_area: (last year of the old classification, first year of the new one)
# in the modelled series.
LEVEL_BREAKS = {"IND": (2020, 2023)}

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
    """r = ISCO-08 group 9 / (6 + 9) by (ref_area, sex), pooled over the
    survey years that report both groups (a year with only one of them says
    nothing about the ratio); also the UN region and world pools. Returns
    three Series."""
    s = survey[survey["classif1"].isin(["OCU_ISCO08_6", "OCU_ISCO08_9"])
               & survey["sex"].isin(SEXES)]
    p = s.pivot_table(index=["ref_area", "sex", "time"], columns="classif1",
                      values="obs_value", aggfunc="sum")
    p = p.reindex(columns=["OCU_ISCO08_6", "OCU_ISCO08_9"]).dropna()
    p = p.groupby(level=["ref_area", "sex"]).sum()
    p = p[(p["OCU_ISCO08_6"] + p["OCU_ISCO08_9"]) > 0].reset_index()
    p["unregion"] = p["ref_area"].map(un_region).fillna("World")
    reg = p.groupby(["unregion", "sex"])[["OCU_ISCO08_6", "OCU_ISCO08_9"]].sum()
    wld = p.groupby("sex")[["OCU_ISCO08_6", "OCU_ISCO08_9"]].sum()
    ratio = lambda d: d["OCU_ISCO08_9"] / (d["OCU_ISCO08_6"] + d["OCU_ISCO08_9"])
    country = ratio(p.set_index(["ref_area", "sex"]))
    return country, ratio(reg), ratio(wld)


def _segment(ref_area, time, breaks: dict) -> list:
    return [sum(t >= b for b in breaks.get(a, ())) for a, t in zip(ref_area, time)]


def segment_ratio(survey: pd.DataFrame, breaks: dict | None = None) -> pd.Series:
    """r = ISCO-08 group 9 / (6 + 9) by (ref_area, sex, segment) for the
    countries in `breaks` (default `RATIO_BREAKS`), pooled over the survey
    years of each segment; segment = number of break years <= the year."""
    breaks = RATIO_BREAKS if breaks is None else breaks
    s = survey[survey["classif1"].isin(["OCU_ISCO08_6", "OCU_ISCO08_9"])
               & survey["sex"].isin(SEXES) & survey["ref_area"].isin(list(breaks))]
    if s.empty:
        return pd.Series(dtype=float)
    p = s.pivot_table(index=["ref_area", "sex", "time"], columns="classif1",
                      values="obs_value", aggfunc="sum")
    p = p.reindex(columns=["OCU_ISCO08_6", "OCU_ISCO08_9"]).dropna().reset_index()
    p["segment"] = _segment(p["ref_area"], p["time"], breaks)
    p = p.groupby(["ref_area", "sex", "segment"])[["OCU_ISCO08_6", "OCU_ISCO08_9"]].sum()
    p = p[p.sum(axis=1) > 0]
    return p["OCU_ISCO08_9"] / p.sum(axis=1)


def merged_elementary(survey: pd.DataFrame) -> set:
    """Countries whose survey reports groups 6 and 8 and at least five major
    groups (ISCO-88 or ISCO-08) but never group 7 or 9: craft workers,
    operators and elementary workers come as one group (Taiwan)."""
    s = survey[survey["classif1"].str.match(r"OCU_ISCO(88|08)_[1-9]$")]
    groups = s.groupby("ref_area")["classif1"].agg(lambda c: {x[-1] for x in c})
    return {a for a, g in groups.items()
            if {"6", "8"} <= g and not ({"7", "9"} & g) and len(g) >= 5}


def elementary_of_manual(survey: pd.DataFrame, un_region: dict, exclude=()) -> tuple:
    """ISCO-08 group 9 / (7 + 8 + 9) by (unregion, sex) and by sex for the
    world, pooled over the survey country-years reporting all three."""
    cols = ["OCU_ISCO08_7", "OCU_ISCO08_8", "OCU_ISCO08_9"]
    s = survey[survey["classif1"].isin(cols) & survey["sex"].isin(SEXES)
               & ~survey["ref_area"].isin(list(exclude))]
    p = s.pivot_table(index=["ref_area", "sex", "time"], columns="classif1",
                      values="obs_value", aggfunc="sum")
    p = p.reindex(columns=cols).dropna().reset_index()
    p["unregion"] = p["ref_area"].map(un_region).fillna("World")
    ratio = lambda d: d["OCU_ISCO08_9"] / d[cols].sum(axis=1)
    reg = p.groupby(["unregion", "sex"])[cols].sum()
    wld = p.groupby("sex")[cols].sum()
    return ratio(reg[reg.sum(axis=1) > 0]), ratio(wld[wld.sum(axis=1) > 0])


def splice_levels(shares: pd.DataFrame, breaks: dict | None = None) -> pd.DataFrame:
    """Carry the level of a new classification back over the old one's years.

    `shares`: low, middle, high by (ref_area, sex, time). For each country in
    `breaks` (default `LEVEL_BREAKS`) with both years present: years up to
    the last old year are multiplied, skill by skill, by new / old and
    renormalised; the years between take the first new year's shares."""
    breaks = LEVEL_BREAKS if breaks is None else breaks
    out = shares.copy()
    area = out.index.get_level_values("ref_area")
    sexes = out.index.get_level_values("sex")
    time = out.index.get_level_values("time")
    for a, (old, new) in breaks.items():
        for s in pd.unique(sexes[area == a]):
            if (a, s, old) not in out.index or (a, s, new) not in out.index:
                continue
            target = out.loc[(a, s, new)].to_numpy(dtype=float)
            base = out.loc[(a, s, old)].to_numpy(dtype=float)
            f = np.divide(target, base, out=np.ones_like(target), where=base > 0)
            here = (area == a) & (sexes == s)
            before = here & (time <= old)
            scaled = out.loc[before].to_numpy(dtype=float) * f
            out.loc[before] = scaled / scaled.sum(axis=1, keepdims=True)
            out.loc[here & (time > old) & (time < new)] = target
    return out


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
    sex, time): group 6 = alpha * agri, with alpha the median survey ratio
    of group 6 to agricultural employment for that sex, used only where it
    is below group 96. Otherwise (alpha * agri >= group 96, which would
    leave no elementary workers) and without agricultural employment, the
    world's pooled ratio.

    The module docstring gives the three country cases: `RATIO_BREAKS`
    (ratio pooled by segment), `merged_elementary` (elementary workers out
    of groups 7 + 8) and `LEVEL_BREAKS` (`splice_levels`). The shares are
    computed over every modelled year and cut to `years` at the end, so the
    splice does not depend on the years asked for.
    """
    m = modelled[modelled["sex"].isin(SEXES)
                 & (modelled["classif1"] != "OCU_ISCO08_TOTAL")]
    p = m.pivot_table(index=["ref_area", "sex", "time"], columns="classif1",
                      values="obs_value", aggfunc="sum").fillna(0.0)
    country, reg, wld = elementary_ratio(survey, un_region)
    idx = p.index.to_frame(index=False)
    r = pd.Series([country.get((a, s), np.nan) for a, s in zip(idx.ref_area, idx.sex)])
    seg = segment_ratio(survey)
    if len(seg):
        hit = idx.ref_area.isin(seg.index.get_level_values("ref_area")).to_numpy()
        sub = idx[hit]
        r[hit] = [seg.get((a, s, k), r0) for a, s, k, r0 in
                  zip(sub.ref_area, sub.sex, _segment(sub.ref_area, sub.time, RATIO_BREAKS), r[hit])]
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
        g6 = np.array([alpha.get(s, np.nan) for s in idx.sex]) * a
        # Only where agriculture is informative: if alpha * agri reaches
        # group 96 (Oman's and Syria's women in the 1990s; Taiwan is handled
        # below), capping g6 at group 96 would leave no elementary workers,
        # so those fall through to the world pool below.
        with np.errstate(invalid="ignore", divide="ignore"):
            r_agri = np.where((g96 > 0) & (g6 < g96), 1 - g6 / g96, np.nan)
        use = miss & np.isfinite(r_agri)
        r[use] = r_agri[use]
    miss = r.isna()
    r[miss] = [wld.get(s, 0.5) for s in idx.sex[miss]]
    r = r.to_numpy()
    # Craft workers, operators and elementary workers reported as one group:
    # group 96 is the farmers, the elementary workers sit in groups 7 + 8.
    lam = np.zeros(len(p))
    merged = merged_elementary(survey)
    one = idx.ref_area.isin(merged).to_numpy()
    if one.any():
        reg_l, wld_l = elementary_of_manual(survey, un_region, exclude=merged)
        lam[one] = [reg_l.get((un_region.get(a, "World"), s), wld_l.get(s, 0.0))
                    for a, s in zip(idx.ref_area[one], idx.sex[one])]
        r[one] = 0.0
    manual = (g("OCU_ISCO08_7") + g("OCU_ISCO08_8")) * np.ones(len(p))
    out = pd.DataFrame({
        "low": g("OCU_ISCO08_96") * r + manual * lam,
        "middle": g("OCU_ISCO08_4") + g("OCU_ISCO08_5") + manual * (1 - lam)
                  + g("OCU_ISCO08_96") * (1 - r),
        "high": g("OCU_ISCO08_1") + g("OCU_ISCO08_2") + g("OCU_ISCO08_3"),
    }, index=p.index)
    out = out[out.sum(axis=1) > 0]
    out = splice_levels(out.div(out.sum(axis=1), axis=0))
    return out[out.index.get_level_values("time").isin(list(years))]


def region_skill_shares(modelled: pd.DataFrame, survey: pd.DataFrame,
                        employment: pd.DataFrame, years) -> pd.DataFrame:
    """Skill shares by (region, sex, time), employment-weighted over countries.

    `employment`: ref_area, EXIO3 (the axis region), sex, classif1, time,
    obs_value; the ECO_DETAILS_TOTAL rows of SEX_M and SEX_F are used.
    """
    e = employment[(employment["classif1"] == "ECO_DETAILS_TOTAL")
                   & employment["sex"].isin(SEXES)
                   & employment["time"].isin(years)
                   & employment["EXIO3"].notna()
                   & ~employment["EXIO3"].isin(["not found", ""])]
    e = e.groupby(["ref_area", "EXIO3", "sex", "time"], as_index=False)["obs_value"].sum()
    un = _un_region(sorted(set(e["ref_area"]) | set(survey["ref_area"]) | set(modelled["ref_area"])))
    a = employment[(employment["classif1"] == "ECO_DETAILS_A") & employment["sex"].isin(SEXES)]
    agri = a.groupby(["ref_area", "sex", "time"])["obs_value"].sum()
    cs = country_skill_shares(modelled, survey, un, years, agri=agri)
    e["unregion"] = e["ref_area"].map(un).fillna("World")

    e = e.join(cs, on=["ref_area", "sex", "time"])
    # A country whose modelled occupation series stops before its employment
    # series (Ukraine: 2021, workforce carried flat to 2025) keeps its own
    # nearest observed mix instead of jumping to its UN region's (Ukraine's
    # high-skilled share went 37.9% to 42.3% at 2021-2022 without this).
    ordered = e.sort_values(["ref_area", "sex", "time"])
    own = ordered.groupby(["ref_area", "sex"], sort=False)[list(SKILLS)]
    e[list(SKILLS)] = own.ffill().fillna(own.bfill()).reindex(e.index)
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
    # A region-sex-year without people gets 1/3 each, harmlessly (nothing to
    # split); one with people but no skill shares is a gap in the fallbacks.
    gap = shares.isna().any(axis=1) & (r["obs_value"] > 0).to_numpy()
    if gap.any():
        print(f"[WARN] skill shares: {int(gap.sum())} region-sex-years with people "
              f"but no skill shares set to 1/3 each, e.g. {list(shares.index[gap][:5])}")
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
            return X
    resid = np.abs(X.sum(axis=1) - rows).max()
    if resid > 1e-6 * max(rows.max(), 1.0):
        print(f"[WARN] ras: no convergence after {iters} iterations, largest row "
              f"residual {resid:.3g} of row total {rows.max():.3g}")
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
