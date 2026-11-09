"""Annual hours from weekly hours (docs/improvement_plan_2026-11-06.md, Phase 1)."""

#: Weekdays in a year (52 weeks of 5 days).
WEEKDAYS_PER_YEAR = 260


def working_weeks(vacation_days):
    """Working weeks in a year: weekdays less paid leave and public holidays.

    Annual hours per worker = weekly hours * working_weeks(vacation). The
    formula used until 2026-11 was weekly hours * 52, which counts leave and
    holiday weeks as worked; against OECD national-accounts hours per worker
    for 38 countries in 2019 it was a median 15% high, and this one a median
    2% high (docs/improvement_plan_2026-11-06.md, Phase 1). The README's
    older `(weekly / 5) * (365 - vacation)` counted weekends as working days.
    """
    return (WEEKDAYS_PER_YEAR - vacation_days) / 5
