# Labour account: assessment and improvement plan (2026-11-06)

Branch `improve-labour-account`, off main at 4439478 (the committed rx2
axis work). Main stays as it is for the rx2 run
(`docs/rx2_axis_plan_2026-11-06.md`, run order 1-4); the work below lands
here and merges after that run.

Richard's questions: is the code working and done the right way, do we
still build everything we used to (gender, forced labour, and so on), and
what is the plan to fix and improve it. His decisions of 2026-11-06 are in
section 4.

## Status, 2026-11-10

The plan below is kept as written on 2026-11-06 and 2026-11-10; where the
build differs from it, this section and the dated notes in section 5 say
how. Commits are on `improve-labour-account`.

- **Phase 1, hours formula: done.** d7ea0fd (formula), d3833f0 (check
  run: world hours per worker -8.9% in 2019), 670739e (a region taking
  its hours from a fallback region keeps its own vacation days). Gate
  result: against OECD annual hours actually worked (38 countries, 2019)
  the new formula is a median 2% high, the old one 15%, so the deduction
  applies to the ILO and the Eurostat rows alike.
- **Phase 2, vulnerable employment: done.** 0b78991, f87f7c5 (survey
  cells with suppressed ICSE 3/5 counts left out of the profiles), 854bebc
  (warning for a cell with people but no share), 4b91417 (rows renamed
  `Vulnerable employment: people` / `Vulnerable employment: hours`, so
  that downstream `Employment people.*` / `Employment hours.*` totals do
  not count them twice). Built differently from the plan: the national
  share by sex is ILO's modelled `EMP_2EMP_SEX_STE_NB_A` for every
  country, spread over the 14 activity groups by the country's survey
  profile pooled over all its survey years (UN region, then world, where
  the country has no survey for a group), with one logit shift that keeps
  ILO's national share. The plan's ILO subregion x income group profile
  was not used.
- **Phase 3, skill from occupation: done.** 54313dc, de5856d, 84cd2c1.
  Built differently from the plan: ILO's *modelled* employment by ISCO-08
  major group (`EMP_2EMP_SEX_OCU_NB_A`) is the primary source for every
  country and year, not the survey skill levels, because many countries
  have one or two survey years (China only its 2000 census). The merged
  group 96 is split by the country's survey ratio 9 / (6 + 9) pooled over
  years reporting both groups; else group 6 = the median survey ratio of
  group 6 to agricultural employment x the country's agricultural
  employment, where that is below group 96; else the world pooled ratio.
  RAS on the wage-bill skill mix; the prior is not divided by relative
  wages (a column scaling, which RAS absorbs). The seven splices are not
  yet re-measured or retired.
- **Phase 4, labour-risk account: built as a separate extension**
  (f9547df, cd122e3, 8bfe486, 0b93e87, ebd6b6d, f512744, 3b47348,
  e5dddde, b2d55e7): `Informal employment: people` / `hours` (ILOSTAT SDG
  8.3.1), `Working poverty (below US$3 a day): people` (SDG 1.1.1), `Long
  hours (49 hours a week or more): people`, `Child labour`, `Child labour:
  hazardous work`, `Forced labour` (modelled layer), `Long working hours:
  attributable deaths` and `attributable DALYs` (WHO/ILO joint
  estimates). Occupational injuries are pending: the WHO/ILO export in
  hand covers long working hours only; injuries need a WHO/ILO
  "occupational injuries" export or IHME GBD (login needed). Not yet
  staged on a release tree.
- **Phase 5, cleanup: partly done.** Done: 12 dead modules deleted
  (9c57e3a); process pool by default, ray only with `LABOR_RAY=1`, debug
  CSVs to the work folder on e3, pytest in `environment.yml` (095aaa7);
  the three equivalence scripts run under pytest and skip without their
  data. Open: vectorising the salary split and hours split loops (the
  `to_string` round trip is still there), a two-region two-year fixture
  run end to end.

