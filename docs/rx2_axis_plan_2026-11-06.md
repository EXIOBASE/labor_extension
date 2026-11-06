# Labour account on the rx2 axis (3.12.0 rx2), plan of 2026-11-06

Decision (Richard, 2026-11-06): 3.12.0 rx2 gets the full e3 account set, so
labour is built on the 159-region rx2 axis by the same code that builds e3,
with the axis as a parameter. No copy of the pipeline.

## What the e3 account is and how it is built

- 12 stressors (not 13): 6 `Employment people: <skill> <sex>` in 1000 p, 6
  `Employment hours: <skill> <sex>` in M.hr (checked on
  `EXIOBASE_3_12_0/raw/Extensions/labour/pxp/2019/unit.txt`). F_Y is all zero.
- labor_extension `run_windows.py`: stage 1 builds the ILO workforce by ISO3
  (plus CIA and hand-compiled supplements), maps each ISO3 to its region with
  country_converter `EXIO3`, aggregates, and splits each region's ILO ISIC4
  totals onto the 163 industries by the SUT wage rows `w03.a/b/c`
  (`workforce_salary/salary_split_ray.py`, ray over years). Stage 2
  (`working_hours/average_working_hours.py`) turns people into hours with ILO
  and Eurostat weekly hours: single-country regions use their own hours,
  the five W buckets the population-weighted average of their members, TW the
  WA average. Output: `final_labor_SUTs_3_12.xlsx` (one sheet per year
  1995-2025, 12 x 7,987 columns).
- desire_upload_prepper `exiobase_labour_extensions_reformat.py` writes ixi and
  derives pxp through the MRSUT product mix, masked by the release `x.txt`.
- `scripts/nowcast_tail.py` projects 2026-2028 on the tree (ixi by
  `io_utils` `level_trend`, from 2009, cap 5%; pxp through the product mix of
  the target year). On e3 labour the nowcast years are 2026-2028 (ILO ends
  2025), not 2024-2028.

## Where the 49-region axis is baked in

1. ISO3 to region: `workforce_salary/ref_label.py` (all ILO rows),
   `workforce_salary/from_cia_to_ilo.py` (3 call sites),
   `working_hours/average_working_hours.py` (hours rows, RoW infill).
2. SUT root (`config.yaml` `paths.sut_csv_root`), handoff workbook name,
   skill splice regions (`skill_split_splice`, e3 codes).
3. Hours stage: the TW special case (TW takes WA's hours), the vacation table
   grouped by `EXIO3`, the final region list `auxdata/region_EXIO3.csv`.
4. Output folders: `d:/indecol/data/labour/{data,final_table}` hardcoded in
   `run_windows.py`, and about 15 debug CSVs written into the repo root (cwd).
5. Reformat and tail: the MRSUT supply and `meta.xlsx` classification, both
   49-region only. rx2 has no MRSUT; it has per-country `raw/sut/current`
   supply tables and `raw/IOT_txt/IOT_<y>_pxp/x.txt`.

## Design

One axis setting, `LABOR_AXIS` (`e3` default, `rx2`), set by
`run_windows.py --axis` before anything imports `config`, and passed to the
ray workers in their runtime env. `config.py` resolves everything axis
dependent from it; `config.yaml` gets an `axes.rx2` block:

- `sut_csv_root`: the rx2 tree `raw/sut/current/`.
- `final_table_dir` and `work_dir`: `D:/data/labor_extension/EXIOBASE_3_12_0_rx2/{final_table,work}`.
  The rx2 run refuses any output dir without `rx2` in it, and never
  downloads (it reads the e3 run's ILO/Eurostat downloads in
  `d:/indecol/data/labour/data` read-only).
- `final_labor_filename`: `final_labor_SUTs_3_12_0_rx2.xlsx`.
- `skill_split_splice: inherit`: each rx2 region takes the splice year of its
  e3 parent (country_converter `EXIO3` of the ISO3, a W bucket is its own
  parent). Measured on the rx2 SUTs: all 69 rx2 regions whose parent is
  spliced on e3 (CN, IN, ID, WA, WF, US, IT) show the step at the parent's
  break year (2.5 to 14.0 points, for 60 of them their largest move), because
  06 fills their `w03.*` rows from the parent's coe-shares.
- Region mapping: e3 keeps the literal country_converter call; rx2 uses
  `io_utils.classification.iso3_to_region("rx2")` (00-class
  `exiobase_rx2.csv`), with codes it does not know (obsolete ones such as CHI)
  falling into their EXIO3 W bucket, else `not found` as on e3. The internal
  column stays named `EXIO3` and holds the axis region code.
- Hours stage: the TW rule is generalised to "a single-country region whose
  country has no hours takes the regional average of its e3 parent bucket".
  On e3 the map is `{TW: WA}` and the average is the existing `av2`, so e3 is
  unchanged. On rx2, 22 countries have no ILO hours (TWN, CMR, TCD, GNQ, ERI,
  LBY, STP, SSD, TGO, CUB, CUW, GRL, SUR, TTO, BHR, KWT, PRK, OMN, SAU, SYR,
  TKM, UZB); they take the population-weighted average of every country in
  their e3 bucket (TWN: WA), which is what they got on e3 as bucket members.
  The rx2 W regions keep the members' average as on e3. Vacation days (read
  but not used in the formula) are grouped by axis region, with the e3
  bucket as fallback. The final region order is `region_codes("rx2")`.
