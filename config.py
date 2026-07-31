"""Central path configuration for the labor_extension repo.

Absolute source/output paths come from ``config.yaml`` at the repo root
(``config.local.yaml`` overrides per machine). No path literals live in
the executable scripts; they import the constants defined here. See
AGENTS.md "Data formats (on-disk)".
"""

from __future__ import annotations

from pathlib import Path

from io_utils.config import get_path, load_config

# This file lives at the repo root, so the repo root is its own parent.
REPO_ROOT = Path(__file__).resolve().parents[0]

_CFG = load_config(repo_root=REPO_ROOT)


def _req_path(key: str) -> Path:
    """Fetch a required path from config.yaml as a Path, failing fast."""
    p = get_path(_CFG, key)
    if p is None:
        raise KeyError(f"config.yaml missing required path: {key!r}")
    return p


def _req_str(key: str) -> str:
    """Fetch a required config value as its raw string.

    Used where the original code concatenated the path literal with
    region and year strings; keeping the raw (forward-slash) string
    preserves the exact path the scripts read on the Linux X-drive
    mount, which a Path conversion would mangle on Windows.
    """
    cur: object = _CFG
    for part in key.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            raise KeyError(f"config.yaml missing required path: {key!r}")
    return str(cur)


def _req_int(key: str) -> int:
    """Fetch a required config value as an int, failing fast."""
    return int(_req_str(key))


# Per-country SUT CSV root read by workforce_salary/salary_split_ray.py.
# Raw string (with trailing slash) so the script can concatenate the region
# code and year directly, matching the legacy behaviour exactly.
SUT_CSV_ROOT = _req_str("paths.sut_csv_root")

# Legacy .xls SUT root off the X-drive mount, still used by the pre-Ray
# workforce_salary/salary_split.py.
SALARY_SUT_ROOT = _req_str("paths.salary_sut_root")

# Inclusive year range for the salary split.
YEAR_START = _req_int("years.start")
YEAR_END = _req_int("years.end")


def year_range() -> range:
    """Years to build, as a range (YEAR_END is inclusive in config)."""
    return range(YEAR_START, YEAR_END + 1)