## 1. Is it working?

Yes. The pipeline runs end to end (`run_windows.py`, 3.9 h on e3 on
2026-10-16), the world totals are set by ILO and matched 3.11.2 on the 3.12
rebuild (3.333 bn people, 2,210 h per person in 2019), the 2026-2028
nowcast method was chosen on holdouts, countries ILO stops reporting
(UKR, SDN, SSD, LBN, PSE) are carried flat since 4305038, and the rx2
change of 2026-11-06 was proved bit-identical on e3. All ten tests pass
(2026-11-06, repo venv): `test_axis` (2), `test_skill_splice` (5) and the
three equivalence tests that run the vectorised hours modules against
transcribed originals.

## 2. Is it done the right way?

### Method

M1. **People by skill are taken from the wage bill, not from labour data.**
`salary_split_ray.py` gives each skill level a share of an industry's
*headcount* equal to its share of the industry's *wage bill* (`w03.a/b/c`
in the per-country SUT). A high-skilled worker earns more than a
low-skilled one, so this counts too many high-skilled people and too few
low-skilled ones. It also makes the account inherit every break in 06's
`coe-shares.mat`, which has needed seven splices so far (CN, IN, ID, WA,
WF, US, IT; WM 1996 pending). Both reference methods do it the other
way round:

- Simas, Wood, Hertwich (2015, appendix): skill types by ISCO-08
  occupation from ILO data; compensation of employees is used only to
  spread a broad sector's workers over the industries inside it.
- Wood et al. (2019, JRC report for the OECD ICIO, section 2.2): workers
  are allocated to skill levels from labour force survey counts by
  occupation (ISCO major groups 9 low; 4-8 medium; 1-3 high, Table 6),
  education as the fallback, and the *wage bill* by skill is then derived
  from those counts times relative wages. Compensation of employees is
  used only to spread a broad sector over its industries (the equation in
  2.2.2), as this repo already does.

M2. **The sex split is applied uniformly across skill levels.** For each
industry, `Split <skill> employment - male` is the skill total times the
ISIC section's male share of employment (`salary_split_ray.py` line 230).
The "by gender" dimension therefore carries ILO's sex share by activity
but no difference in skill mix between men and women.

M3. **Hours per year: code and documentation disagree, and the documented
formula is wrong as written.** The README documents
`(weekly hours / 5) * (365 - paid vacation days)`; the code has used
`weekly hours * 52` since 320334c (2025-06-17) and reads
`auxdata/whole_vacation.csv` without using it. The README formula counts
weekends as working days: for Germany (29 vacation and holiday days) it
gives `weekly hours * 67.2`, 29% above 52 weeks; for the US (10 days)
`* 71`, 37% above. That is the size of the v3.9.5 hours inflation
diagnosed in exio_results KNOWN_ISSUES item 4 (Germany 2,347 h a year),
which was built while that formula was live.

M4. Supplementary countries (about 63) are constant-share projections
after 2022, documented in COVERAGE.md.

### Code

C1. The two hot stages are legacy cell-by-cell loops: 159 and 66
`float(df.loc[...].to_string())` lookups in `salary_split_ray.py` and
`average_working_hours.py`, each a string round trip that discards digits
(the equivalence tests record "the precision the original discarded").
The 2026-11-06 per-region slicing made them fast enough but kept every
statement, including that rounding.

C2. Dead or duplicate modules sit next to the live ones:
`workforce_salary/hours_split.py` (uses `DataFrame.append`, references an
undefined `hours_RoW`), `salary_split.py` (3.8.2 xls route),
`fix_hours.py`, `labor.py`, `from_cia_to_ilo.py` at the repo root,
`working_hours/average_working_hours_modified.py`,
`isic3_to_isic4_old.py`, `isic3_to_isic4.py` (3,476 lines, superseded by
the vectorised module), `complete_hours_3.py`, and the non-vectorised
`aggregate_isic.py` and `combine_isic_3_4.py`. The live import graph is
`run_windows -> workforce -> {ref_label, from_cia_to_ilo, salary_split_ray,
skill_splice}` and `average_working_hours -> {clean_*,
aggregate_isic_vectorised, combine_isic_3_4_vectorised,
isic3_to_isic4_vectorised, complete_hours, complete_hours_2, regression_*,
average_hour, substitute}`.

