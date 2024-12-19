import pandas as pd

def reshape_eurostat(hour_eurostat,cc_all):    
    
    hour_eurostat = hour_eurostat[hour_eurostat['age'].str.contains('Y15-64',regex=True)]
    hour_eurostat = hour_eurostat[hour_eurostat['worktime'].str.contains('TOTAL',regex=True)]
    hour_eurostat = hour_eurostat[hour_eurostat['sex'].str.contains('F|M',regex=True)]
    hour_eurostat = hour_eurostat[hour_eurostat['wstatus'].str.contains('EMP',regex=True)]
    hour_eurostat = hour_eurostat[hour_eurostat['nace_r1'].str.contains('A_B',regex=True)]
    hour_eurostat = hour_eurostat[~hour_eurostat['geo\\TIME_PERIOD'].str.contains('EA19|EU15|EU27_2020|EU28|EA20')]
    hour_eurostat.columns = hour_eurostat.columns.str.replace(' ', '')
    
        
    # hour_eurostat2 = hour_eurostat2[hour_eurostat2['age'].str.contains('Y15-64',regex=True)]
    # hour_eurostat2 = hour_eurostat2[hour_eurostat2['worktime'].str.contains('TOTAL',regex=True)]
    # hour_eurostat2 = hour_eurostat2[hour_eurostat2['sex'].str.contains('F|M',regex=True)]
    # hour_eurostat2 = hour_eurostat2[hour_eurostat2['wstatus'].str.contains('EMP',regex=True)]
    # hour_eurostat2 = hour_eurostat2[hour_eurostat2['nace_r1'].str.contains('A_B',regex=True)]
    # hour_eurostat2 = hour_eurostat2[~hour_eurostat2['geo\\TIME_PERIOD'].str.contains('EA19|EU15|EU27_2020|EU28|EA20')]
    # hour_eurostat2.columns = hour_eurostat2.columns.str.replace(' ', '')
    
    
    for i in range(0,len(hour_eurostat.columns)):
        for j in range(0,len(hour_eurostat.index)):
            if (':') in hour_eurostat.iloc[j][i]:
                hour_eurostat.iloc[j][i]=''
                
    for i in range(7,len(hour_eurostat.columns)):
        for j in range(0,len(hour_eurostat.index)):
            #print(i,j)
            if ('b') in hour_eurostat.iloc[j][i]:
                hour_eurostat.iloc[j][i]=hour_eurostat.iloc[j][i].replace('b','')
            if ('c') in hour_eurostat.iloc[j][i]:
                hour_eurostat.iloc[j][i]=hour_eurostat.iloc[j][i].replace('c','')
            if ('bu') in hour_eurostat.iloc[j][i]:
                hour_eurostat.iloc[j][i]=hour_eurostat.iloc[j][i].replace('bu','')
            if ('u') in hour_eurostat.iloc[j][i]:
                hour_eurostat.iloc[j][i]=hour_eurostat.iloc[j][i].replace('u','')            
    
    '''
    pb with Greece and United Kingdom
    Made modification by hand
    '''
    
    
    # cc_all.convert(names = hour_eurostat['geo\\TIME_PERIOD'],src="EXIO3", to='ISO3')
    hour_eurostat.insert(7, 'ISO3', cc_all.convert(names = hour_eurostat['geo\\TIME_PERIOD'],src="EXIO3", to='ISO3'))
    # hour_eurostat=hour_eurostat.drop(columns='ISO3')
    # hour_eurostat.insert(7, 'ISO3', cc_all.convert(names = hour_eurostat['geo\\TIME_PERIOD'],src="ISO2", to='ISO3'))
    # hour_eurostat.to_csv('hour_eurostat.csv')
    # hour_eurostat.insert(8, 'EXIO3', cc_all.convert(names = hour_eurostat['geo\\TIME_PERIOD'],src="ISO2", to='EXIO3'))
    # hour_eurostat.to_csv('hour_eurostat.csv')
    # hour_eurostat.loc[(hour_eurostat['geo\\TIME_PERIOD']=='EL'),['EXIO3']]='GR'
    hour_eurostat.loc[(hour_eurostat['geo\\TIME_PERIOD']=='EL'),['ISO3']]='GRC'
    hour_eurostat.loc[(hour_eurostat['geo\\TIME_PERIOD']=='UK'),['ISO3']]='GBR'
    # hour_eurostat.loc[(hour_eurostat['geo\\TIME_PERIOD']=='UK'),['EXIO3']]='GB'
    
    # hour_eurostat.loc[(hour_eurostat['geo\\TIME_PERIOD']=='IS'),['EXIO3']]='WE'
    hour_eurostat.loc[(hour_eurostat['geo\\TIME_PERIOD']=='IS'),['ISO3']]='ISL'
    hour_eurostat.loc[(hour_eurostat['geo\\TIME_PERIOD']=='MK'),['ISO3']]='MKD'
    # hour_eurostat.loc[(hour_eurostat['geo\\TIME_PERIOD']=='MK'),['EXIO3']]='WE'
    
    
    hour_eurostat.loc[(hour_eurostat['geo\\TIME_PERIOD']=='UK'),['geo\\TIME_PERIOD']]='GB'
    hour_eurostat.loc[(hour_eurostat['geo\\TIME_PERIOD']=='EL'),['geo\\TIME_PERIOD']]='GR'
    hour_eurostat.insert(8, 'EXIO3', cc_all.convert(names = hour_eurostat['ISO3'],src="ISO3", to='EXIO3'))

    
    
    hour_eurostat[hour_eurostat.columns[10:27]] = hour_eurostat[hour_eurostat.columns[10:27]].apply(pd.to_numeric)
    hour_eurostat = pd.concat([hour_eurostat[hour_eurostat.columns[1:9]], hour_eurostat[hour_eurostat.columns[10:27][:: -1]]], axis=1)
    hour_eurostat[hour_eurostat.columns[10:27]] = hour_eurostat[hour_eurostat.columns[10:27]].interpolate(method='linear',axis=1,limit_area='inside')
    
    hour_eurostat.loc[hour_eurostat.sex == "F", "sex"] = "SEX_F"
    hour_eurostat.loc[hour_eurostat.sex == "M", "sex"] = "SEX_M"
    hour_eurostat= hour_eurostat.drop(columns=['wstatus','worktime','age','unit'])
    hour_eurostat = hour_eurostat.iloc[:, [1, 0] + list(range(2, hour_eurostat.shape[1]))]
    hour_eurostat.insert(2, 'classif1', 'ECO_ISIC4_A')
    hour_eurostat = hour_eurostat.rename(columns={"ISO3": "ref_area"})
    
    for a in range(1992,2009):
        hour_eurostat = hour_eurostat.rename(columns={str(a): int(a)})
    
    hour_eurostat_reshape = pd.DataFrame(data=None,columns=['ref_area','sex','classif1','time','obs_value'])
    for code in hour_eurostat.ref_area.unique():
        for year in range(1992,2009):
            for sex in hour_eurostat.sex.unique():
                for classif in hour_eurostat.classif1.unique():
                    if not hour_eurostat.loc[(hour_eurostat['ref_area']==code)&(hour_eurostat['sex']==sex)&(hour_eurostat['classif1']==classif),[year]].isnull().values.all(): 
                        value =  float(hour_eurostat.loc[(hour_eurostat['ref_area']==code)&(hour_eurostat['sex']==sex)&(hour_eurostat['classif1']==classif),[year]].to_string(index=False, header=False))
                        
                        # print('value',value)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : classif, 'time' : year, 'obs_value' :value}

                        hour_eurostat_reshape.loc[len(hour_eurostat_reshape)] = new_line
                        hour_eurostat_reshape = hour_eurostat_reshape.reset_index(drop=True) 
                        
                                    
                        # hour_eurostat_reshape=hour_eurostat_reshape.append(pd.Series([code,sex,'ECO_ISIC3_A',year,value], index=[i for i in hour_eurostat_reshape]),ignore_index=True)
            
                        break
    return hour_eurostat_reshape
