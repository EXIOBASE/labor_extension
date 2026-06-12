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

def complete2(hours):

    all_hours = {}
    hours2 = hours.copy()
    ray.init(runtime_env=runtime_env,num_cpus = os.cpu_count()-4)

    @ray.remote
    def completeDE_ray(hours2,code):  
        hours=hours2.loc[hours2.ref_area == code]
        
        print(code)

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

                  

        test = hours.copy()
        all_hours[code]=hours.copy()
        return test

 
               
    results = [ray.get([completeDE_ray.remote(hours2, code) for code in hours.ref_area.unique()])]
    
    hour = hours.iloc[:0].copy()
    for a in results[0] :
        hour = pd.concat([hour,a])
    
    ray.shutdown() 
      
    all_hours = {}
    hours2 = hour.copy()
    ray.init(runtime_env=runtime_env,num_cpus = os.cpu_count()-4)

    @ray.remote
    def completeHJ_ray(hours2,code):  
        hours=hours2.loc[hours2.ref_area == code]
        
        print(code)

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

                  

        test = hours.copy()
        all_hours[code]=hours.copy()
        return test

 
               
    results = [ray.get([completeHJ_ray.remote(hours2, code) for code in hours.ref_area.unique()])]
    
    hour = hours.iloc[:0].copy()
    for a in results[0] :
        hour = pd.concat([hour,a])
    
    ray.shutdown()   

    all_hours = {}
    hours2 = hour.copy()
    ray.init(runtime_env=runtime_env,num_cpus = os.cpu_count()-4)

    @ray.remote
    def completeLMN_ray(hours2,code):  
        hours=hours2.loc[hours2.ref_area == code]
        
        print(code)
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

                  

        test = hours.copy()
        all_hours[code]=hours.copy()
        return test

 
               
    results = [ray.get([completeLMN_ray.remote(hours2, code) for code in hours.ref_area.unique()])]
    
    hour = hours.iloc[:0].copy()
    for a in results[0] :
        hour = pd.concat([hour,a])
    
    ray.shutdown()   

    all_hours = {}
    hours2 = hour.copy()
    ray.init(runtime_env=runtime_env,num_cpus = os.cpu_count()-4)

    @ray.remote
    def completeRSTU_ray(hours2,code):  
        hours=hours2.loc[hours2.ref_area == code]
        
        print(code)
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
                    
                  

        test = hours.copy()
        all_hours[code]=hours.copy()
        return test

 
               
    results = [ray.get([completeRSTU_ray.remote(hours2, code) for code in hours.ref_area.unique()])]
    
    hour = hours.iloc[:0].copy()
    for a in results[0] :
        hour = pd.concat([hour,a])
    
    ray.shutdown() 
    
            
    return hour 
    
