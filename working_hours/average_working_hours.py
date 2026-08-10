import pandas as pd
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
import config as _cfg
from regression_ILO_region_with_minimum_ray import regression_r
from regression_ILO_region_with_minimum import regression
import country_converter as coco
from clean_workforce import clean
from clean_hour_list import clean_hour
from clean_hour_eurostat import reshape_eurostat
#from isic3_to_isic4 import correspondance_isic
#from substitute import substitute_isic_a
from substitute import substitute_isic_a_ray
from combine_isic_3_4_vectorised import combine
from aggregate_isic_vectorised import (AGGREGATE_CASCADE_SKIP,
                                       AGGREGATE_YEARS, aggregate)
from average_hour import average_working_hour
from isic3_to_isic4_vectorised import isic3_to_isic4
from complete_hours import complete
from complete_hours_2 import complete2

# The ISIC3 -> ISIC4 conversion used to be 22 task_* functions fanned out over a
# ProcessPoolExecutor, each handed a pickled copy of the workforce frame. See
# isic3_to_isic4_vectorised for what they computed and why they were replaced.
#
# The upper bound is the original's hardcoded range(1995, 2023). It does not
# matter what it is: combine_isic_3_4 keeps ISIC3-derived values only for years
# before 2009 and takes native ISIC4 from 2009 on. Left as it was so the
# intermediate isic4_from_isic3_data.csv is unchanged.
ISIC3_CONVERSION_YEARS = range(1995, 2023)

# Ukraine's population weights were filled from this span, not `build_years`,
# because its ILO series stops in 2021; the 2022 row is then extrapolated from
# 2021 further down.
UKRAINE_POPULATION_YEARS = range(1991, 2022)

# Ukraine's ILO series ends here; the following year is carried forward with the
# population scaled by this factor. The same 0.845 appears in isic3_to_isic4.
UKRAINE_LAST_YEAR = 2021
UKRAINE_WAR_FACTOR = 0.845

#: Per-year hours-by-skill workbook, written by the hours split and read back by
#: the final table build. One name for both: the writer said
#: `hours_split_newSUTS.xlsx` and the reader `hours_split.xlsx`, so the read
#: could only ever have found a file left behind by an older run.
HOURS_SPLIT_FILENAME = 'hours_split_newSUTS.xlsx'

#: Years discarded from the hours series before the split. Empty for the 3.11.2
#: build; was an unconditional `time != 2023`. See the call site.
DROP_YEARS: set[int] = set()


#: Counts of what `sector_hours_pair` had to fall back on, reported at the end
#: of the hours split so a run says out loud how much was substituted.
HOURS_FALLBACKS = {'substituted_other_sex': 0, 'skipped': 0}

#: Every (region, category, year, what-happened) the hours split had to fall
#: back on, written to `hours_fallbacks.csv` so the substitutions and the gaps
#: can be audited instead of taken on trust from a count.
HOURS_FALLBACK_LOG = []


def sector_hours_pair(frame, region_column, region, classif1, year,
                      value_column):
    """Male and female average weekly hours for one (region, category, year).

    Returns (hours_M, hours_F), or (None, None) if neither sex is reported.

    Where only one sex is reported, the other takes its value. This affects 85
    of 22,619 cells on the current data, almost all of them ECO_DETAILS_B
    (mining and quarrying), where female employment is small enough that the
    ILO suppresses the figure; Luxembourg and Malta are 58 of the 85. The
    alternative, treating the missing sex as zero hours, would silently drop
    that sex's employment from the published stressor, which is the worse
    error. No cell in the current data is missing the male figure.

    The original called `float(...to_string(...))` on both without a guard and
    died on the first suppressed cell.
    """
    rows = frame.loc[(frame[region_column] == region)
                     & (frame['classif1'] == classif1)
                     & (frame['time'] == year), ['sex', value_column]].dropna()
    values = {}
    for sex in ('SEX_M', 'SEX_F'):
        match = rows.loc[rows['sex'] == sex, value_column]
        if len(match):
            values[sex] = float(match.iloc[0])

    if not values:
        HOURS_FALLBACKS['skipped'] += 1
        HOURS_FALLBACK_LOG.append((region, classif1, year, 'no hours',
                                   value_column))
        return None, None
    if len(values) == 1:
        HOURS_FALLBACKS['substituted_other_sex'] += 1
        HOURS_FALLBACK_LOG.append(
            (region, classif1, year,
             'only ' + next(iter(values)), value_column))
        only = next(iter(values.values()))
        return values.get('SEX_M', only), values.get('SEX_F', only)
    return values['SEX_M'], values['SEX_F']


#: ILO aggregate economic activity -> the ISIC Rev.4 sections it covers, read
#: off the `classif1.label` values in the ILOSTAT export rather than assumed:
#:   AGR Agriculture
#:   MEL Mining and quarrying; Electricity, gas and water supply
#:   MAN Manufacturing
#:   CON Construction
#:   MKT Trade, Transportation, Accommodation and Food, and Business and
#:       Administrative Services
#:   PUB Public Administration, Community, Social and other Services and
#:       Activities
#: Together they partition A-U, plus X for "not classified".
AGGREGATE_TO_ISIC4 = {
    'AGR': ['A'],
    'MEL': ['B', 'D', 'E'],
    'MAN': ['C'],
    'CON': ['F'],
    'MKT': ['G', 'H', 'I', 'J', 'K', 'L', 'M', 'N'],
    'PUB': ['O', 'P', 'Q', 'R', 'S', 'T', 'U'],
    'X': ['X'],
}


def add_isic4_from_aggregates(hours, verbose=True):
    """Give countries that report only aggregate hours an ISIC Rev.4 breakdown.

    96 countries report hours by ISIC Rev.4 section. A few report only the
    aggregate breakdown, and since the pipeline filters to `ISIC3|ISIC4` at the
    first step they were dropped entirely - carried through to the published
    extension as a workforce with zero hours. Canada is the case that matters:
    1,800 rows of hours over 1976-2025, both sexes, none of it by ISIC. The
    original code carries the author's note about it, untranslated:
    "VERIFIER SI CANADA EST DANS LA NOUVELLE LISTE".

    Each aggregate's hours are copied to every ISIC section it covers, so the
    country's own reported hours are used at the resolution it publishes them.
    Coarser than a real ISIC breakdown - the eight MKT sections all take one
    value - but it is that country's own data, and the alternative is
    publishing its entire workforce at zero hours.
    """
    classif = hours['classif1'].astype(str)
    reports_isic = set(hours.loc[classif.str.contains('ISIC3|ISIC4'),
                                 'ref_area'].unique())
    aggregates = hours[classif.str.startswith('ECO_AGGREGATE_')].copy()
    missing = sorted(set(aggregates['ref_area'].unique()) - reports_isic)
    if not missing:
        return hours

    aggregates = aggregates[aggregates['ref_area'].isin(missing)]
    aggregates['_code'] = aggregates['classif1'].str.removeprefix(
        'ECO_AGGREGATE_')
    aggregates = aggregates[aggregates['_code'].isin(AGGREGATE_TO_ISIC4)]

    mapping = pd.DataFrame(
        [(code, section) for code, sections in AGGREGATE_TO_ISIC4.items()
         for section in sections], columns=['_code', '_section'])
    built = aggregates.merge(mapping, on='_code')
    built['classif1'] = 'ECO_ISIC4_' + built['_section']
    if 'classif1.label' in built.columns:
        built['classif1.label'] = ('Economic activity (ISIC-Rev.4): '
                                   + built['_section']
                                   + ' (from ILO aggregate '
                                   + built['_code'] + ')')
    built = built.drop(columns=['_code', '_section'])

    if verbose:
        print(f'[aggregate hours] {len(built):,} ISIC4 rows built from the ILO '
              f'aggregate breakdown for {len(missing)} countries that report no '
              f'ISIC detail: {missing}')
    return pd.concat([hours, built], ignore_index=True)


def concordance_category(concordance, sector):
    """ILO employment category for an EXIOBASE sector.

    `auxdata/Exiobase_ISIC_Rev-4.xlsx` carries the mapping in
    `ISIC REV 4_ILO_Alteryx`, already collapsed onto the categories the ILO
    actually publishes: D and E both give ECO_DETAILS_DE, H and J give
    ECO_DETAILS_HJ, L/M/N give ECO_DETAILS_LMN, R/S/T/U give ECO_DETAILS_RSTU.

    Read from the concordance rather than derived, because the alternative in
    this file - take the `Summary` column, cut it at the first dot, prepend
    ECO_DETAILS_ - produces the twenty-one bare ISIC letters, and eleven of
    those no longer exist once `aggregate` has collapsed the components.
    """
    match = concordance.loc[concordance['Name'] == sector,
                            'ISIC REV 4_ILO_Alteryx'].dropna()
    if match.empty:
        raise KeyError(f'sector {sector!r} has no ISIC REV 4_ILO_Alteryx entry '
                       'in auxdata/Exiobase_ISIC_Rev-4.xlsx')
    return str(match.iloc[0]).strip()


