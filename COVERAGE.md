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
| `labour` (12 stressors, ixi + pxp) | `EXIOBASE_3_12/raw/Extensions/labour/{ixi,pxp}/<year>/` | 1995-2025 | none declared, but read the note below | not applicable at the account level | ILO modelled estimates end 2025 |
| `labour` (12 stressors, ixi + pxp) | `EXIOBASE_3_11_2/raw/Extensions/labour/{ixi,pxp}/<year>/` | 1995-2024 shipped, 1995-2025 on the tree | TODO | TODO | same |

## Why "none declared" is not the same as "all observed"

The account has no nowcast tail in the usual sense: there is no year
where a projection method is applied to the whole account. But two
things qualify the observed label, and both matter more than a tail
would:

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
2. **2026-2028 do not exist at all.** 2025 is the ILO end year and
   `from_cia_to_ilo.build_years` clamps to it, so raising `years.end`
   above 2025 is a no-op. The 3.12 monetary spine runs to 2028, so the
   labour account stops three years short of it. Whether to project
   those three years, and how, is an open decision.

## Verification, 3.12 (built 2026-09-17/18)

Checked through `exio_hatcher`'s own `get_employment_ext` rather than by
inspecting files:

- 31 years, 1995-2025, both systems. `F` is (12, 7987) on ixi and
  (12, 9800) on pxp; `F_Y` is (12, 343) and is **all zeros by
  construction**, since employment is not booked against final demand.
- Units: 6 x `1000 p`, 6 x `M.hr`.
- ixi and pxp totals agree to 1.7e-16, so the product-mix conversion
  conserves employment. No NaN, no negative cells.
- 2019: 3.333 bn people at 2,210 hours per person, **identical to
  3.11.2**, as expected, since ILO sets the control totals and the SUTs
  only decide how they spread over industries and skill levels.
- Series shape: 2.391 bn people (1995), 3.333 (2019), 3.569 (2025), at
  2,167 / 2,210 / 2,181 hours per person.

The skill mix differs from 3.11.2 (high +1.1% to +6.5%, low and medium
-1.1% to -1.4%) and that traces to the input rather than to this code:
the 3.12 wage bill is 42.23% high skilled against 3.11.2's 41.29%, and
50.11% medium against 51.08%.

**Vintage.** The 3.12 account was built on the 2026-09-15 SUT export. A
full 04 to 06 to 08 chain rerun was started on 2026-09-17, so this
account will need a rerun on the reconciled chain, the same as energy.
The wage vectors actually consumed are fingerprinted in
`indecol/data/labour/final_table/sut_wage_provenance_3_12.json`.
