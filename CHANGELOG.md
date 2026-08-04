# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Fixed

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
  `range(1991, 2023)`, and `aux/Exiobase_Population_Data_not_found.xlsx` has
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
