# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- **`scripts/nowcast_tail.py`: the 2026-2028 projection as a committed
  command (2026-10-15).** Until now the tail nowcast that COVERAGE.md
  describes had no script: it was run by hand on 2026-09-18 and 09-23.
  The script projects ixi from the observed 1995-2025 years with
  `io_utils` `level_trend` (median-robust slope from 2009, capped 5%/yr,
  every target year from the observed history alone), derives pxp from
  the projected ixi through the MRSUT product mix of the target year (the
  route the observed years take in `desire_upload_prepper`), carries F_Y
  flat and copies `unit.txt`. `--check` compares with the files on the
  tree without writing: run on 2026-10-15 against the 09-23 staging it
  reproduced all three ixi years to 1.3e-7 (max abs cell difference).
  pxp could not be compared, because the MRSUT the product mix comes from
  was rewritten by the 08 core build the same morning. It also reports
  the labour that the product mix drops for industries with no output in
  the target year's MRSUT (44 industries, 4e-6 of the total on the 10-15
  MRSUT, led by PL water transport); the reformat script loses the same
  mass silently for the observed years, since its check is one-sided.
  Run it with a venv that imports `io_utils` and `exiobase_meta`
  (06-SUT_balance's does).

  **Stressor-label guard (2026-10-22).** The tail carries the last
  observed year's labels into 2026-2028 (F through the projection, F_Y
  flat, `unit.txt` verbatim), so a 2025 whose `F.txt` still has the
  workbook's `Employment: ...` rows while its `unit.txt` has the release
  `Employment people: ...` rows (the 2026-10-22 staging, where the
  incubator's fix step did not run) was projected as it was. The script
  now refuses a source year whose F, F_Y and unit.txt indices differ,
  whose F carries `Employment: ...` labels, or whose index is not named
  `stressor`, and prints the stressors it carries. `--check` on the
  current tree stops with that error until
  `desire_upload_prepper/exiobase_labour_extensions_reformat.py` (which
  now writes the release names itself) has been rerun.

  **Zero-output product mask (2026-10-22).** The pxp side was derived
  through the raw MRSUT product mix, which can hand a product the core
  snapped to x = 0 (output under 1 EUR) a sliver of its industry's labour,
  the defect 00-qa found in the energy and nutrient converters. The mix
  now goes through io_utils' `extension_convert.mask_zero_output_columns`
  with the release `raw/IOT_txt/IOT_<year>_pxp/x.txt` of the target year
  (`release_gross_output`), the one implementation the other converters
  call: products with x = 0 get no share and each touched industry's row
  is renormalised, so the pxp total still equals the ixi total. A missing
  `x.txt` raises; there is no unmasked fallback. The labour moved is
  printed per year. On the current tree for 2026 it finds nothing to do:
  the MRSUT_2026 supplies none of the 2,035 products with x = 0, so
  before and after have 0 cells on zero-output products and the same
  total, 11,594,332.268615 (checked by driving `project_year` directly,
  since the CLI stops at the label guard above until the reformat has
  been rerun). `--out-root` writes the projected years under another
  root with the same `raw/Extensions/labour` layout, for a run that must
  not touch the tree.

### Changed

- **Repointed at EXIOBASE 3.12 and rebuilt (2026-09-17/18).**
  `sut_version_folder` is now `EXIOBASE_3_12`, `sut_csv_root` follows it
  (note the folder case: 3.11.2 spells it `raw/SUT/current`, 3.12 spells it
  `raw/sut/current`), and the handoff workbook is
  `final_labor_SUTs_3_12.xlsx`.

  **The block was never in this repo.** The 3.12 SUT export had dropped the
  12 value-added rows (`w01`..`w04.d`) that `usebpdom.csv` has always
  carried below its 200 product rows, so the `w03.a/b/c` wage vectors the
  salary split reads did not exist on the 3.12 tree at all. Fixed in
  `06-SUT_balance` (`scripts/export_sut_legacy_csv.py`, commits `1c54301`
  and `d2705e8`) and retrofitted onto all 1,666 files.

  Build result, 2019 against the 3.11.2 run: world employment **3.333 bn
  people** and **2,210 hours per person**, both identical, which is the
  expected shape since ILO sets the control totals and the SUTs only decide
  how they are spread over EXIOBASE industries and skill levels. The skill
  mix moves a little, -1.1% to -1.4% for low and medium and +1.1% to +6.5%
  for high, and that traces to the input: the 3.12 wage bill is 42.23% high
  skilled against 3.11.2's 41.29%, and 50.11% medium against 51.08%.
  31 sheets (1995-2025), 12 stressors x 7,987 columns, no NaN and no
  negative cells.

  Checked before trusting the split: **no (region, ILO mapping group) cell
  has a zero wage bill** in 1995, 2005, 2019, 2025 or 2028, across all 49
  regions and all 14 groups, so the split's division by the group wage bill
  is not degenerate on this vintage. 3.12 is cleaner here than 3.11.2, where
  CN, RU and JP each had one zero group in 2019.

  Two caveats worth carrying forward. The series still ends at **2025**, the
  ILO end year, so 2026-2028 have no labour against a monetary spine that
  reaches 2028. And this build reads the **2026-09-15** SUT vintage: a full
  04 to 06 to 08 chain rerun was started on 2026-09-17, so it will need a
  rerun on the reconciled chain, the same as the energy account. The wage
  vectors actually consumed are fingerprinted in
  `indecol/data/labour/final_table/sut_wage_provenance_3_12.json` (world
  wage bill by skill and year, plus a hash), recorded because that rerun
  will overwrite the files. The SUT tree did not change during the run.

### Fixed

- **The 2006-2007 skill seam (to-do C7-3, 2026-10-27).** World low-skilled
  people and hours jumped +42% to +50% between 2006 and 2007 (4 of the 12
  stressors) while total employment moved +1.6%, and 00-qa
  `cells.breaks.extension_jump` counted 408 pxp cells over 10x at
  2006-2007. The source is not ILO, which only sets the totals: it is the
  SUT skill split of compensation of employees (`w03.a/b/c`) that the
  salary split uses to divide each industry's employment over skill levels.
  06-SUT_balance fills those rows from the legacy `coe-shares.mat`, and that
  file changes structure in one year for CN, IN, ID and WA (WA carries ID's
  shares) between 2006 and 2007: CN agriculture goes from 0.4% low skilled
  and 99.4% medium to 12.1% and 84.9%, public administration from 93% high
  skilled to 44%. WF (which carries ZA's shares) has the same kind of break
  between 2007 and 2008 (agriculture 31% to 47% low skilled), which made
  world low-skilled people rise a further 11% at 2007-2008. The same seam is
  in 3.11.3 (+41% and +46% for low-skilled male and female people).

  New `workforce_salary/skill_splice.py`, called by the salary split right
  after it reads a SUT: for each region in `config.yaml`
  `skill_split_splice` (CN, IN, ID, WA at 2007; WF at 2008) and each year
  before its break year, every industry keeps its own wage bill of the year
  and takes its low/medium/high shares from the break year's SUT, the
  structure the SUT carries for every later year. Industry totals and every
  ILO control total are unchanged; only the skill split before the break
  moves. Industries with no wage in the break year keep their own split.

  Verified without the full build: the salary split rerun for CN, IN, ID
  and WA in scratch with the splice off reproduces the production 2006
  split to 1.4e-12; with it on, it gives the regional skill totals that the
  splice predicts when applied to the staged 3.12 ixi account (people and
  hours are split over skills within region x industry x sex by the same
  shares, and hours per person do not depend on skill). World low-skilled
  people, before and after, 2005 / 2006 / 2007 / 2008, in 1000 p:
  224,281 / 232,126 / 333,678 / 370,804 before, 349,500 / 358,350 /
  366,643 / 370,804 after. Low-skilled hours 501,498 to 727,542 M.hr at
  2006-2007 before, 764,171 to 784,007 after. Cells over 10x at 2006-2007
  on ixi: 402 before, 0 after. World totals by year unchanged. WF was
  checked by the analytic route only.

  This is a fix in the labour account only. The SUT `w03.a/b/c` rows
  themselves still carry the break; the root fix belongs in
  06-SUT_balance's `coe-shares.mat` input. The US 2000-2001 and IT
  1999-2000 breaks in the same file are spliced too (next entry).

- **US and IT skill breaks spliced (to-do C7-3 follow-up, 2026-10-27).**
  Measured on the 3.12 SUT for all 49 regions, 1995-2025: for each
  region-year, the largest one-year move in the economy-wide low, medium or
  high share, with industry skill shares weighted by the staged ixi people
  (which do not depend on the split). Over the 1,470 region-years the
  median move is 0.28 points, the 95th percentile 1.68, the 99th 4.83 and
  the maximum 12.84. Fifteen region-years move more than 5 points. Seven are
  isolated steps (the region's next largest move is under 2 points): WF
  2008 (12.8), US 2001 (12.6), IT 2000 (12.0), CN 2007 (6.9), ID 2007
  (5.6), IN 2007 (5.4), WA 2007 (5.0), plus WM 1996 (5.3, next 1.6), which
  is the 1995-1996 step and is left for review. The other seven (LU 2004,
  RO 2004 and 2008, AT 2004, BE 2001 and 2004, ZA 2004, 5.5-6.5 points)
  sit in series that move in several steps and are not spliced.

  `config.yaml` `skill_split_splice` gains `US: 2001` and `IT: 2000`. US
  economy-wide people-weighted medium / high shares go from 38.3 / 58.0% in
  2000 to 50.9 / 45.4% in 2001 (US fishing medium-skilled people 36.3 to
  16.3 thousand, high 7.3 to 25.2); IT from 57.9 / 34.6% in 1999 to 47.2 /
  46.6% in 2000. Checked by the analytic route on the staged 3.12 ixi
  account (no build): US people medium / high, 1000 p, 1998 / 1999 / 2000 /
  2001: 52,403 / 53,336 / 54,014 / 71,751 and 78,957 / 80,458 / 81,787 /
  64,010 before; 69,702 / 70,743 / 71,843 / 71,751 and 62,117 / 63,067 /
  63,975 / 64,010 after. IT medium / high, 1998 / 1999 / 2000: 12,005 /
  11,986 / 9,880 and 6,903 / 7,158 / 9,747 before; 9,622 / 9,730 / 9,880
  and 9,441 / 9,541 / 9,747 after. US fishing 2000 after: 17.1 medium,
  26.4 high. Every industry's people and hours totals are unchanged (largest
  column difference 6e-11). Needs the labour rebuild with the CN-WF splice.

- **The workbook writes the release stressor names.** The handoff workbook
  labelled the people rows `Employment: <skill> <sex>` while every release
  `unit.txt`, `exio_hatcher` and the shipped `employment` account use
  `Employment people: <skill> <sex>`; `desire_upload_prepper` renamed them
  on the way in (since 2026-10-22). `working_hours/average_working_hours.py`
  (and the legacy `hours_split.py` and `average_working_hours_modified.py`)
  now write `Employment people: ...` directly. The reformat's rename map
  passes these through unchanged.

- **`read_sut_csv` accepts both spellings of the SUT row axis.** The salary
  split selects rows with `df['Row']`, which assumes the SUT CSV names its
  row axis `Row`, as 3.11.2 does in all three files. The 3.12 export left it
  unnamed, so pandas called that column `Unnamed: 0` and every wage lookup
  raised `KeyError`. Reads now normalise the first column to `Row` and raise
  if it is neither, which is what the exporter's own fix (`d2705e8`) will
  make unnecessary at source on the next full export. Verified reading both
  trees.

- **The hours stage recursively forked itself and exhausted memory.**
  `run_windows.py` ran the pipeline at module level with no
  `if __name__ == "__main__":` guard. The hours stage used
  `concurrent.futures.ProcessPoolExecutor`, which on Windows spawns children
  that re-import `__main__`, so every worker re-ran the whole driver: another
  937k-row workforce build and another 22-worker pool, recursively. One
  invocation entered stage 1a thirteen times before dying with
  `BrokenProcessPool`. The pipeline now lives in `main()` behind a guard with
  `multiprocessing.freeze_support()`.
- **The hours stage now runs end to end for the first time.** It had never
  reached its own output: `labor.py` could not call it, and once called it died
  at the first of a long chain of defects in code that had never executed. The
  handoff workbook `final_labor_SUTs_3_11_2.xlsx` is now produced: 31 sheets
  (1995-2025), 12 stressors x 7,987 columns (49 regions x 163 sectors). Global
  hours run 5.18 bn M.hr (1995) to 7.79 bn (2025) with hours per person between
  2,167 and 2,204 in every year, and no region carries employment with zero
  hours. Beyond the items below, the fixes were: the population weights, the
  RoW and Taiwan infills and the Ukraine carry-forward rewritten as merges with
  their unguarded `float(...to_string(...))` lookups made to skip rather than
  raise; four lines inside the Ukraine loop deleted, being a stale copy of the
  Taiwan block that read `a` and `t` from a loop that no longer preceded it and
  appended rows for an arbitrary country and year; `hourSplit` reading the ILO
  category from the concordance's `ISIC REV 4_ILO_Alteryx` column, as the RoW
  branch already did, instead of cutting `Summary` at the first dot to get bare
  ISIC letters that aggregation had already collapsed; and the final-table row
  build guarded on both sides, since it is fed by two different region lists.
- **The tail of `working_hour()` was nested one level too deep.** The second
  year loop, the whole final-table build and the handoff workbook write all sat
  inside the first year loop, so after computing 1995 it tried to write all 31
  sheets and raised `KeyError: 1996`; had it got past that it would have
  rebuilt everything 31 times over.
- **The hours workbook was written and read under different names**
  (`hours_split_newSUTS.xlsx` versus `hours_split.xlsx`), so the read could only
  ever have found a file left by an earlier run. One constant now.
- **Hours were never extrapolated past 2023, so a third of the world published
  zero hours.** `regression_r(..., 1995, 2023)` was hardcoded. It is the step
  that extends each country's series across the build range, and the raw ILO
  hours thin sharply at the end (3,019 series in 2023 against 1,739 in 2025, of
  5,394 rows). Past 2023 nothing was filled, so any region without a raw
  observation got nothing: six regions carrying 28% of global employment
  published zero hours for 2024 (AU, CA, CN, ID, JP, ZA) and eight carrying 32%
  for 2025 (plus LU, WM). Employment was unaffected because the workforce build
  nowcasts independently, so the two sides disagreed. Now the config range.
  Measured effect: global hours +41.9% in 2024 and +47.8% in 2025, with implied
  hours per person moving from 1,529 and 1,469 to 2,169 and 2,171.
- **`time != 2023` was dropped unconditionally from the hours series.** It
  dated from when 2023 was the ragged end of the data; 2023 is now a complete
  year (5,243 rows, as every year from 1995) in a range running to 2025, so the
  drop punched a hole through the middle and left every 2023 sector cell at
  zero. Now the `DROP_YEARS` constant, empty; set it to `{2023}` to restore.
- **Countries reporting hours only at aggregate level were discarded.** The
  first filter keeps `ISIC3|ISIC4`, so a country publishing only the ILO
  aggregate breakdown was dropped and reached the extension as a workforce with
  zero hours. Canada is the case that matters: 1,800 rows of hours, both sexes,
  1976-2025, none of it by ISIC (96 countries report ISIC4 hours; Canada is not
  one). The original carries the author's note about it, untranslated:
  `VERIFIER SI CANADA EST DANS LA NOUVELLE LISTE`. `add_isic4_from_aggregates`
  now copies each aggregate's hours onto the ISIC sections it covers, using the
  mapping read off the export's own `classif1.label` text. Coarse - the eight
  market-service sections share one value - but it is the country's own data.
  Written generically, it also picks up Paraguay. Canada comes out at 1,829
  hours per person for 2024, between Germany (1,726) and the United States
  (1,955).
- **`combine` stopped stripping the ISIC revision digit, which silently killed
  the whole aggregation stage.** `combine` is where `ECO_ISIC4_A` becomes
  `ECO_ISIC_A`, the namespace everything downstream uses:
  `aggregate_isic.py` looks up `ECO_ISIC_D`, `ECO_ISIC_E` and 42 more names,
  and those strings appear nowhere else in the repo. The rename was lost when
  the row append was rewritten: the original
  `...append(pd.Series([code, sex, classi.translate({ord(k): None for k in
  digits}), ...]))` became `new_table_150222.loc[len(...)] = new_line` carrying
  a plain `classi`, and `from string import digits` was commented out to match.
  Every lookup in `aggregate` therefore missed, every year hit its `continue`,
  and `aggregate` returned its input untouched. Restored in
  `combine_isic_3_4_vectorised`. It cannot create duplicate keys: only
  `ECO_ISIC4_*` rows are ever emitted, so there is nothing to collide with.
- **`aggregate` would have crashed the moment it did anything.** It builds its
  output with `DataFrame.append`, removed in pandas 2.0; this environment runs
  2.3.3. Only the defect above kept it from being reached. Replaced by
  `aggregate_isic_vectorised`.
- **`task_S` weighted two of its four sources by the wrong population.** Its
  normal-year branch reads `ECO_DETAILS_LMN` for both `pop_G` and `pop_J`,
  where every analogous task (and `task_S`'s own Ukraine-2022 branch) reads
  `ECO_DETAILS_G` and `ECO_DETAILS_HJ` - the only one of the 22 conversions
  where a task disagrees with itself, checked mechanically. **Corrected**
  (2026-08-03) after quantifying: 1,372 values, 4.8% of converted rows, mean
  absolute change 2.7%, median 1.6%, `ECO_ISIC4_S` mean 39.52 -> 40.45 h/week.
  Only pre-2009 years reach the accounts, as combine takes native ISIC4 from
  2009 on.
- **Kosovo contributed no converted hours at all.** The code rewrote `KOS` to
  `XKX` *before* looking up its ISIC3 rows, which are filed under `KOS`, so
  nothing matched. The relabel belongs after the lookup, and only `XKX` maps to
  an EXIOBASE region (WE). **Corrected in the converter**, which now yields 10
  rows for the year 2000. **They do not reach the accounts**: `combine`
  restricts to keys present in `hour_list`, and the hours export labels Kosovo
  `KOS`, so the newly-emitted `XKX` rows are dropped immediately after. The net
  effect on published numbers is nil. Finishing it means relabelling Kosovo at
  ingestion so every stage agrees; left undone deliberately, being 10 rows in
  one year for a region that aggregates into RoW Europe. Kosovo's post-2009
  hours were never affected, coming from native ISIC4.
  `REPRODUCE_ORIGINAL_DEFECTS` in `isic3_to_isic4_vectorised` restores both,
  and the equivalence test sets it so it still compares like for like.

- **The workforce build produced empty tables.** The retired ILO bulk
  download labelled the ISIC-Rev.4 employment breakdown `ECO_DETAILS_*`; the
  current ILOSTAT rplumber API labels the identical breakdown `ECO_ISIC4_*`
  (same suffixes: A, B, C, DE, F, G, HJ, I, K, LMN, O, P, Q, RSTU, TOTAL).
  Nothing downstream was updated, so on the new export every
  `ECO_DETAILS_*` filter matched zero rows:
  `classif_detail` came out empty, the salary split ran over an empty frame,
  and `workforce_total_iso3.csv` / `workforce_total_exio3.csv` were written
  as header-only files. `workforce_salary/workforce.py` now normalises
  `classif1` on ingestion (`normalise_classif1`) and raises if the expected
  14 detail codes plus TOTAL are not present afterwards, so a further source
  rename fails loudly instead of silently emptying the outputs. Only the
  ISIC4 family is renamed; `ECO_SECTOR_*` (used by `from_cia_to_ilo.py`) and
  `ECO_AGGREGATE_*` are untouched, and an export already using
  `ECO_DETAILS_*` passes through unchanged. Verified on the downloaded
  export: `ECO_DETAILS_TOTAL` 0 -> 28,938 rows, `classif_detail` 0 -> 14
  codes, all 14 concordance codes matched.
- **The salary split read the wrong EXIOBASE version.**
  `workforce_salary/salary_split_ray.py` had `EXIOBASE_3_10_1` hardcoded for
  both SUT inputs, and `config.py`/`config.yaml` (added earlier) were not
  actually wired to anything. The path now comes from
  `paths.sut_csv_root` and points at `EXIOBASE_3_11_2/raw/SUT/current/`
  (same `{REG}_{year}_usebpdom.csv` / `_sup.csv` naming and same `w03.a/b/c`
  wage rows, verified against 3.10.1).

### Changed

- **`aux/` renamed to `auxdata/`: Git on Windows could not see it.** `AUX` is a
  reserved DOS device name, so Git for Windows rejects any path under a
  directory called `aux` in `verify_path()` (gated on `core.protectNTFS`).
  Every `git status` on Windows reported the nine tracked files there as
  deleted while they sat intact on disk, and GitHub Desktop showed the same,
  one stray `commit -a` away from deleting them for real on the remote. Python
  was never affected (a reserved name is only rejected as the final path
  component), so the pipeline always read them fine and no output is affected.
  Reproduced in a clean repo: `git hash-object aux/f.txt` fails, `auxx/f.txt`
  with identical content succeeds. All eleven files moved as pure renames,
  blobs byte-identical, and the 34 path references across the scripts, config
  and docs were repointed.
- **Two workarounds that had accumulated around this are gone.** A
  sparse-checkout rule (`/*`, `!/aux/`) had been added to hide the phantom
  deletions; it only ever applied to two of the eleven files, because Git
  could not stat the other nine to set their skip-worktree bits, so it
  silenced nothing and blocked `git add` on those paths. Sparse checkout is
  now disabled (it was excluding nothing else). `aux/region_EXIO3.ods` was one
  of the two files it did flag, and it had gone missing from disk entirely at
  some point, invisible because Git could not look; it has been restored from
  the object database into `auxdata/`.
- **ISIC3 -> ISIC4 conversion rewritten from 3,476 lines to a lookup table.**
  `working_hours/isic3_to_isic4.py` gave each of the 22 ISIC4 targets its own
  function, and within each, every combination of "which ISIC3 sources are
  non-zero this year" was written out as a separate branch (`task_C` has five
  sources and 31 branches). All of it is one formula: the population-weighted
  mean of the target's ISIC3 sources over those that are non-zero, since a
  zero source drops out of both sums and a lone source makes the weights
  cancel. `working_hours/isic3_to_isic4_vectorised.py` holds that formula plus
  a 22-entry concordance table.

  It was also quadratic. The value lookup sat five loops deep and rescanned
  all 24,599 ISIC3 rows each pass; the population lookups rescanned the
  937,251-row workforce frame, at 89 ms each. Measured on this machine:
  236,544 population lookups (5.9 h) and 2,059,904 hours lookups (1.7 h),
  7.5 h of serial lookup cost, which is what the 22-way fan-out was there to
  hide. Each worker was handed its own pickled copy of the workforce frame,
  766 MB deep, so 16.8 GB across the pool before the recursion multiplied it.

  The replacement runs the full 88-country conversion in **0.42 s** in a
  single process. `tests/test_isic3_to_isic4_equivalence.py` runs the original
  task functions and the rewrite over the same subset and compares every
  value: 3,122 values across all 22 targets agree to 1.6e-16, i.e. floating
  point noise. The old module is kept as the reference implementation the test
  compares against.

  Two behaviours of the original are preserved deliberately and flagged rather
  than fixed: `task_S` above, and Kosovo, whose code was rewritten `KOS` ->
  `XKX` *before* its ISIC3 rows were looked up, so they never matched and
  Kosovo contributed no converted hours at all.

- **`combine` and `aggregate` vectorised.** `combine` ran four nested loops over
  `hour_list`'s unique ref_area x sex x classif1 x time (roughly 180 x 2 x 38 x
  30), doing a four-condition full-frame scan per cell and appending one row at
  a time with `.loc[len(df)] = ...`, which reallocates on every append, fanned
  out over ray to hide the cost. About half those cells could never match: the
  `classif1` loop covers the `ECO_ISIC3_*` codes, which neither input frame
  carries. It is one priority merge (ISIC3-derived before 2009; native ISIC4
  from 2009, falling back to ISIC3-derived), now in
  `combine_isic_3_4_vectorised`: **3,674 rows in 0.01 s against 31 s, on 3 of
  178 countries.** `aggregate` had the same shape, 44 full-frame scans per
  (country, sex, year); now in `aggregate_isic_vectorised`.

  `tests/test_combine_equivalence.py` compares against the real ray
  implementation: identical row set, identical `source` tags, values identical
  to the original's 6-decimal read-back (`float(df.to_string(...))` is exactly
  `round(v, 6)`, verified against the formatter). `tests/`
  `test_aggregate_equivalence.py` compares against a line-by-line transcription
  of the original loop, since the original cannot execute on pandas 2: 2,371
  rows, sources identical, carried-through rows exact, built rows within
  4.2e-07 of the 5.01e-07 bound that truncation allows.

  Two defects in `aggregate` were **corrected for this build** on the owner's
  decision (2026-08-01). Both are switchable at the top of
  `aggregate_isic_vectorised`; set them back to `ORIGINAL_YEARS` / `True` to
  reproduce 3.10 semantics:
  - `AGGREGATE_CASCADE_SKIP`, now `False`. The blocks were chained with
    `continue`, not `pass`, so if D and E were both absent for a (country, sex,
    year) then HJ, RSTU and LMN were skipped too, however complete their own
    components were.
  - `AGGREGATE_YEARS`, now the config range. It looped `range(1995, 2020)`
    while dropping the component rows for *all* years, so from 2020 on eleven
    ISIC letters vanished and no aggregate replaced them: a six-year hole in D,
    E, H, J, L, M, N, R, S, T and U against data reaching 2025.

  Measured on the three-country test input, the two corrections together add
  136 rows and lose none, and **no value that the original produced changes**.

