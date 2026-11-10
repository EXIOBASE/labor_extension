"""Build the labour-risk account from the labour handoff workbook.

    <python> scripts/build_labour_risk.py --final-table <labour final_table dir> \\
        --workbook final_labor_SUTs_3_12.xlsx --out <dir> [--years 1995-2025]

Reads the labour account (people and hours by region, industry, sex, skill),
`workforce.csv` from the same final_table folder (ILO employment by country,
region, sex, activity group), the status tables in the labour data folder and
the ILOSTAT labour-risk downloads in `<data>/risk/ilostat_2026-11-10`.

(region, sector), F_Y zero) and `<out>/world_totals.csv`,
`<out>/country_sources.csv` (which source each country's value came from).
Docs: labour_risk/indicators.py and docs/improvement_plan_2026-11-06.md.
"""
from __future__ import annotations

import argparse
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

UNITS = {
    "Employment people: Informal employment": "1000 p",
    "Employment hours: Informal employment": "M.hr",
    "Employment people: Working poverty (below US$3 a day)": "1000 p",
    "Employment people: Long hours (49 hours a week or more)": "1000 p",
    "Child labour": "1000 p",
    "Child labour: hazardous work": "1000 p",
    "Forced labour": "1000 p",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--final-table", type=Path, required=True)
    ap.add_argument("--workbook", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--years", default="1995-2025")
    args = ap.parse_args()
    lo, hi = (int(x) for x in args.years.split("-"))
    years = list(range(lo, hi + 1))

    wf = pd.read_csv(args.final_table / "workforce.csv", low_memory=False,
                     usecols=["ref_area", "EXIO3", "sex", "classif1", "time", "obs_value"])
    vul = ve.country_table(wf, DATA).rename(columns={"classif1": "group"})
    vul = vul[vul["time"].isin(years)]
    un = common.un_region(sorted(set(vul["ref_area"])))

    built = {
        "informal": indicators.informal(vul, RISK, un),
        "working_poverty": indicators.working_poverty(vul, RISK, un, years),
        "long_hours": indicators.long_hours(vul, RISK, un, years),
    }
    shares = {k: common.region_share(v) for k, v in built.items()}
    counts = child_forced.region_counts(wf, years, un)

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
    totals = []
    for y in years:
        acc = common.read_account(args.final_table / args.workbook, y)
        F = pd.DataFrame(index=acc.index)
        p, h = common.apply_shares(acc, shares["informal"], y, sector_group)
        F["Employment people: Informal employment"] = p
        F["Employment hours: Informal employment"] = h
        p, _ = common.apply_shares(acc, shares["working_poverty"], y, sector_group, hours=False)
        F["Employment people: Working poverty (below US$3 a day)"] = p
        p, _ = common.apply_shares(acc, shares["long_hours"], y, sector_group, hours=False)
        F["Employment people: Long hours (49 hours a week or more)"] = p
        for name, c in counts.items():
            F[name] = common.allocate_counts(acc, c, y, sector_group, key="broad")
        F = F.T
        F.index.name = "stressor"
        d = args.out / "ixi" / str(y)
        d.mkdir(parents=True, exist_ok=True)
        F.to_csv(d / "F.txt", sep="\t")
        pd.DataFrame({"unit": [UNITS[s] for s in F.index]}, index=F.index).to_csv(d / "unit.txt", sep="\t")
        people = sum(acc[c].sum() for sex in common.PEOPLE for c in common.PEOPLE[sex])
        row = {"year": y, "employment_people": people}
        row.update(F.sum(axis=1).to_dict())
        totals.append(row)
        print(y, {k: round(v) for k, v in row.items() if k != "year"}, flush=True)
    pd.DataFrame(totals).to_csv(args.out / "world_totals.csv", index=False)


if __name__ == "__main__":
    main()
