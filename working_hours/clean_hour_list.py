import numpy as np

def clean_hour(hour_list):    

    hour_list = hour_list[hour_list['classif1'].str.contains('ISIC3|ISIC4',regex=True)]
    hour_list = hour_list[hour_list['sex'].str.contains('SEX_F|SEX_M',regex=True)]
    hour_list = hour_list[hour_list['time'] >1994]
    hour_list = hour_list.drop(hour_list.filter(regex='note|indicator|source|obs_status').columns, axis=1)
    hour_list_without_zero = hour_list.replace(0, np.nan)
    return hour_list,hour_list_without_zero