- Ukraine: on rx2 UKR is its own region, so the e3 code that carries UKR's
  2021 population into 2022 inside the WE average is guarded to run only when
  UKR is in a bucket. UKR is zero from 2022 on both axes (ILO stops; the
  known e3 defect in COVERAGE.md).
- Performance: the salary split and the hours split looked every value up
  in the full all-region table, so a region-year cost about a minute and grew
  with the region count (rx2 estimate: 20-35 h on 4 workers). Both loops now
  work on the region's own rows and write them back; the arithmetic is the
  same statement for statement (the legacy `float(df.to_string())` rounding
  included). Checked bit for bit on e3 AT and WA 2019: identical frame, 175 s
  to 24 s.
- Parallelism: ray's raylet would not start on this machine on 2026-11-06
  (node startup timeout, twice). The year function moved from a closure to
  module level (`calcul_year_impl`, body unchanged) so a process pool can run
  it: `LABOR_NO_RAY=1 LABOR_PARALLEL=process LABOR_WORKERS=4`. ray stays the
  default. Check runs can redirect output with `LABOR_FINAL_TABLE_DIR` and
  `LABOR_WORK_DIR`.
- Reformat (desire_upload_prepper) and tail (labor_extension
  `scripts/nowcast_tail.py`) take `--axis rx2`: columns from
  `io_utils.classification.sector_layout/final_demand_layout("rx2")`, product
  mix from `io_utils.sut.per_country_supply.product_mix(..., axis="rx2",
  x=release x.txt)` (sparse block diagonal, masked by the rx2 x, concordance
  fallback for unsupplied industries). Output to
  `EXIOBASE_3_12_0_rx2/raw/Extensions/labour/{ixi,pxp}/<year>/`, 1995-2025
  from the workbook, 2026-2028 by the tail, layout as the rx2 land account.

## Proof that e3 is unchanged

The e3 SUTs were last written 2026-10-29 19:57 and the production labour run
(`d:/indecol/data/labour/final_table`, staged on the tree 10-30 03:04) started
right after on the same downloads, so the modified code run on e3 into the
scratchpad must reproduce the production intermediates exactly. Done
2026-11-06, `--axis e3` with `LABOR_FINAL_TABLE_DIR`/`LABOR_WORK_DIR` in the
scratchpad:

- Stage 1 (workforce): `complete_table.csv`, `table_workforce_by_EXIO3.csv`,
  `table_workforce_by_ISO3.csv`, `workforce_total_exio3.csv` byte-identical
  (sha1) to production; `workforce_total_iso3.csv` byte-identical to the
  repo-root copy.
- Salary split: all 49 regions for 2005, 2006, 2007 (across the CN/IN/ID/WA
  2007 splice), process pool, sheet for sheet `assert_frame_equal(check_exact)`
  against production `split_workforce_by_skill_newSUT.xlsx`: identical. Also
  AT and WA 2019 against the unmodified code: identical.
- Hours stage, all 31 years, from the production split workbook, serial
  stand-in for ray: every debug CSV (hours_ini, isic3/4, pivots) byte-identical
  to the repo-root copies of the production run, `hours_fallbacks.csv`
  byte-identical, and `hours_split_newSUTS.xlsx` and
  `final_labor_SUTs_3_12.xlsx` identical in all 31 sheets (exact compare;
  the xlsx bytes differ only by the zip timestamps).
- `tests/test_axis.py` pins the e3 settings (SUT root, workbook, splice,
  output folders, region list, the region call equal to country_converter's).

Not run on e3: the reformat (its e3 path is untouched: the `--axis` branch
returns before any e3 statement) and `nowcast_tail.py` without `--axis`
(e3 path unchanged, the new code is behind `axis != "e3"`).

Two runtime problems found on the way, both machine state, not code: ray's
raylet would not start (object store `CreateFileMapping` failed, Windows error
1450, with about 15 GB free and a 26 GB job running), and with a smaller store
a worker died with an access violation. The salary split now has a process
pool (`LABOR_PARALLEL=process`) and the four hours modules that call ray take
a serial stand-in under `LABOR_NO_RAY=1` (`working_hours/serial_ray.py`,
arguments deep-copied per call as a ray task would get them). The hours
modules' ray worker count now honours `LABOR_WORKERS`.

## Run order (rx2)

1. `run_windows.py --axis rx2` with `SKIP_DOWNLOAD=1`, `LABOR_WORKERS=4`.
2. Reformat `--axis rx2` (06-SUT_balance venv: io_utils, exiobase_meta, scipy).
3. `nowcast_tail.py --axis rx2 --release-root <rx2 tree>`.
4. Compare: rx2 summed to the 49 e3 regions against the e3 tree, per
   stressor, world and worst regions; pxp against ixi totals.

## Outcome

(filled in after the run)
