import country_converter as coco
import pandas as pd
from datetime import datetime
import numpy as np
from numpy import transpose
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import config as _cfg

# First year of the ILO modelled-estimates series. The build starts here (not
# at years.start) because the supplementary countries are derived as a share of
# the ILO subregion aggregate, and the aggregate series itself starts in 1991.
ILO_FIRST_YEAR = 1991

# Aggregate reference series the supplementary countries are scaled against.
AGG_TOTAL_CLASSIF = "ECO_SECTOR_TOTAL"
AGG_TOTAL_SEX = "SEX_T"

cc = coco.CountryConverter()
cc.valid_class
cc.get_correspondence_dict('ISO3', 'EXIO3')

converter=coco.country_converter

def build_years(data_list):
    """Years to build the supplementary countries for.

    Runs from ILO_FIRST_YEAR to `years.end` in config.yaml, clamped to the
    years the ILO aggregate series actually carries (the aggregates are what
    both supplementary-country methods below scale against, so a year beyond
    them cannot be produced). Was hardcoded `range(1991, 2023)` in three
    places.
    """
    last_available = int(data_list["time"].max())
    end = min(int(_cfg.YEAR_END), last_available)
    if end < int(_cfg.YEAR_END):
        print(f"[cia_to_ilo] config years.end={_cfg.YEAR_END} exceeds the ILO "
              f"series ({last_available}); building to {end}")
    return range(ILO_FIRST_YEAR, end + 1)


def _year_column_map(missing_data):
    """Map int year -> the actual column label in the supplementary xlsx.

    auxdata/Exiobase_Population_Data_not_found.xlsx carries its year columns as
    floats (1990.0 ... 2022.0), so an int lookup is not guaranteed to hit.
    """
    out = {}
    for col in missing_data.columns:
        try:
            as_int = int(float(col))
        except (TypeError, ValueError):
            continue
        if 1900 < as_int < 2100:
            out[as_int] = col
    return out


def _build_agg_lookup(data_list_old):
    """(ref_area.label, classif1, sex) x time -> obs_value.

    One pivot replaces the per-scalar `df.loc[<masks>].to_string()` lookups the
    original did inside its innermost loop.
    """
    key = ["ref_area.label", "classif1", "sex", "time"]
    d = data_list_old.loc[:, key + ["obs_value"]]
    dups = int(d.duplicated(subset=key).sum())
    if dups:
        raise ValueError(
            f"{dups} duplicate (ref_area.label, classif1, sex, time) rows in the "
            "ILO export. The original scalar lookups assumed exactly one match "
            "per key (float() on a multi-row to_string() would have raised), so "
            "refusing to silently pick one."
        )
    return d.set_index(key)["obs_value"].unstack("time").sort_index()


def _agg_total(agg, label, year):
    """The label's ECO_SECTOR_TOTAL / SEX_T value for one year."""
    return float(agg.loc[(label, AGG_TOTAL_CLASSIF, AGG_TOTAL_SEX), year])


