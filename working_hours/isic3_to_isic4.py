import pandas as pd
import string
import concurrent.futures

def task_A(isic4_from_isic3_A,isic3,workforce):
    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}


    print("Starting with ISIC A")
    for code in isic3.ref_area.unique():
    #for code in ['ALB']:
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            #print(code)
            for year in range(1995,2023):
                #print(year)
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
                    if (year ==2022 and code =='UKR'):
                        pop_A = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_A'),'obs_value'].to_string(header = False, index=False))
                        pop_B = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_B'),'obs_value'].to_string(header = False, index=False))
                    else :
                        pop_A = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_A'),'obs_value'].to_string(header = False, index=False))
                        pop_B = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_B'),'obs_value'].to_string(header = False, index=False))
                       
                    if  (var_holder['eco_isic3_a'] != 0 and var_holder['eco_isic3_b'] !=0):
                        eco_isic4_a= ((pop_A * var_holder['eco_isic3_a']) +( pop_B * var_holder['eco_isic3_b'])) / (pop_A + pop_B )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_A', 'time' : year, 'obs_value' :eco_isic4_a}
                        new = pd.DataFrame([new_line])
                        
                        if isic4_from_isic3_A.empty :
                            isic4_from_isic3_A = new.copy()
                        else :
                            isic4_from_isic3_A= pd.concat([isic4_from_isic3_A,new])
                      

                    if (var_holder['eco_isic3_a'] == 0 and var_holder['eco_isic3_b']!=0) :
                        eco_isic4_a=  var_holder['eco_isic3_b']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_A', 'time' : year, 'obs_value' :eco_isic4_a}

                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_A.empty :
                            isic4_from_isic3_A = new.copy()
                        else :
                            isic4_from_isic3_A= pd.concat([isic4_from_isic3_A,new])

                    if (var_holder['eco_isic3_b'] == 0 and var_holder['eco_isic3_a']!=0) :
                        eco_isic4_a=  var_holder['eco_isic3_a']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_A', 'time' : year, 'obs_value' :eco_isic4_a}
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_A.empty :
                            isic4_from_isic3_A = new.copy()
                        else :
                            isic4_from_isic3_A= pd.concat([isic4_from_isic3_A,new])
    

    print("task_A finished")
    isic4_from_isic3_A = isic4_from_isic3_A.reset_index(drop=True)

    return isic4_from_isic3_A
 
    


    #ISIC4 B

def task_B(isic4_from_isic3_B,isic3,workforce):
    #isic4_from_isic3_A = isic4_from_isic3_data.iloc[0:0]
    #workforce = pd.read_csv(final_path/'workforce.csv')
    #isic3=pd.read_csv('isic3.csv')
    #isic4_from_isic3_A=pd.DataFrame(data=None,columns=['ref_area','sex','classif1','time','obs_value'])
    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}


    print("Starting with ISIC B")

    for code in isic3.ref_area.unique():
    #for code in ['ALB']:
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            #print(code)
            for year in range(1995,2023):
                #print(year)
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



                    if  (var_holder['eco_isic3_c'] != 0 ):
                        eco_isic4_b= var_holder['eco_isic3_c']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_B', 'time' : year, 'obs_value' :eco_isic4_b}
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_B.empty :
                            isic4_from_isic3_B = new.copy()
                        else :
                            isic4_from_isic3_B= pd.concat([isic4_from_isic3_B,new])

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
    print("task_B finished")
    isic4_from_isic3_B = isic4_from_isic3_B.reset_index(drop=True)
        
    return isic4_from_isic3_B

def task_C(isic4_from_isic3_C,isic3,workforce):

    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}


    print("Starting with ISIC C")
                   
    


    #ISIC4 C
    #rien de nulle
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            #print(code)
            for year in range(1995,2023):
                #print(year)
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
                    if (year ==2022 and code =='UKR'):
                        pop_D = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_DE'),'obs_value'].to_string(header = False, index=False))
                        pop_F = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_F'),'obs_value'].to_string(header = False, index=False))
                        pop_G = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_G'),'obs_value'].to_string(header = False, index=False))
                        pop_I = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_I'),'obs_value'].to_string(header = False, index=False))
                        pop_K = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))
                    else :
                        pop_D = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_DE'),'obs_value'].to_string(header = False, index=False))
                        pop_F = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_F'),'obs_value'].to_string(header = False, index=False))
                        pop_G = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_G'),'obs_value'].to_string(header = False, index=False))
                        pop_I = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_I'),'obs_value'].to_string(header = False, index=False))
                        pop_K = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))


                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.05 *  pop_F * var_holder['eco_isic3_f']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.029 *  pop_I * var_holder['eco_isic3_i'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / (pop_D + 0.05 *  pop_F + 0.018 *  pop_G + 0.029 *  pop_I +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])



                        #un de nulle
                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((0.05 *  pop_F * var_holder['eco_isic3_f']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.029 *  pop_I * var_holder['eco_isic3_i'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.05 *  pop_F + 0.018 *  pop_G + 0.029 *  pop_I +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])


                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.029 *  pop_I * var_holder['eco_isic3_i'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / (pop_D  + 0.018 *  pop_G + 0.029 *  pop_I +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])

                    
                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.05 *  pop_F * var_holder['eco_isic3_f']) +(0.029 *  pop_I * var_holder['eco_isic3_i'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / (pop_D + 0.05 *  pop_F  + 0.029 *  pop_I +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0):
                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.05 *  pop_F * var_holder['eco_isic3_f']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / (pop_D + 0.05 *  pop_F + 0.018 *  pop_G  +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])


                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0):
    
                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.05 *  pop_F * var_holder['eco_isic3_f']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.029 *  pop_I * var_holder['eco_isic3_i'])) / (pop_D + 0.05 *  pop_F + 0.018 *  pop_G + 0.029 *  pop_I)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])


                    #2 de nulle

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0):
    
                        eco_isic4_c= ((0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.029 *  pop_I * var_holder['eco_isic3_i'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.018 *  pop_G + 0.029 *  pop_I +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])


                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((0.05 *  pop_F * var_holder['eco_isic3_f']) +(0.029 *  pop_I * var_holder['eco_isic3_i'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.05 *  pop_F  + 0.029 *  pop_I +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((0.05 *  pop_F * var_holder['eco_isic3_f']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.05 *  pop_F + 0.018 *  pop_G +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])


                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= ((0.05 *  pop_F * var_holder['eco_isic3_f']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.029 *  pop_I * var_holder['eco_isic3_i'])) / ( 0.05 *  pop_F + 0.018 *  pop_G + 0.029 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])


                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.029 *  pop_I * var_holder['eco_isic3_i'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / (pop_D  + 0.029 *  pop_I +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / (pop_D + 0.018 *  pop_G  +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])


                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.029 *  pop_I * var_holder['eco_isic3_i'])) / (pop_D  + 0.018 *  pop_G + 0.029 *  pop_I)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.05 *  pop_F * var_holder['eco_isic3_f'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / (pop_D + 0.05 *  pop_F  +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.05 *  pop_F * var_holder['eco_isic3_f']) +(0.029 *  pop_I * var_holder['eco_isic3_i'])) / (pop_D + 0.05 *  pop_F  + 0.029 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0):
                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.05 *  pop_F * var_holder['eco_isic3_f']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])) / (pop_D + 0.05 *  pop_F + 0.018 *  pop_G )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])

                    # 3 de nulle

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.05 *  pop_F * var_holder['eco_isic3_f'])) / (pop_D + 0.05 *  pop_F )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])) / (pop_D  + 0.018 *  pop_G )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.029 *  pop_I * var_holder['eco_isic3_i'])) / (pop_D   + 0.029 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])


                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.014 *  pop_K * var_holder['eco_isic3_k'])) / (pop_D + 0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0):
    
                        eco_isic4_c= ((0.05 *  pop_F * var_holder['eco_isic3_f']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])) / ( 0.05 *  pop_F + 0.018 *  pop_G )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= ((0.05 *  pop_F * var_holder['eco_isic3_f']) +(0.029 *  pop_I * var_holder['eco_isic3_i'])) / ( 0.05 *  pop_F  + 0.029 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((0.05 *  pop_F * var_holder['eco_isic3_f']) +(0.014 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.05 *  pop_F   +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])


                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= ( (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.029 *  pop_I * var_holder['eco_isic3_i'])) / ( 0.018 *  pop_G + 0.029 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])
                    
                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ( (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.018 *  pop_G  +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((0.029 *  pop_I * var_holder['eco_isic3_i'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.029 *  pop_I +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])

                    # 4 de nulle
                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= var_holder['eco_isic3_d']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= var_holder['eco_isic3_f']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])


                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= var_holder['eco_isic3_g']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= var_holder['eco_isic3_i']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)   
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_C.empty :
                            isic4_from_isic3_C = new.copy()
                        else :
                            isic4_from_isic3_C= pd.concat([isic4_from_isic3_C,new])


    print("task_C finished")
    isic4_from_isic3_C = isic4_from_isic3_C.reset_index(drop=True)

    return isic4_from_isic3_C