C3. The e3 run writes about 15 debug CSVs into the repo root (cwd),
including a 214 MB `data_list_old.csv`; rx2 already sends them to a work
folder.

C4. ray is a hard dependency with four separate `ray.init` calls in the
hours stage, and it would not start on this machine on 2026-11-06; the
process pool and the serial stand-in exist but are opt-in.

C5. The tests pin configuration and refactor equivalence; there is no
end-to-end run on a small fixture, and `pytest` is not in the repo venv.

## 3. Do we still build everything we used to?

What the releases shipped, from the files on disk:

| Release | Labour stressors |
| --- | --- |
| 3.8.2 (`exio_3_8_ioig_multipliers_satellite_*.csv`) | 14: the 6 `Employment:` people rows, the 6 `Employment hours:` rows, plus `Employment: Vulnerable employment` and `Employment hours: Vulnerable employment` |
| 3.9.5 (exio_results KNOWN_ISSUES item 4) | no Vulnerable employment row |
| 3.11.2, 3.11.3, 3.12.0 (`raw/Extensions/labour/ixi/2019/unit.txt`) | 12 |

**Vulnerable employment is the one shipped account we no longer build.**
This repo has never built it: no code and no commit in its history (51
commits from 2024-12-17) touches it. exio_hatcher and exio_results still
list the two rows, as a cross-cutting attribute, not a seventh skill-sex
class. (Correction 2026-11-10: exio_hatcher only names the 3.8.2 labels
`Employment: Vulnerable employment` and `Employment hours: Vulnerable
employment` in its drop list (`generate.py`), and exio_results only
excludes rows containing "Vulnerable" from its hours total; neither
knows the new `Vulnerable employment: people` / `hours` rows.) Gender is
still built (male and female on every row).

Simas, Golsteijn, Huijbregts, Wood, Hertwich (2014), the "bad labour"
footprint (full text read from vectorsustainability.com), built six
indicators for 2007 as a research layer on EXIOBASE, not as release
stressors:

| Indicator | Definition | 2014 source | 2014 allocation |
| --- | --- | --- | --- |
| Occupational health damage | DALY from occupational cancers, COPD, asthma, noise-induced hearing loss, low back pain, injuries | Concha-Barrientos et al., Nelson et al., European Commission | employment share within broad sector |
| Vulnerable employment | own-account plus contributing family workers | ILO LABORSTA | employment share within broad sector |
| Gender inequality | share of women in employment | ILO LABORSTA | as built |
| Low-skilled workers | elementary occupations, or education up to lower secondary | ILO LABORSTA | as built |
| Child labour (and hazardous child labour) | ILO definition | ILO global report, 3 sectors x 4 regions | share of low-skilled labour |
| Forced labour | ILO definition | ILO global estimate, 3 sectors x 6 regions | share of low-skilled labour |

The paper re-aggregated child and forced labour results to seven regions
and eight consumption categories "to avoid a false representation of the
resolution of the analysis".

What ILOSTAT serves today, checked by API probe on 2026-11-06
(`rplumber.ilo.org/data/indicator/?id=...`):

