import country_converter as coco
import pandas as pd
def add_ref_label(data,add_ref_area_label):
# def add_ref_label(data):
    
    # data.insert(1, 'ref_area.label' ,'')
    add_ref_area_label2=add_ref_area_label[['ref_area','ref_area.label']]
    add_ref_label2=add_ref_area_label2.drop_duplicates()
    

    
    def convert(ref):
        if ref :
            if ref in add_ref_label2['ref_area'].unique():
                label = add_ref_label2[add_ref_label2['ref_area']==ref]['ref_area.label'].values[0]
                return label
            

    data['ref_area.label'] = data['ref_area'].apply(convert)
    
    
    # for index, row in data.iterrows():
    #     print(index)
    #     if add_ref_area_label.loc[add_ref_area_label['ref_area']==row['ref_area']]['ref_area.label'].unique()[0]  :
    #         data.iloc[index, data.columns.get_loc('ref_area.label')] = convert(row)       
    #     else:
    #         continue
            
    # for row in data.itertuples():
    #     if add_ref_area_label.loc[add_ref_area_label['ref_area']==row['ref_area']]['ref_area.label'].unique()[0]  :
            
    #        row[2] = add_ref_area_label.loc[add_ref_area_label['ref_area']==row['ref_area']]['ref_area.label'].unique()[0]         
    #     else :
    #         continue
        

        
    '''
    In ILO table, the ISO3 associated to channel island is CHA. However, in coco CHI is allocated to this location.
    We replace CHA by CHI in ILO table
    '''

    
    data["ref_area"].replace({"CHA": "CHI"}, inplace=True)
   
    '''
    We add the EXIO3 region for each ISO3 countries 
    '''
    
    country_code = list(data['ref_area'])
    
    cc_all = coco.CountryConverter(include_obsolete=True)
    data_ISO3 = data[data['ref_area'].isin(cc_all.ISO3['ISO3'])]
    data_autre = data[~data['ref_area'].isin(cc_all.ISO3['ISO3'])]
    country_code = list(data_ISO3['ref_area'])

    data_ISO3.insert(2, 'EXIO3', cc_all.convert(names = country_code,src="ISO3", to='EXIO3') )
    data_autre.insert(2, 'EXIO3', '' )
    data = pd.concat([data_ISO3,data_autre])

    return data



