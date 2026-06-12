import ray
import pandas as pd
import os

ray.init(num_cpus = os.cpu_count()-4,ignore_reinit_error=True) 

@ray.remote
def process_combination(code, sex, classi, year, isic4_data, isic3_data):
    try:
        if year < 2009:
            df = isic3_data
            source = 3
        else:
            df = isic4_data
            source = 4

        # Check if there's data in the preferred dataset
        value_df = df.loc[
            (df['ref_area'] == code) &
            (df['sex'] == sex) &
            (df['classif1'] == classi) &
            (df['time'] == year),
            ['obs_value']
        ]

        if not value_df.isnull().values.all():
            value = float(value_df.to_string(index=False, header=False))
            return {
                'ref_area': code,
                'sex': sex,
                'classif1': classi,
                'time': year,
                'obs_value': value,
                'source': source
            }

        # Try fallback if year >= 2009 and primary data is missing
        if year >= 2009 and df is isic4_data:
            fallback_df = isic3_data
            value_df = fallback_df.loc[
                (fallback_df['ref_area'] == code) &
                (fallback_df['sex'] == sex) &
                (fallback_df['classif1'] == classi) &
                (fallback_df['time'] == year),
                ['obs_value']
            ]

            if not value_df.isnull().values.all():
                value = float(value_df.to_string(index=False, header=False))
                return {
                    'ref_area': code,
                    'sex': sex,
                    'classif1': classi,
                    'time': year,
                    'obs_value': value,
                    'source': 3
                }

    except Exception as e:
        print(f"Error processing ({code}, {sex}, {classi}, {year}): {e}")
    return None

def combine_ray(hour_list, isic3_data, isic4_data):
    tasks = []

    for code in hour_list.ref_area.unique():
        print(code)
        for sex in hour_list.sex.unique():

            for classi in hour_list.classif1.unique():
                for year in hour_list.time.unique():
                    task = process_combination.remote(code, sex, classi, year, isic4_data, isic3_data)
                    tasks.append(task)

    results = ray.get(tasks)
    results = [r for r in results if r is not None]
    return pd.DataFrame(results)
