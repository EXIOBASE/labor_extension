# Coverage

Year coverage of every account this repo publishes, with the nowcast
years stated separately. Per account, this file answers: which years
exist, which of those are projected rather than observed, what the
projection method is, and which source constrains the last observed
year. It sits next to `CHANGELOG.md` and is maintained with the same
discipline: update it in the same PR as any change that moves coverage
(new years, a moved nowcast boundary, a new or retired account).

The release-level rollup lives in `00-workflow/COVERAGE.md` and ships
with the release package next to `LICENSE.txt`. When this file changes,
update the rollup row for this repo too.

Definitions and rules:

- **Observed years**: estimated from reported source data for that year
  (the estimate may still be modelled; the year is anchored in data).
- **Nowcast years**: projected past the last observed source year. Name
  the method (growth-rate scaling, structural prior from the last
  observed year, trend extrapolation).
- Never write a year range from memory: verify it against the published
  tree or the pipeline config, or write TODO.

## What this repo publishes

Two accounts.

**`labour`**, 14 stressors as built on branch `improve-labour-account`
(2026-11): 6 `Employment people: <skill> <sex>` in 1000 p, 6
`Employment hours: <skill> <sex>` in M.hr (3 skill levels, 2 sexes), and
`Vulnerable employment: people` (1000 p) and `Vulnerable employment:
hours` (M.hr), own-account plus contributing family workers. The two
vulnerable rows are a subset of the six skill and sex rows, not a seventh
class, and are deliberately not named `Employment people: ...` /
`Employment hours: ...`, so downstream totals that sum those prefixes do
not count them twice. Releases up to 3.12.0 carry the 12 skill and sex
rows only (`EXIOBASE_3_12_0/raw/Extensions/labour/ixi/2019/unit.txt`,
read 2026-11-10); the 14-row account reaches a release tree with the next
build. This repo writes the handoff workbook
`final_labor_SUTs_<version>.xlsx`; `desire_upload_prepper` reformats it
into the release tree, deriving pxp from ixi through the MRSUT product
mix.

