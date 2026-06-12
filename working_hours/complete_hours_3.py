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

def complete3(hours_RoW,workforce_iso3):

    all_hours = {}
    hours2 = hours_RoW.copy()
    ray.init(runtime_env=runtime_env,num_cpus = os.cpu_count()-4)

    @ray.remote
    def complete3_ray(hours2,code):  
        hours_RoW=hours2.loc[hours2.ref_area == code]

        if code in workforce_iso3.ref_area.unique() and code in hours.ref_area.unique():
            #print(code)
            if code != 'UKR':
                for sex in ['SEX_F','SEX_M']:
                    for c in workforce_iso3.classif1.unique():
                        for t in range(1995,2023):
                        #aorkforce_iso3.time.unique():
                            #if not (workforce_iso3.loc[(workforce_iso3['ref_area']==code)&(workforce_iso3['sex']==sex)&(workforce_iso3['classif1']==c)&(workforce_iso3['time']==t),['obs_value']]).isnull :
                                P = float(workforce_iso3.loc[(workforce_iso3['ref_area']==code)&(workforce_iso3['sex']==sex)&(workforce_iso3['classif1']==c)&(workforce_iso3['time']==t),['obs_value']].to_string(header=False,index=False))
                            #H = float(hours.loc[(hours['ref_area']==code)&(hours['sex']==sex)&(hours['classif1']==c),str(years)].to_string(header=False, index=False))                        
                                hours_RoW.loc[(hours_RoW['ref_area']==code)&(hours_RoW['sex']==sex)&(hours_RoW['classif1']==c)&(hours_RoW['time']==t),['population (1000)']] = P 


        test = hours.copy()
        all_hours[code]=hours.copy()
        return test

 
               
    results = [ray.get([complete3_ray.remote(hours2, code) for code in workforce_iso3.ref_area.unique()])]
    
    hour = hours.iloc[:0].copy()
    for a in results[0] :
        hour = pd.concat([hour,a])
    
    ray.shutdown() 
      

    
            
    return hour 
    
