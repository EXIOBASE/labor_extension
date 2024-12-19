def substitute_isic_a(hour_eurostat_reshape_pivot_extrapolate,isic4_from_isic3_data):
    for code in hour_eurostat_reshape_pivot_extrapolate.index.get_level_values(0).unique(): 
        for sex in hour_eurostat_reshape_pivot_extrapolate.index.get_level_values(1).unique():
            for year in range(1995,2008):
                if not hour_eurostat_reshape_pivot_extrapolate.loc[(hour_eurostat_reshape_pivot_extrapolate.index.get_level_values(0)==code)&(hour_eurostat_reshape_pivot_extrapolate.index.get_level_values(1)==sex),[year]].isnull().values.all():
                    value=float(hour_eurostat_reshape_pivot_extrapolate.loc[(hour_eurostat_reshape_pivot_extrapolate.index.get_level_values(0)==code)&(hour_eurostat_reshape_pivot_extrapolate.index.get_level_values(1)==sex),[year]].to_string(header=False, index=False))
                    isic4_from_isic3_data.loc[(isic4_from_isic3_data['ref_area']==code)&(isic4_from_isic3_data['sex']==sex)&(isic4_from_isic3_data['classif1']=='ECO_ISIC4_A')&(isic4_from_isic3_data['time']==year),['obs_value']]=value

    return isic4_from_isic3_data