def task_D(isic4_from_isic3_D,isic3,workforce):

    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}


    print("Starting with ISIC D")



    #ISIC4 D
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            #print(code)
            for year in range(1995,2023):
                #print(year)
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


                    if (var_holder['eco_isic3_e'] != 0):
                         
                        eco_isic4_d=  var_holder['eco_isic3_e']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_D', 'time' : year, 'obs_value' :eco_isic4_d}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)   
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_D.empty :
                            isic4_from_isic3_D = new.copy()
                        else :
                            isic4_from_isic3_D= pd.concat([isic4_from_isic3_D,new])

    print("task_D finished")
    isic4_from_isic3_D = isic4_from_isic3_D.reset_index(drop=True)

    return isic4_from_isic3_D

def task_E(isic4_from_isic3_E,isic3,workforce):

    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}


    print("Starting with ISIC E")
                        
    #ISIC4 E
    #rien de nulle
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            #print(code)
            for year in range(1995,2023):
                #print(year)
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
                    if (year ==2022 and code =='UKR'):
                        pop_E = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_DE'),'obs_value'].to_string(header = False, index=False))
                        pop_F = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_F'),'obs_value'].to_string(header = False, index=False))
                        pop_O = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_O'),'obs_value'].to_string(header = False, index=False))

                    else :
                        pop_E = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_DE'),'obs_value'].to_string(header = False, index=False))
                        pop_F = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_F'),'obs_value'].to_string(header = False, index=False))
                        pop_O = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_O'),'obs_value'].to_string(header = False, index=False))





                    # rien de nulle
                    if (var_holder['eco_isic3_e'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_e= ((0.25 * pop_E * var_holder['eco_isic3_e']) +(0.05 *  pop_F * var_holder['eco_isic3_f']) + (0.113 *  pop_O * var_holder['eco_isic3_o'])) / (0.25 * pop_E + 0.05 *  pop_F + 0.113 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_E', 'time' : year, 'obs_value' :eco_isic4_e}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_E.empty :
                            isic4_from_isic3_E = new.copy()
                        else :
                            isic4_from_isic3_E= pd.concat([isic4_from_isic3_E,new])



                    # 1 de nulle
                    if (var_holder['eco_isic3_e'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_o'] != 0 ):
    
                        eco_isic4_e= ((0.05 *  pop_F * var_holder['eco_isic3_f']) + (0.113 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.05 *  pop_F + 0.113 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_E', 'time' : year, 'obs_value' :eco_isic4_e}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_E.empty :
                            isic4_from_isic3_E = new.copy()
                        else :
                            isic4_from_isic3_E= pd.concat([isic4_from_isic3_E,new])



                    if (var_holder['eco_isic3_e'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_e= ((0.25 * pop_E * var_holder['eco_isic3_e']) + (0.113 *  pop_O * var_holder['eco_isic3_o'])) / (0.25 * pop_E  + 0.113 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_E', 'time' : year, 'obs_value' :eco_isic4_e}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_E.empty :
                            isic4_from_isic3_E = new.copy()
                        else :
                            isic4_from_isic3_E= pd.concat([isic4_from_isic3_E,new])


                    if (var_holder['eco_isic3_e'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_e= ((0.25 * pop_E * var_holder['eco_isic3_e']) +(0.05 *  pop_F * var_holder['eco_isic3_f']) ) / (0.25 * pop_E + 0.05 *  pop_F )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_E', 'time' : year, 'obs_value' :eco_isic4_e}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)    
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_E.empty :
                            isic4_from_isic3_E = new.copy()
                        else :
                            isic4_from_isic3_E= pd.concat([isic4_from_isic3_E,new])

                    # 2 de nulle

                    if (var_holder['eco_isic3_e'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_e=  var_holder['eco_isic3_e']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_E', 'time' : year, 'obs_value' :eco_isic4_e}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_E.empty :
                            isic4_from_isic3_E = new.copy()
                        else :
                            isic4_from_isic3_E= pd.concat([isic4_from_isic3_E,new])

                    if (var_holder['eco_isic3_e'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_e=  var_holder['eco_isic3_f']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_E', 'time' : year, 'obs_value' :eco_isic4_e}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_E.empty :
                            isic4_from_isic3_E = new.copy()
                        else :
                            isic4_from_isic3_E= pd.concat([isic4_from_isic3_E,new])


                    if (var_holder['eco_isic3_e'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_e=  var_holder['eco_isic3_o']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_E', 'time' : year, 'obs_value' :eco_isic4_e}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_E.empty :
                            isic4_from_isic3_E = new.copy()
                        else :
                            isic4_from_isic3_E= pd.concat([isic4_from_isic3_E,new])

    print("task_E finished")
    isic4_from_isic3_E = isic4_from_isic3_E.reset_index(drop=True)

    return isic4_from_isic3_E






def task_F(isic4_from_isic3_F,isic3,workforce):

    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}


    print("Starting with ISIC F")

    #ISIC4 F
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            #print(code)
            for year in range(1995,2023):
                #print(year)
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
                    if (year ==2022 and code =='UKR'):
                        pop_F = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_F'),'obs_value'].to_string(header = False, index=False))
                        pop_K = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))
                    else :
                        pop_F = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_F'),'obs_value'].to_string(header = False, index=False))
                        pop_K = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))

                    #print(pop_F,pop_K,var_holder['eco_isic3_f'],var_holder['eco_isic3_k'])
                    if  (var_holder['eco_isic3_f'] != 0 and var_holder['eco_isic3_k'] !=0):
                        eco_isic4_f= ((0.85 * pop_F * var_holder['eco_isic3_f']) +( 0.014* pop_K * var_holder['eco_isic3_k'])) / (0.85*pop_F +0.014 * pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_F', 'time' : year, 'obs_value' :eco_isic4_f}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_F.empty :
                            isic4_from_isic3_F = new.copy()
                        else :
                            isic4_from_isic3_F= pd.concat([isic4_from_isic3_F,new])


                    if (var_holder['eco_isic3_f'] == 0 and var_holder['eco_isic3_k']!=0) :
                        eco_isic4_f=  var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_F', 'time' : year, 'obs_value' :eco_isic4_f}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_F.empty :
                            isic4_from_isic3_F = new.copy()
                        else :
                            isic4_from_isic3_F= pd.concat([isic4_from_isic3_F,new])

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_f']!=0) :
                        eco_isic4_f=  var_holder['eco_isic3_f']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_F', 'time' : year, 'obs_value' :eco_isic4_f}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_F.empty :
                            isic4_from_isic3_F = new.copy()
                        else :
                            isic4_from_isic3_F= pd.concat([isic4_from_isic3_F,new])


    print("task_F finished")
    isic4_from_isic3_F = isic4_from_isic3_F.reset_index(drop=True)

    return isic4_from_isic3_F

def task_G(isic4_from_isic3_G,isic3,workforce):

    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}

    print("Starting with ISIC G")


    #ISIC4 G
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            #print(code)
            for year in range(1995,2023):
                #print(year)
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


    
                    if (var_holder['eco_isic3_g'] != 0):
                        # print(year, code)
                        eco_isic4_g= var_holder['eco_isic3_g']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_G', 'time' : year, 'obs_value' :eco_isic4_g}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)  
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_G.empty :
                            isic4_from_isic3_G = new.copy()
                        else :
                            isic4_from_isic3_G= pd.concat([isic4_from_isic3_G,new])
                    
    print("task_G finished")
    isic4_from_isic3_G = isic4_from_isic3_G.reset_index(drop=True)
    return isic4_from_isic3_G

def task_H(isic4_from_isic3_H,isic3,workforce):

    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}

    print("Starting with ISIC H")

    #ISIC4 H
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            #print(code)
            for year in range(1995,2023):
                #print(year)
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
                    if (year ==2022 and code =='UKR'):
                        pop_G = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_G'),'obs_value'].to_string(header = False, index=False))
                        pop_I = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_I'),'obs_value'].to_string(header = False, index=False))
                        pop_O = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_O'),'obs_value'].to_string(header = False, index=False))

                    else :
                        pop_G = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_G'),'obs_value'].to_string(header = False, index=False))
                        pop_I = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_I'),'obs_value'].to_string(header = False, index=False))
                        pop_O = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_O'),'obs_value'].to_string(header = False, index=False))





                    # rien de nulle
                    if (var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_h= ((0.018 * pop_G * var_holder['eco_isic3_g']) +(0.706 *  pop_I * var_holder['eco_isic3_i']) + (0.019 *  pop_O * var_holder['eco_isic3_o'])) / (0.018 * pop_G + 0.706 *  pop_I + 0.019 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_H', 'time' : year, 'obs_value' :eco_isic4_h}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_H.empty :
                            isic4_from_isic3_H = new.copy()
                        else :
                            isic4_from_isic3_H= pd.concat([isic4_from_isic3_H,new])

                    # 1 de nulle
                    if (var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_h= ((0.706 *  pop_I * var_holder['eco_isic3_i']) + (0.019 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.706 *  pop_I + 0.019 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_H', 'time' : year, 'obs_value' :eco_isic4_h}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_H.empty :
                            isic4_from_isic3_H = new.copy()
                        else :
                            isic4_from_isic3_H= pd.concat([isic4_from_isic3_H,new])


                    if (var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_h= ((0.018 * pop_G * var_holder['eco_isic3_g']) + (0.019 *  pop_O * var_holder['eco_isic3_o'])) / (0.018 * pop_G  + 0.019 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_H', 'time' : year, 'obs_value' :eco_isic4_h}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_H.empty :
                            isic4_from_isic3_H = new.copy()
                        else :
                            isic4_from_isic3_H= pd.concat([isic4_from_isic3_H,new])


                    if (var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_h= ((0.018 * pop_G * var_holder['eco_isic3_g']) +(0.706 *  pop_I * var_holder['eco_isic3_i']) ) / (0.018 * pop_G + 0.706 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_H', 'time' : year, 'obs_value' :eco_isic4_h}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_H.empty :
                            isic4_from_isic3_H = new.copy()
                        else :
                            isic4_from_isic3_H= pd.concat([isic4_from_isic3_H,new])


                    # 2 de nulle

                    if (var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_h=  var_holder['eco_isic3_g']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_H', 'time' : year, 'obs_value' :eco_isic4_h}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_H.empty :
                            isic4_from_isic3_H = new.copy()
                        else :
                            isic4_from_isic3_H= pd.concat([isic4_from_isic3_H,new])

                    if (var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_o'] == 0 ):
    
                        eco_isic4_h=  var_holder['eco_isic3_i']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_H', 'time' : year, 'obs_value' :eco_isic4_h}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_H.empty :
                            isic4_from_isic3_H = new.copy()
                        else :
                            isic4_from_isic3_H= pd.concat([isic4_from_isic3_H,new])


                    if (var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_h=  var_holder['eco_isic3_o']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_H', 'time' : year, 'obs_value' :eco_isic4_h}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_H.empty :
                            isic4_from_isic3_H = new.copy()
                        else :
                            isic4_from_isic3_H= pd.concat([isic4_from_isic3_H,new])

    isic4_from_isic3_H = isic4_from_isic3_H.reset_index(drop=True)

    print("task_H finished")
    return isic4_from_isic3_H

def task_I(isic4_from_isic3_I,isic3,workforce):

    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}

    print("Starting with ISIC I")

    #ISIC4 I

    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            #print(code)
            for year in range(1995,2023):
                #print(year)
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



                    if  (var_holder['eco_isic3_h'] != 0 ):
                        eco_isic4_i= var_holder['eco_isic3_h']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_I', 'time' : year, 'obs_value' :eco_isic4_i}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_I.empty :
                            isic4_from_isic3_I = new.copy()
                        else :
                            isic4_from_isic3_I= pd.concat([isic4_from_isic3_I,new])
    isic4_from_isic3_I = isic4_from_isic3_I.reset_index(drop=True)

    print("task_I finished")
    return isic4_from_isic3_I

def task_J(isic4_from_isic3_J,isic3,workforce): 
    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}

    print("Starting with ISIC J")

    #ISIC4 J

    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            #print(code)
            for year in range(1995,2023):
                #print(year)
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
                    if (year ==2022 and code =='UKR'):
                        pop_K = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))
                        pop_I = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_I'),'obs_value'].to_string(header = False, index=False))
                        pop_O = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_O'),'obs_value'].to_string(header = False, index=False))

                    else :
                        pop_K = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))
                        pop_I = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_I'),'obs_value'].to_string(header = False, index=False))
                        pop_O = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_O'),'obs_value'].to_string(header = False, index=False))





                    # rien de nulle
                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_j= ((0.233 * pop_K * var_holder['eco_isic3_k']) +(0.088 *  pop_I * var_holder['eco_isic3_i']) + (0.208 *  pop_O * var_holder['eco_isic3_o'])) / (0.233 * pop_K + 0.088 *  pop_I + 0.208 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_J', 'time' : year, 'obs_value' :eco_isic4_j}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_J.empty :
                            isic4_from_isic3_J = new.copy()
                        else :
                            isic4_from_isic3_J= pd.concat([isic4_from_isic3_J,new])

                    # 1 de nulle
                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_j= ((0.088 *  pop_I * var_holder['eco_isic3_i']) + (0.208 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.088 *  pop_I + 0.208 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_J', 'time' : year, 'obs_value' :eco_isic4_j}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_J.empty :
                            isic4_from_isic3_J = new.copy()
                        else :
                            isic4_from_isic3_J= pd.concat([isic4_from_isic3_J,new])


                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_j= ((0.233 * pop_K * var_holder['eco_isic3_k']) + (0.208 *  pop_O * var_holder['eco_isic3_o'])) / (0.233 * pop_K  + 0.208 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_J', 'time' : year, 'obs_value' :eco_isic4_j}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_J.empty :
                            isic4_from_isic3_J = new.copy()
                        else :
                            isic4_from_isic3_J= pd.concat([isic4_from_isic3_J,new])



                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_j= ((0.233 * pop_K * var_holder['eco_isic3_k']) +(0.088 *  pop_I * var_holder['eco_isic3_i']) ) / (0.233 * pop_K + 0.088 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_J', 'time' : year, 'obs_value' :eco_isic4_j}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_J.empty :
                            isic4_from_isic3_J = new.copy()
                        else :
                            isic4_from_isic3_J= pd.concat([isic4_from_isic3_J,new])

                    # 2 de nulle

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_o'] == 0 ):
                        eco_isic4_j=  var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_J', 'time' : year, 'obs_value' :eco_isic4_j}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_J.empty :
                            isic4_from_isic3_J = new.copy()
                        else :
                            isic4_from_isic3_J= pd.concat([isic4_from_isic3_J,new])

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_j=  var_holder['eco_isic3_i']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_J', 'time' : year, 'obs_value' :eco_isic4_j}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_J.empty :
                            isic4_from_isic3_J = new.copy()
                        else :
                            isic4_from_isic3_J= pd.concat([isic4_from_isic3_J,new])

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_j=  var_holder['eco_isic3_o']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_J', 'time' : year, 'obs_value' :eco_isic4_j}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_J.empty :
                            isic4_from_isic3_J = new.copy()
                        else :
                            isic4_from_isic3_J= pd.concat([isic4_from_isic3_J,new])

    print("task_J finished")
    isic4_from_isic3_J = isic4_from_isic3_J.reset_index(drop=True)

    return isic4_from_isic3_J

def task_K(isic4_from_isic3_K,isic3,workforce):
    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}

    print("Starting with ISIC K")


    #ISIC4 K
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            #print(code)
            for year in range(1995,2023):
                #print(year)
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
                    if (year ==2022 and code =='UKR'):
                        pop_I = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_I'),'obs_value'].to_string(header = False, index=False))
                        pop_J = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_HJ'),'obs_value'].to_string(header = False, index=False))
                    else :
                        pop_I = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_I'),'obs_value'].to_string(header = False, index=False))
                        pop_J = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_HJ'),'obs_value'].to_string(header = False, index=False))

                    #print(pop_I,pop_J,var_holder['eco_isic3_i'],var_holder['eco_isic3_j'])
                    if  (var_holder['eco_isic3_i'] != 0 and var_holder['eco_isic3_j'] !=0):
                        eco_isic4_k= ((0.029*pop_I * var_holder['eco_isic3_i']) +( 0.926*pop_J * var_holder['eco_isic3_j'])) / (0.029*pop_I + 0.926*pop_J )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_K', 'time' : year, 'obs_value' :eco_isic4_k}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_K.empty :
                            isic4_from_isic3_K = new.copy()
                        else :
                            isic4_from_isic3_K= pd.concat([isic4_from_isic3_K,new])

                    if (var_holder['eco_isic3_i'] == 0 and var_holder['eco_isic3_j']!=0) :
                        eco_isic4_k=  var_holder['eco_isic3_j']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_K', 'time' : year, 'obs_value' :eco_isic4_k}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_K.empty :
                            isic4_from_isic3_K = new.copy()
                        else :
                            isic4_from_isic3_K= pd.concat([isic4_from_isic3_K,new])

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_i']!=0) :
                        eco_isic4_k=  var_holder['eco_isic3_i']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_K', 'time' : year, 'obs_value' :eco_isic4_k}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_K.empty :
                            isic4_from_isic3_K = new.copy()
                        else :
                            isic4_from_isic3_K= pd.concat([isic4_from_isic3_K,new])


    print("task_K finished")
    isic4_from_isic3_K = isic4_from_isic3_K.reset_index(drop=True)

    return isic4_from_isic3_K

def task_L(isic4_from_isic3_L,isic3,workforce):
    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}

    print("Starting with ISIC L")


    #ISIC4 L
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            #print(code)
            for year in range(1995,2023):
                #print(year)
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
                    if (year ==2022 and code =='UKR'):
                        pop_K = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))
                        pop_L = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))
                    else :
                        pop_K = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))
                        pop_L = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))

                    if  (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] !=0):
                        eco_isic4_l= ((0.027*pop_K * var_holder['eco_isic3_k']) +( 0.143*pop_L * var_holder['eco_isic3_l'])) / (0.027*pop_K + 0.143*pop_L )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_L', 'time' : year, 'obs_value' :eco_isic4_l}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_L.empty :
                            isic4_from_isic3_L = new.copy()
                        else :
                            isic4_from_isic3_L= pd.concat([isic4_from_isic3_L,new])

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l']!=0) :
                        eco_isic4_l=  var_holder['eco_isic3_l']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_L', 'time' : year, 'obs_value' :eco_isic4_l}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_L.empty :
                            isic4_from_isic3_L = new.copy()
                        else :
                            isic4_from_isic3_L= pd.concat([isic4_from_isic3_L,new])
                            
                    if (var_holder['eco_isic3_l'] == 0 and var_holder['eco_isic3_k']!=0) :
                        eco_isic4_l=  var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_L', 'time' : year, 'obs_value' :eco_isic4_l}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_L.empty :
                            isic4_from_isic3_L = new.copy()
                        else :
                            isic4_from_isic3_L= pd.concat([isic4_from_isic3_L,new])
    print("task_L finished")
    isic4_from_isic3_L = isic4_from_isic3_L.reset_index(drop=True)

    return isic4_from_isic3_L

def task_M(isic4_from_isic3_M,isic3,workforce):
    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}

    print("Starting with ISIC M")

    #ISIC4 M
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            #print(code)
            for year in range(1995,2023):
                #print(year)
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
                    if (year ==2022 and code =='UKR'):
                        pop_K = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))
                        pop_L = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))
                        pop_N = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))
                        pop_O = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_O'),'obs_value'].to_string(header = False, index=False))
                    else :
                        pop_K = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))
                        pop_L = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))
                        pop_N = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))
                        pop_O = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_O'),'obs_value'].to_string(header = False, index=False))


                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_m= ((0.26*pop_K * var_holder['eco_isic3_k']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.077 *  pop_N * var_holder['eco_isic3_n'])+(0.038 *  pop_O * var_holder['eco_isic3_o'])) / (0.26*pop_K + 0.071 *  pop_L + 0.077 *  pop_N + 0.038 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_M.empty :
                            isic4_from_isic3_M = new.copy()
                        else :
                            isic4_from_isic3_M= pd.concat([isic4_from_isic3_M,new])




                    #un de nulle
                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_m= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.077 *  pop_N * var_holder['eco_isic3_n'])+(0.038 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L + 0.077 *  pop_N + 0.038 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_M.empty :
                            isic4_from_isic3_M = new.copy()
                        else :
                            isic4_from_isic3_M= pd.concat([isic4_from_isic3_M,new])


                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_m= ((0.26*pop_K * var_holder['eco_isic3_k'])  + (0.077 *  pop_N * var_holder['eco_isic3_n'])+(0.038 *  pop_O * var_holder['eco_isic3_o'])) / (0.26*pop_K  + 0.077 *  pop_N + 0.038 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_M.empty :
                            isic4_from_isic3_M = new.copy()
                        else :
                            isic4_from_isic3_M= pd.concat([isic4_from_isic3_M,new])

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_m= ((0.26*pop_K * var_holder['eco_isic3_k']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.038 *  pop_O * var_holder['eco_isic3_o'])) / (0.26*pop_K + 0.071 *  pop_L  + 0.038 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_M.empty :
                            isic4_from_isic3_M = new.copy()
                        else :
                            isic4_from_isic3_M= pd.concat([isic4_from_isic3_M,new])


                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_m= ((0.26*pop_K * var_holder['eco_isic3_k']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.077 *  pop_N * var_holder['eco_isic3_n'])) / (0.26*pop_K + 0.071 *  pop_L + 0.077 *  pop_N  )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_M.empty :
                            isic4_from_isic3_M = new.copy()
                        else :
                            isic4_from_isic3_M= pd.concat([isic4_from_isic3_M,new])





                    # 2 de nulle

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_m= ((0.26*pop_K * var_holder['eco_isic3_k']) +(0.071 *  pop_L * var_holder['eco_isic3_l'])) / (0.26*pop_K + 0.071 *  pop_L )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_M.empty :
                            isic4_from_isic3_M = new.copy()
                        else :
                            isic4_from_isic3_M= pd.concat([isic4_from_isic3_M,new])

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_m= ((0.26*pop_K * var_holder['eco_isic3_k'])  + (0.077 *  pop_N * var_holder['eco_isic3_n'])) / (0.26*pop_K  + 0.077 *  pop_N )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_M.empty :
                            isic4_from_isic3_M = new.copy()
                        else :
                            isic4_from_isic3_M= pd.concat([isic4_from_isic3_M,new])

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_m= ((0.26*pop_K * var_holder['eco_isic3_k']) +(0.038 *  pop_O * var_holder['eco_isic3_o'])) / (0.26*pop_K   + 0.038 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_M.empty :
                            isic4_from_isic3_M = new.copy()
                        else :
                            isic4_from_isic3_M= pd.concat([isic4_from_isic3_M,new])


                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_m= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.077 *  pop_N * var_holder['eco_isic3_n'])) / ( 0.071 *  pop_L + 0.077 *  pop_N )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_M.empty :
                            isic4_from_isic3_M = new.copy()
                        else :
                            isic4_from_isic3_M= pd.concat([isic4_from_isic3_M,new])

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_m= ((0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.038 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L  + 0.038 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_M.empty :
                            isic4_from_isic3_M = new.copy()
                        else :
                            isic4_from_isic3_M= pd.concat([isic4_from_isic3_M,new])



                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_m= ( (0.077 *  pop_N * var_holder['eco_isic3_n'])+(0.038 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.077 *  pop_N + 0.038 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_M.empty :
                            isic4_from_isic3_M = new.copy()
                        else :
                            isic4_from_isic3_M= pd.concat([isic4_from_isic3_M,new])



                    # 3 de nulle
                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_m= var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_M.empty :
                            isic4_from_isic3_M = new.copy()
                        else :
                            isic4_from_isic3_M= pd.concat([isic4_from_isic3_M,new])

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_m= var_holder['eco_isic3_l']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_M.empty :
                            isic4_from_isic3_M = new.copy()
                        else :
                            isic4_from_isic3_M= pd.concat([isic4_from_isic3_M,new])


                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_m= var_holder['eco_isic3_n']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_M.empty :
                            isic4_from_isic3_M = new.copy()
                        else :
                            isic4_from_isic3_M= pd.concat([isic4_from_isic3_M,new])

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_m= var_holder['eco_isic3_o']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_M.empty :
                            isic4_from_isic3_M = new.copy()
                        else :
                            isic4_from_isic3_M= pd.concat([isic4_from_isic3_M,new])
    print("task_M finished")
    isic4_from_isic3_M = isic4_from_isic3_M.reset_index(drop=True)
    
    return isic4_from_isic3_M


def task_N(isic4_from_isic3_N,isic3,workforce):
    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}

    print("Starting with ISIC N")
    

    #ISIC4 N
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            #print(code)
            for year in range(1995,2023):
                #print(year)
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
                    if (year ==2022 and code =='UKR'):
                        pop_J = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_HJ'),'obs_value'].to_string(header = False, index=False))
                        pop_L = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))
                        pop_G = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_G'),'obs_value'].to_string(header = False, index=False))
                        pop_I = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_I'),'obs_value'].to_string(header = False, index=False))
                        pop_K = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))
                        pop_O = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_O'),'obs_value'].to_string(header = False, index=False))

                    else :
                        pop_J = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_HJ'),'obs_value'].to_string(header = False, index=False))
                        pop_L = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))
                        pop_G = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_G'),'obs_value'].to_string(header = False, index=False))
                        pop_I = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_I'),'obs_value'].to_string(header = False, index=False))
                        pop_K = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))
                        pop_O = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_O'),'obs_value'].to_string(header = False, index=False))


                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.071 *  pop_L + 0.018 *  pop_G + 0.147 *  pop_I +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    #un de nulle
                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L + 0.018 *  pop_G + 0.147 *  pop_I +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])



                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J  + 0.018 *  pop_G + 0.147 *  pop_I +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.071 *  pop_L  + 0.147 *  pop_I +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.071 *  pop_L + 0.018 *  pop_G  +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.071 *  pop_L + 0.018 *  pop_G + 0.147 *  pop_I + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])) / (0.037 * pop_J + 0.071 *  pop_L +0.384 *  pop_K+ 0.018 *  pop_G + 0.147 *  pop_I)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    #2 de nulle


                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.071 *  pop_L  +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L  + 0.147 *  pop_I +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.071 *  pop_L  + 0.147 *  pop_I  + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.147 *  pop_I +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / (0.037 * pop_J + 0.071 *  pop_L  + 0.147 *  pop_I +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L + 0.018 *  pop_G  +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.071 *  pop_L + 0.018 *  pop_G  + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J  + 0.018 *  pop_G  +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])
                            
                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / (0.037 * pop_J + 0.071 *  pop_L + 0.018 *  pop_G  +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L + 0.018 *  pop_G + 0.147 *  pop_I  + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ( (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.018 *  pop_G + 0.147 *  pop_I +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.071 *  pop_L + 0.018 *  pop_G + 0.147 *  pop_I +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.018 *  pop_G + 0.147 *  pop_I  + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])) / (0.037 * pop_J + 0.071 *  pop_L + 0.018 *  pop_G + 0.147 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / (0.037 * pop_J  + 0.018 *  pop_G + 0.147 *  pop_I +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])



                    #3 de nulle


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L  +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (  0.147 *  pop_I +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L  + 0.147 *  pop_I  + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / (0.037 * pop_J + 0.147 *  pop_I +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])) / (0.037 * pop_J + 0.071 *  pop_L  + 0.147 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.071 *  pop_L + 0.018 *  pop_G  +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])) / (0.037 * pop_J + 0.071 *  pop_L + 0.018 *  pop_G  )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / (0.037 * pop_J  + 0.018 *  pop_G  +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.384 *  pop_K * var_holder['eco_isic3_k'])) / (0.037 * pop_J + 0.071 *  pop_L   +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])) / ( 0.071 *  pop_L + 0.018 *  pop_G + 0.147 *  pop_I  )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):
                            eco_isic4_n= ( (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.018 *  pop_G + 0.147 *  pop_I +0.384 *  pop_K )
                            new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                            #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                            #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                            new = pd.DataFrame([new_line])
                            if isic4_from_isic3_N.empty :
                                isic4_from_isic3_N = new.copy()
                            else :
                                isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.071 *  pop_L  + 0.147 *  pop_I +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ( (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.018 *  pop_G + 0.147 *  pop_I  + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])) / (0.037 * pop_J + 0.018 *  pop_G + 0.147 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.071 *  pop_L   + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J    +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J  + 0.147 *  pop_I  + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L + 0.018 *  pop_G   + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ( (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.018 *  pop_G  +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.018 *  pop_G  + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    #4 de nulle


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.384 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.071 *  pop_L  +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / (  0.147 *  pop_I +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])) / ( 0.071 *  pop_L  + 0.147 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])) / (0.037 * pop_J + 0.147 *  pop_I  )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) ) / (0.037 * pop_J + 0.071 *  pop_L  )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])) / ( 0.071 *  pop_L + 0.018 *  pop_G   )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])) / (0.037 * pop_J + 0.018 *  pop_G  )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / (0.037 * pop_J    +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])



                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ( (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])) / (  0.018 *  pop_G + 0.147 *  pop_I  )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ( (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.018 *  pop_G  +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])




                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ( (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.018 *  pop_G + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ( (0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.147 *  pop_I  + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])



                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.071 *  pop_L   + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J    + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    #5 de nulle
                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n=  var_holder['eco_isic3_j']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= var_holder['eco_isic3_o']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= var_holder['eco_isic3_g']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        Eco_isic4_n= var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= var_holder['eco_isic3_l']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n=  var_holder['eco_isic3_i']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_N.empty :
                            isic4_from_isic3_N = new.copy()
                        else :
                            isic4_from_isic3_N= pd.concat([isic4_from_isic3_N,new])

    print("task_N finished")

    isic4_from_isic3_N = isic4_from_isic3_N.reset_index(drop=True)

    return isic4_from_isic3_N


def task_O(isic4_from_isic3_O,isic3,workforce):
    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}

    print("Starting with ISIC O")
    #ISIC4 O
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
                #print(code)
            for year in range(1995,2023):
                #print(year)
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



                    if  (var_holder['eco_isic3_l'] != 0 ):
                        eco_isic4_o= var_holder['eco_isic3_l']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_O', 'time' : year, 'obs_value' :eco_isic4_o}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_O.empty :
                            isic4_from_isic3_O = new.copy()
                        else :
                            isic4_from_isic3_O= pd.concat([isic4_from_isic3_O,new])

    print("task_O finished")
    isic4_from_isic3_O = isic4_from_isic3_O.reset_index(drop=True)

    return isic4_from_isic3_O

def task_P(isic4_from_isic3_P,isic3,workforce):
    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}

    print("Starting with ISIC P")

    #ISIC4 P
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            #print(code)
            for year in range(1995,2023):
                #print(year)
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
                    if (year ==2022 and code =='UKR'):
                        pop_K = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))
                        pop_M = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))
                        pop_N = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))
                        pop_O = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_O'),'obs_value'].to_string(header = False, index=False))
                    else :
                        pop_K = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))
                        pop_M = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))
                        pop_N = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))
                        pop_O = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_O'),'obs_value'].to_string(header = False, index=False))


                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_m'] !=0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] !=0 ):
    
                        eco_isic4_p= ((0.027*pop_K * var_holder['eco_isic3_k']) +(1 *  pop_M * var_holder['eco_isic3_m']) + (0.077 *  pop_N * var_holder['eco_isic3_n'])+(0.075 *  pop_O * var_holder['eco_isic3_o'])) / (0.027*pop_K + 1 *  pop_M + 0.077 *  pop_N + 0.075 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_P.empty :
                            isic4_from_isic3_P = new.copy()
                        else :
                            isic4_from_isic3_P= pd.concat([isic4_from_isic3_P,new])
                            
                    #un de nulle
                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_m'] !=0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_p= ((1 *  pop_M * var_holder['eco_isic3_m']) + (0.077 *  pop_N * var_holder['eco_isic3_n'])+(0.075 *  pop_O * var_holder['eco_isic3_o'])) / ( 1 *  pop_M + 0.077 *  pop_N + 0.075 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_P.empty :
                            isic4_from_isic3_P = new.copy()
                        else :
                            isic4_from_isic3_P= pd.concat([isic4_from_isic3_P,new])


                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_m'] ==0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_p= ((0.027*pop_K * var_holder['eco_isic3_k'])  + (0.077 *  pop_N * var_holder['eco_isic3_n'])+(0.075 *  pop_O * var_holder['eco_isic3_o'])) / (0.027*pop_K  + 0.077 *  pop_N + 0.075 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_P.empty :
                            isic4_from_isic3_P = new.copy()
                        else :
                            isic4_from_isic3_P= pd.concat([isic4_from_isic3_P,new])

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_m'] !=0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] !=0 ):
    
                        eco_isic4_p= ((0.027*pop_K * var_holder['eco_isic3_k']) +(1 *  pop_M * var_holder['eco_isic3_m']) +(0.075 *  pop_O * var_holder['eco_isic3_o'])) / (0.027*pop_K + 1 *  pop_M  + 0.075 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_P.empty :
                            isic4_from_isic3_P = new.copy()
                        else :
                            isic4_from_isic3_P= pd.concat([isic4_from_isic3_P,new])


                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_m'] !=0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_p= ((0.027*pop_K * var_holder['eco_isic3_k']) +(1 *  pop_M * var_holder['eco_isic3_m']) + (0.077 *  pop_N * var_holder['eco_isic3_n'])) / (0.027*pop_K + 1 *  pop_M + 0.077 *  pop_N  )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_P.empty :
                            isic4_from_isic3_P = new.copy()
                        else :
                            isic4_from_isic3_P= pd.concat([isic4_from_isic3_P,new])

                # 2 de nulle

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_m'] !=0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] ==0 ):
    
                        eco_isic4_p= ((0.027*pop_K * var_holder['eco_isic3_k']) +(1 *  pop_M * var_holder['eco_isic3_m'])) / (0.027*pop_K + 1 *  pop_M )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_P.empty :
                            isic4_from_isic3_P = new.copy()
                        else :
                            isic4_from_isic3_P= pd.concat([isic4_from_isic3_P,new])

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_m'] ==0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_p= ((0.027*pop_K * var_holder['eco_isic3_k'])  + (0.077 *  pop_N * var_holder['eco_isic3_n'])) / (0.027*pop_K  + 0.077 *  pop_N )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_P.empty :
                            isic4_from_isic3_P = new.copy()
                        else :
                            isic4_from_isic3_P= pd.concat([isic4_from_isic3_P,new])


                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_m'] ==0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_p= ((0.027*pop_K * var_holder['eco_isic3_k']) +(0.075 *  pop_O * var_holder['eco_isic3_o'])) / (0.027*pop_K   + 0.075 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_P.empty :
                            isic4_from_isic3_P = new.copy()
                        else :
                            isic4_from_isic3_P= pd.concat([isic4_from_isic3_P,new])


                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_m'] !=0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_p= ((1 *  pop_M * var_holder['eco_isic3_m']) + (0.077 *  pop_N * var_holder['eco_isic3_n'])) / ( 1 *  pop_M + 0.077 *  pop_N )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_P.empty :
                            isic4_from_isic3_P = new.copy()
                        else :
                            isic4_from_isic3_P= pd.concat([isic4_from_isic3_P,new])

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_m'] !=0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_p= ((1 *  pop_M * var_holder['eco_isic3_m']) +(0.075 *  pop_O * var_holder['eco_isic3_o'])) / ( 1 *  pop_M  + 0.075 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_P.empty :
                            isic4_from_isic3_P = new.copy()
                        else :
                            isic4_from_isic3_P= pd.concat([isic4_from_isic3_P,new])



                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_m'] ==0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_p= ( (0.077 *  pop_N * var_holder['eco_isic3_n'])+(0.075 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.077 *  pop_N + 0.075 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_P.empty :
                            isic4_from_isic3_P = new.copy()
                        else :
                            isic4_from_isic3_P= pd.concat([isic4_from_isic3_P,new])


                    # 3 de nulle
                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_m'] ==0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_p= var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_P.empty :
                            isic4_from_isic3_P = new.copy()
                        else :
                            isic4_from_isic3_P= pd.concat([isic4_from_isic3_P,new])


                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_m'] !=0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_p= var_holder['eco_isic3_m']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_P.empty :
                            isic4_from_isic3_P = new.copy()
                        else :
                            isic4_from_isic3_P= pd.concat([isic4_from_isic3_P,new])


                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_m'] ==0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_p= var_holder['eco_isic3_n']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_P.empty :
                            isic4_from_isic3_P = new.copy()
                        else :
                            isic4_from_isic3_P= pd.concat([isic4_from_isic3_P,new])


                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_m'] ==0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_p= var_holder['eco_isic3_o']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_P.empty :
                            isic4_from_isic3_P = new.copy()
                        else :
                            isic4_from_isic3_P= pd.concat([isic4_from_isic3_P,new])

    print("task_P finished")
    isic4_from_isic3_P = isic4_from_isic3_P.reset_index(drop=True)

    return isic4_from_isic3_P

def task_Q(isic4_from_isic3_Q,isic3,workforce):
    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}

    print("Starting with ISIC Q")
    #ISIC4 Q
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
                #print(code)
            for year in range(1995,2023):
                #print(year)
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
                    if (year ==2022 and code =='UKR'):
                        pop_N = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))
                        pop_L = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))
                    else :
                        pop_N = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))
                        pop_L = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))

                    if  (var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_l'] !=0):
                        eco_isic4_q= ((0.846*pop_N * var_holder['eco_isic3_n']) +( 0.071*pop_L * var_holder['eco_isic3_l'])) / (0.846*pop_N + 0.071*pop_L )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_Q', 'time' : year, 'obs_value' :eco_isic4_q}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_Q.empty :
                            isic4_from_isic3_Q = new.copy()
                        else :
                            isic4_from_isic3_Q= pd.concat([isic4_from_isic3_Q,new])

                    if (var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_l']!=0) :
                        eco_isic4_q=  var_holder['eco_isic3_l']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_Q', 'time' : year, 'obs_value' :eco_isic4_q}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_Q.empty :
                            isic4_from_isic3_Q = new.copy()
                        else :
                            isic4_from_isic3_Q= pd.concat([isic4_from_isic3_Q,new])

                    if (var_holder['eco_isic3_l'] == 0 and var_holder['eco_isic3_n']!=0) :
                        eco_isic4_q=  var_holder['eco_isic3_n']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_Q', 'time' : year, 'obs_value' :eco_isic4_q}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_Q.empty :
                            isic4_from_isic3_Q = new.copy()
                        else :
                            isic4_from_isic3_Q= pd.concat([isic4_from_isic3_Q,new])

    print("task_Q finished")
    isic4_from_isic3_Q = isic4_from_isic3_Q.reset_index(drop=True)
    
    return isic4_from_isic3_Q


def task_R(isic4_from_isic3_R,isic3,workforce):
    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}

    print("Starting with ISIC R")

    
    #ISIC4 R

    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            #print(code)
            for year in range(1995,2023):
                #print(year)
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
                    if (year ==2022 and code =='UKR'):
                        pop_K = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))
                        pop_L = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))
                        pop_O = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_O'),'obs_value'].to_string(header = False, index=False))

                    else :
                        pop_K = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))
                        pop_L = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))
                        pop_O = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_O'),'obs_value'].to_string(header = False, index=False))





                    # rien de nulle
                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_r= ((0.014 * pop_K * var_holder['eco_isic3_k']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.264 *  pop_O * var_holder['eco_isic3_o'])) / (0.014 * pop_K + 0.071 *  pop_L + 0.264 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_R', 'time' : year, 'obs_value' :eco_isic4_r}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_R.empty :
                            isic4_from_isic3_R = new.copy()
                        else :
                            isic4_from_isic3_R= pd.concat([isic4_from_isic3_R,new])

                    # 1 de nulle
                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_r= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.264 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L + 0.264 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_R', 'time' : year, 'obs_value' :eco_isic4_r}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_R.empty :
                            isic4_from_isic3_R = new.copy()
                        else :
                            isic4_from_isic3_R= pd.concat([isic4_from_isic3_R,new])


                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_r= ((0.014 * pop_K * var_holder['eco_isic3_k']) + (0.264 *  pop_O * var_holder['eco_isic3_o'])) / (0.014 * pop_K  + 0.264 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_R', 'time' : year, 'obs_value' :eco_isic4_r}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_R.empty :
                            isic4_from_isic3_R = new.copy()
                        else :
                            isic4_from_isic3_R= pd.concat([isic4_from_isic3_R,new])

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_r= ((0.014 * pop_K * var_holder['eco_isic3_k']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) ) / (0.014 * pop_K + 0.071 *  pop_L )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_R', 'time' : year, 'obs_value' :eco_isic4_r}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_R.empty :
                            isic4_from_isic3_R = new.copy()
                        else :
                            isic4_from_isic3_R= pd.concat([isic4_from_isic3_R,new])

                    # 2 de nulle

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_r=  var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_R', 'time' : year, 'obs_value' :eco_isic4_r}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_R.empty :
                            isic4_from_isic3_R = new.copy()
                        else :
                            isic4_from_isic3_R= pd.concat([isic4_from_isic3_R,new])

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_r=  var_holder['eco_isic3_l']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_R', 'time' : year, 'obs_value' :eco_isic4_r}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_R.empty :
                            isic4_from_isic3_R = new.copy()
                        else :
                            isic4_from_isic3_R= pd.concat([isic4_from_isic3_R,new])

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_r=  var_holder['eco_isic3_o']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_R', 'time' : year, 'obs_value' :eco_isic4_r}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_R.empty :
                            isic4_from_isic3_R = new.copy()
                        else :
                            isic4_from_isic3_R= pd.concat([isic4_from_isic3_R,new])

    print("task_R finished")
    isic4_from_isic3_R = isic4_from_isic3_R.reset_index(drop=True)
    
    return isic4_from_isic3_R


def task_S(isic4_from_isic3_S,isic3,workforce):
    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}

    print("Starting with ISIC S")

    
   
    #ISIC4 S
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            #print(code)
            for year in range(1995,2023):
                #print(year)
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
                    if (year ==2022 and code =='UKR'):
                        pop_K = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))
                        pop_J = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_HJ'),'obs_value'].to_string(header = False, index=False))
                        pop_G = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_G'),'obs_value'].to_string(header = False, index=False))
                        pop_O = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_O'),'obs_value'].to_string(header = False, index=False))
                    else :
                        pop_K = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))
                        pop_J = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))
                        pop_G = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_LMN'),'obs_value'].to_string(header = False, index=False))
                        pop_O = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_O'),'obs_value'].to_string(header = False, index=False))


                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_j'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_s= ((0.014*pop_K * var_holder['eco_isic3_k']) +(0.037 *  pop_J * var_holder['eco_isic3_j']) + (0.109 *  pop_G * var_holder['eco_isic3_g'])+(0.189 *  pop_O * var_holder['eco_isic3_o'])) / (0.014*pop_K + 0.037 *  pop_J + 0.109 *  pop_G + 0.189 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_S.empty :
                            isic4_from_isic3_S = new.copy()
                        else :
                            isic4_from_isic3_S= pd.concat([isic4_from_isic3_S,new])


                    #un de nulle
                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_j'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_s= ((0.037 *  pop_J * var_holder['eco_isic3_j']) + (0.109 *  pop_G * var_holder['eco_isic3_g'])+(0.189 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.037 *  pop_J + 0.109 *  pop_G + 0.189 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_S.empty :
                            isic4_from_isic3_S = new.copy()
                        else :
                            isic4_from_isic3_S= pd.concat([isic4_from_isic3_S,new])


                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_j'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_s= ((0.014*pop_K * var_holder['eco_isic3_k'])  + (0.109 *  pop_G * var_holder['eco_isic3_g'])+(0.189 *  pop_O * var_holder['eco_isic3_o'])) / (0.014*pop_K  + 0.109 *  pop_G + 0.189 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_S.empty :
                            isic4_from_isic3_S = new.copy()
                        else :
                            isic4_from_isic3_S= pd.concat([isic4_from_isic3_S,new])

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_j'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_s= ((0.014*pop_K * var_holder['eco_isic3_k']) +(0.037 *  pop_J * var_holder['eco_isic3_j']) +(0.189 *  pop_O * var_holder['eco_isic3_o'])) / (0.014*pop_K + 0.037 *  pop_J  + 0.189 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_S.empty :
                            isic4_from_isic3_S = new.copy()
                        else :
                            isic4_from_isic3_S= pd.concat([isic4_from_isic3_S,new])

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_j'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_s= ((0.014*pop_K * var_holder['eco_isic3_k']) +(0.037 *  pop_J * var_holder['eco_isic3_j']) + (0.109 *  pop_G * var_holder['eco_isic3_g'])) / (0.014*pop_K + 0.037 *  pop_J + 0.109 *  pop_G  )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_S.empty :
                            isic4_from_isic3_S = new.copy()
                        else :
                            isic4_from_isic3_S= pd.concat([isic4_from_isic3_S,new])
                    
                    # 2 de nulle

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_j'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_s= ((0.014*pop_K * var_holder['eco_isic3_k']) +(0.037 *  pop_J * var_holder['eco_isic3_j'])) / (0.014*pop_K + 0.037 *  pop_J )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_S.empty :
                            isic4_from_isic3_S = new.copy()
                        else :
                            isic4_from_isic3_S= pd.concat([isic4_from_isic3_S,new])

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_j'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_s= ((0.014*pop_K * var_holder['eco_isic3_k'])  + (0.109 *  pop_G * var_holder['eco_isic3_g'])) / (0.014*pop_K  + 0.109 *  pop_G )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_S.empty :
                            isic4_from_isic3_S = new.copy()
                        else :
                            isic4_from_isic3_S= pd.concat([isic4_from_isic3_S,new])

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_j'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_s= ((0.014*pop_K * var_holder['eco_isic3_k']) +(0.189 *  pop_O * var_holder['eco_isic3_o'])) / (0.014*pop_K   + 0.189 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_S.empty :
                            isic4_from_isic3_S = new.copy()
                        else :
                            isic4_from_isic3_S= pd.concat([isic4_from_isic3_S,new])


                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_j'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_s= ((0.037 *  pop_J * var_holder['eco_isic3_j']) + (0.109 *  pop_G * var_holder['eco_isic3_g'])) / ( 0.037 *  pop_J + 0.109 *  pop_G )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_S.empty :
                            isic4_from_isic3_S = new.copy()
                        else :
                            isic4_from_isic3_S= pd.concat([isic4_from_isic3_S,new])

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_j'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_s= ((0.037 *  pop_J * var_holder['eco_isic3_j']) +(0.189 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.037 *  pop_J  + 0.189 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line

                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_S.empty :
                            isic4_from_isic3_S = new.copy()
                        else :
                            isic4_from_isic3_S= pd.concat([isic4_from_isic3_S,new])



                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_j'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_o'] !=0 ):
    
                        eco_isic4_s= ( (0.109 *  pop_G * var_holder['eco_isic3_g'])+(0.189 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.109 *  pop_G + 0.189 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_S.empty :
                            isic4_from_isic3_S = new.copy()
                        else :
                            isic4_from_isic3_S= pd.concat([isic4_from_isic3_S,new])
                    

                    # 3 de nulle
                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_j'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_s= var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_S.empty :
                            isic4_from_isic3_S = new.copy()
                        else :
                            isic4_from_isic3_S= pd.concat([isic4_from_isic3_S,new])

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_j'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_s= var_holder['eco_isic3_j']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_S.empty :
                            isic4_from_isic3_S = new.copy()
                        else :
                            isic4_from_isic3_S= pd.concat([isic4_from_isic3_S,new])


                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_j'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_s= var_holder['eco_isic3_g']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_S.empty :
                            isic4_from_isic3_S = new.copy()
                        else :
                            isic4_from_isic3_S= pd.concat([isic4_from_isic3_S,new])

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_j'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_s= var_holder['eco_isic3_o']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_S.empty :
                            isic4_from_isic3_S = new.copy()
                        else :
                            isic4_from_isic3_S= pd.concat([isic4_from_isic3_S,new])

    print("task_S finished")
    isic4_from_isic3_S = isic4_from_isic3_S.reset_index(drop=True)

    return isic4_from_isic3_S

def task_T(isic4_from_isic3_T,isic3,workforce):
    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}

    print("Starting with ISIC T")

    #ISIC4 T
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            #print(code)
            for year in range(1995,2023):
                #print(year)
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



                    if  (var_holder['eco_isic3_p'] != 0 ):
                        eco_isic4_t= var_holder['eco_isic3_p']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_T', 'time' : year, 'obs_value' :eco_isic4_t}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_T.empty :
                            isic4_from_isic3_T = new.copy()
                        else :
                            isic4_from_isic3_T= pd.concat([isic4_from_isic3_T,new])
    print("task_T finished")
    isic4_from_isic3_T = isic4_from_isic3_T.reset_index(drop=True)

    return isic4_from_isic3_T


def task_U(isic4_from_isic3_U,isic3,workforce):
    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}

    print("Starting with ISIC U")

    #ISIC4 U

    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            #print(code)
            for year in range(1995,2023):
                #print(year)
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
                    
                    if (year ==2022 and code =='UKR'):
                        pop_K = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))
                        pop_F = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_F'),'obs_value'].to_string(header = False, index=False))
                        pop_Q = 0.845 * float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==2021)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_Q'),'obs_value'].to_string(header = False, index=False))

                    else :
                        pop_K = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_K'),'obs_value'].to_string(header = False, index=False))
                        pop_F = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_F'),'obs_value'].to_string(header = False, index=False))
                        pop_Q = float(workforce.loc[(workforce['ref_area']==code)&(workforce['time']==year)&(workforce['sex']==sex)&(workforce['classif1']=='ECO_DETAILS_Q'),'obs_value'].to_string(header = False, index=False))





                    # rien de nulle
                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_q'] != 0 ):

                        eco_isic3_u= ((0.014 * pop_K * var_holder['eco_isic3_k']) +(0.05 *  pop_F * var_holder['eco_isic3_f']) + (1 *  pop_Q * var_holder['eco_isic3_q'])) / (0.014 * pop_K + 0.05 *  pop_F + 1 *  pop_Q)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_U', 'time' : year, 'obs_value' :eco_isic3_u}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_U.empty :
                            isic4_from_isic3_U = new.copy()
                        else :
                            isic4_from_isic3_U= pd.concat([isic4_from_isic3_U,new])

                    # 1 de nulle
                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_q'] != 0 ):

                        eco_isic3_u= ((0.05 *  pop_F * var_holder['eco_isic3_f']) + (1 *  pop_Q * var_holder['eco_isic3_q'])) / ( 0.05 *  pop_F + 1 *  pop_Q)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_U', 'time' : year, 'obs_value' :eco_isic3_u}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_U.empty :
                            isic4_from_isic3_U = new.copy()
                        else :
                            isic4_from_isic3_U= pd.concat([isic4_from_isic3_U,new])


                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_q'] != 0 ):

                        eco_isic3_u= ((0.014 * pop_K * var_holder['eco_isic3_k']) + (1 *  pop_Q * var_holder['eco_isic3_q'])) / (0.014 * pop_K  + 1 *  pop_Q)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_U', 'time' : year, 'obs_value' :eco_isic3_u}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_U.empty :
                            isic4_from_isic3_U = new.copy()
                        else :
                            isic4_from_isic3_U= pd.concat([isic4_from_isic3_U,new])

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_q'] == 0 ):

                        eco_isic3_u= ((0.014 * pop_K * var_holder['eco_isic3_k']) +(0.05 *  pop_F * var_holder['eco_isic3_f']) ) / (0.014 * pop_K + 0.05 *  pop_F )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_U', 'time' : year, 'obs_value' :eco_isic3_u}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line

                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_U.empty :
                            isic4_from_isic3_U = new.copy()
                        else :
                            isic4_from_isic3_U= pd.concat([isic4_from_isic3_U,new])

                    # 2 de nulle

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_q'] == 0 ):

                        eco_isic3_u=  var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_U', 'time' : year, 'obs_value' :eco_isic3_u}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_U.empty :
                            isic4_from_isic3_U = new.copy()
                        else :
                            isic4_from_isic3_U= pd.concat([isic4_from_isic3_U,new])

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_q'] == 0 ):

                        eco_isic3_u=  var_holder['eco_isic3_f']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_U', 'time' : year, 'obs_value' :eco_isic3_u}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_U.empty :
                            isic4_from_isic3_U = new.copy()
                        else :
                            isic4_from_isic3_U= pd.concat([isic4_from_isic3_U,new])

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_q'] != 0 ):

                        eco_isic3_u=  var_holder['eco_isic3_q']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_U', 'time' : year, 'obs_value' :eco_isic3_u}

                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_U.empty :
                            isic4_from_isic3_U = new.copy()
                        else :
                            isic4_from_isic3_U= pd.concat([isic4_from_isic3_U,new])
    print("task_U finished")
    isic4_from_isic3_U = isic4_from_isic3_U.reset_index(drop=True)

    return isic4_from_isic3_U

def task_X(isic4_from_isic3_X,isic3,workforce):
    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}

    print("Starting with ISIC X")

    
    #ISIC4 X
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
                #print(code)
            for year in range(1995,2023):
                #print(year)
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



                    if  (var_holder['eco_isic3_x'] != 0 ):
                        eco_isic4_x= var_holder['eco_isic3_x']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_X', 'time' : year, 'obs_value' :eco_isic4_x}
                        #isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        #isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                        new = pd.DataFrame([new_line])
                        if isic4_from_isic3_X.empty :
                            isic4_from_isic3_X = new.copy()
                        else :
                            isic4_from_isic3_X= pd.concat([isic4_from_isic3_X,new])
    print("task_X finished")
    isic4_from_isic3_X = isic4_from_isic3_X.reset_index(drop=True)

    return isic4_from_isic3_X
    
