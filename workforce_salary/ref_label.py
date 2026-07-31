import country_converter as coco
import pandas as pd
def add_ref_label(data,add_ref_area_label):
# def add_ref_label(data):
    
    # data.insert(1, 'ref_area.label' ,'')
    add_ref_area_label2=add_ref_area_label[['ref_area','ref_area.label']]
    add_ref_label2=add_ref_area_label2.drop_duplicates()
    

    
    # Was: data['ref_area'].apply(convert), where convert() ran
    #   `ref in add_ref_label2['ref_area'].unique()` and then a boolean-mask
    #   lookup, ONCE PER ROW. On the 781k-row ILO export that is 781k
    #   `.unique()` calls plus 781k full-frame scans, and it dominated the
    #   runtime of the whole workforce build. A dict built once from the same
    #   de-duplicated frame gives identical labels.
    _label_by_ref = dict(zip(add_ref_label2['ref_area'],
                             add_ref_label2['ref_area.label']))
    data['ref_area.label'] = data['ref_area'].map(_label_by_ref)

    
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

    
    # Chained-assignment `inplace=True` on a slice is a no-op under pandas 3.
    data["ref_area"] = data["ref_area"].replace({"CHA": "CHI"})

    '''
    We add the EXIO3 region for each ISO3 countries
    '''

    cc_all = coco.CountryConverter(include_obsolete=True)
    is_iso3 = data['ref_area'].isin(cc_all.ISO3['ISO3'])
    data_ISO3 = data[is_iso3].copy()
    data_autre = data[~is_iso3].copy()

    # Was: cc_all.convert(names=list(data_ISO3['ref_area']), ...) - one entry
    # per ROW, so country_converter was asked to resolve ~700k names when there
    # are only ~230 distinct ones. Convert the distinct codes and map back.
    unique_codes = list(pd.unique(data_ISO3['ref_area']))
    exio3_by_code = dict(zip(
        unique_codes,
        cc_all.convert(names=unique_codes, src="ISO3", to='EXIO3'),
    ))
    data_ISO3.insert(2, 'EXIO3', data_ISO3['ref_area'].map(exio3_by_code))
    data_autre.insert(2, 'EXIO3', '' )
    data = pd.concat([data_ISO3,data_autre])

    return data