def regional_infill(targets, workforce_iso3, av2, classifications, build_years,
                    label):
    """Rows for countries that have a population but no reported hours.

    Each gets its region's weighted average hours and its own population.
    `targets` is a list of (ref_area, exio3_label, av2_region) - the label
    written out and the region the average is read from differ for Taiwan.

    Replaces two nested loops that scanned the 937k-row workforce and the
    weighted-average table once per (country, sex, category, year) cell and
    grew the result with `pd.concat` per row. Both lookups were unguarded
    `float(...to_string(...))` and died on the first combination the region had
    no average for. A row cannot be built without both halves, so those are
    skipped rather than invented.
    """
    if not targets:
        return pd.DataFrame()

    frame = pd.MultiIndex.from_product(
        [[t[0] for t in targets], ['SEX_F', 'SEX_M'], list(classifications),
         list(build_years)],
        names=['ref_area', 'sex', 'classif1', 'time']).to_frame(index=False)
    frame['EXIO3'] = frame['ref_area'].map({t[0]: t[1] for t in targets})
    frame['_region'] = frame['ref_area'].map({t[0]: t[2] for t in targets})

    population = workforce_iso3[['ref_area', 'sex', 'classif1', 'time',
                                 'obs_value']].drop_duplicates(
        ['ref_area', 'sex', 'classif1', 'time'], keep='first')
    frame = frame.merge(population, on=['ref_area', 'sex', 'classif1', 'time'],
                        how='left')

    average = av2[['EXIO3', 'sex', 'classif1', 'time',
                   'Weighted average working hours']].rename(
        columns={'EXIO3': '_region'}).drop_duplicates(
        ['_region', 'sex', 'classif1', 'time'], keep='first')
    frame = frame.merge(average, on=['_region', 'sex', 'classif1', 'time'],
                        how='left')

    usable = frame['obs_value'].notna() & frame[
        'Weighted average working hours'].notna()
    print(f'[infill {label}] {len(targets)} countries: {int(usable.sum()):,} '
          f'rows built, {int((~usable).sum()):,} skipped for want of a '
          f'population or a regional average')

    frame = frame[usable]
    return pd.DataFrame({
        'EXIO3': frame['EXIO3'].to_numpy(),
        'ref_area': frame['ref_area'].to_numpy(),
        'sex': frame['sex'].to_numpy(),
        'classif1': frame['classif1'].to_numpy(),
        'time': frame['time'].to_numpy(),
        'average weekly hours': frame[
            'Weighted average working hours'].to_numpy(),
        'population (1000)': frame['obs_value'].to_numpy(),
    })


def population_weights(hours_RoW, workforce, build_years):
    """Population by (ref_area, sex, classif1, time), aligned to `hours_RoW`.

    Replaces two nested loops that did a full-frame scan of the 937k-row
    workforce per (country, sex, category, year) cell and wrote the result one
    cell at a time. It is a left merge.

    Returns NaN where a country has no population for that cell rather than
    raising. The original called `float(...to_string(...))` unguarded - the
    guard above it is commented out, and is broken anyway (`if not (...).isnull`
    tests a bound method, so it is never true) - and died with
    `could not convert string to float: 'Empty DataFrame...'` on the first
    country whose ILO series ends early. Five do: LBN and SSD stop at 2023,
    PSE and SDN at 2022, UKR at 2021. NaN is what the caller wants: it drops
    those rows via `dropna(subset=['population (1000)'])`, and the weighted
    average below needs the column numeric, which an empty string would break.
    """
    keys = ['ref_area', 'sex', 'classif1', 'time']
    population = workforce[workforce['sex'].isin(['SEX_F', 'SEX_M'])][
        keys + ['obs_value']].copy()
    population['obs_value'] = pd.to_numeric(population['obs_value'],
                                            errors='coerce')
    population = population.drop_duplicates(keys, keep='first')

    is_ukraine = population['ref_area'].eq('UKR')
    population = population[
        (is_ukraine & population['time'].isin(list(UKRAINE_POPULATION_YEARS)))
        | (~is_ukraine & population['time'].isin(list(build_years)))]

    filled = hours_RoW[keys].merge(population, on=keys, how='left')
    gaps = filled[filled['obs_value'].isna()]
    if len(gaps):
        known_countries = set(population['ref_area'])
        known_years = set(population['time'])
        no_country = gaps[~gaps['ref_area'].isin(known_countries)]
        no_year = gaps[gaps['ref_area'].isin(known_countries)
                       & ~gaps['time'].isin(known_years)]
        other = len(gaps) - len(no_country) - len(no_year)
        print(f'[population] {len(gaps):,} of {len(filled):,} cells have no '
              f'workforce population and will be dropped: '
              f'{len(no_country):,} country absent '
              f'({gaps["ref_area"].nunique()} codes, e.g. '
              f'{sorted(no_country["ref_area"].unique())[:6]}), '
              f'{len(no_year):,} year out of range '
              f'(years {sorted(no_year["time"].unique())[:8]}), '
              f'{other:,} country and year present but not that combination')
    return filled['obs_value'].to_numpy()

