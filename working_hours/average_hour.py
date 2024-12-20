import pandas as pd
def average_working_hour(new_table_150222_pivot_extrapolate,cc_all,workforce2,final_table):
    
    for year in range(1995,2023):
        for sex in new_table_150222_pivot_extrapolate.index.get_level_values(1).unique():
            for classi in new_table_150222_pivot_extrapolate.index.get_level_values(2).unique():
                for exio in new_table_150222_pivot_extrapolate.EXIO3.unique():
                    countries = []
                    a=cc_all.convert(exio,src="EXIO3", to='ISO3')
                    print(a)
                    if isinstance(a,list):
                        countries = cc_all.convert(exio,src="EXIO3", to='ISO3')
                    else:
                        countries =[a]
    
                    value1=0
                    workforce_region=0
                    '''LA CA BLOQUE'''
                    for code in countries:
                        # print(new_table_150222_pivot_extrapolate.loc[(new_table_150222_pivot_extrapolate.index.get_level_values(0)==code)&(new_table_150222_pivot_extrapolate.index.get_level_values(2)==classi)&(new_table_150222_pivot_extrapolate.index.get_level_values(1)==sex),[year]])
                        #print(new_table_150222_pivot_extrapolate.loc[(new_table_150222_pivot_extrapolate.index.get_level_values(0)==code)&(new_table_150222_pivot_extrapolate.index.get_level_values(2)==classi)&(new_table_150222_pivot_extrapolate.index.get_level_values(1)==sex),[year]].isnull().values.all())
                        #print(workforce2.loc[(workforce2.ref_area==code)&(workforce2.classif1==classi)&(workforce2.sex==sex)&(workforce2.time==year),['obs_value']].isnull().values.all())

                        if not (new_table_150222_pivot_extrapolate.loc[(new_table_150222_pivot_extrapolate.index.get_level_values(0)==code)&(new_table_150222_pivot_extrapolate.index.get_level_values(2)==classi)&(new_table_150222_pivot_extrapolate.index.get_level_values(1)==sex),[year]].isnull().values.all() or workforce2.loc[(workforce2.ref_area==code)&(workforce2.classif1==classi)&(workforce2.sex==sex)&(workforce2.time==year),['obs_value']].isnull().values.all()):
                            value=float(new_table_150222_pivot_extrapolate.loc[(new_table_150222_pivot_extrapolate.index.get_level_values(0)==code)&(new_table_150222_pivot_extrapolate.index.get_level_values(2)==classi)&(new_table_150222_pivot_extrapolate.index.get_level_values(1)==sex),[year]].to_string(header=False,index=False))
                            #print(value)

                            workforce_country=float(workforce2.loc[(workforce2.ref_area==code)&(workforce2.classif1==classi)&(workforce2.sex==sex)&(workforce2.time==year),['obs_value']].to_string(header=False,index=False))
                            value1=value1+value*workforce_country
                            workforce_region=workforce_region+workforce_country
                    if workforce_region != 0 : 
                        value_exio3_region = value1 / workforce_region
                    else :
                        value_exio3_region = 0
                    # print(exio, value_exio3_region,year, sex,classi)  
                    new_line = {'EXIO3' : exio , 'sex' : sex, 'classif1' : classi, 'time' : year, 'obs_value' :value_exio3_region}

                    final_table.loc[len(final_table)] = new_line
                    final_table = final_table.reset_index(drop=True) 
                    # final_table = final_table.append(pd.Series([exio,sex,classi,year,value_exio3_region],index=[i for i in final_table.columns]),ignore_index=True)
    return final_table
    
