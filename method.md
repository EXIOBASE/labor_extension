# Method: how the labour account is built

This file follows the code as it is on branch `improve-labour-account`
(2026-11). It replaces the description of `labor.py`, `download.py`,
`salary_split.py` and `aggregate_isic.py`, which were deleted on
2026-11-10 (9c57e3a). The README gives the sources, the environment
variables (section "Running") and the published rows; `COVERAGE.md` the
years and what is projected; `CHANGELOG.md` the history.

## Pipeline at a glance

```
run_windows.py [--axis e3|rx2]
  1a download_all                      ILOSTAT (rplumber API) and Eurostat CSVs -> data folder
  1b workforce_salary.workforce.workforce_calculation
       ref_label.add_ref_label          ILO labels, ISO3 -> axis region
       from_cia_to_ilo.cia_to_ilo       countries ILO does not model (Factbook, hand-compiled, drop-outs)
       salary_split_ray.salary_split_year
         skill_splice                   skill shares across coe-shares breaks
         skill_from_occupation.rebalance people by skill from ILO occupation (RAS)
  2  working_hours.average_working_hours.working_hour
       clean_*, isic3_to_isic4_vectorised, substitute, combine_isic_3_4_vectorised,
       aggregate_isic_vectorised, regression_*, complete_hours, complete_hours_2
                                        weekly hours by country, sex, ILO activity group, year
       annual_hours.working_weeks       (260 - vacation and holiday days) / 5
       vulnerable_employment.region_shares
     -> final_table/final_labor_SUTs_<version>.xlsx (handoff workbook, one sheet per year)

desire_upload_prepper (other repo)      workbook -> raw/Extensions/labour/{ixi,pxp}/<year>/
scripts/nowcast_tail.py                 2026-2028 on the release tree
scripts/build_labour_risk.py            the separate labour_risk extension
```

Paths come from `config.yaml` (`config.local.yaml` overrides per machine)
through `config.py`. On e3 the downloads go to
`d:/indecol/data/labour/data`, the outputs to
`d:/indecol/data/labour/final_table` and the debug CSVs to
`d:/indecol/data/labour/work`; an rx2 run reads the e3 downloads and writes
under the folders `config.yaml` `axes.rx2` names. Nothing is written into
the repo.

Parallelism: the salary split runs its years on a process pool
(`LABOR_WORKERS`), the hours stage runs the few calls that used ray through
the serial stand-in `working_hours/serial_ray.py`. `LABOR_RAY=1` restores
ray for both.

## Stage 1a: download

`run_windows.download_all` fetches each source as a CSV (the old ILO bulk
endpoint was retired):

| File | Content | Used by |
| --- | --- | --- |
| `EMP_2EMP_SEX_ECO_NB_A` | ILO modelled employment by sex and economic activity | workforce |
| `HOW_TEMP_SEX_ECO_NB_A` | mean weekly hours actually worked by sex and economic activity | hours |
| `POP_2POP_SEX_NB_A` | ILO total population | territory totals to workforce |
| `EMP_2EMP_SEX_STE_NB_A`, `EMP_TEMP_SEX_STE_ECO_NB_A` | employment by status (modelled; survey by activity) | vulnerable employment |
| `EMP_2EMP_SEX_OCU_NB_A`, `EMP_TEMP_SEX_OCU_NB_A` | employment by occupation (modelled; survey) | people by skill |
| Eurostat `lfsa_ewhuna`, `lfsa_ewhun2` | usual weekly hours by NACE | hours, agriculture before 2009 |

`SKIP_DOWNLOAD=1` reuses the files already there; an rx2 run must set it.

## Stage 1b: workforce by country

`workforce_calculation` reads the ILO employment table: for each country
(`ref_area`), sex, year (`time`) and ILO activity group (`classif1`), the
number employed in thousands (`obs_value`):

