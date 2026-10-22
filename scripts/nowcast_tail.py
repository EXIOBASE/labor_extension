"""Project the staged labour account past the ILO end year, on the release tree.

    python scripts/nowcast_tail.py --release-root D:/indecol/Projects/MRIOs/EXIOBASE3/EXIOBASE_3_12 --check
    python scripts/nowcast_tail.py --release-root D:/indecol/Projects/MRIOs/EXIOBASE3/EXIOBASE_3_12 --overwrite

This is the committed form of the 2026-2028 nowcast that COVERAGE.md
describes (method chosen on holdouts there, 2026-09-18):

- ixi is projected from its own history with `io_utils` `level_trend`
  (median-robust slope from 2009, capped at 5% a year), every target year
  from the observed 1995-2025 history alone (`--history observed`, the
  default: steps = target - 2025). That is what `python -m
  io_utils.extension_nowcast --f-method level_trend --ixi independent`
  computes for the ixi side when the later years are not yet on the tree.
- pxp is derived from the projected ixi through the MRSUT product mix of
  the target year, the same route `desire_upload_prepper`'s
  `exiobase_labour_extensions_reformat.py` takes for the observed years
  (`converstion_from = 'i'`). `extension_nowcast` cannot do this: its CLI
  projects pxp and derives ixi, the reverse of this account's direction.
- F_Y is carried flat (it is all zeros: employment is not booked against
  final demand). unit.txt is copied from the last observed year.

`--check` writes nothing and reports the largest absolute difference
against the files already on the tree for each target year, which is how
the recipe was verified against the 2026-09-23 staging on 2026-10-15.

Run with a venv that imports io_utils and exiobase_meta (06-SUT_balance's
does; this repo's own venv imports io_utils).
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from io_utils.extension_convert import (
    mask_zero_output_columns, release_gross_output,
)
from io_utils.extension_io import (
    ExtensionYear, available_years, extension_year_dir, read_extension_year,
    write_extension_year,
)
from io_utils.extension_nowcast import (
    DEFAULT_END_YEARS_START, DEFAULT_MAX_CHANGE_PERC, project_level_trend,
)

EXTENSION = "labour"


def check_stressor_labels(F: pd.DataFrame, F_Y: pd.DataFrame, unit_path: Path) -> None:
    """Refuse a source year whose three files do not share one stressor index.

    The tail carries the last observed year's labels forward (F through the
    projection, F_Y flat, unit.txt verbatim), so whatever that year has is
    what 2026-2028 get. The reformat script writes the release labels
    ('Employment people: ...', 'Employment hours: ...') to all three files;
    a year where F still carries the workbook's 'Employment: ...' rows while
    unit.txt has the release ones (the 2026-10-22 staging) would be
    projected as it is, and the mismatch would reach three more years.
    """
    unit = pd.read_csv(unit_path, sep="\t", index_col=0)
    for name, index in (("F_Y", F_Y.index), ("unit.txt", unit.index)):
        if not index.equals(F.index):
            raise RuntimeError(
                f"{unit_path.parent}: {name} stressors differ from F "
                f"(only in F {sorted(set(F.index) - set(index))[:3]}, "
                f"only in {name} {sorted(set(index) - set(F.index))[:3]}); "
                "rerun desire_upload_prepper/exiobase_labour_extensions_reformat.py first")
    legacy = [s for s in F.index if str(s).startswith("Employment: ")]
    if legacy:
        raise RuntimeError(
            f"{unit_path.parent}: F carries the workbook labels {legacy[:2]}..., "
            "not the release 'Employment people: ...' ones")
    if F.index.name != "stressor":
        raise RuntimeError(f"{unit_path.parent}: F index is named {F.index.name!r}, not 'stressor'")


def product_mix(release_root: Path, year: int) -> pd.DataFrame:
    """(region, industry) x (region, product) product mix from MRSUT supply.

    Mirrors exiobase_labour_extensions_reformat.py: supply is products x
    industries, make = supply.T, C = make / industry output.
    """
    supply = pd.read_csv(
        release_root / "raw" / "MRSUT" / f"MRSUT_{year}" / "supply.csv",
        header=[0, 1], index_col=[0, 1], sep="\t",
    )
    make = supply.T
    ind_out = supply.sum(axis=0).replace(0, 1e-24)
    return make.div(ind_out, axis=0)


def mask_product_mix(T: pd.DataFrame, release_root: Path, year: int
                     ) -> tuple[pd.DataFrame, pd.Series]:
    """``T`` with no share on a product whose released gross output is zero.

    The core snaps a product with output under 1 EUR to x = 0 while the
    MRSUT supply still carries the sub-euro supply, so the mix hands such
    a product a sliver of its industry's labour and the release has an F on
    an x of 0. The mask is io_utils' ``mask_zero_output_columns`` on the
    release ``x.txt`` of the target year (the same call the energy
    converter and the labour reformat make), which zeroes exactly the
    products the core zeroed and renormalises each touched industry's row.
    Fails closed: a missing ``x.txt`` raises, it does not fall back to the
    unmasked mix. An industry whose every product has x = 0 keeps its row
    and is printed. Returns the masked mix and the per-industry share
    moved, for the caller to turn into labour moved.
    """
    try:
        x = release_gross_output(release_root, year, "pxp")
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"{exc}: the {year} pxp must be built by the core before the "
            "labour tail can mask the product mix by it"
        ) from exc
    masked, report = mask_zero_output_columns(T, x, label=f"labour tail {year}")
    print(f"  {year}: {report.n_zero_columns} products with x = 0; "
          f"{len(report.rows_touched)} industries supplied one"
          + (f"; {len(report.rows_fallback)} kept their row because every "
             f"product they supply has x = 0: {report.rows_fallback[:5]}"
             if report.rows_fallback else ""))
    return masked, report.share_moved


def project_year(ixi_panel: list[pd.DataFrame], years: list[int], target: int,
                 release_root: Path, *, max_change_perc: float,
                 end_years_start: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    F_ixi = project_level_trend(
        ixi_panel, years, max_change_perc=max_change_perc,
        end_years_start=end_years_start, overflow="clip",
        steps=target - years[-1],
    )
    T, share_moved = mask_product_mix(product_mix(release_root, target), release_root, target)
    moved = float((F_ixi.sum(axis=0).reindex(share_moved.index, fill_value=0.0)
                   * share_moved).sum())
    print(f"  {target}: {moved:,.6f} of {float(F_ixi.to_numpy(float).sum()):,.3f} "
          f"moved off zero-output products")
    F_pxp = F_ixi @ T
    F_pxp.columns.names = ["region", "sector"]
    F_pxp.index.name = F_ixi.index.name
    # Industries with labour but no output in the MRSUT of the target year
    # have an all-zero product-mix row, so their labour does not reach pxp.
    # The reformat script loses the same mass for the observed years (its
    # check is one-sided and only catches a gain). Report it; refuse only
    # if it is material.
    total = float(F_ixi.to_numpy(float).sum())
    lost = total - float(F_pxp.to_numpy(float).sum())
    if abs(lost) > 1e-9 * abs(total):
        zero_rows = T.index[T.sum(axis=1) == 0]
        lost_cols = F_ixi.reindex(columns=zero_rows).sum(axis=0)
        lost_cols = lost_cols[lost_cols != 0].sort_values(ascending=False)
        print(f"  {target}: product mix drops {lost:,.3f} of {total:,.3f} "
              f"({lost / total:.2e}) over {len(lost_cols)} zero-output industries; "
              f"largest {lost_cols.head(3).to_dict()}")
        if abs(lost) > 1e-3 * abs(total):
            raise RuntimeError(f"{target}: product mix loss {lost / total:.2e} is material")
    return F_ixi, F_pxp


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--release-root", type=Path, required=True)
    ap.add_argument("--years", type=int, nargs="+", default=[2026, 2027, 2028])
    ap.add_argument("--source-end", type=int, default=2025,
                    help="last observed year; years above it on the tree are ignored as sources")
    ap.add_argument("--max-change-perc", type=float, default=DEFAULT_MAX_CHANGE_PERC)
    ap.add_argument("--end-years-start", type=int, default=DEFAULT_END_YEARS_START)
    ap.add_argument("--history", choices=["observed", "sequential"], default="observed",
                    help="observed: every target year is projected from the observed "
                         "years only (steps = target - last observed); sequential: each "
                         "projected year joins the history for the next")
    ap.add_argument("--check", action="store_true",
                    help="write nothing; compare with the files already on the tree")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--out-root", type=Path, default=None,
                    help="write under this root instead of the release root "
                         "(same raw/Extensions/labour layout), for a run that "
                         "must not touch the tree")
    args = ap.parse_args(argv)
    root = args.release_root
    out_root = args.out_root if args.out_root is not None else root

    years = [y for y in available_years(root, EXTENSION, "ixi") if y <= args.source_end]
    if not years:
        raise SystemExit(f"no ixi years up to {args.source_end} under {root}")
    panel = [read_extension_year(root, EXTENSION, "ixi", y) for y in years]
    ixi_panel = [p.F for p in panel]
    FY = panel[-1].F_Y
    unit_path = panel[-1].unit_path
    check_stressor_labels(ixi_panel[-1], FY, unit_path)
    print(f"source years {years[0]}-{years[-1]} ({len(years)}); "
          f"{years[-1]} ixi total {ixi_panel[-1].to_numpy(float).sum():,.3f}; "
          f"stressors carried: {list(ixi_panel[-1].index)}")

    for target in sorted(args.years):
        F_ixi, F_pxp = project_year(
            ixi_panel, years, target, root,
            max_change_perc=args.max_change_perc,
            end_years_start=args.end_years_start,
        )
        tot = F_ixi.to_numpy(float).sum()
        print(f"{target}: ixi total {tot:,.3f}, pxp total {F_pxp.to_numpy(float).sum():,.3f}, "
              f"negatives {(F_ixi.to_numpy(float) < 0).sum()}, "
              f"nan {np.isnan(F_ixi.to_numpy(float)).sum()}")
        if args.check:
            for system, F in (("ixi", F_ixi), ("pxp", F_pxp)):
                folder = extension_year_dir(root, EXTENSION, system, target)
                if not (folder / "F.txt").exists():
                    print(f"  {system}: nothing on the tree to compare with")
                    continue
                old = read_extension_year(root, EXTENSION, system, target).F
                old = old.reindex(index=F.index, columns=F.columns)
                diff = np.nanmax(np.abs(old.to_numpy(float) - F.to_numpy(float)))
                print(f"  {system}: max abs diff against the tree {diff:.3e} "
                      f"(tree total {old.to_numpy(float).sum():,.3f})")
        else:
            for system, F in (("ixi", F_ixi), ("pxp", F_pxp)):
                folder = write_extension_year(
                    ExtensionYear(F=F, F_Y=FY, unit_path=unit_path),
                    out_root, EXTENSION, system, target, overwrite=args.overwrite,
                )
                print(f"  wrote {folder}")
        if args.history == "sequential":
            ixi_panel.append(F_ixi)
            years.append(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