Method changes on the branch that move values but not coverage: annual
hours are weekly hours x (260 - paid vacation and public holiday days) /
5, not x 52 (world hours per worker 2,210 -> 2,012 in 2019 on the
2026-11-10 hours-stage check run, CHANGELOG); people by skill come from
ILO's modelled employment by ISCO-08 occupation, balanced by RAS on the
wage-bill skill mix, instead of the wage-bill shares (README, "People by
skill level"). Neither changes the years covered.

**`labour_risk`**, a separate extension built by
`scripts/build_labour_risk.py` from the labour handoff workbook, in the
release labour extension's format. Its rows are subsets or attributes of
the labour account's people and are never added to them. Not yet staged
on a release tree (no `raw/Extensions/labour_risk/` under
`EXIOBASE_3_12_0`, checked 2026-11-10).

| Account / table | Published to | Years | Of which nowcast | Nowcast method | Binding source constraint |
| --- | --- | --- | --- | --- | --- |
| `labour` (12 stressors, ixi + pxp) | `EXIOBASE_3_12/raw/Extensions/labour/{ixi,pxp}/<year>/` | 1995-2028 | 2026-2028 | `level_trend`, median-robust slope from 2009, capped at 5%/yr (`io_utils.extension_nowcast`); chosen on holdouts, see below | ILO modelled estimates end 2025 |
| `labour` (12 stressors, ixi + pxp) | `EXIOBASE_3_11_2/raw/Extensions/labour/{ixi,pxp}/<year>/` | 1995-2024 shipped, 1995-2025 on the tree | TODO | TODO | same |
| `labour` (14 stressors, branch `improve-labour-account`) | handoff workbook only so far | 1995-2025 built (`config.yaml` years) | none in this repo; the release tail is `scripts/nowcast_tail.py` as above | same | ILO modelled estimates (employment, occupation, status in employment) end 2025 |
| `labour_risk` (ixi only) | `<out>/ixi/<year>/` of `build_labour_risk.py`; not staged | 1995-2025, every indicator computed over the whole span whatever `--years` writes | none projected past 2025; within 1995-2025 several sources are held flat outside their years (below) | n/a | see the table below |

`labour_risk` stressors, sources and which parts are modelled (from the
docstrings of `labour_risk/indicators.py`, `labour_risk/child_forced.py`
and `scripts/build_labour_risk.py`):

| Stressor | Unit | Source and years | Country detail | Industry detail |
| --- | --- | --- | --- | --- |
| `Informal employment: people`, `Informal employment: hours` | 1000 p, M.hr | ILOSTAT SDG 8.3.1 `SDG_0831_SEX_ECO_RT_A`, national data only; most countries start in 2004, so 1995-2003 hold the first observation | observed rate by sex and ECO_AGGREGATE cell, interpolated and held outside observed years; countries never observed (China, the US, Japan, Canada, Australia, small territories) **modelled** from their vulnerable share by the informal/vulnerable ratio of their UN region, else income group, else world, bounded to [vulnerable, 1] | cell rate spread over the 14 activity groups by the vulnerable profile (logit shift keeping the cell rate), then to industries through their activity group |
| `Working poverty (below US$3 a day): people` | 1000 p | ILOSTAT SDG 1.1.1 `SDG_0111_SEX_AGE_RT_A`, ILO modelled, 2000-2025 | national rate by sex; high-income countries set to 0 (ILO does not estimate them); other gaps the UN region's rate | spread over activity groups in proportion to the vulnerable share, capped at 1, national rate kept |
| `Long hours (49 hours a week or more): people` | 1000 p | ILOSTAT `EMP_TEMP_SEX_HOW_NB_A`, hours actually worked, unclassified hours out of the denominator | national by sex, interpolated; gaps the UN region, then world | uniform over activity groups |
| `Child labour`, `Child labour: hazardous work` | 1000 p (children 5-17) | ILOSTAT national surveys (68 countries since 2001); ILO-UNICEF 2024 (2020, 2024 regional totals); ILO 2017 report (world totals 2000-2016) | **modelled**: survey rate where a country has one, else its SDG region's 2024 rate; scaled to ILO's regional and world totals, scale held before 2000 and after 2024 | broad sector from the survey, else the region or world split; industries by low-skilled people |
| `Forced labour` | 1000 p | ILO, Walk Free and IOM 2021 global estimates (five ILO regions); Walk Free Global Slavery Index 2023 as the country key | **modelled**: 2021 regional totals spread over countries by the index, other years a constant rate per worker | world sector composition; industries by low-skilled people |
| `Long working hours: attributable deaths`, `Long working hours: attributable DALYs` | 1000 p, 1000 DALY | WHO/ILO joint estimates 2023, 183 countries, 2000, 2010 and 2016 | per employed person, interpolated between those years and held outside them | industries by long-hours workers |

Not included: occupational injuries and the other occupational risk
factors. The WHO/ILO export in hand covers long working hours only, IHME
GBD needs a login, and ILOSTAT's injury series cover about a quarter of
world employment (docs/improvement_plan_2026-11-06.md, Phase 4).

## Why the observed span is softer than it looks

2026-2028 are projected (see the next section). But two further things
qualify the *observed* label on 1995-2025, and the first matters more
than the projected tail does:

1. **The supplementary countries stop at 2022.** Roughly 63 countries
   are absent from the ILO modelled estimates and are carried by holding
   their share of their ILO subregion x World Bank income-group
   aggregate at the last year observed, letting the aggregate's own
   series (which runs to 2025) supply the year profile and the
   sector/sex composition. Those rows are tagged `obs_status =
   ILO_Subregion_Broad_nowcast`. The hand-compiled workbook behind them
   (`auxdata/Exiobase_Population_Data_not_found.xlsx`) carries 1990-2022,
   so for these entities **every year after 2022 is a constant-share
   projection**, however far ILO runs. Extending them needs new source
   data, not a code change.
2. **Ukraine is held flat from 2022.** ILO stopped reporting Ukraine after
   2021 (`EMP_2EMP_SEX_ECO_NB_A` has 81 rows a year to 2021 and none
   after). Until 2026-09-18 the pipeline booked the missing years as zero,
   which took RoW Europe from 33.6 to 15.3 million between 2021 and 2022
   (the shipped 3.11.2 account has that cliff). Commit 4305038 carries
   every country ILO stops reporting (UKR, SDN, SSD, LBN, PSE) flat at its
   last observed year, tagged `obs_status = ILO_dropout_carried`; the 3.12
   build has UKR at 18,518.87 thousand in 2021 and in every year
   2022-2025 (`table_workforce_by_ISO3.csv`, checked 2026-11-06). Hold flat
   is the no-information projection: it does not represent the war's
   effect on Ukrainian employment.
3. **rx2 only: workers in sections with no activity in the country SUT
   are dropped.** The salary split places an ISIC section's ILO workers
   on the industries of that section by their wage bill. Where every
   industry of the section has zero wages *and* zero output in the
   per-country SUT, there is nothing to place them on and they leave the
   account (sections A and RSTU have a fallback by output, which is also
   zero there). On e3 this never happens, because these countries sit in
   W buckets with activity in every section. On rx2 it hits four
   countries (scan of the staged ixi F.txt against
   `workforce_total_exio3.csv`, 2026-11-10):
   South Sudan 1995-2007, every section, because its rx2 SUT is empty
   in those years (zero output in every industry; activity starts 2008),
   up to 3.04 million people; Paraguay 1995-2025, sections RSTU and K
   (2008 on), 185-378 thousand; Benin 1995-2012, RSTU (and K 2003-2004),
   151-284 thousand; Tajikistan 1995-2007, sections B and DE, 11-22
   thousand. World loss per year is 2.2-3.5 million to 2007 and 0.25-0.56
   million after. This is the whole rx2 WL people gap against e3
   (-0.26%). The fix belongs to the monetary SUTs (no activity where ILO
   counts workers); the labour code does not invent industries for them.

## The 2026-2028 nowcast (added 2026-09-18)

2025 is the ILO end year and `from_cia_to_ilo.build_years` clamps to it,
so raising `years.end` above 2025 is a no-op: these three years cannot
come from the source and are projected on the release tree instead, with
`io_utils.extension_nowcast`, so labour reaches 2028 like the monetary
spine.

**Method: `level_trend`, median-robust slope from 2009, capped at 5% a
year.** Chosen, not assumed. One-step holdouts of 2022, 2023, 2024 and
2025, fitting on everything before each:

| method | country mean abs err | cell, value-weighted | abs world err |
| --- | --- | --- | --- |
| `level_trend` cap 5%, from 2009 | 1.96% | 4.11% | 0.37% |
| `level_trend` cap 5%, from 2015 | 1.95% | 4.05% | 0.40% |
| `level_trend` cap 2%, from 2019 | 1.99% | 4.02% | 0.55% |
| `hold_flat` | 2.23% | 4.36% | 1.46% |
| `intensity` on constant-2020 output | 10.15% | - | - |
| `intensity` on current-price output | 15.99% | - | - |

Two conclusions. **The house `intensity` method is wrong for labour** and
is rejected, as it was for land but for a different reason: employment is
not proportional to output over a three-year horizon, because labour
productivity grows. Its error is five to eight times `level_trend`'s, and
on the 2025 holdout it produces country errors above 1000%. Using a
constant-price driver improves it (16.0% to 10.1%) without making it
competitive, so the price basis is not the problem, the proportionality
assumption is.

**`hold_flat` is beaten mainly on bias.** Employment grows about 1% a
year, so repeating the last year systematically under-projects: its world
error is -1.0% to -1.8% on every holdout, against -0.66% to +0.04% for
`level_trend`. The `level_trend` variants are within noise of each other,
so the module default (cap 5%, from 2009) is used rather than tuning on
four holdouts.

**Direction.** Labour is industry-native, so the ixi account is projected
from its own history and pxp is derived from it through the MRSUT product
mix, the same route the observed years take in `desire_upload_prepper`.
Projecting pxp and deriving ixi would reverse the account's natural
direction. The conversion conserves the total to 4.9e-12.

**The Ukraine cliff does not corrupt the trend**, which was checked
because it could have: with the slope taken from 2019 the RoW Europe trend
is -9.4% a year, entirely an artefact of Ukraine vanishing in 2022, and
the 5% cap would have locked in a 5% annual decline. With the module
default (from 2009) the median over the full history absorbs the single
step and RoW Europe moves -0.25% to -0.67% across the three years. This is
what the median-robust slope is for.

Result: world employment 3.569 bn (2025) to 3.607, 3.644 and 3.683 bn,
about 1.05% a year, with hours per person steady at 2,181 to 2,183, so the
projection does not distort the hours-to-people ratio. No negative or NaN
cells. `F_Y` stays all zeros.

## Verification, 3.12 (built 2026-09-17/18)

Checked through `exio_hatcher`'s own `get_employment_ext` rather than by
inspecting files:

- 34 years, 1995-2028 (1995-2025 built, 2026-2028 projected), both
  systems. `F` is (12, 7987) on ixi and (12, 9800) on pxp; `F_Y` is
  (12, 343) and is **all zeros by construction**, since employment is not
  booked against final demand.
- Units: 6 x `1000 p`, 6 x `M.hr`.
- ixi and pxp totals agree to 1.7e-16, so the product-mix conversion
  conserves employment. No NaN, no negative cells.
- 2019: 3.333 bn people at 2,210 hours per person, **identical to
  3.11.2**, as expected, since ILO sets the control totals and the SUTs
  only decide how they spread over industries and skill levels.
- Series shape: 2.391 bn people (1995), 3.333 (2019), 3.569 (2025),
  3.683 (2028), at 2,167 / 2,210 / 2,181 / 2,183 hours per person. The
  observed-to-projected boundary at 2025/2026 shows no step in either the
  level or the hours-per-person ratio.

The skill mix differs from 3.11.2 (high +1.1% to +6.5%, low and medium
-1.1% to -1.4%) and that traces to the input rather than to this code:
the 3.12 wage bill is 42.23% high skilled against 3.11.2's 41.29%, and
50.11% medium against 51.08%.

**Vintage.** The 3.12 account was first built on the 2026-09-15 SUT
export and **rebuilt on 2026-10-16** (01:40, `run_windows.py` with
`SKIP_DOWNLOAD=1`, the 09-17 ILO and Eurostat downloads) on the SUT
export of 2026-10-14 23:07 from the overnight 10-14/15 chain, re-staged
by `desire_upload_prepper` (01:43) and nowcast to 2028 by
`scripts/nowcast_tail.py` (01:43). Checked on the tree the same morning:
2019 3.333 bn people at 2,210 hours per person (unchanged, as expected),
2025 3.605 bn, 2026 3.642 bn, 2028 3.717 bn at 2,182-2,184 hours per
person; no NaN, no negatives; ixi and pxp totals equal to 2e-9 in every
year checked. On this vintage the product mix drops nothing: the
industries with labour but no output that the 09-23 staging carried are
gone, because the salary split now reads the same SUTs the MRSUT is
built from.
The wage vectors actually consumed are fingerprinted in
`indecol/data/labour/final_table/sut_wage_provenance_3_12.json`.