def _rows_for(agg, label, factor_by_year, columns, ref_area, exio3,
              ref_area_label, status_by_year, classifications, list_sex, years):
    """value(classif1, sex, year) = factor_by_year[year] * agg[label, ...].

    Vectorised form of the original triple nest. Row order is kept as the
    original produced it (sex outermost, then classif1, then year).
    """
    idx = pd.MultiIndex.from_product([classifications, list_sex],
                                     names=["classif1", "sex"])
    block = agg.loc[label].reindex(index=idx, columns=years)
    holes = block.isna()
    if holes.to_numpy().any():
        first = [(c, s, y) for (c, s), row in holes.iterrows()
                 for y in years if bool(row[y])][:3]
        raise ValueError(
            f"{label}: {int(holes.to_numpy().sum())} (classif1, sex, year) "
            f"combinations missing from the ILO aggregate, e.g. {first}. The "
            "original code raised here too (float of an empty selection)."
        )
    values = block.mul(pd.Series({y: float(factor_by_year[y]) for y in years}),
                       axis=1)

    long = values.stack().rename("obs_value").reset_index()
    long["sex"] = pd.Categorical(long["sex"], categories=list_sex, ordered=True)
    long["classif1"] = pd.Categorical(long["classif1"],
                                      categories=classifications, ordered=True)
    long = (long.sort_values(["sex", "classif1", "time"], kind="mergesort")
                .reset_index(drop=True))

    out = pd.DataFrame(index=range(len(long)), columns=columns, dtype=object)
    out["ref_area"] = ref_area
    out["ref_area.label"] = ref_area_label
    if "EXIO3" in out.columns:
        out["EXIO3"] = exio3
    out["sex"] = long["sex"].astype(str).to_numpy()
    out["classif1"] = long["classif1"].astype(str).to_numpy()
    out["time"] = long["time"].to_numpy()
    out["obs_value"] = long["obs_value"].to_numpy()
    out["obs_status"] = [status_by_year[y] for y in long["time"]]
    return out


def _build_cia_countries(missing_countries, fetched_data, df, agg, agg_labels,
                         cc_all, classifications, list_sex, years, columns):
    """Countries with a CIA World Factbook labour-force figure.

    Each country is assumed to hold a constant share of its ILO aggregate, the
    share being fixed in the CIA reference year, and the ILO aggregate supplies
    the whole year profile. Prefers the "<subregion>: <income group>" aggregate
    and falls back to "<region>: <income group>".
    """
    frames = []
    for a in missing_countries:
        if a not in fetched_data["ISO3"].values:
            continue
        row = fetched_data.loc[fetched_data["ISO3"] == a]
        date = int(row["date"].iloc[0])
        pop_known = float(row["population"].iloc[0]) / 1000

        meta = df.loc[df["ISO3 Code"] == a]
        if meta.empty:
            continue
        income = str(meta["World Bank Income Group"].iloc[0])
        sub_label = f'{meta["ILO Subregion - Broad"].iloc[0]}: {income}'
        reg_label = f'{meta["ILO Region"].iloc[0]}: {income}'

        if sub_label in agg_labels:
            label, status = sub_label, "ILO_Subregion_Broad"
            if date <= 1990:
                # Original: the aggregate has no 1990 value for this case
                # (e.g. TCA), so extrapolate back from 1991 and 1992.
                pop_total = (2 * _agg_total(agg, label, 1991)
                             - _agg_total(agg, label, 1992))
            else:
                pop_total = _agg_total(agg, label, date)
        elif reg_label in agg_labels:
            # NB: the original applies no <=1990 extrapolation in this branch.
            label, status = reg_label, "ILO_region"
            pop_total = _agg_total(agg, label, date)
        else:
            continue

        factor = pop_known / pop_total
        print(a, pop_known)
        frames.append(_rows_for(
            agg, label, {y: factor for y in years}, columns,
            ref_area=a,
            exio3=cc_all.convert(names=a, src="ISO3", to="EXIO3"),
            ref_area_label=cc_all.convert(names=a, src="ISO3", to="name_official"),
            status_by_year={y: status for y in years},
            classifications=classifications, list_sex=list_sex, years=years,
        ))
    if not frames:
        return pd.DataFrame(data=None, columns=columns)
    return pd.concat(frames, ignore_index=True)


