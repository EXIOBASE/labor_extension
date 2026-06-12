import ray
import pandas as pd
import os



ray.init(num_cpus = os.cpu_count()-4)
@ray.remote
def process_single_entry(code, sex, year, hour_df):
    try:
        sub_df = hour_df.loc[
            (hour_df.index.get_level_values(0) == code) &
            (hour_df.index.get_level_values(1) == sex), [year]
        ]
        if not sub_df.isnull().values.all():
            value = float(sub_df.to_string(header=False, index=False))
            return (code, sex, year, value)
    except Exception as e:
        print(f"Error processing {code}, {sex}, {year}: {e}")
    return None

def substitute_isic_a_ray(hour_df, isic_df):
    results = []
    codes = hour_df.index.get_level_values(0).unique()
    sexes = hour_df.index.get_level_values(1).unique()

    tasks = [
        process_single_entry.remote(code, sex, year, hour_df)
        for code in codes
        for sex in sexes
        for year in range(1995, 2008)
    ]

    results = ray.get(tasks)

    # Filter out None values
    for result in results:
        if result is not None:
            code, sex, year, value = result
            mask = (
                (isic_df['ref_area'] == code) &
                (isic_df['sex'] == sex) &
                (isic_df['classif1'] == 'ECO_ISIC4_A') &
                (isic_df['time'] == year)
            )
            isic_df.loc[mask, 'obs_value'] = value

    ray.shutdown()
    return isic_df

#def substitute_isic_a(hour_eurostat_reshape_pivot_extrapolate,isic4_from_isic3_data):
#    for code in hour_eurostat_reshape_pivot_extrapolate.index.get_level_values(0).unique(): 
#        for sex in hour_eurostat_reshape_pivot_extrapolate.index.get_level_values(1).unique():
#            for year in range(1995,2008):
#                if not hour_eurostat_reshape_pivot_extrapolate.loc[(hour_eurostat_reshape_pivot_extrapolate.index.get_level_values(0)==code)&(hour_eurostat_reshape_pivot_extrapolate.index.get_level_values(1)==sex),[year]].isnull().values.all():
#                    value=float(hour_eurostat_reshape_pivot_extrapolate.loc[(hour_eurostat_reshape_pivot_extrapolate.index.get_level_values(0)==code)&(hour_eurostat_reshape_pivot_extrapolate.index.get_level_values(1)==sex),[year]].to_string(header=False, index=False))
#                    isic4_from_isic3_data.loc[(isic4_from_isic3_data['ref_area']==code)&(isic4_from_isic3_data['sex']==sex)&(isic4_from_isic3_data['classif1']=='ECO_ISIC4_A')&(isic4_from_isic3_data['time']==year),['obs_value']]=value

#    return isic4_from_isic3_data



#def substitute_isic_a_ray(hour_eurostat_reshape_pivot_extrapolate,isic4_from_isic3_data):






