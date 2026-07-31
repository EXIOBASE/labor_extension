# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Fixed

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
