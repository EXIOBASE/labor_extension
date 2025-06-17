import country_converter as coco
import pandas as pd
from datetime import datetime 
import numpy as np
from numpy import transpose 
import os
import ray

runtime_env = {
    'env_vars': {
        "RAY_memory_monitor_refresh_ms": "0",
        "RAY_record_ref_creation_sites":"1",
        "RAY_verbose_spill_logs":"0"
        
     }
}
cc = coco.CountryConverter()
cc.valid_class
cc.get_correspondence_dict('ISO3', 'EXIO3')

converter=coco.country_converter

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
    
    fetched_data = pd.DataFrame(data=None,columns=['ISO3','population','date'])
    for a in data_cia['countries'].keys():

        name_short_cia = cc_all.convert(names = a ,src = 'regex',to='ISO3')
        for item in missing_countries:
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
    
    

    from_cia_to_ilo =  pd.DataFrame(data=None,columns=column_data_list)
    ray.init(runtime_env=runtime_env,num_cpus = os.cpu_count()-4)
    
    table_of_interest = from_cia_to_ilo.copy()
    @ray.remote

    def calculation_ray(a,table_of_interest):
        from_cia_to_ilo=table_of_interest

        # for a in missing_countries: # This could be runned in parallel as all the countries are independent- 
        print(a)    
        if a in fetched_data['ISO3'].values:
            print(a)
    
            ILO_region = ILO_Subregion_Broad  = None
        
            ILO_region = df.loc[df['ISO3 Code']==a,['ILO Region']]
            ILO_region = ILO_region.to_string(index=False, header=False)
            ILO_Subregion_Broad = df.loc[df['ISO3 Code']==a,['ILO Subregion - Broad']]
            ILO_Subregion_Broad = ILO_Subregion_Broad.to_string(index=False, header=False)
            
            World_Bank_Income_Group = df.loc[df['ISO3 Code']==a,['World Bank Income Group']]
            World_Bank_Income_Group = World_Bank_Income_Group.to_string(index=False, header=False)  
            for s in list_sex:
                for c in classifications :
                    
                    if str(ILO_Subregion_Broad)+': '+str(World_Bank_Income_Group) in data_list_old['ref_area.label'].values:
                        date = int(fetched_data.loc[fetched_data['ISO3']==a,['date']].to_string(index=False, header=False))
                        pop_known_year_know = float(fetched_data.loc[fetched_data['ISO3']==a,['population']].to_string(index=False, header=False))/1000
                        print(a,pop_known_year_know)
                        
                        '''
                        case of TCA, population unknown for the corresponding ILO_Subregion_Broad in  1990.
                        we have to extrapolate known values.
                        We know the population of the ILO_Subregion_Broad for 1991 and  1992. we deduced from these the value for 1990.
                        '''
                        if date <=1990 :
                            pop_total_year_know_1991 = float((data_list_old.loc[(data_list_old['ref_area.label']==str(ILO_Subregion_Broad)+': '+str(World_Bank_Income_Group))&(data_list_old['classif1']=='ECO_SECTOR_TOTAL')&(data_list_old['sex']=='SEX_T')&(data_list_old['time']==1991),['obs_value']].to_string(index=False, header=False)))
                            pop_total_year_know_1992 = float((data_list_old.loc[(data_list_old['ref_area.label']==str(ILO_Subregion_Broad)+': '+str(World_Bank_Income_Group))&(data_list_old['classif1']=='ECO_SECTOR_TOTAL')&(data_list_old['sex']=='SEX_T')&(data_list_old['time']==1992),['obs_value']].to_string(index=False, header=False)))
                            pop_total_year_know = 2*pop_total_year_know_1991-pop_total_year_know_1992
                        
                        else :
                            
                            pop_total_year_know = float((data_list_old.loc[(data_list_old['ref_area.label']==str(ILO_Subregion_Broad)+': '+str(World_Bank_Income_Group))&(data_list_old['classif1']=='ECO_SECTOR_TOTAL')&(data_list_old['sex']=='SEX_T')&(data_list_old['time']==date),['obs_value']].to_string(index=False, header=False)))
                        
                        for year in range(1991,2023):
                            if year == int(fetched_data.loc[fetched_data['ISO3']==a,['date']].to_string(index=False, header=False)):
                                pop_of_interest = float((data_list_old.loc[(data_list_old['ref_area.label']==str(ILO_Subregion_Broad)+': '+str(World_Bank_Income_Group))&(data_list_old['classif1']==c)&(data_list_old['sex']==s)&(data_list_old['time']==year),['obs_value']].to_string(index=False, header=False)))
                                # from_cia_to_ilo=from_cia_to_ilo.append(pd.Series([a,cc_all.convert(names = a ,src = 'ISO3',to='name_official'),cc_all.convert(names = a ,src = 'ISO3',to='EXIO3'),s,c,year,pop_known_year_know/pop_total_year_know*pop_of_interest,'ILO_Subregion_Broad'], index=[i for i in column_data_list]),ignore_index=True)
                                #new_line = pd.Series([a,cc_all.convert(names = a ,src = 'ISO3',to='name_official'),cc_all.convert(names = a ,src = 'ISO3',to='EXIO3'),s,c,year,pop_known_year_know/pop_total_year_know*pop_of_interest,'ILO_Subregion_Broad']).to_frame().T
                                #print(newline)
                                new_line = {'ref_area' : a,'EXIO3' : cc_all.convert(names = a ,src = 'ISO3',to='EXIO3'), 'sex' : s , 'classif1' : c, 'time' : year, 'obs_value' :(pop_known_year_know)/pop_total_year_know*pop_of_interest, 'obs_status' : 'ILO_Subregion_Broad' ,'ref_area.label' : cc_all.convert(names = a ,src = 'ISO3',to='name_official')}
                                #print(newline)
                                from_cia_to_ilo.loc[len(from_cia_to_ilo)] = new_line
                                from_cia_to_ilo = from_cia_to_ilo.reset_index(drop=True)
                            else:
    
                                pop_of_interest = float((data_list_old.loc[(data_list_old['ref_area.label']==str(ILO_Subregion_Broad)+': '+str(World_Bank_Income_Group))&(data_list_old['classif1']==c)&(data_list_old['sex']==s)&(data_list_old['time']==year),['obs_value']].to_string(index=False, header=False)))
                                pop_country=pop_known_year_know*pop_of_interest/pop_total_year_know
                                # from_cia_to_ilo=from_cia_to_ilo.append(pd.Series([a,cc_all.convert(names = a ,src = 'ISO3',to='name_official'),cc_all.convert(names = a ,src = 'ISO3',to='EXIO3'),s,c,year,pop_country,'ILO_Subregion_Broad'], index=[i for i in column_data_list]),ignore_index=True)
                                
                                new_line = {'ref_area' : a,'EXIO3' : cc_all.convert(names = a ,src = 'ISO3',to='EXIO3'), 'sex' : s , 'classif1' : c, 'time' : year, 'obs_value' :pop_country, 'obs_status' : 'ILO_Subregion_Broad' ,'ref_area.label' : cc_all.convert(names = a ,src = 'ISO3',to='name_official')}

                                from_cia_to_ilo.loc[len(from_cia_to_ilo)] = new_line
                                from_cia_to_ilo = from_cia_to_ilo.reset_index(drop=True)       
                
      
                    else :
                        if str(ILO_region)+': '+str(World_Bank_Income_Group) in data_list_old['ref_area.label'].values:
                            date = int(fetched_data.loc[fetched_data['ISO3']==a,['date']].to_string(index=False, header=False))
                            pop_total_year_know = float((data_list_old.loc[(data_list_old['ref_area.label']==str(ILO_region)+': '+str(World_Bank_Income_Group))&(data_list_old['classif1']=='ECO_SECTOR_TOTAL')&(data_list_old['sex']=='SEX_T')&(data_list_old['time']==date),['obs_value']].to_string(index=False, header=False)))
                            pop_known_year_know = float(fetched_data.loc[fetched_data['ISO3']==a,['population']].to_string(index=False, header=False))/1000
                            for year in range(1991,2023):
                                if year == int(fetched_data.loc[fetched_data['ISO3']==a,['date']].to_string(index=False, header=False)):
                                    pop_of_interest = float((data_list_old.loc[(data_list_old['ref_area.label']==str(ILO_region)+': '+str(World_Bank_Income_Group))&(data_list_old['classif1']==c)&(data_list_old['sex']==s)&(data_list_old['time']==year),['obs_value']].to_string(index=False, header=False)))
                                    # from_cia_to_ilo=from_cia_to_ilo.append(pd.Series([a,cc_all.convert(names = a ,src = 'ISO3',to='name_official'),cc_all.convert(names = a ,src = 'ISO3',to='EXIO3'),s,c,year,pop_known_year_know/pop_total_year_know*pop_of_interest,'ILO_region'], index=[i for i in column_data_list]),ignore_index=True)
                                
                                    new_line = {'ref_area' : a,'EXIO3' : cc_all.convert(names = a ,src = 'ISO3',to='EXIO3'), 'sex' : s , 'classif1' : c, 'time' : year, 'obs_value' :(pop_known_year_know)/pop_total_year_know*pop_of_interest, 'obs_status' : 'ILO_region' ,'ref_area.label' : cc_all.convert(names = a ,src = 'ISO3',to='name_official')}

                                    from_cia_to_ilo.loc[len(from_cia_to_ilo)] = new_line
                                    from_cia_to_ilo = from_cia_to_ilo.reset_index(drop=True) 
                                
                                
                                
                                else:
                                    pop_of_interest = float((data_list_old.loc[(data_list_old['ref_area.label']==str(ILO_region)+': '+str(World_Bank_Income_Group))&(data_list_old['classif1']==c)&(data_list_old['sex']==s)&(data_list_old['time']==year),['obs_value']].to_string(index=False, header=False)))
                                    pop_country=pop_known_year_know*pop_of_interest/pop_total_year_know
                                    # from_cia_to_ilo=from_cia_to_ilo.append(pd.Series([a,cc_all.convert(names = a ,src = 'ISO3',to='name_official'),cc_all.convert(names = a ,src = 'ISO3',to='EXIO3'),s,c,year,pop_country,'ILO_region'], index=[i for i in column_data_list]),ignore_index=True)
                                    
                                    new_line = {'ref_area' : a,'EXIO3' : cc_all.convert(names = a ,src = 'ISO3',to='EXIO3'), 'sex' : s , 'classif1' : c, 'time' : year, 'obs_value' :pop_country, 'obs_status' : 'ILO_region' ,'ref_area.label' : cc_all.convert(names = a ,src = 'ISO3',to='name_official')}
                                    from_cia_to_ilo.loc[len(from_cia_to_ilo)] = new_line
                                    from_cia_to_ilo = from_cia_to_ilo.reset_index(drop=True)     
                                    
                                    
                                    
        table_of_interest = from_cia_to_ilo

        return table_of_interest  

    results = [ray.get([calculation_ray.remote(a,table_of_interest) for a in missing_countries])]


    for a in results : 
        final_table= pd.concat([a for a in results[0] if not a.empty])

    
    ray.shutdown()
    from_cia_to_ilo = final_table
    # return final_table                            
                                    
                                        
                                    
                                    
                                    
                                    
    #from_cia_to_ilo.to_csv('frist_part.csv',index =False)
    
    from_cia_to_ilo2 =  pd.DataFrame(data=None,columns=column_data_list)
    ray.init(runtime_env=runtime_env,num_cpus = os.cpu_count()-4)
    
    table_of_interest = from_cia_to_ilo2.copy()
    @ray.remote

    def calculation_ray2(code,table_of_interest): 
        '''25min on 8 cpus'''
        from_cia_to_ilo2=table_of_interest


    # for code in missing_data['ISO3'].values:  # This could be runned in parallel as all the countries are independent- 
        if (len(str(code)) == 3 and str(code) != 'nan'):
            if not code in from_cia_to_ilo.ref_area.unique() :
                label  = missing_data.loc[missing_data['ISO3']==code,['Label_short']]
                print(code)
                for s in list_sex:
                    for c in classifications:
                        if label.to_string(index=False, header=False) in data_list_old['ref_area.label'].values:
                            for year in range(1991,2023):
                                '''total pop country of interest'''
                                pop_known_year_know = float(missing_data.loc[missing_data['ISO3']==code,[year]].to_string(index=False, header=False))
                                '''total population in the region where the country belongs too'''
                                pop_of_interest = float((data_list_old.loc[(data_list_old['ref_area.label']==label.to_string(index=False, header=False))&(data_list_old['classif1']==c)&(data_list_old['sex']==s)&(data_list_old['time']==year),['obs_value']].to_string(index=False, header=False)))
                            
                                pop_total_year_know = float((data_list_old.loc[(data_list_old['ref_area.label']==label.to_string(index=False, header=False))&(data_list_old['classif1']=='ECO_SECTOR_TOTAL')&(data_list_old['sex']=='SEX_T')&(data_list_old['time']==year),['obs_value']].to_string(index=False, header=False)))
                                pop_country=pop_known_year_know*pop_of_interest/pop_total_year_know

                                # print(code, year,c, pop_known_year_know,pop_of_interest,pop_total_year_know,pop_country)

                                # pop_total_year_know = float((data_list_old.loc[(data_list_old['ref_area.label']==label.to_string(index=False, header=False))&(data_list_old['classif1']=='ECO_SECTOR_TOTAL')&(data_list_old['sex']=='SEX_T')&(data_list_old['time']==date),['obs_value']].to_string(index=False, header=False)))

                                # pop_country=pop_known_year_know*pop_of_interest/pop_total_year_know
 

                                # from_cia_to_ilo=from_cia_to_ilo.append(pd.Series([code,cc_all.convert(names = code ,src = 'ISO3',to='name_official'),cc_all.convert(names = code ,src = 'ISO3',to='EXIO3'),s,c,year,pop_country,'ILO_Subregion_Broad'], index=[i for i in column_data_list]),ignore_index=True)
                            
                                new_line = {'ref_area' : code, 'sex' : s , 'classif1' : c, 'time' : year, 'obs_value' :pop_country, 'obs_status' : 'ILO_Subregion_Broad' ,'ref_area.label' : cc_all.convert(names = code ,src = 'ISO3',to='name_official')}
                                # print(new_line)
                                from_cia_to_ilo2.loc[len(from_cia_to_ilo2)] = new_line
                                from_cia_to_ilo2 = from_cia_to_ilo2.reset_index(drop=True) 
                            
        table_of_interest = from_cia_to_ilo2

        return table_of_interest  

    results = [ray.get([calculation_ray2.remote(code,table_of_interest) for code in missing_data['ISO3'].values])]


    for a in results : 
        final_table2= pd.concat([a for a in results[0] if not a.empty])

    final_table2=final_table2.drop(columns=['EXIO3'],axis = 1) 
    country_code = list(final_table2['ref_area'])
    final_table2.insert(1, 'EXIO3', converter.convert(names = country_code, to='EXIO3'))
    ray.shutdown()
    from_cia_to_ilo2 = final_table2
    
    from_cia_to_ilo = pd.concat([from_cia_to_ilo,from_cia_to_ilo2])

    return from_cia_to_ilo,missing_countries