def _build_xlsx_entities(missing_data, agg, agg_labels, cc_all, already_covered,
                         year_cols, last_xlsx_year, classifications, list_sex,
                         years, columns):
    """Entities with hand-compiled totals in auxdata/Exiobase_Population_Data_not_found.xlsx.

    Same constant-share method, but the country total is observed per year, so
    the ratio is recomputed each year. Past `last_xlsx_year` the ratio is held
    at its last observed value and the aggregate carries the series forward -
    those rows are tagged `..._nowcast`.
    """
    frames = []
    for code in missing_data["ISO3"].values:
        if not (len(str(code)) == 3 and str(code) != "nan"):
            continue
        if code in already_covered:
            continue
        row = missing_data.loc[missing_data["ISO3"] == code]
        if row.empty:
            continue
        label = str(row["Label_short"].iloc[0])
        if label not in agg_labels:
            continue

        factor_by_year, status_by_year = {}, {}
        for y in years:
            anchor = min(y, last_xlsx_year)
            pop_known = float(row[year_cols[anchor]].iloc[0])
            factor_by_year[y] = pop_known / _agg_total(agg, label, anchor)
            status_by_year[y] = ("ILO_Subregion_Broad_nowcast"
                                 if y > last_xlsx_year else "ILO_Subregion_Broad")
        print(code)
        frames.append(_rows_for(
            agg, label, factor_by_year, columns,
            ref_area=code,
            exio3=cc_all.convert(names=code, src="ISO3", to="EXIO3"),
            ref_area_label=cc_all.convert(names=code, src="ISO3", to="name_official"),
            status_by_year=status_by_year,
            classifications=classifications, list_sex=list_sex, years=years,
        ))
    if not frames:
        return pd.DataFrame(data=None, columns=columns)
    return pd.concat(frames, ignore_index=True)


