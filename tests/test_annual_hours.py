"""Annual hours per worker from weekly hours (working_hours/annual_hours.py)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "working_hours"))

from annual_hours import working_weeks  # noqa: E402


def test_no_vacation_is_52_weeks():
    assert working_weeks(0) == 52


def test_germany_29_days():
    # 260 weekdays less 29 leave and holiday days = 231 days = 46.2 weeks.
    assert abs(working_weeks(29) - 46.2) < 1e-12


def test_vectorises_over_a_series():
    import pandas as pd
    out = working_weeks(pd.Series([0, 10, 35]))
    assert list(out) == [52, 50, 45]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("ok")
