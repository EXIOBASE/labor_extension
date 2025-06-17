import pandas as pd
import string

def correspondance_isic(workforce,isic3):
    
    isic4_from_isic3_data=pd.DataFrame(data=None,columns=['ref_area','sex','classif1','time','obs_value'])
    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)
    var_holder = {}
    
    
    '''
    Here we transforme the ISIC3 categories to ISIC4 categories
    Coefficients given by Etienne
    '''
    
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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

                    #print(pop_A,pop_B,var_holder['eco_isic3_a'],var_holder['eco_isic3_b'])
                    if  (var_holder['eco_isic3_a'] != 0 and var_holder['eco_isic3_b'] !=0):
                        eco_isic4_a= ((pop_A * var_holder['eco_isic3_a']) +( pop_B * var_holder['eco_isic3_b'])) / (pop_A + pop_B )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_A', 'time' : year, 'obs_value' :eco_isic4_a}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_a'] == 0 and var_holder['eco_isic3_b']!=0) :
                        eco_isic4_a=  var_holder['eco_isic3_b']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_A', 'time' : year, 'obs_value' :eco_isic4_a}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_b'] == 0 and var_holder['eco_isic3_a']!=0) :
                        eco_isic4_a=  var_holder['eco_isic3_a']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_A', 'time' : year, 'obs_value' :eco_isic4_a}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)




    #ISIC4 B
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                   


    #ISIC4 C
    #rien de nulle
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)




                    #un de nulle
                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((0.05 *  pop_F * var_holder['eco_isic3_f']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.029 *  pop_I * var_holder['eco_isic3_i'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.05 *  pop_F + 0.018 *  pop_G + 0.029 *  pop_I +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.029 *  pop_I * var_holder['eco_isic3_i'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / (pop_D  + 0.018 *  pop_G + 0.029 *  pop_I +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.05 *  pop_F * var_holder['eco_isic3_f']) +(0.029 *  pop_I * var_holder['eco_isic3_i'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / (pop_D + 0.05 *  pop_F  + 0.029 *  pop_I +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.05 *  pop_F * var_holder['eco_isic3_f']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / (pop_D + 0.05 *  pop_F + 0.018 *  pop_G  +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.05 *  pop_F * var_holder['eco_isic3_f']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.029 *  pop_I * var_holder['eco_isic3_i'])) / (pop_D + 0.05 *  pop_F + 0.018 *  pop_G + 0.029 *  pop_I)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    #2 de nulle

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.029 *  pop_I * var_holder['eco_isic3_i'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.018 *  pop_G + 0.029 *  pop_I +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((0.05 *  pop_F * var_holder['eco_isic3_f']) +(0.029 *  pop_I * var_holder['eco_isic3_i'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.05 *  pop_F  + 0.029 *  pop_I +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((0.05 *  pop_F * var_holder['eco_isic3_f']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.05 *  pop_F + 0.018 *  pop_G +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= ((0.05 *  pop_F * var_holder['eco_isic3_f']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.029 *  pop_I * var_holder['eco_isic3_i'])) / ( 0.05 *  pop_F + 0.018 *  pop_G + 0.029 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.029 *  pop_I * var_holder['eco_isic3_i'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / (pop_D  + 0.029 *  pop_I +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / (pop_D + 0.018 *  pop_G  +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.029 *  pop_I * var_holder['eco_isic3_i'])) / (pop_D  + 0.018 *  pop_G + 0.029 *  pop_I)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.05 *  pop_F * var_holder['eco_isic3_f'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / (pop_D + 0.05 *  pop_F  +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.05 *  pop_F * var_holder['eco_isic3_f']) +(0.029 *  pop_I * var_holder['eco_isic3_i'])) / (pop_D + 0.05 *  pop_F  + 0.029 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.05 *  pop_F * var_holder['eco_isic3_f']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])) / (pop_D + 0.05 *  pop_F + 0.018 *  pop_G )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    # 3 de nulle

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.05 *  pop_F * var_holder['eco_isic3_f'])) / (pop_D + 0.05 *  pop_F )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])) / (pop_D  + 0.018 *  pop_G )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.029 *  pop_I * var_holder['eco_isic3_i'])) / (pop_D   + 0.029 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((pop_D * var_holder['eco_isic3_d']) +(0.014 *  pop_K * var_holder['eco_isic3_k'])) / (pop_D + 0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= ((0.05 *  pop_F * var_holder['eco_isic3_f']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])) / ( 0.05 *  pop_F + 0.018 *  pop_G )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= ((0.05 *  pop_F * var_holder['eco_isic3_f']) +(0.029 *  pop_I * var_holder['eco_isic3_i'])) / ( 0.05 *  pop_F  + 0.029 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((0.05 *  pop_F * var_holder['eco_isic3_f']) +(0.014 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.05 *  pop_F   +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= ( (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.029 *  pop_I * var_holder['eco_isic3_i'])) / ( 0.018 *  pop_G + 0.029 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ( (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.018 *  pop_G  +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= ((0.029 *  pop_I * var_holder['eco_isic3_i'])+(0.014 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.029 *  pop_I +0.014 *  pop_K)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    # 4 de nulle
                    if (var_holder['eco_isic3_d'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= var_holder['eco_isic3_d']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= var_holder['eco_isic3_f']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= var_holder['eco_isic3_g']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0):

                        eco_isic4_c= var_holder['eco_isic3_i']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_d'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0):

                        eco_isic4_c= var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_C', 'time' : year, 'obs_value' :eco_isic4_c}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)   





    #ISIC4 D
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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
                        # print(year, code)
                        eco_isic4_d=  var_holder['eco_isic3_e']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_D', 'time' : year, 'obs_value' :eco_isic4_d}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)   
                    
                        
    #ISIC4 E
    #rien de nulle
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    # 1 de nulle
                    if (var_holder['eco_isic3_e'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_e= ((0.05 *  pop_F * var_holder['eco_isic3_f']) + (0.113 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.05 *  pop_F + 0.113 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_E', 'time' : year, 'obs_value' :eco_isic4_e}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_e'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_e= ((0.25 * pop_E * var_holder['eco_isic3_e']) + (0.113 *  pop_O * var_holder['eco_isic3_o'])) / (0.25 * pop_E  + 0.113 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_E', 'time' : year, 'obs_value' :eco_isic4_e}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_e'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_e= ((0.25 * pop_E * var_holder['eco_isic3_e']) +(0.05 *  pop_F * var_holder['eco_isic3_f']) ) / (0.25 * pop_E + 0.05 *  pop_F )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_E', 'time' : year, 'obs_value' :eco_isic4_e}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)    

                    # 2 de nulle

                    if (var_holder['eco_isic3_e'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_e=  var_holder['eco_isic3_e']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_E', 'time' : year, 'obs_value' :eco_isic4_e}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_e'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_e=  var_holder['eco_isic3_f']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_E', 'time' : year, 'obs_value' :eco_isic4_e}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_e'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_e=  var_holder['eco_isic3_o']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_E', 'time' : year, 'obs_value' :eco_isic4_e}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)





    #ISIC4 F
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_f'] == 0 and var_holder['eco_isic3_k']!=0) :
                        eco_isic4_f=  var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_F', 'time' : year, 'obs_value' :eco_isic4_f}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_f']!=0) :
                        eco_isic4_f=  var_holder['eco_isic3_f']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_F', 'time' : year, 'obs_value' :eco_isic4_f}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)






    #ISIC4 G
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)  
                    


    #ISIC4 H
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    # 1 de nulle
                    if (var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_h= ((0.706 *  pop_I * var_holder['eco_isic3_i']) + (0.019 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.706 *  pop_I + 0.019 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_H', 'time' : year, 'obs_value' :eco_isic4_h}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_h= ((0.018 * pop_G * var_holder['eco_isic3_g']) + (0.019 *  pop_O * var_holder['eco_isic3_o'])) / (0.018 * pop_G  + 0.019 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_H', 'time' : year, 'obs_value' :eco_isic4_h}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_h= ((0.018 * pop_G * var_holder['eco_isic3_g']) +(0.706 *  pop_I * var_holder['eco_isic3_i']) ) / (0.018 * pop_G + 0.706 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_H', 'time' : year, 'obs_value' :eco_isic4_h}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    # 2 de nulle

                    if (var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_h=  var_holder['eco_isic3_g']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_H', 'time' : year, 'obs_value' :eco_isic4_h}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_h=  var_holder['eco_isic3_i']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_H', 'time' : year, 'obs_value' :eco_isic4_h}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_h=  var_holder['eco_isic3_o']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_H', 'time' : year, 'obs_value' :eco_isic4_h}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)



    #ISIC4 I

    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)





    #ISIC4 J

    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    # 1 de nulle
                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_j= ((0.088 *  pop_I * var_holder['eco_isic3_i']) + (0.208 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.088 *  pop_I + 0.208 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_J', 'time' : year, 'obs_value' :eco_isic4_j}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_j= ((0.233 * pop_K * var_holder['eco_isic3_k']) + (0.208 *  pop_O * var_holder['eco_isic3_o'])) / (0.233 * pop_K  + 0.208 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_J', 'time' : year, 'obs_value' :eco_isic4_j}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_j= ((0.233 * pop_K * var_holder['eco_isic3_k']) +(0.088 *  pop_I * var_holder['eco_isic3_i']) ) / (0.233 * pop_K + 0.088 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_J', 'time' : year, 'obs_value' :eco_isic4_j}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    # 2 de nulle

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_j=  var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_J', 'time' : year, 'obs_value' :eco_isic4_j}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_j=  var_holder['eco_isic3_i']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_J', 'time' : year, 'obs_value' :eco_isic4_j}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_j=  var_holder['eco_isic3_o']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_J', 'time' : year, 'obs_value' :eco_isic4_j}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)




    #ISIC4 K
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_i'] == 0 and var_holder['eco_isic3_j']!=0) :
                        eco_isic4_k=  var_holder['eco_isic3_j']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_K', 'time' : year, 'obs_value' :eco_isic4_k}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_i']!=0) :
                        eco_isic4_k=  var_holder['eco_isic3_i']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_K', 'time' : year, 'obs_value' :eco_isic4_k}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)







    #ISIC4 L
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l']!=0) :
                        eco_isic4_l=  var_holder['eco_isic3_l']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_L', 'time' : year, 'obs_value' :eco_isic4_l}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_l'] == 0 and var_holder['eco_isic3_k']!=0) :
                        eco_isic4_l=  var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_L', 'time' : year, 'obs_value' :eco_isic4_l}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


    #ISIC4 M
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)




                    #un de nulle
                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_m= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.077 *  pop_N * var_holder['eco_isic3_n'])+(0.038 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L + 0.077 *  pop_N + 0.038 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_m= ((0.26*pop_K * var_holder['eco_isic3_k'])  + (0.077 *  pop_N * var_holder['eco_isic3_n'])+(0.038 *  pop_O * var_holder['eco_isic3_o'])) / (0.26*pop_K  + 0.077 *  pop_N + 0.038 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_m= ((0.26*pop_K * var_holder['eco_isic3_k']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.038 *  pop_O * var_holder['eco_isic3_o'])) / (0.26*pop_K + 0.071 *  pop_L  + 0.038 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_m= ((0.26*pop_K * var_holder['eco_isic3_k']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.077 *  pop_N * var_holder['eco_isic3_n'])) / (0.26*pop_K + 0.071 *  pop_L + 0.077 *  pop_N  )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)





                    # 2 de nulle

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_m= ((0.26*pop_K * var_holder['eco_isic3_k']) +(0.071 *  pop_L * var_holder['eco_isic3_l'])) / (0.26*pop_K + 0.071 *  pop_L )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_m= ((0.26*pop_K * var_holder['eco_isic3_k'])  + (0.077 *  pop_N * var_holder['eco_isic3_n'])) / (0.26*pop_K  + 0.077 *  pop_N )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_m= ((0.26*pop_K * var_holder['eco_isic3_k']) +(0.038 *  pop_O * var_holder['eco_isic3_o'])) / (0.26*pop_K   + 0.038 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_m= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.077 *  pop_N * var_holder['eco_isic3_n'])) / ( 0.071 *  pop_L + 0.077 *  pop_N )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_m= ((0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.038 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L  + 0.038 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)



                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_m= ( (0.077 *  pop_N * var_holder['eco_isic3_n'])+(0.038 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.077 *  pop_N + 0.038 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)



                    # 3 de nulle
                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_m= var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_m= var_holder['eco_isic3_l']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_m= var_holder['eco_isic3_n']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_m= var_holder['eco_isic3_o']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_M', 'time' : year, 'obs_value' :eco_isic4_m}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


    #ISIC4 N
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    #un de nulle
                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L + 0.018 *  pop_G + 0.147 *  pop_I +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J  + 0.018 *  pop_G + 0.147 *  pop_I +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.071 *  pop_L  + 0.147 *  pop_I +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.071 *  pop_L + 0.018 *  pop_G  +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.071 *  pop_L + 0.018 *  pop_G + 0.147 *  pop_I + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])) / (0.037 * pop_J + 0.071 *  pop_L +0.384 *  pop_K+ 0.018 *  pop_G + 0.147 *  pop_I)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    #2 de nulle


                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.071 *  pop_L  +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L  + 0.147 *  pop_I +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.071 *  pop_L  + 0.147 *  pop_I  + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.147 *  pop_I +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / (0.037 * pop_J + 0.071 *  pop_L  + 0.147 *  pop_I +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L + 0.018 *  pop_G  +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.071 *  pop_L + 0.018 *  pop_G  + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J  + 0.018 *  pop_G  +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / (0.037 * pop_J + 0.071 *  pop_L + 0.018 *  pop_G  +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L + 0.018 *  pop_G + 0.147 *  pop_I  + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ( (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.018 *  pop_G + 0.147 *  pop_I +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.071 *  pop_L + 0.018 *  pop_G + 0.147 *  pop_I +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.018 *  pop_G + 0.147 *  pop_I  + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])) / (0.037 * pop_J + 0.071 *  pop_L + 0.018 *  pop_G + 0.147 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / (0.037 * pop_J  + 0.018 *  pop_G + 0.147 *  pop_I +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)



                    #3 de nulle


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L  +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (  0.147 *  pop_I +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L  + 0.147 *  pop_I  + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / (0.037 * pop_J + 0.147 *  pop_I +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])) / (0.037 * pop_J + 0.071 *  pop_L  + 0.147 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.071 *  pop_L + 0.018 *  pop_G  +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])) / (0.037 * pop_J + 0.071 *  pop_L + 0.018 *  pop_G  )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / (0.037 * pop_J  + 0.018 *  pop_G  +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.384 *  pop_K * var_holder['eco_isic3_k'])) / (0.037 * pop_J + 0.071 *  pop_L   +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])) / ( 0.071 *  pop_L + 0.018 *  pop_G + 0.147 *  pop_I  )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ( (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.018 *  pop_G + 0.147 *  pop_I +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.071 *  pop_L  + 0.147 *  pop_I +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ( (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.018 *  pop_G + 0.147 *  pop_I  + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])) / (0.037 * pop_J + 0.018 *  pop_G + 0.147 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.071 *  pop_L   + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J    +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J  + 0.147 *  pop_I  + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L + 0.018 *  pop_G   + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ( (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.018 *  pop_G  +0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J + 0.018 *  pop_G  + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    #4 de nulle


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.384 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.071 *  pop_L  +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / (  0.147 *  pop_I +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])) / ( 0.071 *  pop_L  + 0.147 *  pop_I )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.147 *  pop_I * var_holder['eco_isic3_i'])) / (0.037 * pop_J + 0.147 *  pop_I  )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) ) / (0.037 * pop_J + 0.071 *  pop_L  )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.018 *  pop_G * var_holder['eco_isic3_g'])) / ( 0.071 *  pop_L + 0.018 *  pop_G   )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j'])  + (0.018 *  pop_G * var_holder['eco_isic3_g'])) / (0.037 * pop_J + 0.018 *  pop_G  )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / (0.037 * pop_J    +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)



                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ( (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.147 *  pop_I * var_holder['eco_isic3_i'])) / (  0.018 *  pop_G + 0.147 *  pop_I  )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= ( (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.384 *  pop_K * var_holder['eco_isic3_k'])) / ( 0.018 *  pop_G  +0.384 *  pop_K )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)




                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ( (0.018 *  pop_G * var_holder['eco_isic3_g'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.018 *  pop_G + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ( (0.147 *  pop_I * var_holder['eco_isic3_i'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.147 *  pop_I  + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)



                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.071 *  pop_L * var_holder['eco_isic3_l']) +(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.071 *  pop_L   + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.384 *  pop_K * var_holder['eco_isic3_k'])+(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.384 *  pop_K + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= ((0.037 * pop_J * var_holder['eco_isic3_j']) +(0.094 *  pop_O * var_holder['eco_isic3_o'])) / (0.037 * pop_J    + 0.094 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    #5 de nulle
                    if (var_holder['eco_isic3_j'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n=  var_holder['eco_isic3_j']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] != 0):

                        eco_isic4_n= var_holder['eco_isic3_o']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= var_holder['eco_isic3_g']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] ==0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n= var_holder['eco_isic3_l']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_j'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_i'] !=0 and var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_o'] == 0):

                        eco_isic4_n=  var_holder['eco_isic3_i']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_N', 'time' : year, 'obs_value' :eco_isic4_n}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)



    #ISIC4 O
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


    #ISIC4 P
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                    #un de nulle
                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_m'] !=0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_p= ((1 *  pop_M * var_holder['eco_isic3_m']) + (0.077 *  pop_N * var_holder['eco_isic3_n'])+(0.075 *  pop_O * var_holder['eco_isic3_o'])) / ( 1 *  pop_M + 0.077 *  pop_N + 0.075 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_m'] ==0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_p= ((0.027*pop_K * var_holder['eco_isic3_k'])  + (0.077 *  pop_N * var_holder['eco_isic3_n'])+(0.075 *  pop_O * var_holder['eco_isic3_o'])) / (0.027*pop_K  + 0.077 *  pop_N + 0.075 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_m'] !=0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_p= ((0.027*pop_K * var_holder['eco_isic3_k']) +(1 *  pop_M * var_holder['eco_isic3_m']) +(0.075 *  pop_O * var_holder['eco_isic3_o'])) / (0.027*pop_K + 1 *  pop_M  + 0.075 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_m'] !=0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_p= ((0.027*pop_K * var_holder['eco_isic3_k']) +(1 *  pop_M * var_holder['eco_isic3_m']) + (0.077 *  pop_N * var_holder['eco_isic3_n'])) / (0.027*pop_K + 1 *  pop_M + 0.077 *  pop_N  )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    # 2 de nulle

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_m'] !=0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_p= ((0.027*pop_K * var_holder['eco_isic3_k']) +(1 *  pop_M * var_holder['eco_isic3_m'])) / (0.027*pop_K + 1 *  pop_M )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_m'] ==0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_p= ((0.027*pop_K * var_holder['eco_isic3_k'])  + (0.077 *  pop_N * var_holder['eco_isic3_n'])) / (0.027*pop_K  + 0.077 *  pop_N )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_m'] ==0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_p= ((0.027*pop_K * var_holder['eco_isic3_k']) +(0.075 *  pop_O * var_holder['eco_isic3_o'])) / (0.027*pop_K   + 0.075 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_m'] !=0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_p= ((1 *  pop_M * var_holder['eco_isic3_m']) + (0.077 *  pop_N * var_holder['eco_isic3_n'])) / ( 1 *  pop_M + 0.077 *  pop_N )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_m'] !=0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_p= ((1 *  pop_M * var_holder['eco_isic3_m']) +(0.075 *  pop_O * var_holder['eco_isic3_o'])) / ( 1 *  pop_M  + 0.075 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)



                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_m'] ==0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_p= ( (0.077 *  pop_N * var_holder['eco_isic3_n'])+(0.075 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.077 *  pop_N + 0.075 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    # 3 de nulle
                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_m'] ==0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_p= var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_m'] !=0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_p= var_holder['eco_isic3_m']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_m'] ==0 and var_holder['eco_isic3_n'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_p= var_holder['eco_isic3_n']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_m'] ==0 and var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_p= var_holder['eco_isic3_o']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_P', 'time' : year, 'obs_value' :eco_isic4_p}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line


    
    #ISIC4 Q
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_n'] == 0 and var_holder['eco_isic3_l']!=0) :
                        eco_isic4_q=  var_holder['eco_isic3_l']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_Q', 'time' : year, 'obs_value' :eco_isic4_q}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_l'] == 0 and var_holder['eco_isic3_n']!=0) :
                        eco_isic4_q=  var_holder['eco_isic3_n']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_Q', 'time' : year, 'obs_value' :eco_isic4_q}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)




    #ISIC4 R

    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                    # 1 de nulle
                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_r= ((0.071 *  pop_L * var_holder['eco_isic3_l']) + (0.264 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.071 *  pop_L + 0.264 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_R', 'time' : year, 'obs_value' :eco_isic4_r}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_r= ((0.014 * pop_K * var_holder['eco_isic3_k']) + (0.264 *  pop_O * var_holder['eco_isic3_o'])) / (0.014 * pop_K  + 0.264 *  pop_O)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_R', 'time' : year, 'obs_value' :eco_isic4_r}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_r= ((0.014 * pop_K * var_holder['eco_isic3_k']) +(0.071 *  pop_L * var_holder['eco_isic3_l']) ) / (0.014 * pop_K + 0.071 *  pop_L )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_R', 'time' : year, 'obs_value' :eco_isic4_r}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    # 2 de nulle

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_r=  var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_R', 'time' : year, 'obs_value' :eco_isic4_r}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] !=0 and var_holder['eco_isic3_o'] == 0 ):

                        eco_isic4_r=  var_holder['eco_isic3_l']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_R', 'time' : year, 'obs_value' :eco_isic4_r}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_l'] ==0 and var_holder['eco_isic3_o'] != 0 ):

                        eco_isic4_r=  var_holder['eco_isic3_o']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_R', 'time' : year, 'obs_value' :eco_isic4_r}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

   
    #ISIC4 S
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                    #un de nulle
                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_j'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_s= ((0.037 *  pop_J * var_holder['eco_isic3_j']) + (0.109 *  pop_G * var_holder['eco_isic3_g'])+(0.189 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.037 *  pop_J + 0.109 *  pop_G + 0.189 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_j'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_s= ((0.014*pop_K * var_holder['eco_isic3_k'])  + (0.109 *  pop_G * var_holder['eco_isic3_g'])+(0.189 *  pop_O * var_holder['eco_isic3_o'])) / (0.014*pop_K  + 0.109 *  pop_G + 0.189 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_j'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_s= ((0.014*pop_K * var_holder['eco_isic3_k']) +(0.037 *  pop_J * var_holder['eco_isic3_j']) +(0.189 *  pop_O * var_holder['eco_isic3_o'])) / (0.014*pop_K + 0.037 *  pop_J  + 0.189 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_j'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_s= ((0.014*pop_K * var_holder['eco_isic3_k']) +(0.037 *  pop_J * var_holder['eco_isic3_j']) + (0.109 *  pop_G * var_holder['eco_isic3_g'])) / (0.014*pop_K + 0.037 *  pop_J + 0.109 *  pop_G  )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                    # 2 de nulle

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_j'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_s= ((0.014*pop_K * var_holder['eco_isic3_k']) +(0.037 *  pop_J * var_holder['eco_isic3_j'])) / (0.014*pop_K + 0.037 *  pop_J )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_j'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_s= ((0.014*pop_K * var_holder['eco_isic3_k'])  + (0.109 *  pop_G * var_holder['eco_isic3_g'])) / (0.014*pop_K  + 0.109 *  pop_G )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_j'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_s= ((0.014*pop_K * var_holder['eco_isic3_k']) +(0.189 *  pop_O * var_holder['eco_isic3_o'])) / (0.014*pop_K   + 0.189 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_j'] !=0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_s= ((0.037 *  pop_J * var_holder['eco_isic3_j']) + (0.109 *  pop_G * var_holder['eco_isic3_g'])) / ( 0.037 *  pop_J + 0.109 *  pop_G )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_j'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_s= ((0.037 *  pop_J * var_holder['eco_isic3_j']) +(0.189 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.037 *  pop_J  + 0.189 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)



                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_j'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_s= ( (0.109 *  pop_G * var_holder['eco_isic3_g'])+(0.189 *  pop_O * var_holder['eco_isic3_o'])) / ( 0.109 *  pop_G + 0.189 *  pop_O )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                    # 3 de nulle
                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_j'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_s= var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_j'] !=0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_s= var_holder['eco_isic3_j']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_j'] ==0 and var_holder['eco_isic3_g'] != 0 and var_holder['eco_isic3_o'] ==0 ):

                        eco_isic4_s= var_holder['eco_isic3_g']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_j'] ==0 and var_holder['eco_isic3_g'] == 0 and var_holder['eco_isic3_o'] !=0 ):

                        eco_isic4_s= var_holder['eco_isic3_o']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_S', 'time' : year, 'obs_value' :eco_isic4_s}
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


    #ISIC4 T
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

    #ISIC4 U

    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
                    # 1 de nulle
                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_q'] != 0 ):

                        eco_isic3_u= ((0.05 *  pop_F * var_holder['eco_isic3_f']) + (1 *  pop_Q * var_holder['eco_isic3_q'])) / ( 0.05 *  pop_F + 1 *  pop_Q)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_U', 'time' : year, 'obs_value' :eco_isic3_u}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)


                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_q'] != 0 ):

                        eco_isic3_u= ((0.014 * pop_K * var_holder['eco_isic3_k']) + (1 *  pop_Q * var_holder['eco_isic3_q'])) / (0.014 * pop_K  + 1 *  pop_Q)
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_U', 'time' : year, 'obs_value' :eco_isic3_u}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_q'] == 0 ):

                        eco_isic3_u= ((0.014 * pop_K * var_holder['eco_isic3_k']) +(0.05 *  pop_F * var_holder['eco_isic3_f']) ) / (0.014 * pop_K + 0.05 *  pop_F )
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_U', 'time' : year, 'obs_value' :eco_isic3_u}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    # 2 de nulle

                    if (var_holder['eco_isic3_k'] != 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_q'] == 0 ):

                        eco_isic3_u=  var_holder['eco_isic3_k']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_U', 'time' : year, 'obs_value' :eco_isic3_u}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_f'] !=0 and var_holder['eco_isic3_q'] == 0 ):

                        eco_isic3_u=  var_holder['eco_isic3_f']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_U', 'time' : year, 'obs_value' :eco_isic3_u}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

                    if (var_holder['eco_isic3_k'] == 0 and var_holder['eco_isic3_f'] ==0 and var_holder['eco_isic3_q'] != 0 ):

                        eco_isic3_u=  var_holder['eco_isic3_q']
                        new_line = {'ref_area' : code , 'sex' : sex, 'classif1' : 'ECO_ISIC4_U', 'time' : year, 'obs_value' :eco_isic3_u}

                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)

    #ISIC4 X
    for code in isic3.ref_area.unique():
        if code in isic3.ref_area.unique()  :
            if code == 'KOS':
                code = 'XKX'
            else :
                code =code
            print(code)
            for year in range(1995,2023):
                print(year)
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
                        isic4_from_isic3_data.loc[len(isic4_from_isic3_data)] = new_line
                        isic4_from_isic3_data = isic4_from_isic3_data.reset_index(drop=True)
    isic4_from_isic3_data.to_csv('isic4_from_isic3_data2103.csv')
    return isic4_from_isic3_data
