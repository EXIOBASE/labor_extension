import os
import ray
import pandas as pd

runtime_env = {
    'env_vars': {
        "RAY_memory_monitor_refresh_ms": "0",
        "RAY_record_ref_creation_sites":"1",
        "RAY_verbose_spill_logs":"0"

     }
}

def complete(hours):

    all_hours = {}
    hours2 = hours.copy()
    ray.init(runtime_env=runtime_env,num_cpus = os.cpu_count()-4)

    @ray.remote
    def complete_ray(hours2,code):  
        hours=hours2.loc[hours2.ref_area == code]
        
        print(code)
        for sex in hours.sex.unique() : 

            
            for years in range(1995, 2024):
                
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

        test = hours.copy()
        all_hours[code]=hours.copy()
        return test

 
               
    results = [ray.get([complete_ray.remote(hours2, code) for code in hours.ref_area.unique()])]
    
    hour = hours.iloc[:0].copy()
    for a in results[0] :
        hour = pd.concat([hour,a])
    
    ray.shutdown()   
    return hour 
    