def working_hour(workforce,src_csv2,data_path,src_csv3,final_path=None):
    # final_path was referenced further down but never defined or passed,
    # so this function could not reach its own combine step: it raised
    # NameError on `final_path / 'split_workforce_by_skill.xlsx'`.
    if final_path is None:
        raise ValueError('working_hour() needs final_path (the labour final_table directory)')
    final_path = Path(final_path)
    build_years = list(_cfg.year_range())
    print(f'[working_hour] years {build_years[0]}-{build_years[-1]} '
          f'({len(build_years)}) | final_path {final_path}')
        
    def w_avg(df, values, weights):
        d = df[values]
        w = df[weights]
        return (d * w).sum() / w.sum()
    
    '''
    workforce  = pd.read_csv('table_workforce_by_ISO3.csv')
    '''
    workforce,workforce2 = clean (workforce,coco)
   
    cc_all = coco.CountryConverter(include_obsolete=True)
    
    hour_list = pd.read_csv(data_path/src_csv2, encoding="utf-8-sig")
    # Before clean_hour filters to ISIC3|ISIC4 and so discards any country that
    # reports hours only at the aggregate level.
    hour_list = add_isic4_from_aggregates(hour_list)
    hour_list,hour_list_without_zero = clean_hour(hour_list)
                                
    hour_eurostat = pd.read_csv(data_path/src_csv3,  sep='\t|,', engine = 'python')
    # hour_eurostat2 = pd.read_csv(data_path/src_csv4,  sep='\t|,')

    hour_eurostat_reshape = reshape_eurostat(hour_eurostat,cc_all)
                    
    hour_eurostat_reshape_pivot = hour_eurostat_reshape.pivot(index=['ref_area','sex','classif1'],columns='time')['obs_value']
    hour_eurostat_reshape_pivot_interpolate = hour_eurostat_reshape_pivot.interpolate(method='linear',axis=1,limit_area='inside')
    
    hour_eurostat_reshape_pivot_extrapolate = regression(hour_eurostat_reshape_pivot_interpolate,1992,2008)
    
    hour_eurostat_reshape_pivot_extrapolate.to_csv('hour_eurostat.csv')
    
    isic3=hour_list_without_zero[hour_list_without_zero['classif1'].str.contains('ISIC3',regex=True)].copy()
    isic3.to_csv('isic3.csv',index=False)
    isic4=hour_list_without_zero[hour_list_without_zero['classif1'].str.contains('ISIC4',regex=True)].copy()
    isic4.to_csv('isic4.csv',index=False)

    isic4_from_isic3_data = isic3_to_isic4(isic3, workforce,
                                           ISIC3_CONVERSION_YEARS)

    isic4_from_isic3_data.to_csv('isic4_from_isic3_data.csv')
    
    '''
    Substituer ISIC A par la valeur de Eurostat pour 1995 a 2008
    '''
    #isic4_from_isic3_data = substitute_isic_a(hour_eurostat_reshape_pivot_extrapolate,isic4_from_isic3_data)
    isic4_from_isic3_data = substitute_isic_a_ray(hour_eurostat_reshape_pivot_extrapolate,isic4_from_isic3_data)

    
                           
    isic4_from_isic3_data['obs_value'] = pd.to_numeric(isic4_from_isic3_data['obs_value'])
    isic4_from_isic3_data['time']=isic4_from_isic3_data['time'].astype(int)
    
    isic4_from_isic3_data_pivot = pd.pivot_table(isic4_from_isic3_data, values="obs_value", index=["ref_area", "sex","classif1"], columns=["time"])
    isic4_from_isic3_data_pivot=isic4_from_isic3_data_pivot.reset_index()
    isic4_from_isic3_data_pivot.to_csv("isic4_from_isic3_data_pivot_ray.csv")
    
    
    new_table_150222=pd.DataFrame(data=None,columns=['ref_area','sex','classif1','time','obs_value','source'])
    new_table_150222_columns = new_table_150222.columns
    
    
    '''
    In order to get a new set of data, we choose to keep
    the data from ISIC4 from 2009
    the data from ISIC3 transformed to ISIC4 from 2009
    the data from ISIC3 before 2009
    '''
    '''JE ME SUIS ARRETE ICI'''
    '''VERIFIER SI CANADA EST DANS LA NOUVELLE LISTE'''
    
    new_table_150222 = combine(hour_list,isic4_from_isic3_data,new_table_150222,new_table_150222_columns,isic4)
    #new_table_150222 = combine_ray(hour_list,isic4_from_isic3_data,isic4)
    #new_table_150222.to_csv('new_table_150222.csv')
    
    new_table_150222_pivot = pd.pivot_table(new_table_150222, values="obs_value", index=["ref_area", "sex","classif1"], columns=["time"])
    new_table_150222_pivot=new_table_150222_pivot.reset_index()
    
    
    new_table_150222 = aggregate(new_table_150222, new_table_150222_columns,
                                 years=AGGREGATE_YEARS,
                                 cascade_skip=AGGREGATE_CASCADE_SKIP)

    
    #new_table_150222.to_csv('new_table_150222_aggregate_ISIC.csv') 
    
    new_table_150222_pivot = new_table_150222.pivot(index=['ref_area','sex','classif1'],columns='time')['obs_value']
    new_table_150222_pivot.to_csv("new_table_150222_pivot_aggregate_ISIC.csv")  
    
    new_table_150222_pivot_interpolate = new_table_150222_pivot.interpolate(method='linear',axis=1,limit_area='inside')
    new_table_150222_pivot_interpolate=new_table_150222_pivot_interpolate.round(2)
    new_table_150222_pivot_interpolate.to_csv("new_table_150222_aggregate_ISIC_pivot_interpolate.csv")
    new_table_150222_pivot_interpolate_old=new_table_150222_pivot_interpolate.copy()
    
    
    
    # Extend every country's hours series across the whole build range, filling
    # from adjacent observations. The bound was hardcoded to 2023, so nothing
    # was extended into 2024 or 2025 and only the raw ILO observations survived
    # there - 1,739 series in 2025 against 5,394 rows. The consequence reached
    # the published extension: eight regions, 32% of global employment
    # (CN, JP, ID, AU, ZA, CA, LU, WM), carried employment with zero hours in
    # 2025, and six regions, 28%, in 2024. Now the config range.
    new_table_150222_pivot_extrapolate = regression_r(
        new_table_150222_pivot_interpolate, build_years[0], build_years[-1])
    '''OK jusque la'''
    
    new_table_150222_pivot_extrapolate=new_table_150222_pivot_extrapolate.round(2)
    #new_table_150222_pivot_extrapolate.to_csv("new_table_150222_pivot_extrapolate_regression3_5_10.csv")
    
    new_table_150222_pivot_extrapolate2 =  new_table_150222_pivot_extrapolate.reset_index()
    
    new_table_150222_pivot_extrapolate2 = new_table_150222_pivot_extrapolate2.replace('KOS','XKX')
    #country_code_final = list(new_table_150222_pivot_extrapolate.index.get_level_values(0))
    country_code_final = list(new_table_150222_pivot_extrapolate2.ref_area)

    #new_table_150222_pivot_extrapolate2.insert(0, 'EXIO3', cc_all.convert(names = country_code_final,src="ISO3", to='EXIO3'))
    
    #final_table_workforce =pd.DataFrame(data=None,columns=['EXIO3','sex','classif1','time','obs_value'])
    
        
    '''VOIR CETTE PARTIE LA 
    j en ai besoin'''
    
    '''JE SUIS ICI'''
    #final_table = average_working_hour(new_table_150222_pivot_extrapolate,cc_all,workforce2,final_table)

    #final_table = average_working_hour(new_table_150222_pivot_extrapolate2,cc_all,workforce2,final_table)
    '''  
    final_table.to_csv("final_table.csv",index = False)
    final_table = final_table[final_table.time != 2020]
    '''
    
    table_hours = new_table_150222_pivot_extrapolate.stack()
    table_hours = table_hours.reset_index()
    
    table_hours = table_hours.rename({0: 'average weekly hours'}, axis='columns')    

    workforce_iso3 = workforce.copy()
    #workforce_iso3 = pd.read_csv('table_workforce_by_ISO3.csv')
    workforce_iso3 = workforce_iso3.loc[workforce_iso3.classif1 !='ECO_SECTOR_TOTAL']
    workforce_iso3 = workforce_iso3.loc[workforce_iso3.classif1 !='ECO_SECTOR_AGR']
    workforce_iso3 = workforce_iso3.loc[workforce_iso3.classif1 !='ECO_SECTOR_IND']
    workforce_iso3 = workforce_iso3.loc[workforce_iso3.classif1 !='ECO_SECTOR_SER']
    workforce_iso3 = workforce_iso3.loc[workforce_iso3.classif1 !='ECO_AGGREGATE_TOTAL']
    workforce_iso3 = workforce_iso3.loc[workforce_iso3.classif1 !='ECO_AGGREGATE_AGR']
    workforce_iso3 = workforce_iso3.loc[workforce_iso3.classif1 !='ECO_AGGREGATE_MAN']
    workforce_iso3 = workforce_iso3.loc[workforce_iso3.classif1 !='ECO_AGGREGATE_CON']
    workforce_iso3 = workforce_iso3.loc[workforce_iso3.classif1 !='ECO_AGGREGATE_MEL']
    workforce_iso3 = workforce_iso3.loc[workforce_iso3.classif1 !='ECO_AGGREGATE_MKT']
    workforce_iso3 = workforce_iso3.loc[workforce_iso3.classif1 !='ECO_AGGREGATE_PUB']
    workforce_iso3 = workforce_iso3.loc[workforce_iso3.classif1 !='ECO_DETAILS_TOTAL']
    #workforce_iso3 = workforce_iso3.drop(['ref_area.label'],axis = 1)
    
    hours = table_hours.copy()
    
    hours=hours.reset_index()
    hours = hours.drop(['index'],axis = 1)
    
    '''THIS SHOULD USE RAY'''    
    complete_hour = complete(hours)
    # for code in hours.ref_area.unique() :
    #     print(code)
    #     for sex in hours.sex.unique() : 

                
    #         for years in range(1995, 2024):
    #     #for b in hours.classif1 :
    #             if not 'ECO_ISIC4_A' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_A','time' :[years]})
    #                 hours=pd.concat([hours,new_row])
    #             if not 'ECO_ISIC4_B' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_B','time' :[years]})
    #                 hours=pd.concat([hours,new_row])
    #             if not 'ECO_ISIC4_C' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_C','time' :[years]})
    #                 hours=pd.concat([hours,new_row])
    #             if not 'ECO_ISIC4_D' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_D','time' :[years]})
    #                 hours=pd.concat([hours,new_row])    
    #             if not 'ECO_ISIC4_E' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_E','time' :[years]})
    #                 hours=pd.concat([hours,new_row])
    #             if not 'ECO_ISIC4_F' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_F','time' :[years]})
    #                 hours=pd.concat([hours,new_row])
    #             if not 'ECO_ISIC4_G' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_G','time' :[years]})
    #                 hours=pd.concat([hours,new_row])
    #             if not 'ECO_ISIC4_H' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_H','time' :[years]})
    #                 hours=pd.concat([hours,new_row])   
                    
    #             if not 'ECO_ISIC4_I' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_I','time' :[years]})
    #                 hours=pd.concat([hours,new_row])
    #             if not 'ECO_ISIC4_J' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_J','time' :[years]})
    #                 hours=pd.concat([hours,new_row])
    #             if not 'ECO_ISIC4_K' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_K','time' :[years]})
    #                 hours=pd.concat([hours,new_row])
    #             if not 'ECO_ISIC4_L' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_L','time' :[years]})
    #                 hours=pd.concat([hours,new_row])    
    #             if not 'ECO_ISIC4_M' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_M','time' :[years]})
    #                 hours=pd.concat([hours,new_row])
    #             if not 'ECO_ISIC4_N' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_N','time' :[years]})
    #                 hours=pd.concat([hours,new_row])
    #             if not 'ECO_ISIC4_O' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_O','time' :[years]})
    #                 hours=pd.concat([hours,new_row])
    #             if not 'ECO_ISIC4_P' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_P','time' :[years]})
    #                 hours=pd.concat([hours,new_row])                  
                   
    #             if not 'ECO_ISIC4_Q' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_Q','time' :[years]})
    #                 hours=pd.concat([hours,new_row])
    #             if not 'ECO_ISIC4_R' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_R','time' :[years]})
    #                 hours=pd.concat([hours,new_row])
    #             if not 'ECO_ISIC4_S' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_S','time' :[years]})
    #                 hours=pd.concat([hours,new_row])
    #             if not 'ECO_ISIC4_T' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_T','time' :[years]})
    #                 hours=pd.concat([hours,new_row])    
    #             if not 'ECO_ISIC4_U' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_U','time' :[years]})
    #                 hours=pd.concat([hours,new_row])
    #             if not 'ECO_ISIC4_X' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_X','time' :[years]})
    #                 hours=pd.concat([hours,new_row])            
    #             if not 'ECO_ISIC4_DE' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_DE','time' :[years]})
    #                 hours=pd.concat([hours,new_row]) 
    #             if not 'ECO_ISIC4_HJ' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_HJ','time' :[years]})
    #                 hours=pd.concat([hours,new_row])   
    #             if not 'ECO_ISIC4_LMN' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_LMN','time' :[years]})
    #                 hours=pd.concat([hours,new_row])   
    #             if not 'ECO_ISIC4_RSTU' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
    #                 new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_RSTU','time' :[years]})
    #                 hours=pd.concat([hours,new_row])  
    
    complete_hour = complete_hour.reset_index()
    complete_hour = complete_hour.drop(columns = 'index',axis = 1)

    complete_hour.to_csv('hours_ini.csv',index=False)               
    hours = complete_hour.copy()
    '''Kosovo ISO3 is defined as KOS instead of XKX'''
    hours = hours.replace('KOS','XKX')
    hours=hours.reset_index()
    hours = hours.drop(['index'],axis = 1)
    
    country_code_final = list(hours.ref_area)
    hours.insert(0, 'EXIO3', cc_all.convert(names = country_code_final,src="ISO3", to='EXIO3'))
    workforce_iso3["average weekly hours"] = ''

    complete_hour2 = complete2(hours)
    complete_hour2 = complete_hour2.reset_index()
    complete_hour2 = complete_hour2.drop(columns = 'index',axis = 1)

    complete_hour2.to_csv('hours_ini2_ray.csv',index=False)               
    hours = complete_hour2.copy()    
    #hours.fillna(0)
    
    '''a faire aussi en ray'''

    # for code in hours.ref_area.unique() :
    #     for sex in hours.sex.unique() :
    #         for years in range(1995, 2024):
    #             print(code, sex, years)
    #             if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_D')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                 D = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_D')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
    #                 if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_E')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                     E = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_E')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
    #                     DE = (D+E)/2
    #                     hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_DE')&(hours.time == years), 'average weekly hours']=DE                    
    #                 else :
    #                     DE = D
    #                     hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_DE')&(hours.time == years), 'average weekly hours']=DE           
    #             elif not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_E')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                 E = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_E')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
    #                 DE = E

    #                 hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_DE')&(hours.time == years), 'average weekly hours']=DE                      
    #             else :

    #                 hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_DE')&(hours.time == years), 'average weekly hours']=0                    

                        
                        
    # for code in hours.ref_area.unique() :
    #     for sex in hours.sex.unique() :
    #         for years in range(1995, 2024):
    #             print(code, sex, years)

    #             if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_H')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                 H = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_H')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
    #                 if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_J')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                     J = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_J')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
    #                     HJ = (H+J)/2
    #                     hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_HJ')&(hours.time == years), 'average weekly hours']=HJ                    
    #                 else :
    #                     HJ = H
    #                     hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_HJ')&(hours.time == years), 'average weekly hours']=HJ          
    #             elif not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_J')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                 J = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_J')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
    #                 HJ = J

    #                 hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_HJ')&(hours.time == years), 'average weekly hours']=HJ               
    #             else :

    #                 hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_HJ')&(hours.time == years), 'average weekly hours']=0                    

                                   
    # for code in hours.ref_area.unique() :
    #     for sex in hours.sex.unique() :
    #         for years in range(1995, 2024):
    #             print(code, sex, years)

    #             if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_L')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                 L = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_L')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
    #                 if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_M')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                     M = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_M')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
    #                     if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_N')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                         N = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_N')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                        
    #                         LMN = (L+M+N)/3
    #                         hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_LMN')&(hours.time == years), 'average weekly hours']=LMN   
    #                     else :
    #                         LMN = (L+M)/2
    #                         hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_LMN')&(hours.time == years), 'average weekly hours']=LMN   
    #                 else :
    #                     if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_N')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                         N = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_N')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                        
    #                         LMN = (L+N)/2
    #                         hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_LMN')&(hours.time == years), 'average weekly hours']=LMN   
    #                     else :
    #                         LMN = L
    #                         hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_LMN')&(hours.time == years), 'average weekly hours']=LMN   
    #             else :
    #                 if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_M')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                     M = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_M')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
    #                     if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_N')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                         N = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_N')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                        
    #                         LMN = (M+N)/2
    #                         hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_LMN')&(hours.time == years), 'average weekly hours']=LMN   
    #                     else :
    #                         LMN = M
    #                         hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_LMN')&(hours.time == years), 'average weekly hours']=LMN   
    #                 else :
                        
    #                     if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_N')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                         N = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_N')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                        
    #                         LMN = N
    #                         hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_LMN')&(hours.time == years), 'average weekly hours']=LMN   
    #                     else :
    #                         LMN = 0
    #                         hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_LMN')&(hours.time == years), 'average weekly hours']=LMN   
                        
                
                        
                
    # for code in hours.ref_area.unique() :
    #     for sex in hours.sex.unique() :
    #         for years in range(1995, 2024):
    #             print(code, sex, years)

    #             if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_R')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                 R = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_R')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
    #                 if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_S')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                     S = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_S')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
    #                     if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_T')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                         T = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_T')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
    #                         if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                             U = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False)) 
    #                             RSTU = (R+S+T+U)/4
    #                             hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
    #                         else :
    #                             RSTU = (R+S+T)/3
    #                             hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                                
    #                     else :
                            
    #                         if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                             U = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False)) 
    #                             RSTU = (R+S+U)/3
    #                             hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
    #                         else :
    #                             RSTU = (R+S)/2
    #                             hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU                               
                                                            
    #                 else :
    #                     if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_T')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                         T = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_T')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
    #                         if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                             U = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False)) 
    #                             RSTU = (R+T+U)/3
    #                             hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
    #                         else :
    #                             RSTU = (R+T)/2
    #                             hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                                
    #                     else :
                            
    #                         if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                             U = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False)) 
    #                             RSTU = (R+U)/2
    #                             hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
    #                         else :
    #                             RSTU = (R)
    #                             hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                        
                                
    #             else :
    #                if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_S')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                    S = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_S')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
    #                    if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_T')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                        T = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_T')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
    #                        if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                            U = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False)) 
    #                            RSTU = (S+T+U)/3
    #                            hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
    #                        else :
    #                            RSTU = (S+T)/2
    #                            hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                               
    #                    else :
                           
    #                        if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                            U = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False)) 
    #                            RSTU = (S+U)/2
    #                            hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
    #                        else :
    #                            RSTU = (S)
    #                            hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU                               
                                                           
    #                else :
    #                    if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_T')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                        T = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_T')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
    #                        if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                            U = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False)) 
    #                            RSTU = (T+U)/2
    #                            hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
    #                        else :
    #                            RSTU = (T)
    #                            hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                               
    #                    else :
                           
    #                        if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].isna().all()):
    #                            U = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False)) 
    #                            RSTU = (U)
    #                            hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
    #                        else :
    #                            RSTU = 0
    #                            hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                    
                            
                            