| ref_area | indicator           | source  | sex   | classif1            | time | obs_value |
|----------|---------------------|---------|-------|---------------------|------|-----------|
| AFG      | EMP_2EMP_SEX_ECO_NB | XA:2198 | SEX_T | ECO_DETAILS_TOTAL   | 1991 | 2923.281  |
| AFG      | EMP_2EMP_SEX_ECO_NB | XA:2198 | SEX_T | ECO_DETAILS_A       | 1991 | 1854.403  |
| AFG      | EMP_2EMP_SEX_ECO_NB | XA:2198 | SEX_T | ECO_DETAILS_B       | 1991 | 5.82      |
| AFG      | EMP_2EMP_SEX_ECO_NB | XA:2198 | SEX_T | ECO_DETAILS_C       | 1991 | 150.362   |
| AFG      | EMP_2EMP_SEX_ECO_NB | XA:2198 | SEX_T | ECO_DETAILS_DE      | 1991 | 3.317     |
| AFG      | EMP_2EMP_SEX_ECO_NB | XA:2198 | SEX_T | ECO_DETAILS_F       | 1991 | 203.942   |
| AFG      | EMP_2EMP_SEX_ECO_NB | XA:2198 | SEX_T | ECO_DETAILS_G       | 1991 | 198.676   |
| AFG      | EMP_2EMP_SEX_ECO_NB | XA:2198 | SEX_T | ECO_DETAILS_HJ      | 1991 | 100.881   |
| AFG      | EMP_2EMP_SEX_ECO_NB | XA:2198 | SEX_T | ECO_DETAILS_I       | 1991 | 6.051     |
| AFG      | EMP_2EMP_SEX_ECO_NB | XA:2198 | SEX_T | ECO_DETAILS_K       | 1991 | 1.572     |
| AFG      | EMP_2EMP_SEX_ECO_NB | XA:2198 | SEX_T | ECO_DETAILS_LMN     | 1991 | 8.442     |
| AFG      | EMP_2EMP_SEX_ECO_NB | XA:2198 | SEX_T | ECO_DETAILS_O       | 1991 | 145.662   |
| AFG      | EMP_2EMP_SEX_ECO_NB | XA:2198 | SEX_T | ECO_DETAILS_P       | 1991 | 14.215    |
| AFG      | EMP_2EMP_SEX_ECO_NB | XA:2198 | SEX_T | ECO_DETAILS_Q       | 1991 | 203.657   |
| AFG      | EMP_2EMP_SEX_ECO_NB | XA:2198 | SEX_T | ECO_DETAILS_RSTU    | 1991 | 26.282    |

