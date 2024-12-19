'''
We select here the classification and sex of interest.
We also insert the EXIO3 corresponding region for each ISO3 code.
Finally, we replace in the table the word "DETAIL" by "ISIC" in order to link two tables.
''' 

def clean(workforce,coco):    
    
    workforce = workforce.drop(columns=['ref_area.label','EXIO3','obs_status'])
    workforce = workforce[workforce['classif1'].str.contains('ECO_DETAILS',regex=True)]
    workforce = workforce[workforce['sex'].str.contains('SEX_F|SEX_M',regex=True)]
    
    country_code = list(workforce['ref_area'])
    cc_all = coco.CountryConverter(include_obsolete=True)
    workforce.insert(2, 'EXIO3', cc_all.convert(names = country_code,src="ISO3", to='EXIO3'))
    workforce2 = workforce.copy()
    workforce2['classif1']=workforce2['classif1'].str.replace('_DETAILS_', '_ISIC_')

    return workforce,workforce2
