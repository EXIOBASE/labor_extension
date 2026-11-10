"""Build the labour-risk account from the labour handoff workbook.

    <python> scripts/build_labour_risk.py --final-table <labour final_table dir> \
        --workbook final_labor_SUTs_3_12.xlsx --out <dir> [--axis e3|rx2] [--years 1995-2025]

Reads the labour account (people and hours by region, industry, sex, skill),
`workforce.csv` from the same final_table folder (ILO employment by country,
region, sex, activity group), the status tables in the labour data folder and
the ILOSTAT labour-risk downloads in `<data>/risk/ilostat_2026-11-10`.

Writes, per year, `<out>/ixi/<year>/` in the release labour extension's
format (desire_upload_prepper exiobase_labour_extensions_reformat.py
write_year): `F.txt` (stressor rows, (region, sector) columns in the release
order of the axis, io_utils.classification sector_layout), `F_Y.txt` (zero,
the release final-demand columns), `unit.txt` and `file_parameters.json`
(name "labour_risk"). Also `<out>/world_totals.csv` and
`<out>/country_sources.csv` (which source each country's value came from).
Every indicator is computed over 1995-2025 whatever --years says; --years
only picks the years written.

No stressor starts with "Employment people" or "Employment hours":
downstream composites sum those prefixes into the employment totals.
Docs: labour_risk/indicators.py, labour_risk/child_forced.py and
docs/improvement_plan_2026-11-06.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "working_hours")]

from labour_risk import common, indicators  # noqa: E402
from labour_risk import child_forced  # noqa: E402
import vulnerable_employment as ve  # noqa: E402

DATA = Path("d:/indecol/data/labour/data")
RISK = DATA / "risk" / "ilostat_2026-11-10"

INFORMAL_P = "Informal employment: people"
INFORMAL_H = "Informal employment: hours"
POVERTY = "Working poverty (below US$3 a day): people"
LONG_HOURS = "Long hours (49 hours a week or more): people"
UNITS = {
    "Informal employment: people": "1000 p",
    "Informal employment: hours": "M.hr",
    "Working poverty (below US$3 a day): people": "1000 p",
    "Long hours (49 hours a week or more): people": "1000 p",
    "Child labour": "1000 p",
    "Child labour: hazardous work": "1000 p",
    "Forced labour": "1000 p",
    "Long working hours: attributable deaths": "1000 p",
    "Long working hours: attributable DALYs": "1000 DALY",
}

#: pymrio folder descriptor, as exiobase_labour_extensions_reformat.write_year.
FILE_PARAMETERS = {
    "files": {
        "F": {"name": "F.txt", "nr_index_col": "1", "nr_header": "2"},
        "F_Y": {"name": "F_Y.txt", "nr_index_col": "1", "nr_header": "2"},
        "unit": {"name": "unit.txt", "nr_index_col": "1", "nr_header": "1"},
    },
    "systemtype": "Extension",
    "name": "labour_risk",
}
IO_AXIS = {"e3": "exiobase3", "rx2": "rx2"}


def release_layout(axis: str, layout_from: Path | None = None):
    """(region, sector) and (region, category) columns of the release labour
    F.txt and F_Y.txt: io_utils.classification, as the reformat uses, else
    the header of a release labour year folder."""
    if layout_from is not None:
        F = pd.read_csv(layout_from / "F.txt", sep="	", header=[0, 1], index_col=0, nrows=0)
        FY = pd.read_csv(layout_from / "F_Y.txt", sep="	", header=[0, 1], index_col=0, nrows=0)
        return F.columns.set_names(["region", "sector"]), FY.columns.set_names(["region", "category"])
    from io_utils.classification import final_demand_layout, sector_layout
    return sector_layout(IO_AXIS[axis], "ixi"), final_demand_layout(IO_AXIS[axis])


def write_year(out_dir: Path, F: pd.DataFrame, fd_cols: pd.MultiIndex) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    F_Y = pd.DataFrame(0.0, index=F.index, columns=fd_cols)
    F.to_csv(out_dir / "F.txt", sep="	")
    F_Y.to_csv(out_dir / "F_Y.txt", sep="	")
    pd.DataFrame({"unit": [UNITS[s] for s in F.index]},
                 index=F.index).to_csv(out_dir / "unit.txt", sep="	")
    with open(out_dir / "file_parameters.json", "w", encoding="utf-8") as fh:
        json.dump(FILE_PARAMETERS, fh, indent=4)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--final-table", type=Path, required=True)
    ap.add_argument("--workbook", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--years", default="1995-2025")
    ap.add_argument("--axis", choices=sorted(IO_AXIS), default="e3")
    ap.add_argument("--layout-from", type=Path, default=None,
                    help="release labour ixi year folder to take the column order from "
                         "(default: io_utils.classification)")
    args = ap.parse_args()
    lo, hi = (int(x) for x in args.years.split("-"))
    years = list(range(lo, hi + 1))

    wf = pd.read_csv(args.final_table / "workforce.csv", low_memory=False,
                     usecols=["ref_area", "EXIO3", "sex", "classif1", "time", "obs_value"])
    # Every year of the vulnerable table, not only the requested ones: the
    # indicators pool and interpolate over the full source span, and a year's
    # values must not depend on --years.
    vul = ve.country_table(wf, DATA).rename(columns={"classif1": "group"})
    un = common.un_region(sorted(set(vul["ref_area"])))

    built = {
        "informal": indicators.informal(vul, RISK, un, years),
        "working_poverty": indicators.working_poverty(vul, RISK, un, years),
        "long_hours": indicators.long_hours(vul, RISK, un, years),
    }
    shares = {k: common.region_share(v) for k, v in built.items()}
    counts = child_forced.region_counts(wf, years, un)
    who = indicators.who_long_hours(common.employment_by_country(wf), RISK, years)

    src = []
    for k, v in built.items():
        col = [c for c in v.columns if c.endswith("_source")]
        if col:
            src.append(v.drop_duplicates("ref_area")[["ref_area", col[0]]]
                       .rename(columns={col[0]: "source"}).assign(indicator=k))
    args.out.mkdir(parents=True, exist_ok=True)
    if src:
        pd.concat(src).to_csv(args.out / "country_sources.csv", index=False)

    sector_group = common.sector_groups()
    ixi_cols, fd_cols = release_layout(args.axis, args.layout_from)
    totals = []
    for y in years:
        acc = common.read_account(args.final_table / args.workbook, y)
        F = pd.DataFrame(index=acc.index)
        p, h = common.apply_shares(acc, shares["informal"], y, sector_group)
        F[INFORMAL_P] = p
        F[INFORMAL_H] = h
        p, _ = common.apply_shares(acc, shares["working_poverty"], y, sector_group, hours=False)
        F[POVERTY] = p
        p, _ = common.apply_shares(acc, shares["long_hours"], y, sector_group, hours=False)
        F[LONG_HOURS] = p
        for name, c in counts.items():
            F[name] = common.allocate_counts(acc, c, y, sector_group, key="broad")
        # Burden of long hours, spread over a region's industries by their
        # people working 49 hours or more.
        lh = F[LONG_HOURS]
        lh_tot = lh.groupby(level="region").transform("sum")
        for name, key in (("Long working hours: attributable deaths", "deaths"),
                          ("Long working hours: attributable DALYs", "dalys")):
            r = who[key].xs(y, level="time") if y in who[key].index.get_level_values("time") else pd.Series(dtype=float)
            tgt = lh.index.get_level_values("region").map(r).fillna(0.0).to_numpy()
            F[name] = (tgt * lh / lh_tot.where(lh_tot > 0)).fillna(0.0)
        unknown = F.index.difference(ixi_cols)
        if len(unknown):
            raise ValueError(f"{y}: {len(unknown)} workbook (region, sector) pairs are not on the "
                             f"{args.axis} release layout, e.g. {list(unknown[:3])}")
        F = F.T.reindex(columns=ixi_cols).fillna(0.0)
        F.index.name = "stressor"
        write_year(args.out / "ixi" / str(y), F, fd_cols)
        people = sum(acc[c].sum() for sex in common.PEOPLE for c in common.PEOPLE[sex])
        row = {"year": y, "employment_people": people}
        row.update(F.sum(axis=1).to_dict())
        totals.append(row)
        print(y, {k: round(v) for k, v in row.items() if k != "year"}, flush=True)
    pd.DataFrame(totals).to_csv(args.out / "world_totals.csv", index=False)


if __name__ == "__main__":
    main()