#    hours = hours.loc[hours.classif1 !='ECO_ISIC4_D']
#    hours = hours.loc[hours.classif1 !='ECO_ISIC4_E']
#    hours = hours.loc[hours.classif1 !='ECO_ISIC4_H']
#    hours = hours.loc[hours.classif1 !='ECO_ISIC4_J']
#    hours = hours.loc[hours.classif1 !='ECO_ISIC4_L']
#    hours = hours.loc[hours.classif1 !='ECO_ISIC4_M']
#    hours = hours.loc[hours.classif1 !='ECO_ISIC4_N']
#    hours = hours.loc[hours.classif1 !='ECO_ISIC4_R']                            
#    hours = hours.loc[hours.classif1 !='ECO_ISIC4_S']
#    hours = hours.loc[hours.classif1 !='ECO_ISIC4_T']
#    hours = hours.loc[hours.classif1 !='ECO_ISIC4_U']                   
                            
    hours=hours.fillna(0)
    # Put the hours onto the workforce's category names so the two join. This
    # was 24 literal `replace('ECO_ISIC4_<x>', 'ECO_DETAILS_<x>')` calls, which
    # stopped matching once `combine` resumed stripping the revision digit:
    # the rows arrive as ECO_ISIC_G, not ECO_ISIC4_G. One rule covers both
    # spellings, so it works whichever convention upstream uses. The block also
    # named ECO_ISIC4_DE/HJ/LMN/RSTU, which the ILO export does not contain at
    # all - those exist only as `aggregate` output, and `aggregate` emits the
    # stripped form - so the literals were stale by one revision.
    hours['classif1'] = hours['classif1'].str.replace(r'^ECO_ISIC\d?_',
                                                      'ECO_DETAILS_', regex=True)

    # `hours` arrives as an empty skeleton (workforce categories, no values,
    # zeroed by the fillna above) plus the rows carrying the actual hours. The
    # rename lands the second on the first, leaving two rows per key: the
    # placeholder and the value. Drop the placeholders. Verified on this data:
    # every skeleton row is 0.0 and every hours row is non-zero, so no real
    # observation is lost - a zero average weekly hours is not an observation.
    zero_hours = hours['average weekly hours'] == 0
    print(f'[hours] dropping {int(zero_hours.sum()):,} placeholder rows with no '
          f'hours, keeping {int((~zero_hours).sum()):,}')
    hours = hours[~zero_hours]


    list_exio3 = []
    for a in hours.EXIO3.unique() : 
        if not a in ['WA','WE','WF','WM','WL','not found']:
            list_exio3.append(a)
    list_RoW = []
    for a in hours.EXIO3.unique() : 
        if  a in ['WA','WE','WF','WM','WL','not found']:
            list_RoW.append(a)
    hours_RoW = hours.copy()
    hours_RoW = hours_RoW.loc[(hours_RoW.EXIO3 =='WA') | (hours_RoW.EXIO3 =='WE') | (hours_RoW.EXIO3 =='WF')|  (hours_RoW.EXIO3 =='WM') | (hours_RoW.EXIO3 =='WL')]
    hours_RoW = hours_RoW.loc[(hours_RoW.classif1 !='ECO_DETAILS_TOTAL')]
    hours_RoW = hours_RoW.loc[(hours_RoW.classif1 !='ECO_ISIC4_TOTAL')]
    hours_RoW = hours_RoW.loc[hours_RoW.classif1 !='ECO_DETAILS_D']
    hours_RoW = hours_RoW.loc[hours_RoW.classif1 !='ECO_DETAILS_E']
    hours_RoW = hours_RoW.loc[hours_RoW.classif1 !='ECO_DETAILS_H']
    hours_RoW = hours_RoW.loc[hours_RoW.classif1 !='ECO_DETAILS_J']
    hours_RoW = hours_RoW.loc[hours_RoW.classif1 !='ECO_DETAILS_L']
    hours_RoW = hours_RoW.loc[hours_RoW.classif1 !='ECO_DETAILS_M']
    hours_RoW = hours_RoW.loc[hours_RoW.classif1 !='ECO_DETAILS_N']
    hours_RoW = hours_RoW.loc[hours_RoW.classif1 !='ECO_DETAILS_R']                            
    hours_RoW = hours_RoW.loc[hours_RoW.classif1 !='ECO_DETAILS_S']
    hours_RoW = hours_RoW.loc[hours_RoW.classif1 !='ECO_DETAILS_T']
    hours_RoW = hours_RoW.loc[hours_RoW.classif1 !='ECO_DETAILS_U']                   
                                
    hours_RoW['population (1000)'] = population_weights(hours_RoW, workforce,
                                                        build_years)
    hours.to_csv('hours2203_1.csv',index = False)
    hours_RoW.to_csv('hoursRoW2403_2.csv',index = False)

    hours_RoW = hours_RoW.loc[hours_RoW.ref_area !='SYC']
    hours_RoW = hours_RoW.loc[hours_RoW.ref_area !='REU']
    hours_RoW = hours_RoW.loc[hours_RoW.ref_area !='IMN']


    # Both frames used to have `time != 2023` applied here, unconditionally.
    # That dates from when 2023 was the ragged last year of the series; it is
    # now a complete year (5,243 rows, the same as every year from 1995 to
    # 2022, verified on this data) sitting in the middle of a range that runs
    # to 2025, so dropping it punched a hole through the published series and
    # left every 2023 sector cell at zero. Set DROP_YEARS to {2023} to restore
    # the old behaviour.
    if DROP_YEARS:
        print(f'[hours] dropping years {sorted(DROP_YEARS)} by configuration')
        hours_RoW = hours_RoW.loc[~hours_RoW.time.isin(DROP_YEARS)]
        hours = hours.loc[~hours.time.isin(DROP_YEARS)]
    hours_RoW = hours_RoW.loc[hours_RoW.classif1 !='ECO_DETAILS_X']    
    hours = hours.loc[hours.classif1 !='ECO_DETAILS_X']                   
    hours_RoW.dropna(subset=['population (1000)'], inplace=True)               

    ''' Add values for 2022 for Ukraine as they are missing.
    We assume that the 2022 values are 15.5% below the 2021 values ->
    Source ILO
    '''
    
    '''drop data for UKR 2022'''
    rem = hours_RoW.loc[(hours_RoW.ref_area =='UKR')&(hours_RoW.time == 2022)].index
    hours_RoW = hours_RoW.drop(rem)
    
    for code in workforce_iso3.ref_area.unique() : 
        if code == 'UKR':
            for sex in ['SEX_F','SEX_M']:
                for c in hours_RoW.classif1.unique():
                    print(sex, c)
                    
                    value_2021 = float(hours_RoW.loc[(hours_RoW['ref_area']=='UKR')&(hours_RoW['sex']==sex)&(hours_RoW['classif1']==c)&(hours_RoW['time']==2021),['population (1000)']].to_string(index=False, header=False))
                    hours_2021 = float(hours_RoW.loc[(hours_RoW['ref_area']=='UKR')&(hours_RoW['sex']==sex)&(hours_RoW['classif1']==c)&(hours_RoW['time']==2021),['average weekly hours']].to_string(index=False, header=False))
                    print(c,value_2021,hours_2021)
                    new_row = pd.DataFrame({'EXIO3' : 'WE','ref_area':'UKR','sex':[sex],'classif1':[c],'time' :2022,'average weekly hours': [hours_2021], 'population (1000)': 0.845 * value_2021 })
                    hours_RoW=pd.concat([hours_RoW,new_row])
    
    hours_RoW = hours_RoW.reset_index()
    hours_RoW = hours_RoW.drop(['index'],axis =1)
    
    '''weighted average'''
    av2 = hours_RoW.groupby(['EXIO3','sex','classif1','time']).apply(w_avg, 'average weekly hours', 'population (1000)')
    av2 = av2.reset_index()
    av2.rename({0: 'Weighted average working hours'}, axis=1, inplace=True)
    ''' - 15.5% from previsous year'''
    
    
    '''WE NEED TO ADD DATA FOR COUNTRIES FOR WHICH WE HAVE WORKFORCE BUT NOT WORKING HOURS'''
    '''we need to add to hours_Row the countries (part of a RoW region) for which we have the population but not the working hours.'''
    #workforce_iso3.drop(workforce_iso3.tail(1276).index,inplace=True)
    #rm = workforce_iso3.loc[819830:821105].index
    #workforce_iso3 = workforce_iso3.drop(rm)
    hours_RoW.to_csv('hours_RoW_2403_3.csv',index=False)
    
    missing_hours = []
    known = set(hours_RoW.ref_area.unique())
    for a in workforce2.ref_area.unique():
        if a not in known and not any(chr.isdigit() for chr in a):
            region = cc_all.convert(names=a, src="ISO3", to='EXIO3')
            if region in list_RoW:
                missing_hours.append((a, region, region))
    infilled = regional_infill(missing_hours, workforce_iso3, av2,
                               hours_RoW.classif1.unique(), build_years, 'RoW')
    if len(infilled):
        hours_RoW = pd.concat([hours_RoW, infilled])


    hours_RoW = hours_RoW.reset_index()
    hours_RoW = hours_RoW.drop(['index'],axis =1)

    hours_RoW_old = hours_RoW.copy()
    hours_main_country = hours.copy()
    hours_main_country =  hours_main_country.loc[(hours_main_country.EXIO3 !='WA') & (hours_main_country.EXIO3 !='WE') & (hours_main_country.EXIO3 !='WF') &  (hours_main_country.EXIO3 !='WM') & (hours_main_country.EXIO3 !='WL')]


    # Taiwan: published under its own EXIO3 region TW, but it reports no hours,
    # so it borrows the Asia-Pacific RoW average (WA).
    taiwan = [('TWN', 'TW', 'WA')] if (
        'TWN' in set(workforce2.ref_area.unique())
        and 'TWN' not in set(hours_main_country.ref_area.unique())) else []
    infilled_taiwan = regional_infill(taiwan, workforce_iso3, av2,
                                      hours_RoW.classif1.unique(), build_years,
                                      'TWN')
    if len(infilled_taiwan):
        hours_main_country = pd.concat([hours_main_country, infilled_taiwan])

    # Ukraine's ILO series stops in 2021, so 2022 carries its 2021 hours with
    # the population scaled by the war-year factor. Was a per-(sex, category)
    # loop of unguarded lookups; categories with no 2021 row now drop out
    # instead of raising, since there is nothing to carry forward.
    #
    # Four lines that lived in this loop have been deleted rather than
    # converted: they were a copy of the Taiwan block above, still reading `a`
    # and `t` from the loop that used to precede it. In the original those held
    # whatever the previous loop last left behind, so the block appended
    # TW-labelled rows for an arbitrary country in an arbitrary year, once per
    # (sex, category) of the Ukraine loop. Taiwan is handled properly above.
    ukraine_2021 = hours_RoW[(hours_RoW['ref_area'] == 'UKR')
                             & (hours_RoW['time'] == UKRAINE_LAST_YEAR)]
    if len(ukraine_2021):
        ukraine_2022 = ukraine_2021.copy()
        ukraine_2022['EXIO3'] = 'WE'
        ukraine_2022['time'] = UKRAINE_LAST_YEAR + 1
        ukraine_2022['population (1000)'] = (
            UKRAINE_WAR_FACTOR * pd.to_numeric(
                ukraine_2021['population (1000)']).to_numpy())
        print(f'[ukraine] carrying {len(ukraine_2022):,} rows from '
              f'{UKRAINE_LAST_YEAR} to {UKRAINE_LAST_YEAR + 1} at '
              f'{UKRAINE_WAR_FACTOR} population')
        hours_RoW = pd.concat([hours_RoW, ukraine_2022])


    for code in workforce2.ref_area.unique() : 
        if  code in hours_main_country.ref_area.unique():
            if code != 'TWN':
                if code == 'AUS':
                    for sex in ['SEX_F','SEX_M']:
                        #for c in hours_main_country.classif1.unique():
                        for c in workforce2.classif1.unique():
                            for t in workforce2.time.unique():
                                P = float(workforce2.loc[(workforce2['ref_area']==code)&(workforce2['sex']==sex)&(workforce2['classif1']==c)&(workforce2['time']==t),['obs_value']].to_string(header=False,index=False))
                                print(code, sex, c,t,P)
                                #H = float(hours.loc[(hours['ref_area']==code)&(hours['sex']==sex)&(hours['classif1']==c),str(years)].to_string(header=False, index=False))                        
                                hours_main_country.loc[(hours_main_country['ref_area']==code)&(hours_main_country['sex']==sex)&(hours_main_country['classif1']==c)&(hours_main_country['time']==t),['population (1000)']] = P 
                                    
                    
    hours_main_country = hours_main_country.reset_index()            
    hours_main_country = hours_main_country.drop(['index'],axis =1)            
    
    # for code in workforce_iso3.ref_area.unique():
    #     if not code in hours.ref_area.unique() :
    #         if not any(chr.isdigit() for chr in code):
                
    #             print(code) 
    #             for sex in hours.sex.unique() : 
    #                 for years in range(1995, 2024):
    #             #for b in hours.classif1 :
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_A','time' :[years]})
    #                     hours=pd.concat([hours,new_row])
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_B','time' :[years]})
    #                     hours=pd.concat([hours,new_row])
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_C','time' :[years]})
    #                     hours=pd.concat([hours,new_row])
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_D','time' :[years]})
    #                     hours=pd.concat([hours,new_row])    
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_E','time' :[years]})
    #                     hours=pd.concat([hours,new_row])
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_F','time' :[years]})
    #                     hours=pd.concat([hours,new_row])
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_G','time' :[years]})
    #                     hours=pd.concat([hours,new_row])
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_H','time' :[years]})
    #                     hours=pd.concat([hours,new_row])   
                        
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_I','time' :[years]})
    #                     hours=pd.concat([hours,new_row])
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_J','time' :[years]})
    #                     hours=pd.concat([hours,new_row])
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_K','time' :[years]})
    #                     hours=pd.concat([hours,new_row])
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_L','time' :[years]})
    #                     hours=pd.concat([hours,new_row])    
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_M','time' :[years]})
    #                     hours=pd.concat([hours,new_row])
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_N','time' :[years]})
    #                     hours=pd.concat([hours,new_row])
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_O','time' :[years]})
    #                     hours=pd.concat([hours,new_row])
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_P','time' :[years]})
    #                     hours=pd.concat([hours,new_row])                  
                       
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_Q','time' :[years]})
    #                     hours=pd.concat([hours,new_row])
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_R','time' :[years]})
    #                     hours=pd.concat([hours,new_row])
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_S','time' :[years]})
    #                     hours=pd.concat([hours,new_row])
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_T','time' :[years]})
    #                     hours=pd.concat([hours,new_row])    
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_U','time' :[years]})
    #                     hours=pd.concat([hours,new_row])
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_X','time' :[years]})
    #                     hours=pd.concat([hours,new_row])            
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_DE','time' :[years]})
    #                     hours=pd.concat([hours,new_row]) 
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_HJ','time' :[years]})
    #                     hours=pd.concat([hours,new_row])   
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_LMN','time' :[years]})
    #                     hours=pd.concat([hours,new_row])   
    #                     new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_RSTU','time' :[years]})
    #                     hours=pd.concat([hours,new_row])  
                        
                        
    vacation = pd.read_csv('auxdata/whole_vacation.csv')
    #vacation = vacation.drop(['Paid Leave Days'],axis=1)
    #vacation = vacation.drop(['Paid Public Holidays'],axis=1)
    vacation = vacation.drop(['Country','ISO3'],axis =1)
    vacation_average = round(vacation.groupby(['EXIO3']).mean())
    vacation_average = vacation_average.reset_index()
    '''il faut ouvrir split et proceder au calsul pour avoir les heures totales'''
    # hours_main_country = hours.copy()
    # hours_main_country =  hours_main_country.loc[(hours_main_country.EXIO3 !='WA') & (hours_main_country.EXIO3 !='WE') & (hours_main_country.EXIO3 !='WF') &  (hours_main_country.EXIO3 !='WM') & (hours_main_country.EXIO3 !='WL')]
    all_countries = []
    
    for a in hours_RoW.EXIO3.unique() : 
        all_countries.append(a)
    for a in hours_main_country.EXIO3.unique():
        all_countries.append(a)

        
    #hours_split_final = hours_split_year(all_countries)
    concordance = pd.read_excel('auxdata/Exiobase_ISIC_Rev-4.xlsx')    
    hours_split= pd.DataFrame(columns = ['EXIO3','Sector','Mapping', 'Hours High qualification employement - total', 'Hours Middle qualification employement - total', 'Hours Low qualification employement - total','Hours High qualification employement - male', 'Hours Middle qualification employement - male', 'Hours Low qualification employement - male','Hours High qualification employement - female', 'Hours Middle qualification employement - female', 'Hours Low qualification employement - female'])

    for code in all_countries:
        # for a in hours_main_country.classif1.unique():
        for a in hours_RoW.classif1.unique():

            'This was the correspondance to the full name of exiobase sector'
            list_name = concordance.loc[concordance['ISIC REV 4_ILO_Alteryx']==a,['Name']]
            'we changed it to the exiobase sector code -> CodeNr'
            #list_name = concordance.loc[concordance['ISIC REV 4_ILO_Alteryx']==a,['CodeNr']]
            # for b in list_name['Name']:

            for b in list_name['Name']:
                new_row = pd.DataFrame({'EXIO3':[code],'Sector':[b],'Mapping':[a], 'Hours High qualification employement - total':0, 'Hours Middle qualification employement - total':0, 'Hours Low qualification employement - total':0,'Hours High qualification employement - male':0, 'Hours Middle qualification employement - male':0, 'Hours Low qualification employement - male':0,'Hours High qualification employement - female':0, 'Hours Middle qualification employement - female':0, 'Hours Low qualification employement - female':0})
                hours_split=pd.concat([hours_split,new_row])

                #hours_split=hours_split.append(pd.Series([code,b,a,0,0,0,0,0,0,0,0,0], index=[i for i in hours_split.columns]),ignore_index=True)
    hours_split_empty = hours_split.copy()

    #xl = pd.ExcelFile('split_updated_1610.xlsx')
    xl = pd.ExcelFile(final_path / 'split_workforce_by_skill_newSUT.xlsx')


    hourSplit = {}
    #writer = pd.ExcelWriter('hours_split.xlsx',engine='xlsxwriter')

    for years in build_years:
        hours_split = hours_split_empty.copy()

        workforce_year = xl.parse(str(years))
        workforce_year.dropna(subset=['Country'],inplace=True)
        workforce_year=workforce_year.drop(columns='Unnamed: 0', axis =1)

        for code in  all_countries:
            print(years,code)
            if code in all_countries:
                if code in list_RoW :
                    for sector in hours_split['Sector'].unique():
                        pop_high_skill_men = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split High qualification employment - male'].to_string(index=False, header=False))
                        pop_middle_skill_men = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split Middle qualification employment - male'].to_string(index=False, header=False))
                        pop_low_skill_men = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split Low qualification employment - male'].to_string(index=False, header=False))

                        pop_high_skill_women = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split High qualification employment - female'].to_string(index=False, header=False))
                        pop_middle_skill_women = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split Middle qualification employment - female'].to_string(index=False, header=False))
                        pop_low_skill_women = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split Low qualification employment - female'].to_string(index=False, header=False))


                        vacation = float(vacation_average.loc[vacation_average.EXIO3 == code,'Total Paid Vacation Days'].to_string(index=False,header=False))

                        classif1 = concordance_category(concordance, sector)

                        hours_M, hours_F = sector_hours_pair(
                            av2, 'EXIO3', code, classif1, years,
                            'Weighted average working hours')
                        if hours_M is None:
                            continue
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - male' ] = pop_high_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - male' ] = pop_middle_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - male' ] = pop_low_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - male' ] = pop_high_skill_men * (hours_M) * (52) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - male' ] = pop_middle_skill_men * (hours_M) * (52) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - male' ] = pop_low_skill_men * (hours_M) * (52) / 1000000

                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - female' ] = pop_high_skill_women * (hours_F/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - female' ] = pop_middle_skill_women * (hours_F/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - female' ] = pop_low_skill_women * (hours_F/5) * (365-vacation) / 1000000

                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - female' ] = pop_high_skill_women * (hours_F) * (52) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - female' ] = pop_middle_skill_women * (hours_F) * (52) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - female' ] = pop_low_skill_women * (hours_F) * (52) / 1000000

                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - total' ] = (pop_high_skill_men * (hours_M/5) * (365-vacation) / 1000000) + (pop_high_skill_women * (hours_F/5) * (365-vacation) / 1000000)
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - total' ] = (pop_middle_skill_men * (hours_M/5) * (365-vacation) / 1000000) + (pop_middle_skill_women * (hours_F/5) * (365-vacation) / 1000000)
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - total' ] = (pop_low_skill_men * (hours_M/5) * (365-vacation) / 1000000) + (pop_low_skill_women * (hours_F/5) * (365-vacation) / 1000000)
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - total' ] = (pop_high_skill_men * (hours_M) * (52) / 1000000)+(pop_high_skill_women * (hours_F) * (52) / 1000000)
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - total' ] = (pop_middle_skill_men * (hours_M) * (52) / 1000000) + (pop_middle_skill_women * (hours_F) * (52) / 1000000)
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - total' ] = (pop_low_skill_women * (hours_F) * (52) / 1000000) + (pop_low_skill_men * (hours_M) * (52) / 1000000)

                elif code =='TW':
                    for sector in hours_split['Sector'].unique():
                        pop_high_skill_men = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split High qualification employment - male'].to_string(index=False, header=False))
                        pop_middle_skill_men = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split Middle qualification employment - male'].to_string(index=False, header=False))
                        pop_low_skill_men = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split Low qualification employment - male'].to_string(index=False, header=False))

                        pop_high_skill_women = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split High qualification employment - female'].to_string(index=False, header=False))
                        pop_middle_skill_women = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split Middle qualification employment - female'].to_string(index=False, header=False))
                        pop_low_skill_women = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split Low qualification employment - female'].to_string(index=False, header=False))


                        vacation = float(vacation_average.loc[vacation_average.EXIO3 == 'WA','Total Paid Vacation Days'].to_string(index=False,header=False))

                        classif1 = concordance_category(concordance, sector)

                        hours_M, hours_F = sector_hours_pair(
                            av2, 'EXIO3', 'WA', classif1, years,
                            'Weighted average working hours')
                        if hours_M is None:
                            continue
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - male' ] = pop_high_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - male' ] = pop_middle_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - male' ] = pop_low_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - male' ] = pop_high_skill_men * (hours_M) * (52-(vacation/5)) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - male' ] = pop_middle_skill_men * (hours_M) * (52-(vacation/5)) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - male' ] = pop_low_skill_men * (hours_M) * (52-(vacation/5)) / 1000000

                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - male' ] = pop_high_skill_men * (hours_M) * (52) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - male' ] = pop_middle_skill_men * (hours_M) * (52) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - male' ] = pop_low_skill_men * (hours_M) * (52) / 1000000


                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - female' ] = pop_high_skill_women * (hours_F/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - female' ] = pop_middle_skill_women * (hours_F/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - female' ] = pop_low_skill_women * (hours_F/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - female' ] = pop_high_skill_women * (hours_F) * (52-(vacation/5)) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - female' ] = pop_middle_skill_women * (hours_F) * (52-(vacation/5)) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - female' ] = pop_low_skill_women * (hours_F) * (52-(vacation/5)) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - female' ] = pop_high_skill_women * (hours_F) * (52) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - female' ] = pop_middle_skill_women * (hours_F) * (52) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - female' ] = pop_low_skill_women * (hours_F) * (52) / 1000000


                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - total' ] = (pop_high_skill_men * (hours_M/5) * (365-vacation) / 1000000) + (pop_high_skill_women * (hours_F/5) * (365-vacation) / 1000000)
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - total' ] = (pop_middle_skill_men * (hours_M/5) * (365-vacation) / 1000000) + (pop_middle_skill_women * (hours_F/5) * (365-vacation) / 1000000)
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - total' ] = (pop_low_skill_men * (hours_M/5) * (365-vacation) / 1000000) + (pop_low_skill_women * (hours_F/5) * (365-vacation) / 1000000)
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - total' ] = (pop_high_skill_men * (hours_M) * (52-(vacation/5)) / 1000000) + (pop_high_skill_women * (hours_F) * (52-(vacation/5)) / 1000000)
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - total' ] = (pop_middle_skill_men * (hours_M) * (52-(vacation/5)) / 1000000)+(pop_middle_skill_women * (hours_F) * (52-(vacation/5)) / 1000000)
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - total' ] = (pop_low_skill_men * (hours_M) * (52-(vacation/5)) / 1000000)+(pop_low_skill_women * (hours_F) * (52-(vacation/5)) / 1000000)
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - total' ] = (pop_high_skill_men * (hours_M) * (52) / 1000000) + (pop_high_skill_women * (hours_F) * (52) / 1000000)
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - total' ] = (pop_middle_skill_men * (hours_M) * (52) / 1000000)+(pop_middle_skill_women * (hours_F) * (52) / 1000000)
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - total' ] = (pop_low_skill_men * (hours_M) * (52) / 1000000)+(pop_low_skill_women * (hours_F) * (52) / 1000000)


                else :
                    for sector in hours_split['Sector'].unique():
                        pop_high_skill_men = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split High qualification employment - male'].to_string(index=False, header=False))
                        #print(sector,pop_high_skill_men)
                        
                        pop_middle_skill_men = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split Middle qualification employment - male'].to_string(index=False, header=False))
                        pop_low_skill_men = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split Low qualification employment - male'].to_string(index=False, header=False))

                        pop_high_skill_women = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split High qualification employment - female'].to_string(index=False, header=False))
                        pop_middle_skill_women = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split Middle qualification employment - female'].to_string(index=False, header=False))
                        pop_low_skill_women = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split Low qualification employment - female'].to_string(index=False, header=False))

                        
                        vacation = float(vacation_average.loc[vacation_average.EXIO3 == code,'Total Paid Vacation Days'].to_string(index=False,header=False))
                        classif1 = concordance_category(concordance, sector)
                        hours_M, hours_F = sector_hours_pair(
                            hours_main_country, 'EXIO3', code, classif1, years,
                            'average weekly hours')
                        if hours_M is None:
                            continue
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - male' ] = pop_high_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - male' ] = pop_middle_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - male' ] = pop_low_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - male' ] = pop_high_skill_men * (hours_M) * (52) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - male' ] = pop_middle_skill_men * (hours_M) * (52) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - male' ] = pop_low_skill_men * (hours_M) * (52) / 1000000

                        print(code, sector, hours_M, hours_F, vacation)
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - female' ] = pop_high_skill_women * (hours_F/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - female' ] = pop_middle_skill_women * (hours_F/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - female' ] = pop_low_skill_women * (hours_F/5) * (365-vacation) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - female' ] = pop_high_skill_women * (hours_F) * (52) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - female' ] = pop_middle_skill_women * (hours_F) * (52) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - female' ] = pop_low_skill_women * (hours_F) * (52) / 1000000

                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - total' ] = (pop_high_skill_men * (hours_M/5) * (365-vacation) / 1000000) + (pop_high_skill_women * (hours_F/5) * (365-vacation) / 1000000)
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - total' ] = (pop_middle_skill_men * (hours_M/5) * (365-vacation) / 1000000) + (pop_middle_skill_women * (hours_F/5) * (365-vacation) / 1000000)
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - total' ] = (pop_low_skill_men * (hours_M/5) * (365-vacation) / 1000000) + (pop_low_skill_women * (hours_F/5) * (365-vacation) / 1000000)
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - total' ] = (pop_high_skill_men * (hours_M) * (52) / 1000000) + (pop_high_skill_women * (hours_F) * (52) / 1000000)
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - total' ] = (pop_middle_skill_men * (hours_M) * (52) / 1000000) + (pop_middle_skill_women * (hours_F) * (52) / 1000000)
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - total' ] = (pop_low_skill_men * (hours_M) * (52) / 1000000) + (pop_low_skill_women * (hours_F) * (52) / 1000000)

        hourSplit[years]=hours_split.copy()
    print(f'[hours split] {HOURS_FALLBACKS["substituted_other_sex"]:,} '
          'sector-cells took one sex\'s hours for the other (the ILO '
          'suppresses the second), '
          f'{HOURS_FALLBACKS["skipped"]:,} skipped with no hours at all')
    pd.DataFrame(HOURS_FALLBACK_LOG,
                 columns=['region', 'classif1', 'time', 'reason', 'source']
                 ).to_csv(final_path / 'hours_fallbacks.csv', index=False)
    print(f'[hours split] audit written to '
          f'{final_path / "hours_fallbacks.csv"}')
    writer = pd.ExcelWriter(final_path / HOURS_SPLIT_FILENAME,engine='xlsxwriter')

    for year in build_years:
        hourSplit[year].to_excel(writer, sheet_name=str(year))
    writer.close()



    xls = pd.ExcelFile(final_path / HOURS_SPLIT_FILENAME)
    xls2 = pd.ExcelFile(final_path / 'split_workforce_by_skill_newSUT.xlsx')
    exio3_regions = pd.read_csv('auxdata/region_EXIO3.csv')

    final_table= pd.DataFrame(columns = ['region','sector', 'Employment: Low-skilled male', 'Employment: Low-skilled female', 'Employment: Medium-skilled male','Employment: Medium-skilled female', 'Employment: High-skilled male', 'Employment: High-skilled female','Employment hours: Low-skilled male', 'Employment hours: Low-skilled female', 'Employment hours: Medium-skilled male',  'Employment hours: Medium-skilled female','Employment hours: High-skilled male',  'Employment hours: High-skilled female'])
    final_table_empty = final_table.copy()
    final = {}
    for years in build_years:
        print(years)
        final_table=final_table_empty.copy()
        whours = pd.read_excel(xls, str(years))
        whours=whours.drop(['Unnamed: 0'],axis =1)

        pop = pd.read_excel(xls2, str(years))
        pop=pop.drop(['Unnamed: 0'],axis =1)
        pop = pop.dropna()


        # One row per (region, sector): employment from the salary split,
        # hours from the split written above. Both sides were twelve
        # `float(...to_string(...))` lookups inside a single expression, with a
        # guard on the employment side only - a region present in
        # auxdata/region_EXIO3.csv but absent from the hours split (they are built
        # from different country lists) blew up on the hours half. Missing on
        # either side now means zero, which is what the guarded branch already
        # did for missing employment.
        EMPLOYMENT = [
            ('Employment: Low-skilled male', 'Split Low qualification employment - male'),
            ('Employment: Low-skilled female', 'Split Low qualification employment - female'),
            ('Employment: Medium-skilled male', 'Split Middle qualification employment - male'),
            ('Employment: Medium-skilled female', 'Split Middle qualification employment - female'),
            ('Employment: High-skilled male', 'Split High qualification employment - male'),
            ('Employment: High-skilled female', 'Split High qualification employment - female'),
        ]
        HOURS = [
            ('Employment hours: Low-skilled male', 'Hours Low qualification employement - male'),
            ('Employment hours: Low-skilled female', 'Hours Low qualification employement - female'),
            ('Employment hours: Medium-skilled male', 'Hours Middle qualification employement - male'),
            ('Employment hours: Medium-skilled female', 'Hours Middle qualification employement - female'),
            ('Employment hours: High-skilled male', 'Hours High qualification employement - male'),
            ('Employment hours: High-skilled female', 'Hours High qualification employement - female'),
        ]

        def first_value(frame, column):
            if not len(frame) or column not in frame.columns:
                return 0.0
            values = pd.to_numeric(frame[column], errors='coerce').dropna()
            return float(values.iloc[0]) if len(values) else 0.0

        sector_codes = {sector: concordance.loc[concordance.Name == sector,
                                                'CodeNr'].to_string(index=False)
                        for sector in whours['Sector'].unique()}
        rows = []
        for code in exio3_regions['EXIO3']:
            for sector in whours['Sector'].unique():
                employment = pop.loc[(pop.Country == code)
                                     & (pop.Sector == sector_codes[sector])]
                worked = whours.loc[(whours.EXIO3 == code)
                                    & (whours.Sector == sector)]
                row = {'region': [code], 'sector': [sector]}
                row.update({name: [first_value(employment, column)]
                            for name, column in EMPLOYMENT})
                row.update({name: [first_value(worked, column)]
                            for name, column in HOURS})
                rows.append(pd.DataFrame(row))
        final_table = pd.concat([final_table] + rows, ignore_index=True)

        final[years]=final_table.copy()

    writer = pd.ExcelWriter(final_path / _cfg.FINAL_LABOR_FILENAME,engine='xlsxwriter')

    for year in build_years:
        table_pivot = final[year].pivot_table(columns=['region','sector'],sort = False)
        table_pivot.to_excel(writer, sheet_name=str(year))
    writer.close()



