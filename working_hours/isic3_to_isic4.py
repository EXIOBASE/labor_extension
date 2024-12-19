import pandas as pd
import string

def correspondance_isic(isic3):
    
    isic4_from_isic3_data=pd.DataFrame(data=None,columns=['ref_area','sex','classif1','time','obs_value'])
    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}
    
    
    '''
    Here we transforme the ISIC3 categories to ISIC4 categories
    Coefficients given by Etienne
    '''
    
    for code in isic3.ref_area.unique():
        for year in range(1995,2023):
            for sex in isic3.sex.unique():
                for classif in isic3.classif1.unique():
    
                    for letter in alphabet_list :
                        if classif == 'ECO_ISIC3_'+str(letter):
                            if not isic3.loc[(isic3['ref_area']==code)&(isic3['sex']==sex)&(isic3['time']==year)&(isic3['classif1']=='ECO_ISIC3_'+str(letter)),['obs_value']].isnull().values.all(): 
                                value =  float(isic3.loc[(isic3['ref_area']==code)&(isic3['sex']==sex)&(isic3['time']==year)&(isic3['classif1']==classif),['obs_value']].to_string(index=False, header=False))
                                var_holder['eco_isic3_' + str(letter.lower())] = value
                                break
                            else:
                                var_holder['eco_isic3_' + str(letter.lower())] = 0
                                break
                            
                
                '''For ECO ISIC A, we use the value from Eurostat'''
                print(code, sex, classif, year)
    
                if not (var_holder['eco_isic3_a'] == 0 and var_holder['eco_isic3_b'] ==0):
                    # print(year, code)
                    eco_isic4_a= var_holder['eco_isic3_a'] + var_holder['eco_isic3_b']
                    
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_A', 'time' : year, 'obs_value' :eco_isic4_a}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True) 
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_A',year,eco_isic4_a], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
     
            
                
                if not (var_holder['eco_isic3_c'] == 0):
                    # print(year, code)
                    eco_isic4_b= var_holder['eco_isic3_c']
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_B', 'time' : year, 'obs_value' :eco_isic4_b}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True) 
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_B',year,eco_isic4_b], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
                    
                if not (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0):
                    # print(year, code)
                    eco_isic4_c= var_holder['eco_isic3_d'] + 0.05 * var_holder['eco_isic3_f'] + 0.018 * var_holder['eco_isic3_g'] + 0.029 * var_holder['eco_isic3_i'] + 0.014 * var_holder['eco_isic3_k']
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)                     
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_C',year,eco_isic4_c], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
                    
                if not (var_holder['eco_isic3_e'] == 0):
                    # print(year, code)
                    eco_isic4_d= 0.75 * var_holder['eco_isic3_e']
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_D', 'time' : year, 'obs_value' :eco_isic4_d}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)   
                    
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_D',year,eco_isic4_d], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
    
                if not (var_holder['eco_isic3_e'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_o'] ==0):
                    # print(year, code)
                    eco_isic4_e= 0.25 * var_holder['eco_isic3_e'] + 0.05 * var_holder['eco_isic3_f'] + 0.113 * var_holder['eco_isic3_o']
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_E',year,eco_isic4_e], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_E', 'time' : year, 'obs_value' :eco_isic4_e}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)   
                    
                if not (var_holder['eco_isic3_f'] == 0 and var_holder['eco_isic3_k'] ==0):
                    # print(year, code)
                    eco_isic4_f= 0.85 * var_holder['eco_isic3_f'] + 0.014 * var_holder['eco_isic3_k']
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_F', 'time' : year, 'obs_value' :eco_isic4_f}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)  
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_F',year,eco_isic4_f], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
    
                if not (var_holder['eco_isic3_g'] == 0):
                    # print(year, code)
                    eco_isic4_g= 0.836 * var_holder['eco_isic3_g']
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_G', 'time' : year, 'obs_value' :eco_isic4_g}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)  
                    
                    
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_G',year,eco_isic4_g], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
    
                if not (var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_o'] ==0):
                    # print(year, code)
                    eco_isic4_h= 0.018 * var_holder['eco_isic3_g'] + 0.706 * var_holder['eco_isic3_i'] + 0.019 * var_holder['eco_isic3_o']
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_H', 'time' : year, 'obs_value' :eco_isic4_h}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)  
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_H',year,eco_isic4_h], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
    
                if not (var_holder['eco_isic3_h'] == 0):
                    # print(year, code)
                    eco_isic4_i=  var_holder['eco_isic3_h']
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_I', 'time' : year, 'obs_value' :eco_isic4_i}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True) 
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_I',year,eco_isic4_i], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
    
                if not (var_holder['eco_isic3_i'] == 0 and var_holder['eco_isic3_k'] ==0 and var_holder['eco_isic3_o'] ==0):
                    # print(year, code)
                    eco_isic4_j= 0.088 * var_holder['eco_isic3_i'] + 0.233 * var_holder['eco_isic3_k'] + 0.208 * var_holder['eco_isic3_o']
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_J', 'time' : year, 'obs_value' :eco_isic4_j}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True) 
                    
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_J',year,eco_isic4_j], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
    
                if not (var_holder['eco_isic3_i'] == 0 and var_holder['eco_isic3_j'] ==0):
                    # print(year, code)
                    eco_isic4_k= 0.029 * var_holder['eco_isic3_i'] + 0.926 * var_holder['eco_isic3_j']
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_K', 'time' : year, 'obs_value' :eco_isic4_k}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True) 
                    
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_K',year,eco_isic4_k], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
    
                if not (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] ==0):
                    # print(year, code)
                    eco_isic4_l= 0.027 * var_holder['eco_isic3_k'] + 0.143 * var_holder['eco_isic3_l']
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_L', 'time' : year, 'obs_value' :eco_isic4_l}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True) 
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_L',year,eco_isic4_l], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
    
                if not (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] ==0):
                    # print(year, code)
                    eco_isic4_m= 0.26 * var_holder['eco_isic3_k'] + 0.071 * var_holder['eco_isic3_l'] + 0.077 * var_holder['eco_isic3_n'] + 0.038 * var_holder['eco_isic3_o'] 
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True) 
                    
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_M',year,eco_isic4_m], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
    
                if not (var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_k'] ==0 and var_holder['eco_isic3_l'] == 0 and var_holder['eco_isic3_o'] == 0):
                    # print(year, code)
                    eco_isic4_n= 0.018 * var_holder['eco_isic3_g'] + 0.147 * var_holder['eco_isic3_i'] + 0.037 * var_holder['eco_isic3_j'] + 0.384 * var_holder['eco_isic3_k'] + 0.071 * var_holder['eco_isic3_l']+ 0.094 * var_holder['eco_isic3_o']
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)                     
                    
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_N',year,eco_isic4_n], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
    
                if not (var_holder['eco_isic3_l'] == 0):
                    # print(year, code)
                    eco_isic4_o=  0.571 * var_holder['eco_isic3_l']
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_O', 'time' : year, 'obs_value' :eco_isic4_o}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)                       
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_O',year,eco_isic4_o], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
    
                if not (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_m'] ==0 and var_holder['eco_isic3_n'] ==0 and var_holder['eco_isic3_o'] ==0):
                    # print(year, code)
                    
                    eco_isic4_p= 0.027 * var_holder['eco_isic3_k'] + var_holder['eco_isic3_m'] + 0.077 * var_holder['eco_isic3_n'] + 0.075 * var_holder['eco_isic3_o']
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)                       
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_P',year,eco_isic4_p], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
    
                if not (var_holder['eco_isic3_l'] == 0 and var_holder['eco_isic3_n'] ==0):
                    # print(year, code)
                    
                    eco_isic4_q= 0.071 * var_holder['eco_isic3_l'] + 0.846 * var_holder['eco_isic3_n']
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_Q', 'time' : year, 'obs_value' :eco_isic4_q}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)                      
                    
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_Q',year,eco_isic4_q], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
                
                if not (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_o'] ==0):
                    # print(year, code)
                    eco_isic4_r= 0.014 * var_holder['eco_isic3_k'] + 0.071 * var_holder['eco_isic3_l'] + 0.264 * var_holder['eco_isic3_o']
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_R', 'time' : year, 'obs_value' :eco_isic4_r}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)                    
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_R',year,eco_isic4_r], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
    
                if not (var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_j'] ==0 and var_holder['eco_isic3_k'] ==0 and var_holder['eco_isic3_o'] ==0):
                    # print(year, code)
                    eco_isic4_s= 0.109 * var_holder['eco_isic3_g'] + 0.037 * var_holder['eco_isic3_j'] + 0.014 * var_holder['eco_isic3_k'] + 0.189 * var_holder['eco_isic3_o']
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)   
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_S',year,eco_isic4_s], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
    
                if not (var_holder['eco_isic3_p'] == 0):
                    # print(year, code)
                    eco_isic4_t=  var_holder['eco_isic3_p']
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_T', 'time' : year, 'obs_value' :eco_isic4_t}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)  
                    
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_T',year,eco_isic4_t], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
    
                if not (var_holder['eco_isic3_f'] == 0 and var_holder['eco_isic3_k'] ==0 and var_holder['eco_isic3_q'] ==0):
                    # print(year, code)
                    eco_isic4_u= 0.05 * var_holder['eco_isic3_f'] + 0.014 * var_holder['eco_isic3_k'] +  var_holder['eco_isic3_q']
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_U', 'time' : year, 'obs_value' :eco_isic4_u}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)  
                    
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_U',year,eco_isic4_u], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
    
                if not (var_holder['eco_isic3_x'] == 0):
                    # print(year, code)
                    eco_isic4_x=  var_holder['eco_isic3_x']
                    new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_X', 'time' : year, 'obs_value' :eco_isic4_x}

                    isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                    isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)  
                    # isic4_from_isic3_data=isic4_from_isic3_data.append(pd.Series([code,sex,'ECO_ISIC4_X',year,eco_isic4_x], index=[i for i in isic4_from_isic3_data]),ignore_index=True)
     
    return isic4_from_isic3_data