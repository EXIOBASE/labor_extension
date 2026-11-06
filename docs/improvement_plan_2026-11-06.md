# Labour account: assessment and improvement plan (2026-11-06)

Branch `improve-labour-account`, off main at 4439478 (the committed rx2
axis work). Main stays as it is for the rx2 run
(`docs/rx2_axis_plan_2026-11-06.md`, run order 1-4); the work below lands
here and merges after that run.

Richard's questions: is the code working and done the right way, do we
still build everything we used to (gender, forced labour, and so on), and
what is the plan to fix and improve it.

## 1. Is it working?

Yes. The pipeline runs end to end (`run_windows.py`, 3.9 h on e3 on
2026-10-16), the world totals are set by ILO and matched 3.11.2 on the 3.12
rebuild (3.333 bn people, 2,210 h per person in 2019), the 2026-2028
nowcast method was chosen on holdouts, and the rx2 change of 2026-11-06 was
proved bit-identical on e3. All ten tests pass (2026-11-06, repo venv):
`test_axis` (2), `test_skill_splice` (5) and the three equivalence tests
that run the vectorised hours modules against transcribed originals.

## 2. Is it done the right way?

### Method

M1. **The skill split comes from the SUT wage bill, not from labour data.**
`salary_split_ray.py` divides each ILO ISIC-section employment total over
EXIOBASE industries and skill levels in proportion to `w03.a/b/c`
(compensation of employees by skill) read from the per-country SUT. Two
consequences. First, the account inherits a monetary artefact: 06 fills
those rows from the legacy `coe-shares.mat`, whose structural breaks have
already needed seven splices (CN, IN, ID, WA, WF, US, IT) with WM 1996
pending. Second, splitting *headcount* by *wage bill* overstates the
high-skilled share wherever high-skilled wages per head are higher, which
is everywhere; the 3.12 CHANGELOG records the skill mix moving with the
wage-bill vintage (+1.1% to +6.5% high skilled between SUT vintages) for
exactly this reason. Simas, Wood and Hertwich (2015, appendix Table A.1)
defined the EXIOBASE skill types by ISCO-08 occupation from ILO data and
used compensation of employees only to spread a broad sector over the
industries inside it.

M2. **The sex split is applied uniformly across skill levels.** For each
industry, `Split <skill> employment - male` is the skill total times the
ISIC section's male share of employment (line 230 of
`salary_split_ray.py`). So the "by gender" dimension carries the ILO sex
share by activity but no information on how skill differs by sex.

M3. **Hours per year: code and documentation disagree.** The README
documents `(weekly hours / 5) * (365 - paid vacation days)` and the repo
carries `auxdata/whole_vacation.csv`; the code computes `weekly hours *
52` (`average_working_hours.py` line 1240) and reads the vacation table
without using it. The ILO series is mean weekly hours *actually worked*
per employed person, which already averages leave weeks in, so `* 52` is
the defensible convention and the vacation adjustment would double count.
Decision for Richard: keep `* 52` and delete the table and the README
formula (recommended), or switch to the documented formula.

M4. **Known gaps carried in COVERAGE.md:** Ukraine is zero from 2022 (ILO
stopped reporting; the pipeline books missing as zero), and the 63
supplementary countries are constant-share projections after 2022.

### Code

C1. The two hot stages are legacy cell-by-cell loops: 159 and 66
`float(df.loc[...].to_string())` lookups in `salary_split_ray.py` and
`average_working_hours.py`, each a string round trip that discards digits
(the equivalence tests note "the precision the original discarded"). The
2026-11-06 per-region slicing made them fast enough but kept every
statement, including that rounding.

C2. Dead or duplicate modules sit next to the live ones:
`workforce_salary/hours_split.py` (uses `DataFrame.append`, references an
undefined `hours_RoW`), `salary_split.py` (3.8.2 xls route),
`fix_hours.py`, `labor.py`, `working_hours/average_working_hours_modified.py`,
`isic3_to_isic4_old.py`, `isic3_to_isic4.py` (3,476 lines, superseded by
the vectorised module), `complete_hours_3.py`, the non-vectorised
`aggregate_isic.py` and `combine_isic_3_4.py`. The live import graph is
`run_windows -> workforce -> {ref_label, from_cia_to_ilo, salary_split_ray,
skill_splice}` and `average_working_hours -> {clean_*, aggregate_isic_vectorised,
combine_isic_3_4_vectorised, isic3_to_isic4_vectorised, complete_hours,
complete_hours_2, regression_*, average_hour, substitute}`.

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

So **vulnerable employment is the one shipped account we no longer
build.** This repo has never built it: no code, no commit in its history
(51 commits from 2024-12-17) touches it. exio_hatcher and exio_results
still list the two rows (as a cross-cutting attribute, not a seventh
skill-sex class).

The three references:

