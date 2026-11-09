"""The country-axis switch in config.py (docs/rx2_axis_plan_2026-11-06.md).

e3 must resolve to exactly the settings and region codes the pipeline used
before the axis existed; rx2 must map every ISO3 onto the 159-region axis.
Each axis is loaded in a fresh interpreter, since config resolves the axis
at import. Runs under pytest or directly::

    <python> tests/test_axis.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

_PROBE = r"""
import json, config as c
import country_converter as coco
codes = ['AUT', 'TWN', 'CHI', 'AGO', 'ABW', 'UKR', 'XKX', 'CHN', 'IDN', 'USA']
print(json.dumps({
    'axis': c.AXIS, 'sut': c.SUT_CSV_ROOT, 'workbook': c.FINAL_LABOR_FILENAME,
    'splice': c.SKILL_SPLICE, 'final_table': str(c.FINAL_TABLE_DIR),
    'work': None if c.WORK_DIR is None else str(c.WORK_DIR),
    'regions': c.region_order(), 'mapped': c.convert_to_region(codes),
    'coco': coco.CountryConverter(include_obsolete=True).convert(names=codes, src='ISO3', to='EXIO3'),
}))
"""


def _load(axis: str) -> dict:
    env = {k: v for k, v in os.environ.items()
           if k not in ("LABOR_FINAL_TABLE_DIR", "LABOR_WORK_DIR")}
    env["LABOR_AXIS"] = axis
    out = subprocess.run([sys.executable, "-c", _PROBE], cwd=REPO, env=env,
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out.strip().splitlines()[-1])


def test_e3_is_the_legacy_configuration():
    e3 = _load("e3")
    assert e3["sut"].endswith("/EXIOBASE_3_12_0/raw/sut/current/")
    assert e3["workbook"] == "final_labor_SUTs_3_12.xlsx"
    assert e3["splice"] == {"CN": 2007, "IN": 2007, "ID": 2007, "WA": 2007,
                            "WF": 2008, "US": 2001, "IT": 2000}
    assert Path(e3["final_table"]) == Path("d:/indecol/data/labour/final_table")
    assert e3["work"].replace("\\", "/").endswith("labour/work")
    assert e3["mapped"] == e3["coco"]          # the same country_converter call
    assert len(e3["regions"]) == 49 and e3["regions"][0] == "AT"


def test_rx2_maps_onto_159_regions():
    rx2 = _load("rx2")
    assert len(rx2["regions"]) == 159 and rx2["regions"][-5:] == ["WA", "WL", "WE", "WF", "WM"]
    assert rx2["mapped"] == ["AUT", "TWN", "WE", "AGO", "WL", "UKR", "XKX", "CHN", "IDN", "USA"]
    assert "rx2" in rx2["final_table"] and "rx2" in rx2["work"] and "rx2" in rx2["sut"]
    assert rx2["workbook"].endswith("_rx2.xlsx")
    # Inherited splice: every region of a spliced e3 parent, at the parent's year.
    splice = rx2["splice"]
    assert splice["CHN"] == 2007 and splice["IDN"] == 2007 and splice["USA"] == 2001
    assert splice["ITA"] == 2000 and splice["WA"] == 2007 and splice["AGO"] == 2008
    assert "AUT" not in splice and "TWN" not in splice


if __name__ == "__main__":
    test_e3_is_the_legacy_configuration()
    test_rx2_maps_onto_159_regions()
    print("ok")