#    ax1 = plt.boxplot
#    for code in final_table.EXIO3.unique():    
    
    '''PB with Ukraine, no data for 2022 from ILO'''
    
    
#    for code in workforce_iso3.ref_area.unique() : 
#        if code in workforce_iso3.ref_area.unique() and code in hours.ref_area.unique():
#            #if code in ['UKR'] :
#                for sex in ['SEX_F','SEX_M']:
#                    for c in workforce_iso3.classif1.unique():
#                        for t in workforce_iso3.time.unique():
#                            P = float(workforce_iso3.loc[(workforce_iso3['ref_area']==code)&(workforce_iso3['sex']==sex)&(workforce_iso3['classif1']==c)&(workforce_iso3['time']==t),['population(1000)']].to_string(header=False,index=False))
#                            H = float(hours.loc[(hours['ref_area']==code)&(hours['sex']==sex)&(hours['classif1']==c),str(years)].to_string(header=False, index=False))                        
                            
#                            workforce_iso3.loc[(workforce_iso3['ref_area']==code)&(workforce_iso3['sex']==sex)&(workforce_iso3['classif1']==c)&(workforce_iso3['time']==t),['average weekly hours (1000)']] = P * H
    
#    for code in workforce_iso3.ref_area.unique() : 
#        if code in workforce_iso3.ref_area.unique() and code in hours.ref_area.unique():
#            if code == 'UKR' :
#                for sex in ['SEX_F','SEX_M']:
#                    for c in workforce_iso3.classif1.unique():
#                        for t in range(1991,2022):
#                            P = float(workforce_iso3.loc[(workforce_iso3['ref_area']==code)&(workforce_iso3['sex']==sex)&(workforce_iso3['classif1']==c)&(workforce_iso3['time']==t),['population(1000)']].to_string(header=False,index=False))
#                            H = float(hours.loc[(hours['ref_area']==code)&(hours['sex']==sex)&(hours['classif1']==c),str(years)].to_string(header=False, index=False))                        
                            