- Simas, Golsteijn, Huijbregts, Wood, Hertwich (2014), the "bad labour"
  footprint. Only the abstract could be read (MDPI returns 403 to
  machine fetches; the Semantic Scholar record gives the abstract). It
  lists occupational health damage, vulnerable employment, gender
  inequality, share of unskilled workers, child labour and forced labour.
  These were a research layer on EXIOBASE; none of them except
  vulnerable employment appears in the 3.8.2 release stressor list.
- Simas, Wood, Hertwich (2015), labour embodied in trade. Read in full
  (PDF fetched). Labour input: persons engaged per skill type, skill by
  ISCO-08, from ILO LABORSTA and OECD STAN, disaggregated to the MRIO
  industries by compensation of employees "considering that, inside a
  broad economic sector industry, average wages would be similar, as well
  as hours worked per person" (appendix). Hours are used in the results.
- Amores, Corsatea, Kuenen, Schmidt, Simas, Wiebe, Wood (2019), the JRC
  environmental and labour accounts for the OECD ICIO. Only the catalogue
  abstract could be read (CORE, the JRC repository and the Publications
  Office all refuse machine fetches). To be read by hand before Phase 3
  if its labour chapter is to be the template.

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
invalid), the earnings ids tried were invalid (the catalogue needs a
lookup), and forced labour has no country indicator (ILO publishes global
and regional estimates only).

## 4. Plan

Phases in order of value per effort. Each phase ends with a CHANGELOG
entry, a COVERAGE.md update where coverage moves, and the world skill and
sex totals compared against the 3.12 account.

### Phase 0, done 2026-11-06
Commit the rx2 work on main (4439478), push, branch here.

### Phase 1: decisions (Richard)
1. Hours convention (M3): keep `* 52` or switch to the vacation formula.
2. Reinstate vulnerable employment as two release stressors (14 rows as
   in 3.8.2)? That touches desire_upload_prepper, exio_incubator's
   naming fix, exio_hatcher's lists and the 00-qa label guards.
3. Skill split source (M1): ILO occupation as the control, SUT wage
   shares as the industry prior; or keep the wage-bill split.
4. Whether injuries, child labour and forced labour belong in the
   release or in a separate labour-risk account (own COVERAGE row,
   source coverage audit first).
5. Ukraine from 2022: hold at 2021, or leave the documented zero.

### Phase 2: vulnerable employment (smallest, additive)
- Download `EMP_TEMP_SEX_STE_ECO_NB_A` and `EMP_2EMP_SEX_STE_NB_A`
  through the existing `download_all` list.
- Vulnerable share = (own-account + contributing family) / total, by
  country, sex and ISIC section where the national table has it;
  elsewhere the modelled national share by sex, scaled by the section
  profile of the country's ILO subregion x income group (the same
  fallback structure `from_cia_to_ilo` uses).
- Apply the share to the people rows summed over skill, and to the hours
  rows with the same hours per person. Two new rows in the workbook,
  reformat and tail carry them, `unit.txt` gains them.
- Test: world vulnerable share by year against the ILO modelled world
  share; the rows stay below the six-class totals in every cell.

### Phase 3: skill split rebased on ILO occupation (M1)
- National skill totals by sex from `EMP_TEMP_SEX_OCU_NB_A` (L1 low, L2
  medium, L3-4 high) with `EMP_2EMP_SEX_OCU_NB_A` mapped through the
  ISCO-08 major groups as the modelled fallback, interpolated and
  carried like the hours series.
- Within a country-year, the SUT wage-bill shares give the industry
  prior; a two-margin balance (industries from the ILO ISIC sections, skill
  from the occupation totals) replaces the proportional split.
- Keep the splice machinery but expect it to be redundant: measure the
  seven break region-years again after the change.
- This also fixes M2, since the occupation totals are by sex.
- Validation: 2019 world skill shares against 3.12 (42.2% high-skilled
  wage bill is not a headcount share; the new headcount shares will be
  lower for high skill), per-region largest one-year move as in the
  2026-10-27 break scan.

### Phase 4: code cleanup (after Phase 3 fixes the arithmetic, so the
equivalence tests are rewritten once)
- Vectorise the salary split and the hours split per region-year
  (groupby and merge), dropping the `to_string` round trip; record the
  1e-6 relative change it causes.
- Delete the dead modules in C2; keep one implementation per step.
- Debug CSVs to the work folder on every axis; nothing written to cwd.
- Process pool as the default, ray optional.
- `pytest` in the venv, a two-region two-year fixture run end to end.
- README and method.md rewritten to the code as it is (hours formula,
  skill source, vulnerable employment).

### Phase 5: labour-risk account (only if decided in Phase 1)
- Coverage audit of the injury and child labour indicators (countries and
  years), then the same subregion x income-group fallback as the
  workforce build.
- Forced labour only as a regional rate applied to hours, labelled as a
  modelled estimate, if at all.

## 5. What this does not change
The rx2 run on main proceeds on the committed code. Phases 2 to 4 change
the e3 and rx2 accounts alike through the axis setting; neither axis gets a
separate pipeline.