def cia_to_ilo(data_list,data_cia,df,missing_data):

    cc_all = coco.CountryConverter(include_obsolete=True)
   
    '''
    Create a list of ISO3 available in ILO
    '''
    
    ISO3_in_ILO=[item for item in list(data_list['ref_area'].unique()) if  item.isalpha()]
    ISO3_in_EXIOBASE = cc_all.ISO3.ISO3
    
    
    '''
    We compare the list of ISO3 available in the ILO table and the ISO3 in EXIOBASE
    We then create a list with the missing coutries in ILO table
    ''' 
    
    missing_countries = []
    for item in ISO3_in_EXIOBASE:
        if not item in ISO3_in_ILO:
            missing_countries.append(item)
            
            

    
    data_list_old = data_list.copy()
    #data_list_old.to_csv('data_list_old.csv', index=False)

    # Year range for the supplementary countries, from config (was hardcoded).
    years_to_build = build_years(data_list_old)
    year_cols = _year_column_map(missing_data)
    last_xlsx_year = max(year_cols) if year_cols else None
    print(f"[cia_to_ilo] building supplementary countries for "
          f"{years_to_build[0]}-{years_to_build[-1]}; "
          f"hand-compiled xlsx totals end {last_xlsx_year}")
    


    data_list = data_list.drop(['source','indicator'], axis = 1)
    
    list_sex = list(data_list['sex'].unique())
    '''
    classifications
    '''
    classifications = list(data_list['classif1'].unique())
    
    
    '''
    Add missing countries in data_list
    '''
        
    name_missing_official = []
    name_short = []
    for item in missing_countries:
        name_missing=cc_all.convert(names = item,src = 'ISO3',to='name_official')
        short=cc_all.convert(names = item,src = 'ISO3',to='name_short')
        
        name_missing_official.append(name_missing) 
        name_short.append(short)
    
    
    '''
    Search for population and date in CIA for missing countries
    Create a df fetch_data with EXI3, population and date as columns
    '''
    
    # One batched regex conversion instead of ~260 individual
    # `cc_all.convert(names=a, src='regex', ...)` calls, which dominated the
    # runtime of this stage once the country loops below were vectorised.
    # Same result: the original only used the converted code to test membership
    # of `missing_countries`.
    cia_names = list(data_cia['countries'].keys())
    cia_iso3 = cc_all.convert(names=cia_names, src='regex', to='ISO3')
    if not isinstance(cia_iso3, list):
        cia_iso3 = [cia_iso3]
    missing_set = set(missing_countries)

    fetched_data = pd.DataFrame(data=None,columns=['ISO3','population','date'])
    for a, name_short_cia in zip(cia_names, cia_iso3):

        for item in ([name_short_cia] if name_short_cia in missing_set else []):
            name_missing=item
            if name_missing == name_short_cia:
                if data_cia['countries'].get(a).get('data').get('economy').get('labor_force') is not None :
                    if 'total_size' in data_cia['countries'].get(a).get('data').get('economy').get('labor_force').keys():
                        # fetched_data = fetched_data.append(pd.Series([item,data_cia['countries'].get(a).get('data').get('economy').get('labor_force').get('total_size').get('total_people'),data_cia['countries'].get(a).get('data').get('economy').get('labor_force').get('total_size').get('date')],index=['ISO3','population','date']),ignore_index=True)
                        fetched_data = pd.concat([fetched_data,pd.Series([item,data_cia['countries'].get(a).get('data').get('economy').get('labor_force').get('total_size').get('total_people'),data_cia['countries'].get(a).get('data').get('economy').get('labor_force').get('total_size').get('date')],index=['ISO3','population','date']).to_frame().T],ignore_index=True)

                        continue
                    else:
                        continue
                else :
                    continue
            else :
                continue
            
    '''
    Make sure only the year appear in fetched_data['date'] ( not date and month )
    '''
    
    for item in missing_countries:
        if item in fetched_data['ISO3'].values :
            of_interest = fetched_data.loc[fetched_data['ISO3']==item,['date']].to_string(index=False, header=False)
            if len(str(of_interest))!=4:
                date_object = datetime.strptime(of_interest,'%Y-%m-%d')
                date_object_year=date_object.strftime('%Y')
                fetched_data.loc[fetched_data['ISO3']==item,['date']]=date_object_year
            else :
                continue
    
    # data_list = data_list[~data_list['EXIO3'].str.contains("not found")]
            
            
    column_data_list = []
    for i in data_list.columns:
        column_data_list.append(i)
    
    

    # ------------------------------------------------------------------
    # Supplementary countries, vectorised.
    #
    # The original built these two blocks with `@ray.remote` functions whose
    # bodies were `for sex: for classif1: for year:` nests, each iteration
    # pulling one scalar out of the 780k-row ILO frame with
    # `float(df.loc[<4 boolean masks>, ['obs_value']].to_string(...))` and
    # appending a row via `df.loc[len(df)] = ...`. That is thousands of full
    # frame scans per country; a run took hours and needed ray to be bearable.
    #
    # In every branch the body reduced to the same arithmetic,
    #     value = pop_known / pop_total * pop_of_interest
    # where only `pop_of_interest` varies with (classif1, sex, year). So the
    # whole nest is one broadcast multiply against a pivoted lookup. No ray.
    # ------------------------------------------------------------------
    agg = _build_agg_lookup(data_list_old)
    agg_labels = set(agg.index.get_level_values("ref_area.label").unique())
    years_list = list(years_to_build)

    from_cia_to_ilo = _build_cia_countries(
        missing_countries=missing_countries,
        fetched_data=fetched_data,
        df=df,
        agg=agg,
        agg_labels=agg_labels,
        cc_all=cc_all,
        classifications=classifications,
        list_sex=list_sex,
        years=years_list,
        columns=column_data_list,
    )

    from_cia_to_ilo2 = _build_xlsx_entities(
        missing_data=missing_data,
        agg=agg,
        agg_labels=agg_labels,
        cc_all=cc_all,
        already_covered=set(from_cia_to_ilo["ref_area"].unique()),
        year_cols=year_cols,
        last_xlsx_year=last_xlsx_year,
        classifications=classifications,
        list_sex=list_sex,
        years=years_list,
        columns=column_data_list,
    )

    print(f"[cia_to_ilo] built {len(from_cia_to_ilo):,} rows from CIA-anchored "
          f"countries and {len(from_cia_to_ilo2):,} rows from the hand-compiled "
          f"entities")

    from_cia_to_ilo = pd.concat([from_cia_to_ilo, from_cia_to_ilo2])

    return from_cia_to_ilo,missing_countries