- The salary-split year range comes from `config.yaml` (`years.start` /
  `years.end`, both inclusive) instead of three separate hardcoded
  `range(1995, 2023)` literals. Default stays 1995-2022: the ILO estimates
  now reach 2025 and the 3.11.2 SUTs reach 2028, but the CIA / hand-compiled
  supplementary countries stop at 2022 (`from_cia_to_ilo.py` loops
  `range(1991, 2023)`, and `auxdata/Exiobase_Population_Data_not_found.xlsx` has
  year columns 1990-2022 for its 21 entities). Extending past 2022 needs
  those inputs extended first. `LABOR_YEARS=2020` or `LABOR_YEARS=1995-2010`
  overrides the range for a smoke test.
- `ray` is imported lazily in `salary_split_ray.py` and the year loop falls
  back to a sequential run with `LABOR_NO_RAY=1`. The remote function body is
  unchanged (`ray.remote(calcul_year)` wraps the same function), so the ray
  and no-ray paths compute identically. This makes single-year testing
  possible without a ray install.
- Moved the hardcoded absolute SUT source path out of
  `workforce_salary/salary_split.py` into a repo-root `config.yaml`
  (`paths.salary_sut_root`). The script now imports the value from a new
  repo-root `config.py`, which loads `config.yaml` via the shared
  `io_utils.config` loader. The default resolves to exactly the path used
  before. Override per machine with a gitignored `config.local.yaml`.

### Added

- Repo-root `config.py` and `config.yaml` for path configuration.
- `.gitignore` (ignores `config.local.yaml`, caches, and generated data).