#                            workforce_iso3.loc[(workforce_iso3['ref_area']==code)&(workforce_iso3['sex']==sex)&(workforce_iso3['classif1']==c)&(workforce_iso3['time']==t),['average weekly hours (1000)']] = P * H



#    for code in workforce_iso3.ref_area.unique() : 
#        if code in workforce_iso3.ref_area.unique() and code in hours.ref_area.unique():
#            if code != 'UKR':
#                for c in workforce_iso3.classif1.unique():
#                    for t in workforce_iso3.time.unique():
#                        M = float(workforce_iso3.loc[(workforce_iso3['ref_area']==code)&(workforce_iso3['sex']=='SEX_M')&(workforce_iso3['classif1']==c)&(workforce_iso3['time']==t),['average weekly hours (1000)']].to_string(header=False,index=False))
#                        W =  float(workforce_iso3.loc[(workforce_iso3['ref_area']==code)&(workforce_iso3['sex']=='SEX_F')&(workforce_iso3['classif1']==c)&(workforce_iso3['time']==t),['average weekly hours (1000)']].to_string(header=False,index=False))
                        
#                        workforce_iso3.loc[(workforce_iso3['ref_area']==code)&(workforce_iso3['sex']=='SEX_T')&(workforce_iso3['classif1']==c)&(workforce_iso3['time']==t),['average weekly hours (1000)']] = M + W