ILO counts all persons of working age who, in a short reference period,
were in paid employment (at work, or with a job but not at work) or
self-employed. The activity is the main activity of the establishment.
The series are [ILO modelled estimates](https://ilostat.ilo.org/resources/concepts-and-definitions/ilo-modelled-estimates/):
missing national data are estimated by ILO.

`ref_label.add_ref_label` attaches the ILO area labels (taken from the
export itself) and the axis region of every ISO3 code
(`config.convert_to_region`: country_converter `EXIO3` on e3, io_utils on
rx2).

### Countries ILO does not model

ILO's modelled estimates do not cover every country of the axis.
`from_cia_to_ilo.cia_to_ilo` adds three groups, each tagged in
`obs_status`:

1. **Countries in the CIA World Factbook** (`auxdata/CIA.json`). The
   Factbook gives a total workforce for one year. The country is placed in
   an ILO aggregate with `auxdata/countries_en.csv`:

   | ISO3 Code | Country             | ILO Region              | ILO Subregion - Broad                 | ILO Subregion - Detailed | World Bank Income Group |
   |-----------|---------------------|-------------------------|---------------------------------------|--------------------------|-------------------------|
   | AFG       | Afghanistan         | Asia and the Pacific    | Southern Asia                         | Southern Asia            | Low income              |
   | ALB       | Albania             | Europe and Central Asia | Northern, Southern and Western Europe | Southern Europe          | Upper-middle income     |
   | ASM       | American Samoa      | Asia and the Pacific    | South-Eastern Asia and the Pacific    | Pacific Islands          | Upper-middle income     |

   The aggregate is "<ILO subregion>: <income group>", else "<ILO region>:
   <income group>", else "World: <income group>"
   (`resolve_aggregate`). The country's share of that aggregate in the
   Factbook year is held for every year, and the aggregate's own
   breakdown by sex and activity is applied. Example: American Samoa had a
   workforce of 17,850 in 2015 (Factbook); its aggregate, "South-Eastern
   Asia and the Pacific: Upper-middle income" (X52), had 172,292.597
   thousand employed in 2015, of whom 53,674.541 in `ECO_DETAILS_A`:

   | ref_area | ref_area.label                                          | sex   | classif1          | time | obs_value  |
   |----------|---------------------------------------------------------|-------|-------------------|------|------------|
   | X52      | South-Eastern Asia and the Pacific: Upper-middle income | SEX_T | ECO_DETAILS_TOTAL | 2015 | 172292.597 |
   | X52      | South-Eastern Asia and the Pacific: Upper-middle income | SEX_T | ECO_DETAILS_A     | 2015 | 53674.541  |
   | X52      | South-Eastern Asia and the Pacific: Upper-middle income | SEX_T | ECO_DETAILS_C     | 2015 | 25256.27   |
   | X52      | South-Eastern Asia and the Pacific: Upper-middle income | SEX_T | ECO_DETAILS_G     | 2015 | 30913.497  |

   so American Samoa's agriculture in 2015 is 17,850 x 53,674.541 /
   172,292.597 = 5,560 people, and other years follow the aggregate.
   Jersey and Guernsey are built only when ILO lacks the Channel Islands
   (CHI), so the islands are not counted twice; Factbook names
   country_converter does not resolve are mapped in `CIA_ISO3_OVERRIDES`.

2. **Hand-compiled entities** (`auxdata/Exiobase_Population_Data_not_found.xlsx`,
   sheet "Exiobase data not automatised"): a yearly total for 1990-2022 and
   the ILO aggregate of each entity, for example:

   | ISO3 | Name                              | Label_short           | 2015 | 2016 | 2017  |
   |------|-----------------------------------|-----------------------|------|------|-------|
   | CCK  | Cocos (Keeling) Islands           | Pacific Islands       | 553  | 563  | 574   |
   | CXR  | Christmas Island                  | Pacific Islands       | 1812 | 1843 | 1878  |

   These totals are population, so each is multiplied by the
   employment-to-population ratio of its ILO aggregate (ILO employment
   over `POP_2POP_SEX_NB_A`, same aggregate and year);
   `LABOR_TERRITORY_PARTICIPATION=0` books them as they are. The
   breakdown by sex and activity is the aggregate's, as above. After 2022
   the share of the aggregate is held at its last year
   (`ILO_Subregion_Broad_nowcast`, see COVERAGE.md).

3. **Countries ILO stops reporting** (Ukraine after 2021, also SDN, SSD,
   LBN, PSE): every cell is held at its last reported value
   (`ILO_dropout_carried`).

The complete table is summed to the axis regions
(`table_workforce_by_EXIO3.csv`, `workforce_total_exio3.csv` in the
final_table folder) and written as `workforce.csv` by `run_windows.py`.

### Salary split: ILO activity groups to EXIOBASE industries

`salary_split_ray.salary_split_year` spreads each region's ILO employment
of an activity group over the EXIOBASE industries in it
(`auxdata/Exiobase_ISIC_Rev-4.xlsx`, sheet `ILO_mapping_sector`) in
proportion to each industry's compensation of employees, the SUT
value-added rows `w03.a/b/c` (low, medium, high skilled) of the
per-country `usebpdom.csv` under `config.yaml` `paths.sut_csv_root`.
Sections whose industries have no wages fall back to output for A and
RSTU; men and women follow ILO's sex shares of the activity group. One
year is one task (`calcul_year_impl`), working one region at a time.

`skill_splice` replaces, for the regions and years listed in
`config.yaml` `skill_split_splice`, an industry's wage-bill skill shares
before a break in 06-SUT_balance's `coe-shares.mat` with the shares of the
first year after it (CN, IN, ID, WA, WF, US, IT); the industry totals are
unchanged.

### People by skill from ILO occupation

`skill_from_occupation.rebalance` sets the number of people at each skill
level (since 2026-11; `LABOR_SKILL_FROM_WAGES=1` keeps the wage-share
split). Per region, year and sex:

- row totals: the people of each industry from the salary split;
- column totals: people by ISCO-08 skill level from ILO's modelled
  employment by occupation (`EMP_2EMP_SEX_OCU_NB_A`): groups 1-3 high,
  4-8 medium, 9 low. ILO merges groups 6 and 9 into group 96, split by the
  country's survey ratio 9 / (6 + 9) (`EMP_TEMP_SEX_OCU_NB_A`, pooled over
  the years that report both groups); else group 6 = alpha x the
  country's agricultural employment, alpha the median survey ratio of
  group 6 to agricultural employment for that sex, where that is below
  group 96; else the world's pooled ratio. Countries are summed to the
  region with their employment as weight; a country with no modelled row
  takes its UN region's mix, then the world's;
- structure inside each industry: the wage bill by skill, balanced to
  both totals by RAS.

Outputs: `split_workforce_by_skill_newSUT.xlsx` (one sheet per year) and
`skill_shares_occupation.csv` in the final_table folder.

## Stage 2: hours

`average_working_hours.working_hour` turns people into hours.

### Weekly hours by country, sex and activity group

- ILO mean weekly hours actually worked (`HOW_TEMP_SEX_ECO_NB_A`), zero
  values dropped. Countries that report only activity aggregates get ISIC4
  rows from them (`add_isic4_from_aggregates`).
- Eurostat usual weekly hours (`lfsa_ewhuna`), kept for ages 15-64, men
  and women separately, full-time and part-time together, employed and
  self-employed, NACE A_B (agriculture and forestry, where NACE and ISIC
  match), country rows only, 1992-2008 (`clean_hour_eurostat`).
