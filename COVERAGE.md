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

One account, `labour`, as 12 stressors: 6 `Employment people: <skill>
<sex>` in 1000 p and 6 `Employment hours: <skill> <sex>` in M.hr, over
3 skill levels and 2 sexes. This repo writes the handoff workbook
`final_labor_SUTs_<version>.xlsx`; `desire_upload_prepper` reformats it
into the release tree, deriving pxp from ixi through the MRSUT product
mix.

| Account / table | Published to | Years | Of which nowcast | Nowcast method | Binding source constraint |
| --- | --- | --- | --- | --- | --- |
| `labour` (12 stressors, ixi + pxp) | `EXIOBASE_3_12/raw/Extensions/labour/{ixi,pxp}/<year>/` | 1995-2028 | 2026-2028 | `level_trend`, median-robust slope from 2009, capped at 5%/yr (`io_utils.extension_nowcast`); chosen on holdouts, see below | ILO modelled estimates end 2025 |
| `labour` (12 stressors, ixi + pxp) | `EXIOBASE_3_11_2/raw/Extensions/labour/{ixi,pxp}/<year>/` | 1995-2024 shipped, 1995-2025 on the tree | TODO | TODO | same |

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
2. **Ukraine is zero from 2022.** ILO stopped reporting Ukraine after
   2021 (`EMP_2EMP_SEX_ECO_NB_A` has 81 rows a year to 2021 and none
   after), and the pipeline books missing as zero rather than carrying
   the country forward. RoW Europe's workforce therefore falls from
   33.6 to 15.3 million between 2021 and 2022 and stays there, a 54%
   drop in the region. **This is in the shipped 3.11.2 account too**,
   byte-identical, so it is not a 3.12 regression. It is a defect, not
   a nowcast boundary, and fixing it is an owner decision: hold Ukraine
   at its 2021 level, or bring in another source.

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

**Vintage.** The 3.12 account was built on the 2026-09-15 SUT export. A
full 04 to 06 to 08 chain rerun was started on 2026-09-17, so this
account will need a rerun on the reconciled chain, the same as energy.
The wage vectors actually consumed are fingerprinted in
`indecol/data/labour/final_table/sut_wage_provenance_3_12.json`.
