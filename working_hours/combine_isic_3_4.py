
import pandas as pd
#from string import digits
import os
import ray

runtime_env = {
    'env_vars': {
        "RAY_memory_monitor_refresh_ms": "0",
        "RAY_record_ref_creation_sites":"1",
        "RAY_verbose_spill_logs":"0"

     }
}

def combine(hour_list,isic4_from_isic3_data,new_table_150222,new_table_150222_columns,isic4): 
    table = pd.DataFrame(columns = new_table_150222_columns)
    combine = {}
    ray.init(runtime_env=runtime_env,num_cpus = os.cpu_count()-4)   
    @ray.remote
   

    
    def combine_ray(code,table):
    	     
    #for code in hour_list.ref_area.unique():
        print(code)
        new_table_150222 = table.copy()        
        for sex in hour_list.sex.unique():
            for classi in hour_list.classif1.unique():
                for year in hour_list.time.unique():

                    if (year<2009):#mapping ISIC4

                    	if not isic4_from_isic3_data.loc[(isic4_from_isic3_data['ref_area']==code)&(isic4_from_isic3_data['sex']==sex)&(isic4_from_isic3_data['classif1']==classi)&(isic4_from_isic3_data['time']==year),['obs_value']].isnull().values.all():
                    		
                    	
                        

                            	value=isic4_from_isic3_data.loc[(isic4_from_isic3_data['ref_area']==code)&(isic4_from_isic3_data['sex']==sex)&(isic4_from_isic3_data['classif1']==classi)&(isic4_from_isic3_data['time']==year),['obs_value']]
                            	value = float(value.to_string(index=False, header=False))
                            	new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : classi, 'time' : year, 'obs_value' :value,'source' : 3}
                            
                            	new_table_150222.loc[len(new_table_150222)] = new_line
                            	#new_table_150222 = new_table_150222.reset_index(drop=True)


                            	# new_table_150222=new_table_150222.append(pd.Series([code,sex,classi.translate({ord(k): None for k in digits}),year,value,3], index=[i for i in new_table_150222_columns]),ignore_index=True)



                    else :
                        if (year>=2009): #1ere etape
                        


                            if not isic4.loc[(isic4['ref_area']==code)&(isic4['sex']==sex)&(isic4['classif1']==classi)&(isic4['time']==year),['obs_value']].isnull().values.all():

                                #print('2',year,isic4.loc[(isic4['ref_area']==code)&(isic4['sex']==sex)&(isic4['classif1']==classi)&(isic4['time']==year),['obs_value']])

                                value=isic4.loc[(isic4['ref_area']==code)&(isic4['sex']==sex)&(isic4['classif1']==classi)&(isic4['time']==year),['obs_value']]
                                value = float(value.to_string(index=False, header=False))
                                new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : classi, 'time' : year, 'obs_value' :value,'source':4}

                                new_table_150222.loc[len(new_table_150222)] = new_line
                                #new_table_150222 = new_table_150222.reset_index(drop=True)
                                #new_table_280121=new_table_280121.append(pd.Series([code,sex,classi.translate({ord(k): None for k in digits}),year,value,4], index=[i for i in new_table_280121_columns]),ignore_index=True)
                                # new_table_150222=new_table_150222.append(pd.Series([code,sex,classi.translate({ord(k): None for k in digits}),year,value,4], index=[i for i in new_table_150222_columns]),ignore_index=True)
                            else :
                                if not isic4_from_isic3_data.loc[(isic4_from_isic3_data['ref_area']==code)&(isic4_from_isic3_data['sex']==sex)&(isic4_from_isic3_data['classif1']==classi)&(isic4_from_isic3_data['time']==year),['obs_value']].isnull().values.all():
                                  value=isic4_from_isic3_data.loc[(isic4_from_isic3_data['ref_area']==code)&(isic4_from_isic3_data['sex']==sex)&(isic4_from_isic3_data['classif1']==classi)&(isic4_from_isic3_data['time']==year),['obs_value']]
                                  value = float(value.to_string(index=False, header=False))
                                  new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : classi, 'time' : year, 'obs_value' :value,'source' : 3}

                                  new_table_150222.loc[len(new_table_150222)] = new_line
                                  #new_table_150222 = new_table_150222.reset_index(drop=True)

        test = new_table_150222.copy()
        combine[code]=new_table_150222.copy()
        return test
    results = [ray.get([combine_ray.remote(code, table) for code in hour_list.ref_area.unique()])]
    new_table_150222 = pd.DataFrame(columns = new_table_150222_columns)
    for a,b in zip(results[0],hour_list.ref_area.unique()) :

    	print(b,a)
    	combine[b] = a
    	new_table_150222 = pd.concat([new_table_150222,combine[b]])
    new_table_150222 = new_table_150222.reset_index(drop=True)


    ray.shutdown()
                                 

    return new_table_150222
