"""Windows driver for the labor_extension pipeline (replaces the stale labor.py).

Stage 1 (workforce build): download ILO/Eurostat -> workforce_calculation.

Run from the repo root with an env that has ray/pandas/country_converter/requests,
e.g. the conda ``fao_data`` env::

    set SKIP_SALARY_SPLIT=1   # workforce build only (skip the heavy Ray salary split)
    <fao_data-python> run_windows.py

Env vars:
    SKIP_DOWNLOAD=1        skip the network download step (reuse already-downloaded data)
    SKIP_SALARY_SPLIT=1    skip the Ray salary-split step inside workforce_calculation

Note: the legacy ILO bulk endpoint (www.ilo.org/ilostat-files/WEB_bulk_download/...)
was retired and now 404s. We download per-indicator CSVs from the current ILOSTAT
rplumber API instead. Eurostat SDMX URLs are unchanged.

Outputs go to d:/indecol/data/labour/{data,final_table}. The submodule scripts also
write a few bare-named CSVs into the repo root (cwd) by design.
"""
import os
import sys
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parent
os.chdir(REPO)  # aux/ and several bare relative reads/writes assume repo root as cwd
sys.path.insert(1, str(REPO / "workforce_salary"))
sys.path.insert(2, str(REPO / "working_hours"))

import workforce_salary.workforce as workforce

DATAFOLDER = Path("d:/indecol/data/labour")
data_path = DATAFOLDER / "data"
final_path = DATAFOLDER / "final_table"
data_path.mkdir(parents=True, exist_ok=True)
final_path.mkdir(parents=True, exist_ok=True)

# Filenames workforce_calculation / the hours stage read from data_path.
src_csv = Path("EMP_2EMP_SEX_ECO_NB_A.csv")
src_csv2 = Path("HOW_TEMP_SEX_ECO_NB_A.csv")

# Current source URLs (ILO -> rplumber API returning plain CSV; Eurostat unchanged).
_ILO_API = "https://rplumber.ilo.org/data/indicator/?id={id}&type=both&format=.csv"
SOURCES = [
    (_ILO_API.format(id="EMP_2EMP_SEX_ECO_NB_A"), "EMP_2EMP_SEX_ECO_NB_A.csv"),
    (_ILO_API.format(id="HOW_TEMP_SEX_ECO_NB_A"), "HOW_TEMP_SEX_ECO_NB_A.csv"),
    ("https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/LFSA_EWHUNA/?format=TSV", "estat_lfsa_ewhuna.tsv"),
    ("https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/LFSA_EWHUN2/?format=TSV", "estat_lfsa_ewhun2.tsv"),
]


def download_all(dest_dir: Path) -> None:
    hdr = {"User-Agent": "Mozilla/5.0"}
    for url, fname in SOURCES:
        dest = dest_dir / fname
        print(f"  downloading {fname} ...", flush=True)
        r = requests.get(url, headers=hdr, timeout=600, stream=True)
        r.raise_for_status()
        with open(dest, "wb") as fh:
            for chunk in r.iter_content(1 << 16):
                fh.write(chunk)
        print(f"    -> {dest} ({dest.stat().st_size:,} bytes)", flush=True)


if os.environ.get("SKIP_DOWNLOAD") == "1":
    print(">>> Stage 1a: download SKIPPED (SKIP_DOWNLOAD=1)")
else:
    print(">>> Stage 1a: downloading ILO/Eurostat source data ...")
    download_all(data_path)
    print(">>> download done")

print(">>> Stage 1b: workforce_calculation ...")
wf = workforce.workforce_calculation(data_path, src_csv, src_csv2, final_path)
print(">>> workforce_calculation done; shape:", wf.shape)
wf.to_csv(final_path / "workforce.csv", index=False)
print(">>> Stage 1 complete. final_table outputs at:", final_path)