| Indicator | Content | Note |
| --- | --- | --- |
| `EMP_TEMP_SEX_STE_ECO_NB_A` | employment by sex, status (ICSE-93: 1 employees, 2 employers, 3 own-account, 5 contributing family) and economic activity | national data, 125 countries in 2019 |
| `EMP_2EMP_SEX_STE_NB_A` | modelled employment by sex and status | all countries, no activity detail |
| `EMP_TEMP_SEX_OCU_NB_A` | employment by sex and occupation, with `OCU_SKILL_L1`, `L2`, `L3-4` | national data, 207 countries in 2019 |
| `EMP_2EMP_SEX_OCU_NB_A` | modelled employment by sex and ISCO-08 major group | all countries |
| `INJ_FATL_ECO_NB_A`, `INJ_FATL_ECO_RT_A`, `INJ_NFTL_ECO_*` | fatal and non-fatal occupational injuries by economic activity, count and rate | coverage not yet counted |
| `CLD_XCHL_SEX_AGE_ECO_NB_A` | child labour by sex, age and economic activity | coverage not yet counted |

No activity-by-occupation cross exists in the API (the `ECO_OCU` ids are
invalid), the earnings ids tried were invalid, and forced labour has no
country indicator (ILO publishes global and regional estimates only).

## 4. Decisions (Richard, 2026-11-06)

1. **Hours: use the vacation formula.** Implemented in its corrected
   form, `annual hours = weekly hours * (260 - paid vacation and public
   holiday days) / 5`: 260 weekdays, not 365 days. For Germany that is
   46.2 working weeks, against 52 now and 67.2 under the README formula.
   One caveat to settle by data, not by argument: ILO's series is hours
   *actually* worked, and where the survey runs all year that mean already
   includes leave weeks, so deducting leave again would undercount. The
   JRC report used actual hours times 52 for this reason. Gate in
   Phase 2: compare hours per worker with the national-accounts annual
   hours per worker for the OECD and EU countries; if the deduction
   undercounts systematically there, apply it to the Eurostat usual-hours
   rows only and say so in the CHANGELOG.
2. **Reinstate vulnerable employment** as the two 3.8.2 stressors (14
   rows).
3. **Skill split: take people by skill from ILO occupation counts.**
   (Richard asked what this means. In short: today the number of
   low-, medium- and high-skilled *people* is assumed proportional to what
   each group is *paid*; the fix counts the people directly from ILO's
   occupation data, as both reference methods do, and keeps the wage bill
   only for spreading a sector over its industries.) Adopted as the plan,
   Phase 3.
4. **Injuries, child labour and forced labour as an additional account**
   (`labour_risk`), separate from the 14-row labour account, with its own
   COVERAGE row.
5. **Ukraine: already dealt with** (4305038, carried flat from 2022). The
   stale "zero from 2022" text in COVERAGE.md and the rx2 plan was
   corrected on main in c9b63ec.

## 5. Plan

Each phase ends with a CHANGELOG entry, a COVERAGE.md update where
coverage moves, and world skill and sex totals compared against the 3.12
account. Every phase builds both axes through the axis setting.

### Phase 0, done 2026-11-06
rx2 work committed and pushed on main (4439478), Ukraine documentation
corrected (c9b63ec), branch created, this plan.

