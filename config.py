"""Central path configuration for the labor_extension repo.

Absolute source/output paths come from ``config.yaml`` at the repo root
(``config.local.yaml`` overrides per machine). No path literals live in
the executable scripts; they import the constants defined here. See
AGENTS.md "Data formats (on-disk)".
"""

from __future__ import annotations

import os
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
FINAL_LABOR_FILENAME = _req_str("final_labor_filename")


def _opt(key: str):
    cur: object = _CFG
    for part in key.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


# ---------------------------------------------------------------------------
# Country axis (docs/rx2_axis_plan_2026-11-06.md). `e3` is the 49-region
# release axis and the default: every value below is then exactly what it was
# before the axis existed. Another axis is chosen with LABOR_AXIS (set by
# `run_windows.py --axis`, and passed on to the ray workers), and its block
# under `axes:` in config.yaml overrides what differs.
# ---------------------------------------------------------------------------
AXIS = os.environ.get("LABOR_AXIS", "e3")
_AXES = _opt("axes") or {}
if AXIS != "e3" and AXIS not in _AXES:
    raise KeyError(f"LABOR_AXIS={AXIS!r}: no axes.{AXIS} block in config.yaml "
                   f"(known: e3, {', '.join(_AXES)})")
_AXIS_CFG = _AXES.get(AXIS, {}) if AXIS != "e3" else {}
IS_E3 = AXIS == "e3"

#: io_utils / 00-class name of the axis.
IO_AXIS = "exiobase3" if IS_E3 else str(_AXIS_CFG.get("io_axis", AXIS))

if not IS_E3:
    SUT_CSV_ROOT = str(_AXIS_CFG["sut_csv_root"])
    FINAL_LABOR_FILENAME = str(_AXIS_CFG["final_labor_filename"])

#: W buckets: regions that aggregate several countries (same codes on e3 and rx2).
ROW_BUCKETS = ("WA", "WL", "WE", "WF", "WM")

#: Where the e3 run writes (unchanged): run_windows.py's labour data folder.
_E3_LABOUR_ROOT = Path("d:/indecol/data/labour")


def _axis_dir(key: str) -> Path:
    path = Path(str(_AXIS_CFG[key]))
    if AXIS not in path.as_posix():
        raise ValueError(f"axis {AXIS}: {key} {path} does not name the axis; "
                         f"refusing so an {AXIS} run cannot write into an e3 folder")
    return path


#: Downloaded ILO/Eurostat sources. Shared by all axes; only e3 downloads.
DATA_DIR = _E3_LABOUR_ROOT / "data"
#: final_table folder: the intermediates and the handoff workbook.
FINAL_TABLE_DIR = _E3_LABOUR_ROOT / "final_table" if IS_E3 else _axis_dir("final_table_dir")
#: Folder for the debug CSVs the pipeline writes as it goes. None on e3,
#: which keeps writing them into the current directory (the repo root).
WORK_DIR = None if IS_E3 else _axis_dir("work_dir")

# A check run (such as the e3 equivalence run of 2026-11-06) can send both
# elsewhere without touching config.yaml: LABOR_FINAL_TABLE_DIR, LABOR_WORK_DIR.
if os.environ.get("LABOR_FINAL_TABLE_DIR"):
    FINAL_TABLE_DIR = Path(os.environ["LABOR_FINAL_TABLE_DIR"])
if os.environ.get("LABOR_WORK_DIR"):
    WORK_DIR = Path(os.environ["LABOR_WORK_DIR"])


def work_file(name: str):
    """Where a debug CSV goes: the bare name (cwd) on e3, WORK_DIR otherwise."""
    if WORK_DIR is None:
        return name
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    return WORK_DIR / name


#: Ray workers for the salary split. Was os.cpu_count() - 4; LABOR_WORKERS caps it.
RAY_WORKERS = int(os.environ.get("LABOR_WORKERS", (os.cpu_count() or 8) - 4))


def _rx2_region_map() -> dict:
    """ISO3 -> region on a member axis (rx2): io_utils' map from 00-class, plus
    the codes it leaves out (obsolete ones country_converter still knows, such
    as CHI) in their EXIO3 W bucket."""
    import country_converter as coco
    from io_utils.classification import iso3_to_region

    out = dict(iso3_to_region(IO_AXIS))
    cc = coco.CountryConverter(include_obsolete=True)
    data = cc.data[["ISO3", "EXIO3"]].dropna().drop_duplicates("ISO3")
    for iso3, bucket in zip(data["ISO3"], data["EXIO3"]):
        if iso3 not in out and bucket in ROW_BUCKETS:
            out[iso3] = bucket
    return out


_REGION_MAP = None


def convert_to_region(names, cc_all=None):
    """The region of an ISO3 code (or list of codes) on the axis.

    On e3 this is exactly the call the pipeline made,
    ``cc_all.convert(names=..., src="ISO3", to="EXIO3")`` (with the caller's
    converter if given). On another axis it maps through the axis table; an
    unknown code gives "not found", as country_converter does.
    """
    global _REGION_MAP
    if IS_E3:
        if cc_all is None:
            import country_converter as coco
            cc_all = coco.CountryConverter(include_obsolete=True)
        return cc_all.convert(names=names, src="ISO3", to="EXIO3")
    if _REGION_MAP is None:
        _REGION_MAP = _rx2_region_map()
    if isinstance(names, str):
        return _REGION_MAP.get(names, "not found")
    return [_REGION_MAP.get(n, "not found") for n in names]


def e3_parent(code: str) -> str:
    """The e3 region an axis region sits in (a W bucket is its own parent)."""
    if IS_E3 or code in ROW_BUCKETS or len(code) == 2:
        return code
    import country_converter as coco
    return coco.CountryConverter(include_obsolete=True).convert(
        names=code, src="ISO3", to="EXIO3")


def region_order() -> list:
    """Regions of the handoff workbook, in release order."""
    if IS_E3:
        import pandas as pd
        return list(pd.read_csv(REPO_ROOT / "auxdata" / "region_EXIO3.csv")["EXIO3"])
    from io_utils.classification import region_codes
    return list(region_codes(IO_AXIS))


# Skill-split splice across the coe-shares structural breaks (C7-3): region
# code -> first year of the later structure. Optional: absent means no splice.
SKILL_SPLICE = {str(k): int(v) for k, v in (_opt("skill_split_splice") or {}).items()}
if not IS_E3:
    _splice = _AXIS_CFG.get("skill_split_splice", {})
    if _splice == "inherit":
        # Each axis region takes its e3 parent's break year.
        _e3_splice = SKILL_SPLICE
        SKILL_SPLICE = {}
        for _code in region_order():
            _parent = e3_parent(_code)
            if _parent in _e3_splice:
                SKILL_SPLICE[_code] = _e3_splice[_parent]
    else:
        SKILL_SPLICE = {str(k): int(v) for k, v in (_splice or {}).items()}
