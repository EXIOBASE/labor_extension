import pandas as pd
import json
from pathlib import Path
from from_cia_to_ilo import cia_to_ilo
from ref_label import add_ref_label
import country_converter as coco

from salary_split_ray import salary_split_year

def workforce_calculation(data_path,src_csv,src_csv2):
    
    '''
    We read the downloaded data and add to it the column ref_area.label which correspond to the name_short designation in country converter
    '''
    
    data_list = pd.read_csv(data_path/src_csv, encoding="utf-8-sig",low_memory=(False)) 
    # data_list = data_list[~data_list["ref_area"].str.contains(r'[0-9]')] 

    add_ref_area_label = pd.read_csv('aux/EMP_2EMP_SEX_ECO_NB_A-full-2021-11-30.csv', encoding="utf-8-sig",low_memory=False) 

    data_list = add_ref_label(data_list,add_ref_area_label)
    # data_list = add_ref_label(data_list)

    
    
    '''
    Looking at the countries in EXIOBASE (cc_all.ISO3.ISO3), and looking at the countries available from ILO (data_list),
    we can see that some countries are not in ILO.
    We have to list them and look for other sources in order to get the workforce for each countries.
    We will, as a first step, get the missing data from CIA, the-world-factbook
    '''
    
    
    with open("aux/CIA.json", "r") as read_file:
        data_cia = json.load(read_file)
    
    filename = Path('aux/countries_en.csv')
    correspondance_ilo = pd.read_csv(filename)
    xls = pd.ExcelFile('aux/Exiobase_Population_Data_not_found.xlsx')
    missing_data = pd.read_excel(xls, 'Exiobase data not automatised')
    
    missing_data.columns = missing_data.iloc[missing_data[missing_data.values=='ISO3'].index.values[0]]
    missing_data = missing_data.iloc[3: , :]
    
    from_cia_to_ilo, missing_countries = cia_to_ilo(data_list,data_cia,correspondance_ilo,missing_data)
    
    # final = data_list.append(from_cia_to_ilo)
    final = pd.concat([data_list,from_cia_to_ilo])
    

    '''
    table : workforce by iso3, year, sex, category : complete_table
    cleaned table : table_workforce_by_ISO3.csv
    '''
    final.to_csv('complete_table.csv',index=False)
    
    
    '''
    table by EXIO3 region : final_table.csv
    '''
    cc_all = coco.CountryConverter(include_obsolete=True)
    ISO3 = cc_all.ISO3['ISO3'].to_list()
    workforce_iso3 = final.copy()
    workforce_iso3 = workforce_iso3.drop(['obs_status'],axis=1)
    workforce_iso3=workforce_iso3[workforce_iso3.classif1.isin(['ECO_DETAILS_TOTAL'])]
    workforce_iso3 = workforce_iso3.rename(columns={'obs_value': 'Workforce (1000)'})
    workforce_iso3=workforce_iso3[workforce_iso3.ref_area.isin(ISO3)]
    workforce_iso3 = workforce_iso3.drop(['classif1'],axis=1)
    workforce_iso3.to_csv('workforce_total_iso3.csv',index=False)
    country_code = list(workforce_iso3['ref_area'])
    workforce_exio3 = workforce_iso3.copy()
    #workforce_exio3.insert(2, 'EXIO3', cc_all.convert(names = country_code ,src="ISO3", to='EXIO3') )

    workforce_exio3 = workforce_exio3.drop(['ref_area'],axis=1)
    workforce_exio3 = workforce_exio3.drop(['ref_area.label'],axis=1)
    aggregation_exio3 = workforce_exio3.groupby(['EXIO3', 'sex','time'], axis=0).sum()
    aggregation_exio3=aggregation_exio3.reset_index()

    aggregation_exio3.to_csv('workforce_total_exio3.csv',index=False)

    
    
    aggregation_ISO3 = final.groupby(['ref_area', 'sex','classif1','time'], axis=0).sum()
    aggregation_ISO3.to_csv('table_workforce_by_ISO3.csv')
    cc_all = coco.CountryConverter(include_obsolete=True)
    country_code = list(final['ref_area'])

    #final.insert(2, 'EXIO3', cc_all.convert(names = country_code ,src="ISO3", to='EXIO3') )


    aggregation = final.groupby(['EXIO3', 'sex','classif1','time'], axis=0).sum()
    aggregation.to_csv('table_workforce_by_EXIO3.csv')
    aggregation=aggregation.reset_index()
    aggregation_ISO3=aggregation_ISO3.reset_index()
    
    '''
    Create a list of the classification containing DETAILS
    '''
    
    column_names = ['Country','Sector','Mapping','Compensation of employees; wages, salaries, & employers social contributions: Low-skilled','Compensation of employees; wages, salaries, & employers social contributions: Middle-skilled','Compensation of employees; wages, salaries, & employers social contributions: High-skilled','Compensation of employees; wages, salaries, & employers social contributions: Total','ILO data /country / sector','Split','Split Low qualification employment - total','Split Middle qualification employment - total','Split High qualification employment - total','Split Low qualification employment - male','Split Middle qualification employment - male','Split High qualification employment - male','Split Low qualification employment - female','Split Middle qualification employment - female','Split High qualification employment - female']
    classif_detail = [s for s in final['classif1'].unique() if ("DETAILS" in s and "TOTAL" not in s)]
    concordance = pd.read_excel('aux/Exiobase_ISIC_Rev-4.xlsx', 'ILO_mapping_sector')
    
    '''
    Creation of dataframe for salary split. One per year will be created
    '''
    
    salary_split_per_year = salary_split_year(column_names,final,classif_detail,concordance,aggregation) #22:05
    
    return final