### Phase 1: hours formula (small, isolated); done, see Status
- In `average_working_hours.py`, replace `* 52` by
  `* (260 - vacation) / 5`, with `vacation` the region's `Total Paid
  Vacation Days` (already looked up per region, unused today). On rx2 the
  table is already grouped by axis region with the e3 bucket fallback.
- Check `whole_vacation.csv` covers every ISO3 in the workforce table;
  missing countries take their e3 bucket mean, as rx2 already does.
- Gate (decision 1): hours per worker against national-accounts annual
  hours for the OECD and EU countries, 2019.
- README formula corrected to the one in the code.

### Phase 2: vulnerable employment; done, built differently, see Status
- Add `EMP_TEMP_SEX_STE_ECO_NB_A` and `EMP_2EMP_SEX_STE_NB_A` to
  `download_all`.
- Vulnerable share = (ICSE-93 3 + 5) / total, by country, sex and ISIC
  section where the national table has it; elsewhere the modelled
  national share by sex, spread over sections by the section profile of
  the country's ILO subregion x income group (the fallback structure
  `from_cia_to_ilo` already uses); interpolated and carried like the
  hours series.
- Apply it to the people rows summed over skill, and to the hours rows
  with the same hours per person, as two new workbook rows. The reformat
  in desire_upload_prepper, `nowcast_tail.py`, `unit.txt`, exio_incubator's
  naming fix and the 00-qa label guards learn the two rows; exio_hatcher
  and exio_results already list them. (Correction 2026-11-10: they do not;
  see the note in section 3.)
- Tests: world vulnerable share by year against ILO's modelled world
  share; the rows stay at or below the six-class totals in every cell.

### Phase 3: skill split from ILO occupation; done, built differently, see Status
- National people by skill and sex from `EMP_TEMP_SEX_OCU_NB_A`
  (`OCU_SKILL_L1` low, `L2` medium, `L3-4` high), with
  `EMP_2EMP_SEX_OCU_NB_A` mapped through the ISCO-08 major groups (JRC
  Table 6) as the fallback, interpolated and carried like hours.
- Per country-year and sex, a two-margin balance: industry totals from
  the ILO ISIC sections (spread by compensation of employees, as now),
  skill totals from the occupation counts, with the SUT wage-bill skill
  shares as the starting structure inside each industry, divided by
  relative wages so the prior is in people, not money.
- This also fixes M2, because the occupation totals are by sex.
- Measure the seven spliced break region-years again: the national skill
  margins come from labour data, so the coe-shares breaks should no
  longer reach the totals, and the splice may be retired.
- Validation: 2019 world and regional skill shares before and after
  (headcount high-skilled share expected to fall), largest one-year move
  per region as in the 2026-10-27 break scan.

### Phase 4: labour-risk account; built, injuries pending, see Status
- Coverage audit of the injury and child labour indicators (countries,
  years, activity detail) before any build.
- Stressors, people-based, allocated to industries by the labour account:
  fatal occupational injuries (cases), non-fatal occupational injuries
  (cases), child labour (1000 p), forced labour (1000 p). Injuries and
  child labour by ISIC section where the source has it; forced labour
  from ILO's regional estimates allocated by low-skilled people, as in the
  2014 paper, and labelled as a modelled regional estimate in `unit.txt`
  and COVERAGE.
- The 2014 DALY measure needs disease-burden sources outside ILOSTAT;
  left out unless a current source is identified.
- Own folder `raw/Extensions/labour_risk/`, own COVERAGE row.

Coverage audit, 2026-11-10 (ILOSTAT API downloads of that day; share of
world employment from `EMP_2EMP_SEX_ECO_NB_A`, 2019, country rows only):

| Indicator | Countries ever | Countries per year 2015-2022 | 2019 employment covered | Activity detail |
| --- | --- | --- | --- | --- |
| `INJ_FATL_ECO_NB_A` fatal injuries | 148 | 55-66 | 27% | ISIC3, ISIC4, aggregate, sector |
| `INJ_NFTL_ECO_NB_A` non-fatal injuries | 146 | 59-66 | 28% | ISIC3, ISIC4, aggregate |
| `CLD_XCHL_SEX_AGE_ECO_NB_A` child labour | 107 | 25-62 (5-7 a year before 2008) | 24% | broad sector only (3) |

The large employers have stale or no injury data: last year China 2002,
India 2008, Indonesia 1999, Pakistan 2002, Brazil 2011, Nigeria 2006,
Bangladesh, Ethiopia and Viet Nam none. Child labour has no China, Japan or
Germany row. Forced labour has no country series (as found 2026-11-06).

Gate: not built. Three quarters of world employment would be imputed for
injuries and child labour, and the imputation would be driven by the
countries that report, mostly high-income for injuries. A labour-risk
account on this basis would be a modelled layer, not a country time series,
which is what the 2014 paper also concluded when it re-aggregated to seven
regions. Decision needed from Richard: build it as an explicitly modelled
regional layer (ILO global and regional estimates, allocated within region
by section and low-skilled people), or wait for a better source (for
injuries, the ILO/WHO joint estimates of work-related burden of disease).

Decision (Richard, 2026-11-10): both. Injuries and occupational health
from the WHO/ILO joint estimates (deaths and DALYs attributable to 19
occupational risk factors, national for 183 countries, 2000-2016, by sex
and age, no activity split; download from the WHO Occupational Burden of
Disease application), allocated to industries by ILOSTAT injury rates by
section where reported, else the region's pooled profile. Child and forced
labour as an explicitly modelled regional layer from the ILO-UNICEF 2024
and ILO/Walk Free/IOM 2021 global estimates, with ILOSTAT national child
labour where it exists. Open before the build: whether the WHO download is
scriptable, the regional and sector tables of the two global reports (not
yet read), and how years outside the sources are filled (proposed: rates
per worker held flat).

Wider source search, 2026-11-10 (Richard: "surely there is more data now
than when we did Simas et al"). ILOSTAT coverage measured on API downloads
of that day, share of world employment 2019 from `EMP_2EMP_SEX_ECO_NB_A`,
country rows with an observation within two years:

| Theme | Source | Coverage | Activity detail |
| --- | --- | --- | --- |
| Informal employment | ILOSTAT `EMP_NIFL_SEX_ECO_NB_A`, `SDG_0831_SEX_ECO_RT_A` | 122 countries, 55% (2017-2021); no China, no US | broad sector and aggregate (8 groups) |
| Working poverty (< US$3 PPP) | ILOSTAT `SDG_0111_SEX_AGE_RT_A` | 117 countries, 81%, incl. China and India | none (sex, age) |
| Labour rights compliance | ILOSTAT `SDG_0882_NOC_RT_A` | 187 countries, 99%, 2015-2024 | none (national score) |
| Hours bands (long hours) | ILOSTAT `EMP_TEMP_SEX_HOW_NB_A` | 180 areas listed | none |
| Earnings, pay gap | ILOSTAT `EAR_*_SEX_ECO/OCU` | 105-197 areas listed | activity, occupation |
| Child labour, hazardous work | ILOSTAT `CLD_XCHL/XHAZ_SEX_AGE_ECO_NB_A`; ILO-UNICEF 2024 global estimates | see audit above; global report regional by 3 sectors | broad sector |
| Occupational burden of disease | WHO/ILO joint estimates (19 risk factors incl. injuries and long hours; deaths, DALYs; 183 countries, 2000-2016); IHME GBD occupational risks (204 countries, 1990-2023, account needed) | national | none |
| Forced labour | Walk Free Global Slavery Index 2023 (160 countries, reference 2021, modelled); ILO/Walk Free/IOM 2021 global estimates (regional, by sector) | national (GSI), regional | sector in the global report |
| Goods made with child or forced labour | US DOL ILAB list 2024 (204 goods, 82 countries) | country x good flags | product |

Coverage figures for the WHO/ILO, GBD, GSI and DOL rows are as stated by
their publishers, not checked against a download. Related work found: the
2020 PLOS ONE "indecent labour footprint" (fatal and non-fatal injuries,
forced labour, MRIO) and PSILCA v4 (106 social indicators on Eora).

### Phase 5 (partly done, see Status): code cleanup (after Phase 3 changes the arithmetic, so the
equivalence tests are rewritten once)
- Vectorise the salary split and the hours split per region-year (groupby
  and merge), dropping the `to_string` round trip; record the 1e-6
  relative change it causes.
- Delete the dead modules in C2; keep one implementation per step.
- Debug CSVs to the work folder on every axis; nothing written to cwd.
- Process pool as the default, ray optional.
- `pytest` in the venv, a two-region two-year fixture run end to end.
- README and method.md rewritten to the code as it is.

## 6. What this does not change
The rx2 run on main proceeds on the committed code. Phases 1 to 5 change
the e3 and rx2 accounts alike; neither axis gets a separate pipeline.
