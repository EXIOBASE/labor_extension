import statistics
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

def regression_r(hour_pivot,year_begin,year_end):


    relevant_years = list(range(year_begin,year_end+1))
    backward = list(reversed(range(year_begin,year_end+1)))
    #for code in hour_pivot.index.get_level_values(0).unique():
    #	print(code)
    #code_values = hour_pivot.index.get_level_values(0).uniques():
    
    #mask = code_values.str.contains(code)
    #selected = hour_pivot[mask]

    #print(relevant_years)
    #for code in ['ALB','FRA']:
    
    #for code in hour_pivot.index:
    #    print(code)
    #    first_consecutive_values={}
    #    last_consecutive_values={}
        
    #code_unique = hour_pivot.index.get_level_values(0).unique()
    #code_values = hour_pivot.index.get_level_values(0)
    #for code in code_unique:
   # 	print(code)
   #     mask = code_values.str.contains(code)
   #     selected = hour_pivot[mask]
   #     print(selected)

    
	
    reg = {}
    hour_pivot2 = hour_pivot.copy()
    hour_pivot3 = hour_pivot.iloc[:0].copy()


    # writer = pd.ExcelWriter('split.xlsx',engine='xlsxwriter')

    ray.init(runtime_env=runtime_env,num_cpus = os.cpu_count()-4)

    @ray.remote
    def regression_ray(code_country,hour_pivot2):  
	
        first_consecutive_values={}
        last_consecutive_values={} 

        hour_pivot = hour_pivot2.copy()  

        code_values = hour_pivot.index.get_level_values(0)
        
        mask = code_values.str.contains(code_country)
        hour_pivot = hour_pivot2[mask]
        print(code_country)

              
        for code in hour_pivot.index:
            for years in relevant_years:

                if  not hour_pivot.loc[(hour_pivot.index==code),[years]].isnull().values.all():
                    first_year = years
                    break
                else:
                    first_year= None
                    
            for years in backward:
                if  not hour_pivot.loc[(hour_pivot.index==code),[years]].isnull().values.all():
                    last_year = years
                    break
                else :
                    last_year= None
                    
            # print(first_year,last_year)
            if first_year == year_begin and last_year == year_end:
                continue
            
                                                                    
            if  (first_year == None and last_year == None):
                continue
            
            if first_year == last_year:
                value =hour_pivot.loc[(hour_pivot.index==code),[first_year]]
                value=float(value.to_string(index=False, header=False))
                for years  in list(range(year_begin,year_end+1)):   
                    hour_pivot.loc[(hour_pivot.index==code),[years]] = value

                continue
            pass
            
            if last_year-first_year==1 :
                valeur=0
                for years in range (first_year, last_year+1):
                    instant=hour_pivot.loc[(hour_pivot.index==code),[years]]
                    instant=float(instant.to_string(index=False, header=False))
                    valeur=valeur+instant
                valeur= valeur // 2
                
                
                for years in range (year_begin,first_year):
                    if hour_pivot.loc[(hour_pivot.index==code),[years]].isnull().values.all():
                        hour_pivot.loc[(hour_pivot.index==code),[years]]=valeur

                for years in range (last_year,year_end+1):
                    if hour_pivot.loc[(hour_pivot.index==code),[years]].isnull().values.all():
                        hour_pivot.loc[(hour_pivot.index==code),[years]]=valeur
                
                continue
            
            pass
        
            if (last_year-first_year>=2) : 
                # print(code)
                known_values = (last_year-first_year)+1
                first_values = list(i for i in range(1,known_values+1))
                last_values = list(i for i in range(known_values+1,2*known_values+1))
                # print(known_values, first_values, last_values)
                for years in range(first_year-1,year_begin-1,-1):
                    for num in first_values:
                        # print(num, first_year-1, year_begin-1)
                        value_num= hour_pivot.loc[(hour_pivot.index==code),[years+num]]
                        value_num=float(value_num.to_string(index=False, header=False))
                        first_consecutive_values[(num)]=value_num  
                    numbers1 = [first_consecutive_values[key] for key in first_consecutive_values]
                    average = statistics.mean(numbers1)
                    #if average> minimum  :
                    hour_pivot.loc[(hour_pivot.index==code),[years]]=average
                first_consecutive_values={}
                known_values = (last_year-year_begin)+1
                
                
                last_values = list(i for i in range(1,known_values+1))
                # print(code, known_values, last_values)
                for years in range(last_year+1,year_end+1):
                    # print(years)
                    for num in last_values:
                        value_num= hour_pivot.loc[(hour_pivot.index==code),[years-num]]
                        value_num=float(value_num.to_string(index=False, header=False))
                        last_consecutive_values[(num)]=value_num 
                            
                            
                    numbers1 = [last_consecutive_values[key] for key in last_consecutive_values]
                    average = statistics.mean(numbers1)
                    # print(average)
                    #if average> minimum:
                    hour_pivot.loc[(hour_pivot.index==code),[years]]=average
                last_consecutive_values={}             
                
                continue
            pass   
                
            
        test = hour_pivot.copy()

        reg[code]=hour_pivot.copy()
        return test
    
    results = [ray.get([regression_ray.remote(code_country, hour_pivot2) for code_country in hour_pivot2.index.get_level_values(0).unique()])]
    #results = [ray.get([regression_ray.remote(code_country, hour_pivot2) for code_country in ['ABW']])]
    #results = [ray.get([regression_ray.remote(code_country, hour_pivot2) for code_country in hour_pivot2.index.get_level_values(0).unique()])]
    for a in results[0] :
        hour_pivot3 = pd.concat([hour_pivot3,a])

    
    ray.shutdown()
    
    table_of_interest = hour_pivot3.copy()
    
    
    return table_of_interest 
