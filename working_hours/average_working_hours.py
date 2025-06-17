import pandas as pd
from regression_ILO_region_with_minimum import regression
import country_converter as coco
from clean_workforce import clean
from clean_hour_list import clean_hour
from clean_hour_eurostat import reshape_eurostat
from isic3_to_isic4 import correspondance_isic
from substitute import substitute_isic_a
from combine_isic_3_4 import combine
from aggregate_isic import aggregate
from average_hour import average_working_hour



def working_hour(workforce,src_csv2,data_path,src_csv3):
        
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
    hour_list,hour_list_without_zero = clean_hour(hour_list)
                                
    hour_eurostat = pd.read_csv(data_path/src_csv3,  sep='\t|,', engine = 'python')
    # hour_eurostat2 = pd.read_csv(data_path/src_csv4,  sep='\t|,')

    hour_eurostat_reshape = reshape_eurostat(hour_eurostat,cc_all)
                    
    hour_eurostat_reshape_pivot = hour_eurostat_reshape.pivot(index=['ref_area','sex','classif1'],columns='time')['obs_value']
    hour_eurostat_reshape_pivot_interpolate = hour_eurostat_reshape_pivot.interpolate(method='linear',axis=1,limit_area='inside')
    
    hour_eurostat_reshape_pivot_extrapolate = regression(hour_eurostat_reshape_pivot_interpolate,1992,2008)
    
    hour_eurostat_reshape_pivot_extrapolate.to_csv('hour_eurostat.csv')
    
    isic3=hour_list_without_zero[hour_list_without_zero['classif1'].str.contains('ISIC3',regex=True)].copy()
    isic4=hour_list_without_zero[hour_list_without_zero['classif1'].str.contains('ISIC4',regex=True)].copy()
    
    isic4_from_isic3_data = correspondance_isic(workforce,isic3)
    
    isic4_from_isic3_data.to_csv('isic4_from_isic3_data.csv') 
    
    '''
    Substituer ISIC A par la valeur de Eurostat pour 1995 a 2008
    '''
    isic4_from_isic3_data = substitute_isic_a(hour_eurostat_reshape_pivot_extrapolate,isic4_from_isic3_data)
   
                           
    isic4_from_isic3_data['obs_value'] = pd.to_numeric(isic4_from_isic3_data['obs_value'])
    isic4_from_isic3_data['time']=isic4_from_isic3_data['time'].astype(int)
    
    isic4_from_isic3_data_pivot = pd.pivot_table(isic4_from_isic3_data, values="obs_value", index=["ref_area", "sex","classif1"], columns=["time"])
    isic4_from_isic3_data_pivot=isic4_from_isic3_data_pivot.reset_index()
    isic4_from_isic3_data_pivot.to_csv("isic4_from_isic3_data_pivot.csv")
    
    
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

    #new_table_150222.to_csv('new_table_150222.csv')
    
    new_table_150222_pivot = pd.pivot_table(new_table_150222, values="obs_value", index=["ref_area", "sex","classif1"], columns=["time"])
    new_table_150222_pivot=new_table_150222_pivot.reset_index()
    
    
    new_table_150222 = aggregate(new_table_150222,new_table_150222_columns)

    
    #new_table_150222.to_csv('new_table_150222_aggregate_ISIC.csv') 
    
    new_table_150222_pivot = new_table_150222.pivot(index=['ref_area','sex','classif1'],columns='time')['obs_value']
    new_table_150222_pivot.to_csv("new_table_150222_pivot_aggregate_ISIC.csv")  
    
    new_table_150222_pivot_interpolate = new_table_150222_pivot.interpolate(method='linear',axis=1,limit_area='inside')
    new_table_150222_pivot_interpolate=new_table_150222_pivot_interpolate.round(2)
    new_table_150222_pivot_interpolate.to_csv("new_table_150222_aggregate_ISIC_pivot_interpolate.csv")
    new_table_150222_pivot_interpolate_old=new_table_150222_pivot_interpolate.copy()
    
    
    
    new_table_150222_pivot_extrapolate = regression(new_table_150222_pivot_interpolate,1995,2023)
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
    
    for code in hours.ref_area.unique() :
        for sex in hours.sex.unique() : 
            for years in range(1995, 2024):
        #for b in hours.classif1 :
                if not 'ECO_ISIC4_A' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_A','time' :[years]})
                    hours=pd.concat([hours,new_row])
                if not 'ECO_ISIC4_B' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_B','time' :[years]})
                    hours=pd.concat([hours,new_row])
                if not 'ECO_ISIC4_C' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_C','time' :[years]})
                    hours=pd.concat([hours,new_row])
                if not 'ECO_ISIC4_D' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_D','time' :[years]})
                    hours=pd.concat([hours,new_row])    
                if not 'ECO_ISIC4_E' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_E','time' :[years]})
                    hours=pd.concat([hours,new_row])
                if not 'ECO_ISIC4_F' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_F','time' :[years]})
                    hours=pd.concat([hours,new_row])
                if not 'ECO_ISIC4_G' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_G','time' :[years]})
                    hours=pd.concat([hours,new_row])
                if not 'ECO_ISIC4_H' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_H','time' :[years]})
                    hours=pd.concat([hours,new_row])   
                    
                if not 'ECO_ISIC4_I' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_I','time' :[years]})
                    hours=pd.concat([hours,new_row])
                if not 'ECO_ISIC4_J' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_J','time' :[years]})
                    hours=pd.concat([hours,new_row])
                if not 'ECO_ISIC4_K' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_K','time' :[years]})
                    hours=pd.concat([hours,new_row])
                if not 'ECO_ISIC4_L' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_L','time' :[years]})
                    hours=pd.concat([hours,new_row])    
                if not 'ECO_ISIC4_M' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_M','time' :[years]})
                    hours=pd.concat([hours,new_row])
                if not 'ECO_ISIC4_N' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_N','time' :[years]})
                    hours=pd.concat([hours,new_row])
                if not 'ECO_ISIC4_O' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_O','time' :[years]})
                    hours=pd.concat([hours,new_row])
                if not 'ECO_ISIC4_P' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_P','time' :[years]})
                    hours=pd.concat([hours,new_row])                  
                   
                if not 'ECO_ISIC4_Q' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_Q','time' :[years]})
                    hours=pd.concat([hours,new_row])
                if not 'ECO_ISIC4_R' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_R','time' :[years]})
                    hours=pd.concat([hours,new_row])
                if not 'ECO_ISIC4_S' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_S','time' :[years]})
                    hours=pd.concat([hours,new_row])
                if not 'ECO_ISIC4_T' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_T','time' :[years]})
                    hours=pd.concat([hours,new_row])    
                if not 'ECO_ISIC4_U' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_U','time' :[years]})
                    hours=pd.concat([hours,new_row])
                if not 'ECO_ISIC4_X' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_X','time' :[years]})
                    hours=pd.concat([hours,new_row])            
                if not 'ECO_ISIC4_DE' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_DE','time' :[years]})
                    hours=pd.concat([hours,new_row]) 
                if not 'ECO_ISIC4_HJ' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_HJ','time' :[years]})
                    hours=pd.concat([hours,new_row])   
                if not 'ECO_ISIC4_LMN' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_LMN','time' :[years]})
                    hours=pd.concat([hours,new_row])   
                if not 'ECO_ISIC4_RSTU' in hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.time == years),['classif1']].values:
                    new_row = pd.DataFrame({'ref_area':[code],'sex':[sex],'classif1':'ECO_ISIC4_RSTU','time' :[years]})
                    hours=pd.concat([hours,new_row])  
    

                    
    
    '''Kosovo ISO3 is defined as KOS instead of XKX'''
    hours = hours.replace('KOS','XKX')
    hours=hours.reset_index()
    hours = hours.drop(['index'],axis = 1)
    
    country_code_final = list(hours.ref_area)
    hours.insert(0, 'EXIO3', cc_all.convert(names = country_code_final,src="ISO3", to='EXIO3'))
    workforce_iso3["average weekly hours"] = ''

    #hours.fillna(0)
    
    

    for code in hours.ref_area.unique() :
        for sex in hours.sex.unique() :
            for years in range(1995, 2024):
                print(code, sex, years)
                if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_D')&(hours.time == years), 'average weekly hours'].isna().all()):
                    D = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_D')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                    if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_E')&(hours.time == years), 'average weekly hours'].isna().all()):
                        E = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_E')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                        DE = (D+E)/2
                        hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_DE')&(hours.time == years), 'average weekly hours']=DE                    
                    else :
                        DE = D
                        hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_DE')&(hours.time == years), 'average weekly hours']=DE           
                elif not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_E')&(hours.time == years), 'average weekly hours'].isna().all()):
                    E = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_E')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                    DE = E

                    hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_DE')&(hours.time == years), 'average weekly hours']=DE                      
                else :

                    hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_DE')&(hours.time == years), 'average weekly hours']=0                    

                        
                        
    for code in hours.ref_area.unique() :
        for sex in hours.sex.unique() :
            for years in range(1995, 2024):
                print(code, sex, years)

                if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_H')&(hours.time == years), 'average weekly hours'].isna().all()):
                    H = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_H')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                    if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_J')&(hours.time == years), 'average weekly hours'].isna().all()):
                        J = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_J')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                        HJ = (H+J)/2
                        hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_HJ')&(hours.time == years), 'average weekly hours']=HJ                    
                    else :
                        HJ = H
                        hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_HJ')&(hours.time == years), 'average weekly hours']=HJ          
                elif not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_J')&(hours.time == years), 'average weekly hours'].isna().all()):
                    J = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_J')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                    HJ = J

                    hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_HJ')&(hours.time == years), 'average weekly hours']=HJ               
                else :

                    hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_HJ')&(hours.time == years), 'average weekly hours']=0                    

                                   
    for code in hours.ref_area.unique() :
        for sex in hours.sex.unique() :
            for years in range(1995, 2024):
                print(code, sex, years)

                if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_L')&(hours.time == years), 'average weekly hours'].isna().all()):
                    L = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_L')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                    if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_M')&(hours.time == years), 'average weekly hours'].isna().all()):
                        M = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_M')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                        if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_N')&(hours.time == years), 'average weekly hours'].isna().all()):
                            N = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_N')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                        
                            LMN = (L+M+N)/3
                            hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_LMN')&(hours.time == years), 'average weekly hours']=LMN   
                        else :
                            LMN = (L+M)/2
                            hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_LMN')&(hours.time == years), 'average weekly hours']=LMN   
                    else :
                        if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_N')&(hours.time == years), 'average weekly hours'].isna().all()):
                            N = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_N')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                        
                            LMN = (L+N)/2
                            hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_LMN')&(hours.time == years), 'average weekly hours']=LMN   
                        else :
                            LMN = L
                            hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_LMN')&(hours.time == years), 'average weekly hours']=LMN   
                else :
                    if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_M')&(hours.time == years), 'average weekly hours'].isna().all()):
                        M = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_M')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                        if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_N')&(hours.time == years), 'average weekly hours'].isna().all()):
                            N = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_N')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                        
                            LMN = (M+N)/2
                            hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_LMN')&(hours.time == years), 'average weekly hours']=LMN   
                        else :
                            LMN = M
                            hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_LMN')&(hours.time == years), 'average weekly hours']=LMN   
                    else :
                        
                        if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_N')&(hours.time == years), 'average weekly hours'].isna().all()):
                            N = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_N')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                        
                            LMN = N
                            hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_LMN')&(hours.time == years), 'average weekly hours']=LMN   
                        else :
                            LMN = 0
                            hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_LMN')&(hours.time == years), 'average weekly hours']=LMN   
                        
                
                        
                
    for code in hours.ref_area.unique() :
        for sex in hours.sex.unique() :
            for years in range(1995, 2024):
                print(code, sex, years)

                if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_R')&(hours.time == years), 'average weekly hours'].isna().all()):
                    R = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_R')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                    if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_S')&(hours.time == years), 'average weekly hours'].isna().all()):
                        S = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_S')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                        if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_T')&(hours.time == years), 'average weekly hours'].isna().all()):
                            T = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_T')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                            if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].isna().all()):
                                U = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False)) 
                                RSTU = (R+S+T+U)/4
                                hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                            else :
                                RSTU = (R+S+T)/3
                                hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                                
                        else :
                            
                            if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].isna().all()):
                                U = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False)) 
                                RSTU = (R+S+U)/3
                                hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                            else :
                                RSTU = (R+S)/2
                                hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU                               
                                                            
                    else :
                        if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_T')&(hours.time == years), 'average weekly hours'].isna().all()):
                            T = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_T')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                            if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].isna().all()):
                                U = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False)) 
                                RSTU = (R+T+U)/3
                                hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                            else :
                                RSTU = (R+T)/2
                                hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                                
                        else :
                            
                            if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].isna().all()):
                                U = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False)) 
                                RSTU = (R+U)/2
                                hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                            else :
                                RSTU = (R)
                                hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                        
                                
                else :
                   if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_S')&(hours.time == years), 'average weekly hours'].isna().all()):
                       S = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_S')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                       if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_T')&(hours.time == years), 'average weekly hours'].isna().all()):
                           T = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_T')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                           if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].isna().all()):
                               U = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False)) 
                               RSTU = (S+T+U)/3
                               hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                           else :
                               RSTU = (S+T)/2
                               hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                               
                       else :
                           
                           if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].isna().all()):
                               U = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False)) 
                               RSTU = (S+U)/2
                               hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                           else :
                               RSTU = (S)
                               hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU                               
                                                           
                   else :
                       if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_T')&(hours.time == years), 'average weekly hours'].isna().all()):
                           T = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_T')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False))
                           if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].isna().all()):
                               U = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False)) 
                               RSTU = (T+U)/2
                               hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                           else :
                               RSTU = (T)
                               hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                               
                       else :
                           
                           if not (hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].isna().all()):
                               U = float(hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_U')&(hours.time == years), 'average weekly hours'].to_string(header = False,index=False)) 
                               RSTU = (U)
                               hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                           else :
                               RSTU = 0
                               hours.loc[(hours.ref_area == code)&(hours.sex == sex)&(hours.classif1 == 'ECO_ISIC4_RSTU')&(hours.time == years), 'average weekly hours']=RSTU   
                    
                            
                            
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
    hours = hours.replace('ECO_ISIC4_A','ECO_DETAILS_A')
    hours =hours.replace('ECO_ISIC4_B','ECO_DETAILS_B')
    hours =hours.replace('ECO_ISIC4_C','ECO_DETAILS_C')
    hours =hours.replace('ECO_ISIC4_D','ECO_DETAILS_D')
    hours =hours.replace('ECO_ISIC4_E','ECO_DETAILS_E')
    hours =hours.replace('ECO_ISIC4_DE','ECO_DETAILS_DE')
    hours =hours.replace('ECO_ISIC4_F','ECO_DETAILS_F')
    hours =hours.replace('ECO_ISIC4_G','ECO_DETAILS_G')
    hours =hours.replace('ECO_ISIC4_H','ECO_DETAILS_H')
    hours =hours.replace('ECO_ISIC4_J','ECO_DETAILS_J')
    hours =hours.replace('ECO_ISIC4_HJ','ECO_DETAILS_HJ')
    hours =hours.replace('ECO_ISIC4_I','ECO_DETAILS_I')
    hours =hours.replace('ECO_ISIC4_K','ECO_DETAILS_K')
    hours =hours.replace('ECO_ISIC4_LMN','ECO_DETAILS_LMN')
    hours =hours.replace('ECO_ISIC4_O','ECO_DETAILS_O')
    hours =hours.replace('ECO_ISIC4_P','ECO_DETAILS_P')
    hours =hours.replace('ECO_ISIC4_Q','ECO_DETAILS_Q')
    hours =hours.replace('ECO_ISIC4_L','ECO_DETAILS_L')
    hours =hours.replace('ECO_ISIC4_M','ECO_DETAILS_M')
    hours =hours.replace('ECO_ISIC4_N','ECO_DETAILS_N')
    hours =hours.replace('ECO_ISIC4_RSTU','ECO_DETAILS_RSTU')
    hours =hours.replace('ECO_ISIC4_X','ECO_DETAILS_X')
    hours =hours.replace('ECO_ISIC4_R','ECO_DETAILS_R')
    hours =hours.replace('ECO_ISIC4_S','ECO_DETAILS_S')
    hours =hours.replace('ECO_ISIC4_T','ECO_DETAILS_T')
    hours =hours.replace('ECO_ISIC4_U','ECO_DETAILS_U')


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
                                
    hours_RoW['population (1000)'] = ''
    workforce_iso3 =   workforce.copy()  
    for code in workforce_iso3.ref_area.unique() : 
        if code in workforce_iso3.ref_area.unique() and code in hours_RoW.ref_area.unique():
            print(code)
            if code != 'UKR':
                for sex in ['SEX_F','SEX_M']:
                    for c in workforce_iso3.classif1.unique():
                        for t in range(1995,2023):
                        #aorkforce_iso3.time.unique():
                            #if not (workforce_iso3.loc[(workforce_iso3['ref_area']==code)&(workforce_iso3['sex']==sex)&(workforce_iso3['classif1']==c)&(workforce_iso3['time']==t),['obs_value']]).isnull :
                                P = float(workforce_iso3.loc[(workforce_iso3['ref_area']==code)&(workforce_iso3['sex']==sex)&(workforce_iso3['classif1']==c)&(workforce_iso3['time']==t),['obs_value']].to_string(header=False,index=False))
                            #H = float(hours.loc[(hours['ref_area']==code)&(hours['sex']==sex)&(hours['classif1']==c),str(years)].to_string(header=False, index=False))                        
                                hours_RoW.loc[(hours_RoW['ref_area']==code)&(hours_RoW['sex']==sex)&(hours_RoW['classif1']==c)&(hours_RoW['time']==t),['population (1000)']] = P 
    hours.to_csv('hours2203_1.csv',index = False)
    for code in workforce_iso3.ref_area.unique() : 
        if code in workforce_iso3.ref_area.unique() and code in hours_RoW.ref_area.unique():
            if code == 'UKR' :
                for sex in ['SEX_F','SEX_M']:
                    for c in workforce_iso3.classif1.unique():
                        for t in range(1991,2022):
                            P = float(workforce_iso3.loc[(workforce_iso3['ref_area']==code)&(workforce_iso3['sex']==sex)&(workforce_iso3['classif1']==c)&(workforce_iso3['time']==t),['obs_value']].to_string(header=False,index=False))
                            #H = float(hours.loc[(hours['ref_area']==code)&(hours['sex']==sex)&(hours['classif1']==c),str(years)].to_string(header=False, index=False))                        
                            
                            hours_RoW.loc[(hours_RoW['ref_area']==code)&(hours_RoW['sex']==sex)&(hours_RoW['classif1']==c)&(hours_RoW['time']==t),['population (1000)']] = P 
    hours_RoW.to_csv('hoursRoW2403_2.csv',index = False)

    hours_RoW = hours_RoW.loc[hours_RoW.ref_area !='SYC']
    hours_RoW = hours_RoW.loc[hours_RoW.ref_area !='REU']
    hours_RoW = hours_RoW.loc[hours_RoW.ref_area !='IMN']


    hours_RoW = hours_RoW.loc[hours_RoW.time !=2023] 
    hours = hours.loc[hours.time !=2023]                   
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
    
    for a in workforce2.ref_area.unique():
         
        if not a in hours_RoW.ref_area.unique():
            if not (any(chr.isdigit() for chr in a)):
                if (cc_all.convert(names = a,src="ISO3", to='EXIO3')) in list_RoW :
                    print(a)
                    for  sex in ['SEX_F','SEX_M']:
                        for c in hours_RoW.classif1.unique():
                            for t in range(1995,2023):
                                 P = float(workforce_iso3.loc[(workforce_iso3['ref_area']==a)&(workforce_iso3['sex']==sex)&(workforce_iso3['classif1']==c)&(workforce_iso3['time']==t),['obs_value']].to_string(header=False,index=False))
                                 H =  float(av2.loc[(av2.EXIO3 == cc_all.convert(names = a,src="ISO3", to='EXIO3'))&(av2.sex == sex)&(av2.classif1 == c)&(av2.time == t),['Weighted average working hours']].to_string(header=False,index=False))
                                 new_row = pd.DataFrame({'EXIO3' : [cc_all.convert(names = a,src="ISO3", to='EXIO3')],'ref_area':[a],'sex':[sex],'classif1':[c],'time' :[t],'average weekly hours': [H], 'population (1000)': [P] })
                                 hours_RoW=pd.concat([hours_RoW,new_row])   
    
    hours_RoW = hours_RoW.reset_index()
    hours_RoW = hours_RoW.drop(['index'],axis =1)

    hours_RoW_old = hours_RoW.copy()
    hours_main_country = hours.copy()
    hours_main_country =  hours_main_country.loc[(hours_main_country.EXIO3 !='WA') & (hours_main_country.EXIO3 !='WE') & (hours_main_country.EXIO3 !='WF') &  (hours_main_country.EXIO3 !='WM') & (hours_main_country.EXIO3 !='WL')]


    for a in workforce2.ref_area.unique():

        if not a in hours_main_country.ref_area.unique():

            if not (cc_all.convert(names = a,src="ISO3", to='EXIO3')) in  list_RoW :
                if a == 'TWN':
                    for  sex in ['SEX_F','SEX_M']:
                        for c in hours_RoW.classif1.unique():
                            for t in range(1995,2023):
                                P = float(workforce_iso3.loc[(workforce_iso3['ref_area']==a)&(workforce_iso3['sex']==sex)&(workforce_iso3['classif1']==c)&(workforce_iso3['time']==t),['obs_value']].to_string(header=False,index=False))
                                H =  float(av2.loc[(av2.EXIO3 == 'WA' )&(av2.sex == sex)&(av2.classif1 == c)&(av2.time == t),['Weighted average working hours']].to_string(header=False,index=False))
                                new_row = pd.DataFrame({'EXIO3' : 'TW' ,'ref_area':[a],'sex':[sex],'classif1':[c],'time' :[t],'average weekly hours': [H], 'population (1000)': [P] })
                                hours_main_country=pd.concat([hours_main_country,new_row])

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
                    P = float(workforce_iso3.loc[(workforce_iso3['ref_area']==a)&(workforce_iso3['sex']==sex)&(workforce_iso3['classif1']==c)&(workforce_iso3['time']==t),['obs_value']].to_string(header=False,index=False))
                    H =  float(av2.loc[(av2.EXIO3 == 'WA' )&(av2.sex == sex)&(av2.classif1 == c)&(av2.time == t),['Weighted average working hours']].to_string(header=False,index=False))
                    new_row = pd.DataFrame({'EXIO3' : 'TW' ,'ref_area':[a],'sex':[sex],'classif1':[c],'time' :[t],'average weekly hours': [H], 'population (1000)': [P] })
                    hours_main_country=pd.concat([hours_main_country,new_row])  
                                 
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
                        
                        
    vacation = pd.read_csv('aux/whole_vacation.csv')
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
    concordance = pd.read_excel('aux/Exiobase_ISIC_Rev-4.xlsx')    
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
    xl = pd.ExcelFile('../tmp/labor/final_table/split_workforce_by_skill_newSUT.xlsx')


    hourSplit = {}
    #writer = pd.ExcelWriter('hours_split.xlsx',engine='xlsxwriter')

    for years in range(1995,2023):
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

                        classif1 = concordance.loc[concordance['Name']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(index = False, header = False)

                        hours_M = float(av2.loc[(av2.EXIO3 ==code) & (av2.sex == 'SEX_M') &(av2.classif1==classif1)&(av2.time == years),'Weighted average working hours'].to_string(index = False, header = False))
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - male' ] = pop_high_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - male' ] = pop_middle_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - male' ] = pop_low_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - male' ] = pop_high_skill_men * (hours_M) * (52) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - male' ] = pop_middle_skill_men * (hours_M) * (52) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - male' ] = pop_low_skill_men * (hours_M) * (52) / 1000000

                        hours_F = float(av2.loc[(av2.EXIO3 ==code) & (av2.sex == 'SEX_F') &(av2.classif1==classif1)&(av2.time == years),'Weighted average working hours'].to_string(index = False, header = False))
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

                        classif1 = concordance.loc[concordance['Name']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(index = False, header = False)

                        hours_M = float(av2.loc[(av2.EXIO3 =='WA') & (av2.sex == 'SEX_M') &(av2.classif1==classif1)&(av2.time == years),'Weighted average working hours'].to_string(index = False, header = False))
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - male' ] = pop_high_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - male' ] = pop_middle_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - male' ] = pop_low_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - male' ] = pop_high_skill_men * (hours_M) * (52-(vacation/5)) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - male' ] = pop_middle_skill_men * (hours_M) * (52-(vacation/5)) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - male' ] = pop_low_skill_men * (hours_M) * (52-(vacation/5)) / 1000000

                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - male' ] = pop_high_skill_men * (hours_M) * (52) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - male' ] = pop_middle_skill_men * (hours_M) * (52) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - male' ] = pop_low_skill_men * (hours_M) * (52) / 1000000


                        hours_F = float(av2.loc[(av2.EXIO3 =='WA') & (av2.sex == 'SEX_F') &(av2.classif1==classif1)&(av2.time == years),'Weighted average working hours'].to_string(index = False, header = False))
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
                        classif1 = concordance.loc[concordance['Name']==sector,['Summary']].to_string(index = False, header = False)
                        letter = classif1.split('.',1)[0]
                        print(letter)
                        hours_M = float(hours_main_country.loc[(hours_main_country.EXIO3 ==code) & (hours_main_country.sex == 'SEX_M') &(hours_main_country.classif1=='ECO_DETAILS_'+letter)&(hours_main_country.time == years),'average weekly hours'].to_string(index = False, header = False))
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - male' ] = pop_high_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - male' ] = pop_middle_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        #hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - male' ] = pop_low_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - male' ] = pop_high_skill_men * (hours_M) * (52) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - male' ] = pop_middle_skill_men * (hours_M) * (52) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - male' ] = pop_low_skill_men * (hours_M) * (52) / 1000000

                        hours_F = float(hours_main_country.loc[(hours_main_country.EXIO3 ==code) & (hours_main_country.sex == 'SEX_F') &(hours_main_country.classif1=='ECO_DETAILS_'+letter)&(hours_main_country.time == years),'average weekly hours'].to_string(index = False, header = False))
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
        writer = pd.ExcelWriter('hours_split_newSUTS.xlsx',engine='xlsxwriter')

        for year in range(1995,2023):
            hourSplit[year].to_excel(writer, sheet_name=str(year))
        writer.close()



        xls = pd.ExcelFile('hours_split.xlsx')
        xls2 = pd.ExcelFile(final_path / 'split_workforce_by_skill.xlsx')
        exio3_regions = pd.read_csv('aux/region_EXIO3.csv')

        final_table= pd.DataFrame(columns = ['region','sector', 'Employment: Low-skilled male', 'Employment: Low-skilled female', 'Employment: Medium-skilled male','Employment: Medium-skilled female', 'Employment: High-skilled male', 'Employment: High-skilled female','Employment hours: Low-skilled male', 'Employment hours: Low-skilled female', 'Employment hours: Medium-skilled male',  'Employment hours: Medium-skilled female','Employment hours: High-skilled male',  'Employment hours: High-skilled female'])
        final_table_empty = final_table.copy()
        final = {}
        for years in range(1995,2023):
            print(years)
            final_table=final_table_empty.copy()
            whours = pd.read_excel(xls, str(years))
            whours=whours.drop(['Unnamed: 0'],axis =1)

            pop = pd.read_excel(xls2, str(years))
            pop=pop.drop(['Unnamed: 0'],axis =1)
            pop = pop.dropna()


            for code in  exio3_regions['EXIO3']:
                print(code)
                for sector in whours['Sector'].unique():
                    #if not sector in pop.loc[(pop.Country == code),'Sector'].values :
                    if not concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False) in pop.loc[(pop.Country == code),'Sector'].values :

                        new_row = pd.DataFrame({'region':[code],   'sector':[sector],   'Employment: Low-skilled male': [0],'Employment: Low-skilled female': [0],'Employment: Medium-skilled male':[0],'Employment: Medium-skilled female': [0],'Employment: High-skilled male':[0],'Employment: High-skilled female':[0], 'Employment hours: Low-skilled male' :[0],  'Employment hours: Low-skilled female' :[0],'Employment hours: Medium-skilled male' :[0],  'Employment hours: Medium-skilled female' :[0],'Employment hours: High-skilled male' :[0],  'Employment hours: High-skilled female' :[0]})
                    else :

                        #new_row = pd.DataFrame({'region':[code],   'sector':[sector],   'Employment: Low-skilled male': [float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split Low qualification employment - male'].to_string(header=False,index=False))],'Employment: Low-skilled female': [float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split Low qualification employment - female'].to_string(header=False,index=False))],'Employment: Medium-skilled male':[float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split Middle qualification employment - male'].to_string(header=False,index=False))],'Employment: Medium-skilled female': [float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split Middle qualification employment - female'].to_string(header=False,index=False))],'Employment: High-skilled male':[float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split High qualification employment - male'].to_string(header=False,index=False))],'Employment: High-skilled female':[float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split High qualification employment - female'].to_string(header=False,index=False))], 'Employment hours: Low-skilled male' :[float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours Low qualification employement - male' ].to_string(index=False,header=False))],  'Employment hours: Low-skilled female' :[float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours Low qualification employement - female' ].to_string(index=False,header=False))],'Employment hours: Medium-skilled male' :[float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours Middle qualification employement - male' ].to_string(index=False,header=False))],  'Employment hours: Medium-skilled female' :[float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours Middle qualification employement - female' ].to_string(index=False,header=False))],'Employment hours: High-skilled male' :[float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours High qualification employement - male' ].to_string(index=False,header=False))],  'Employment hours: High-skilled female' :[float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours High qualification employement - female' ].to_string(index=False,header=False))]})


                        new_row = pd.DataFrame({'region':[code],   'sector':[sector],   'Employment: Low-skilled male': [float(pop.loc[(pop.Country == code)&(pop.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split Low qualification employment - male'].to_string(header=False,index=False))]  ,'Employment: Low-skilled female': [float(pop.loc[(pop.Country == code)&(pop.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split Low qualification employment - female'].to_string(header=False,index=False))],'Employment: Medium-skilled male':[float(pop.loc[(pop.Country == code)&(pop.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split Middle qualification employment - male'].to_string(header=False,index=False))],'Employment: Medium-skilled female': [float(pop.loc[(pop.Country == code)&(pop.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split Middle qualification employment - female'].to_string(header=False,index=False))],'Employment: High-skilled male':[float(pop.loc[(pop.Country == code)&(pop.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split High qualification employment - male'].to_string(header=False,index=False))],'Employment: High-skilled female':[float(pop.loc[(pop.Country == code)&(pop.Sector == concordance.loc[concordance.Name == sector,'CodeNr'].to_string(index=False)),'Split High qualification employment - female'].to_string(header=False,index=False))], 'Employment hours: Low-skilled male' :[float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours Low qualification employement - male' ].to_string(index=False,header=False))],  'Employment hours: Low-skilled female' :[float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours Low qualification employement - female' ].to_string(index=False,header=False))],'Employment hours: Medium-skilled male' :[float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours Middle qualification employement - male' ].to_string(index=False,header=False))],  'Employment hours: Medium-skilled female' :[float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours Middle qualification employement - female' ].to_string(index=False,header=False))],'Employment hours: High-skilled male' :[float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours High qualification employement - male' ].to_string(index=False,header=False))],  'Employment hours: High-skilled female' :[float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours High qualification employement - female' ].to_string(index=False,header=False))]})


                    #new_row = pd.DataFrame({'region':[code],   'sector':[sector],   'Employment: Low-skilled male': [float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split Low qualification employment - male'].to_string(header=False,index=False))],'Employment: Low-skilled female': [float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split Low qualification employment - female'].to_string(header=False,index=False))],'Employment: Medium-skilled male':[float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split Middle qualification employment - male'].to_string(header=False,index=False))],'Employment: Medium-skilled female': [float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split Middle qualification employment - female'].to_string(header=False,index=False))],'Employment: High-skilled male':[float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split High qualification employment - male'].to_string(header=False,index=False))],'Employment: High-skilled female':[float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split High qualification employment - female'].to_string(header=False,index=False))], 'Employment hours: Low-skilled male' : [float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours Low qualification employement - male'].to_string(index=False,header=False))]})
                    final_table=pd.concat([final_table,new_row])

            final[years]=final_table.copy()

        writer = pd.ExcelWriter('final_labor_SUTs_3_10.xlsx',engine='xlsxwriter')

        for year in range(1995,2023):
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