#    for code in workforce_iso3.ref_area.unique() : 
#        if code in workforce_iso3.ref_area.unique() and code in hours.ref_area.unique():
#            if code == 'UKR':
#                for c in workforce_iso3.classif1.unique():
#                    for t in range(1991,2022):
#                        M = float(workforce_iso3.loc[(workforce_iso3['ref_area']==code)&(workforce_iso3['sex']=='SEX_M')&(workforce_iso3['classif1']==c)&(workforce_iso3['time']==t),['average weekly hours (1000)']].to_string(header=False,index=False))
#                        W =  float(workforce_iso3.loc[(workforce_iso3['ref_area']==code)&(workforce_iso3['sex']=='SEX_F')&(workforce_iso3['classif1']==c)&(workforce_iso3['time']==t),['average weekly hours (1000)']].to_string(header=False,index=False))
                        
#                        workforce_iso3.loc[(workforce_iso3['ref_area']==code)&(workforce_iso3['sex']=='SEX_T')&(workforce_iso3['classif1']==c)&(workforce_iso3['time']==t),['average weekly hours (1000)']] = M + W
               





#        for sex in final_table.sex.unique():
#            final_table[(final_table['EXIO3']==code)&(final_table['sex']==sex)].boxplot(by = 'classif1',column=['obs_value'],grid = False,figsize=(20,10))
#            
#            #plt.savefig('line_plot.pdf')
#            plt.savefig("{code}_{sex}.png".format(code=code,sex=sex))
#    
#    #import seaborn as sns
#    final_table_1998_2020 = final_table.copy()
#    final_table_1998_2020 = final_table_1998_2020.drop(columns=['1995','1996','1997'])
#            
#    ax1 = plt
#    sns.lmplot('EXIO3', 'obs_value', data=final_table, hue='classif1', fit_reg=False,size=5*3)
#    plt.show()
#    plt.savefig("improved_technique.png")
  
    return final_table