- ISIC Rev.3 rows (to 2008) are converted to ISIC Rev.4
  (`isic3_to_isic4_vectorised`, `auxdata/correspondance_ISIC3_ISIC4.xls`,
  weighted by the workforce), and section A before 2009 is replaced by
  the Eurostat value (`substitute`), because the conversion scatters
  agriculture. `combine_isic_3_4_vectorised` keeps the converted Rev.3
  values before 2009 and native Rev.4 from 2009.
- Sections are grouped as ILO groups them (D+E, H+J, L+M+N, R+S+T+U) by
  averaging (`aggregate_isic_vectorised`).

Gaps in a series are filled linearly between observed years; outside them
(`regression_ILO_region_with_minimum`, `..._ray`):

- one observed value: held for every year;
- two: their mean (no longer floored to a whole hour since 3.12.0 release
  2);
- three or more: each missing year takes the mean of as many neighbouring
  values as there are observations, moving outwards.

`complete_hours` adds empty rows for the ISIC4 sections a country does
not report, and `complete_hours_2` fills the grouped sections (DE, HJ,
LMN, RSTU) from their components (the mean where both are there, else the
one that is), before the regional averages.

### Regions

A single-country region uses its own country. A rest-of-world bucket (WA,
WE, WF, WL, WM) takes the average of its countries weighted by
workforce; a country with no hours for a cell takes its region's average
(`regional_infill`). A single-country region whose country reports no
hours (Taiwan on e3, 22 countries on rx2) takes its e3 bucket's average,
and a main-country cell with no hours takes the rest-of-world bucket of
its ILO region (`ILO_REGION_BUCKET`). Ukraine's 2022 row in WE carries its
2021 hours with the population scaled by 0.845 (e3 only).

### Hours per year

For each region, industry, skill level and sex:

**Employment hours = weekly hours x people x (260 - paid vacation and
public holiday days) / 5**

`annual_hours.working_weeks`; vacation days from
`auxdata/whole_vacation.csv`, the unweighted mean of a region's countries,
else the mean of its e3 bucket. A region that takes its hours from another
region keeps its own vacation days. Until 2026-11 the code used weekly
hours x 52. The industry's weekly hours are those of its ILO activity
group and sex (`concordance_category`). Fallbacks the split had to use are
written to `hours_fallbacks.csv`; the hours by skill to
`hours_split_newSUTS.xlsx`.

### Vulnerable employment

`vulnerable_employment.region_shares` gives the share of own-account and
contributing family workers (ICSE-93 groups 3 and 5) by region, sex, ILO
activity group and year: the national share by sex from
`EMP_2EMP_SEX_STE_NB_A`, spread over the 14 activity groups by the
country's survey profile (`EMP_TEMP_SEX_STE_ECO_NB_A`, pooled over its
survey years; UN region, then world, where it has no survey for a group)
with one logit shift that keeps the national share, then weighted by
employment over a region's countries. The share of an industry's group
applies to its people and hours (`vulnerable_shares.csv`).

### The handoff workbook

`final_labor_SUTs_<version>.xlsx`, one sheet per year, 14 rows by (region,
sector) columns in the axis order (rx2 sheets are written long, since 159
x 163 columns exceed Excel's limit):

| Row | Unit |
| --- | --- |
| `Employment people: <Low/Medium/High>-skilled <male/female>` (6) | 1000 p |
| `Employment hours: <Low/Medium/High>-skilled <male/female>` (6) | M.hr |
| `Vulnerable employment: people` | 1000 p |
| `Vulnerable employment: hours` | M.hr |

The vulnerable rows are a subset of the six skill and sex rows and are
named so that totals summing `Employment people.*` or `Employment hours.*`
do not count them twice. `desire_upload_prepper`
(`exiobase_labour_extensions_reformat.py`) writes the workbook into
`raw/Extensions/labour/{ixi,pxp}/<year>/`, deriving pxp from ixi through
the MRSUT product mix.

## After the build

- `scripts/nowcast_tail.py` projects ixi on the release tree to 2028
  (io_utils `level_trend`, median-robust slope from 2009, capped at 5% a
  year) and derives pxp through the product mix of the target year;
  `--check` compares without writing, `--axis rx2` uses the per-country
  supply tables. Method choice: COVERAGE.md.
- `scripts/build_labour_risk.py` builds the `labour_risk` extension from
  the workbook and `workforce.csv` (informal employment, working poverty,
  long hours, child labour, forced labour, deaths and DALYs from long
  working hours). Sources and method: README, COVERAGE.md and the
  docstrings of `labour_risk/`.

## Tests

`pytest tests` with the repo venv. The equivalence tests
(`test_isic3_to_isic4_equivalence`, `test_combine_equivalence`,
`test_aggregate_equivalence`) compare the vectorised hours modules with
the original implementations on three countries; they need the stage-1
outputs on D: (and ray for the combine test) and skip without them.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
