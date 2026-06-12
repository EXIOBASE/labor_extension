import pandas as pd
import os
import ray
import time

runtime_env = {
    'env_vars': {
        "RAY_memory_monitor_refresh_ms": "0",
        "RAY_record_ref_creation_sites":"1",
        "RAY_verbose_spill_logs":"0"

     }
}


def salary_split_year(column_names,final,classif_detail,concordance,aggregation,final_path):
    salary_split2= pd.DataFrame(columns = column_names)
    #print('start')
    for code in final['EXIO3'].unique():
        for a in classif_detail:

            'This was the correspondance to the full name of exiobase sector'
            #list_name = concordance.loc[concordance['ISIC REV 4_ILO_Alteryx']==a,['Name']]
            'we changed it to the exiobase sector code -> CodeNr'
            list_name = concordance.loc[concordance['ISIC REV 4_ILO_Alteryx']==a,['CodeNr']]
            # for b in list_name['Name']:

            for b in list_name['CodeNr']:
                new_row = pd.DataFrame({'Country':[code],   'Sector':[b],   'Mapping': [a],'Compensation of employees; wages, salaries, & employers social contributions: Low-skilled':[0],'Compensation of employees; wages, salaries, & employers social contributions: Middle-skilled':[0],'Compensation of employees; wages, salaries, & employers social contributions: High-skilled':[0],'Compensation of employees; wages, salaries, & employers social contributions: Total':[0],'ILO data /country / sector':[0],'Split':[0],'Split Low qualification employment - total':[0],'Split Middle qualification employment - total':[0],'Split High qualification employment - total':[0],'Split Low qualification employment - male':[0],'Split Middle qualification employment - male':[0],'Split High qualification employment - male':[0],'Split Low qualification employment - female':[0],'Split Middle qualification employment - female':[0],'Split High qualification employment - female':[0]})
                salary_split2=pd.concat([salary_split2,new_row])
                #salary_split2=salary_split2.append(pd.Series([code,b,a,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], index=[i for i in column_names]),ignore_index=True)



    #final = final[~final['EXIO3'].str.contains("")]
    final = final[final['EXIO3'] != ""]
    final = final[final['EXIO3'].notna()]

    # final 2 = final.drop (columns = ['indicator','source' ,'obs_status'])
    final.to_csv(final_path / 'table_workforce_by_ISO3.csv', index = False)

    split = {}

    # writer = pd.ExcelWriter('split.xlsx',engine='xlsxwriter')

    ray.init(runtime_env=runtime_env,num_cpus = os.cpu_count()-4)

    @ray.remote
    def calcul_ray(years,salary_split2):
        salary_split = salary_split2.copy()
        for code in   final['EXIO3'].unique():
            #for code in  ['WA','WE','FR']:

            print(years,code)
            data = '../Xdrive/indecol/USERS/Kajwan/Box/EXIOBASE/EXIOBASE_3_10_1/upload_prep/raw/SUT/current/' + str(code) +'_' + str(years) + '_usebpdom.csv'
            data2 = '../Xdrive/indecol/USERS/Kajwan/Box/EXIOBASE/EXIOBASE_3_10_1/upload_prep/raw/SUT/current/' + str(code) +'_' + str(years) + '_sup.csv'


            #data = '/media/ntnu/Xdrive/indecol/Projects/MRIOs/EXIOBASE3/EXIOBASE_3_8_2/upload_to_Box/public/SUT/' + str(code) +'_' + str(years) + '.xls'               
            #data = '../Xdrive/indecol/Projects/MRIOs/EXIOBASE3/EXIOBASE_3_8_2/upload_to_Box/public/SUT/' + str(code) +'_' + str(years) + '.xls'

            df = pd.read_csv(data)
            output = pd.read_csv(data2)


            #df = pd.read_excel(data,'bpdom_fin')      

            ''' we have to use this only if we read tables from /media/ntnu/Xdrive/indecol/Projects/MRIOs/EXIOBASE3/EXIOBASE_3_8_2/upload_to_Box/public/SUT/'''

            #df.dropna(axis = 0, how = 'all', inplace = True)
            #if (df.head(1) % 1  == 0).values.any():  # Delete first row if contains integer
            #     df = df.iloc[1: , :]
            #df.dropna(axis = 1, how = 'all', inplace = True)
            #if (df. iloc[:, 0] % 1 == 0).values.any():
            #    df = df.iloc[: , 1:]
            #df.columns = df.iloc[0]
            '''finish here'''
            ISICA = concordance.loc[(concordance['ISIC_A'] == 1)]
            code_ISICA = ISICA.CodeNr.unique()
            sumA_wa = df.loc[df[df['Row'] == 'w03.a'].index[0], df.columns.isin(code_ISICA)].sum()
            sumA_wb = df.loc[df[df['Row'] == 'w03.b'].index[0], df.columns.isin(code_ISICA)].sum()
            sumA_wc = df.loc[df[df['Row'] == 'w03.c'].index[0], df.columns.isin(code_ISICA)].sum()

            ISICB = concordance.loc[(concordance['ISIC_B'] == 1)]
            code_ISICB = ISICB.CodeNr.unique()
            sumB_wa = df.loc[df[df['Row'] == 'w03.a'].index[0], df.columns.isin(code_ISICB)].sum()
            sumB_wb = df.loc[df[df['Row'] == 'w03.b'].index[0], df.columns.isin(code_ISICB)].sum()
            sumB_wc = df.loc[df[df['Row'] == 'w03.c'].index[0], df.columns.isin(code_ISICB)].sum()

            ISICC = concordance.loc[(concordance['ISIC_C'] == 1)]
            code_ISICC = ISICC.CodeNr.unique()
            sumC_wa = df.loc[df[df['Row'] == 'w03.a'].index[0], df.columns.isin(code_ISICC)].sum()
            sumC_wb = df.loc[df[df['Row'] == 'w03.b'].index[0], df.columns.isin(code_ISICC)].sum()
            sumC_wc = df.loc[df[df['Row'] == 'w03.c'].index[0], df.columns.isin(code_ISICC)].sum()

            ISICDE = concordance.loc[(concordance['ISIC_D'] == 1 )| ( concordance['ISIC_E'] == 1 )]
            code_ISICDE = ISICDE.CodeNr.unique()
            sumDE_wa = df.loc[df[df['Row'] == 'w03.a'].index[0], df.columns.isin(code_ISICDE)].sum()
            sumDE_wb = df.loc[df[df['Row'] == 'w03.b'].index[0], df.columns.isin(code_ISICDE)].sum()
            sumDE_wc = df.loc[df[df['Row'] == 'w03.c'].index[0], df.columns.isin(code_ISICDE)].sum()

            ISICF = concordance.loc[(concordance['ISIC_F'] == 1)]
            code_ISICF = ISICF.CodeNr.unique()
            sumF_wa = df.loc[df[df['Row'] == 'w03.a'].index[0], df.columns.isin(code_ISICF)].sum()
            sumF_wb = df.loc[df[df['Row'] == 'w03.b'].index[0], df.columns.isin(code_ISICF)].sum()
            sumF_wc = df.loc[df[df['Row'] == 'w03.c'].index[0], df.columns.isin(code_ISICF)].sum()

            ISICG = concordance.loc[(concordance['ISIC_G'] == 1)]
            code_ISICG = ISICG.CodeNr.unique()
            sumG_wa = df.loc[df[df['Row'] == 'w03.a'].index[0], df.columns.isin(code_ISICG)].sum()
            sumG_wb = df.loc[df[df['Row'] == 'w03.b'].index[0], df.columns.isin(code_ISICG)].sum()
            sumG_wc = df.loc[df[df['Row'] == 'w03.c'].index[0], df.columns.isin(code_ISICG)].sum()

            ISICHJ = concordance.loc[(concordance['ISIC_H'] == 1 )| ( concordance['ISIC_J'] == 1 )]
            code_ISICHJ = ISICHJ.CodeNr.unique()
            sumHJ_wa = df.loc[df[df['Row'] == 'w03.a'].index[0], df.columns.isin(code_ISICHJ)].sum()
            sumHJ_wb = df.loc[df[df['Row'] == 'w03.b'].index[0], df.columns.isin(code_ISICHJ)].sum()
            sumHJ_wc = df.loc[df[df['Row'] == 'w03.c'].index[0], df.columns.isin(code_ISICHJ)].sum()

            ISICK = concordance.loc[(concordance['ISIC_K'] == 1 )| ( concordance['ISIC_K'] == 1 )]
            code_ISICK = ISICK.CodeNr.unique()
            sumK_wa = df.loc[df[df['Row'] == 'w03.a'].index[0], df.columns.isin(code_ISICK)].sum()
            sumK_wb = df.loc[df[df['Row'] == 'w03.b'].index[0], df.columns.isin(code_ISICK)].sum()
            sumK_wc = df.loc[df[df['Row'] == 'w03.c'].index[0], df.columns.isin(code_ISICK)].sum()

            ISICLMN = concordance.loc[(concordance['ISIC_L'] == 1 )| ( concordance['ISIC_M'] == 1 )| ( concordance['ISIC_N'] == 1 )]
            code_ISICLMN = ISICLMN.CodeNr.unique()
            sumLMN_wa = df.loc[df[df['Row'] == 'w03.a'].index[0], df.columns.isin(code_ISICLMN)].sum()
            sumLMN_wb = df.loc[df[df['Row'] == 'w03.b'].index[0], df.columns.isin(code_ISICLMN)].sum()
            sumLMN_wc = df.loc[df[df['Row'] == 'w03.c'].index[0], df.columns.isin(code_ISICLMN)].sum()

            ISICRSTU = concordance.loc[(concordance['ISIC_R'] == 1 )| ( concordance['ISIC_S'] == 1 )| ( concordance['ISIC_T'] == 1 )| ( concordance['ISIC_U'] == 1 )]
            code_ISICRSTU = ISICRSTU.CodeNr.unique()
            sumRSTU_wa = df.loc[df[df['Row'] == 'w03.a'].index[0], df.columns.isin(code_ISICRSTU)].sum()
            sumRSTU_wb = df.loc[df[df['Row'] == 'w03.b'].index[0], df.columns.isin(code_ISICRSTU)].sum()
            sumRSTU_wc = df.loc[df[df['Row'] == 'w03.c'].index[0], df.columns.isin(code_ISICRSTU)].sum()

            code_ISICTOTAL = concordance.CodeNr.unique()
            sumTOTAL_wa = df.loc[df[df['Row'] == 'w03.a'].index[0], df.columns.isin(code_ISICTOTAL)].sum()
            sumTOTAL_wb = df.loc[df[df['Row'] == 'w03.b'].index[0], df.columns.isin(code_ISICTOTAL)].sum()
            sumTOTAL_wc = df.loc[df[df['Row'] == 'w03.c'].index[0], df.columns.isin(code_ISICTOTAL)].sum()

            
            for sector in salary_split['Sector'].unique():
                value_low_skill = df.loc[df[df.values=='w03.a'].index.values,[sector]].to_string(index=False, header=False)
                value_middle_skill = df.loc[df[df.values=='w03.b'].index.values,[sector]].to_string(index=False, header=False)
                value_high_skill = df.loc[df[df.values=='w03.c'].index.values,[sector]].to_string(index=False, header=False)
    
                salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Low-skilled']]=float(value_low_skill)/1000000
                salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Middle-skilled']]=float(value_middle_skill)/1000000
                salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: High-skilled']]=float(value_high_skill)/1000000
                salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']] = (float(value_high_skill)+float(value_middle_skill)+float(value_low_skill))/1000000
            for map_value in salary_split['Mapping'].unique():
                #salary_split.loc[(salary_split['Country']==code)&(salary_split['Mapping']==map_value),['ILO data /country / sector']] = 1000 * aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==map_value)&(aggregation['time']==years)]['obs_value'].values[0]
                '''need to change the unit'''
                salary_split.loc[(salary_split['Country']==code)&(salary_split['Mapping']==map_value),['ILO data /country / sector']] =  aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==map_value)&(aggregation['time']==years)]['obs_value'].values[0]
            for sector in salary_split['Sector'].unique():
                #print(sector)
                salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split']]=(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']].to_string(header=False,index=False)))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==concordance.loc[concordance['CodeNr']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(salary_split.loc[(salary_split['Country'] == code)&(salary_split['Mapping'] ==concordance.loc[concordance['CodeNr']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(header=False,index=False)),['Compensation of employees; wages, salaries, & employers social contributions: Total']].sum(axis=0).values[0])
                if float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']].to_string(header=False,index=False)) != 0:

                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - total']]=(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split']].to_string(header=False,index=False))*float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Low-skilled']].to_string(header = False, index=False)))/float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']].to_string(header=False,index=False))
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - male']]=float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - total']].to_string(header=False,index=False))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_M')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - female']]=float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - total']].to_string(header=False,index=False))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_F')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])

                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - total']]=(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split']].to_string(header=False,index=False))*float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Middle-skilled']].to_string(header = False, index=False)))/float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']].to_string(header=False,index=False))
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - male']]=float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - total']].to_string(header=False,index=False))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_M')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - female']]=float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - total']].to_string(header=False,index=False))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_F')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])

                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - total']]=(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split']].to_string(header=False,index=False))*float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: High-skilled']].to_string(header = False, index=False)))/float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']].to_string(header=False,index=False))
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - male']]=float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - total']].to_string(header=False,index=False))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_M')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - female']]=float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - total']].to_string(header=False,index=False))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_F')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])
                


                else :
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - total']]=0
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - total']]=0
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - total']]=0
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - male']]=0
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - male']]=0
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - male']]=0
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - female']]=0
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - female']]=0
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - female']]=0
                    
                
                
            sumLST =  salary_split.loc[(salary_split['Country']==code),'Split Low qualification employment - total'].sum()
            sumMST = salary_split.loc[(salary_split['Country']==code),'Split Middle qualification employment - total'].sum()
            sumHST = salary_split.loc[(salary_split['Country']==code),'Split High qualification employment - total'].sum()

            sumLSM =  salary_split.loc[(salary_split['Country']==code),'Split Low qualification employment - male'].sum()
            sumMSM = salary_split.loc[(salary_split['Country']==code),'Split Middle qualification employment - male'].sum()
            sumHSM = salary_split.loc[(salary_split['Country']==code),'Split High qualification employment - male'].sum()

            sumLSW =  salary_split.loc[(salary_split['Country']==code),'Split Low qualification employment - female'].sum()
            sumMSW = salary_split.loc[(salary_split['Country']==code),'Split Middle qualification employment - female'].sum()
            sumHSW = salary_split.loc[(salary_split['Country']==code),'Split High qualification employment - female'].sum()

            'sum all skill total population'
            sumAST = sumLST+sumMST+sumHST
            sumASM =sumLSM+sumMSM+sumHSM
            sumASW = sumLSW+sumMSW+sumHSW    


            for sector in salary_split['Sector'].unique():
                value_low_skill = df.loc[df[df.values=='w03.a'].index.values,[sector]].to_string(index=False, header=False)
                value_middle_skill = df.loc[df[df.values=='w03.b'].index.values,[sector]].to_string(index=False, header=False)
                value_high_skill = df.loc[df[df.values=='w03.c'].index.values,[sector]].to_string(index=False, header=False)
    
                salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Low-skilled']]=float(value_low_skill)/1000000
                salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Middle-skilled']]=float(value_middle_skill)/1000000
                salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: High-skilled']]=float(value_high_skill)/1000000
                salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']] = (float(value_high_skill)+float(value_middle_skill)+float(value_low_skill))/1000000
            for map_value in salary_split['Mapping'].unique():
                #salary_split.loc[(salary_split['Country']==code)&(salary_split['Mapping']==map_value),['ILO data /country / sector']] = 1000 * aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==map_value)&(aggregation['time']==years)]['obs_value'].values[0]
                '''need to change the unit'''
                salary_split.loc[(salary_split['Country']==code)&(salary_split['Mapping']==map_value),['ILO data /country / sector']] =  aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==map_value)&(aggregation['time']==years)]['obs_value'].values[0]
            for sector in salary_split['Sector'].unique():
               
                salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split']]=(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']].to_string(header=False,index=False)))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==concordance.loc[concordance['CodeNr']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(salary_split.loc[(salary_split['Country'] == code)&(salary_split['Mapping'] ==concordance.loc[concordance['CodeNr']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(header=False,index=False)),['Compensation of employees; wages, salaries, & employers social contributions: Total']].sum(axis=0).values[0])
                if float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']].to_string(header=False,index=False)) != 0:

                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - total']]=(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split']].to_string(header=False,index=False))*float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Low-skilled']].to_string(header = False, index=False)))/float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']].to_string(header=False,index=False))
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - male']]=float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - total']].to_string(header=False,index=False))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_M')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - female']]=float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - total']].to_string(header=False,index=False))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_F')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])

                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - total']]=(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split']].to_string(header=False,index=False))*float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Middle-skilled']].to_string(header = False, index=False)))/float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']].to_string(header=False,index=False))
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - male']]=float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - total']].to_string(header=False,index=False))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_M')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - female']]=float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - total']].to_string(header=False,index=False))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_F')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])

                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - total']]=(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split']].to_string(header=False,index=False))*float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: High-skilled']].to_string(header = False, index=False)))/float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']].to_string(header=False,index=False))
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - male']]=float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - total']].to_string(header=False,index=False))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_M')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - female']]=float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - total']].to_string(header=False,index=False))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_F')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])
                elif (float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']].to_string(header=False,index=False)) == 0 and sector in ['i55','i75','i80','i85'] and float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Mapping']==concordance.loc[concordance['CodeNr']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(header=False,index=False)),['ILO data /country / sector']].to_string(header = False,index=False))!=0):
                    #float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Mapping']==concordance.loc[concordance['CodeNr']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(header=False,index=False)),['ILO data /country / sector']].to_string(header = False,index=False)))
                    #print('2', sector)

                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - total']] =float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Mapping']==concordance.loc[concordance['CodeNr']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(header=False,index=False)),['ILO data /country / sector']].to_string(header = False,index=False))*sumLST/sumAST
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - total']] =float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Mapping']==concordance.loc[concordance['CodeNr']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(header=False,index=False)),['ILO data /country / sector']].to_string(header = False,index=False))*sumMST/sumAST
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - total']] = float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Mapping']==concordance.loc[concordance['CodeNr']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(header=False,index=False)),['ILO data /country / sector']].to_string(header = False,index=False))*sumHST/sumAST


                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - male']] = float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Mapping']==concordance.loc[concordance['CodeNr']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(header=False,index=False)),['ILO data /country / sector']].to_string(header = False,index=False))*sumLSM/sumAST
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - male']] = float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Mapping']==concordance.loc[concordance['CodeNr']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(header=False,index=False)),['ILO data /country / sector']].to_string(header = False,index=False))*sumMSM/sumAST
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - male']] = float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Mapping']==concordance.loc[concordance['CodeNr']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(header=False,index=False)),['ILO data /country / sector']].to_string(header = False,index=False))*sumHSM/sumAST


                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - female']] = float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Mapping']==concordance.loc[concordance['CodeNr']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(header=False,index=False)),['ILO data /country / sector']].to_string(header = False,index=False))*sumLSW/sumAST
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - female']] = float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Mapping']==concordance.loc[concordance['CodeNr']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(header=False,index=False)),['ILO data /country / sector']].to_string(header = False,index=False))*sumMSW/sumAST
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - female']] =float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Mapping']==concordance.loc[concordance['CodeNr']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(header=False,index=False)),['ILO data /country / sector']].to_string(header = False,index=False))*sumHSW/sumAST



                else :
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - total']]=0
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - total']]=0
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - total']]=0
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - male']]=0
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - male']]=0
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - male']]=0
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - female']]=0
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - female']]=0
                    salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - female']]=0
             
            salary_split=salary_split.fillna(0)
            
            
            values_split=[]
            for sub in code_ISICA:
                values_split.append(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False)))
                float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False))
            pourcent = []
            total_value = 0
            item_value = []
            
            if len(set(values_split)) == 1 :
                for item in set(values_split):
                    if item == 0 or isnan(item):
                        for sub in code_ISICA:
                            sum_item = output[sub].sum()
                            total_value = total_value+sum_item
                            item_value.append(sum_item)
		for item in item_value :
                	pourcent.append(100*item/total_value)

		for idx, x in enumerate(code_ISICA):
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']] = float(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']=='ECO_DETAILS_A')&(aggregation['time']==years)]['obs_value'].to_string(header=False,index=False)) * pourcent[idx] / 100
                
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLST/sumAST	
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - total']] = (float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMST/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHST/sumAST


                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumHSM/sumAST


                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumLSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))  *sumMSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHSW/sumAST
                
                
                
                
                
            values_split=[]
            for sub in code_ISICRSTU:
                values_split.append(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False)))
                float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False))
            pourcent = []
            total_value = 0
            item_value = []
            
            if len(set(values_split)) == 1 :
                for item in set(values_split):
                    if item == 0 or isnan(item):
                        for sub in code_ISICRSTU:
                            sum_item = output[sub].sum()
                            total_value = total_value+sum_item
                            item_value.append(sum_item)
            	for item in item_value :
                	pourcent.append(100*item/total_value)

            	for idx, x in enumerate(code_ISICRSTU):
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']] = float(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']=='ECO_DETAILS_RSTU')&(aggregation['time']==years)]['obs_value'].to_string(header=False,index=False)) * pourcent[idx] / 100
                
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLST/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - total']] = (float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMST/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHST/sumAST


                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumHSM/sumAST


                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumLSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))  *sumMSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHSW/sumAST
                
                
                
            values_split=[]
            for sub in code_ISICB:
                values_split.append(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False)))
                float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False))
            pourcent = []
            total_value = 0
            item_value = []
            if len(set(values_split)) == 1 :
                for item in set(values_split):
                    if item == 0 or isnan(item):
                        for sub in code_ISICB:
                            sum_item = output[sub].sum()
                            total_value = total_value+sum_item
                            item_value.append(sum_item)
            	for item in item_value :
                	pourcent.append(100*item/total_value)

            	for idx, x in enumerate(code_ISICB):
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']] = float(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']=='ECO_DETAILS_B')&(aggregation['time']==years)]['obs_value'].to_string(header=False,index=False)) * pourcent[idx] / 100
                
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLST/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - total']] = (float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMST/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHST/sumAST


                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumHSM/sumAST


                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumLSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))  *sumMSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHSW/sumAST
                
                
            values_split=[]
            for sub in code_ISICC:
                values_split.append(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False)))
                float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False))
            pourcent = []
            total_value = 0
            item_value = []
            if len(set(values_split)) == 1 :
                for item in set(values_split):
                    if item == 0 or isnan(item):
                        for sub in code_ISICC:
                            sum_item = output[sub].sum()
                            total_value = total_value+sum_item
                            item_value.append(sum_item)
            	for item in item_value :
                	pourcent.append(100*item/total_value)

            	for idx, x in enumerate(code_ISICC):
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']] = float(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']=='ECO_DETAILS_C')&(aggregation['time']==years)]['obs_value'].to_string(header=False,index=False)) * pourcent[idx] / 100
                
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLST/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - total']] = (float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMST/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHST/sumAST


                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumHSM/sumAST


                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumLSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))  *sumMSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHSW/sumAST
                               
                
            values_split=[]
            for sub in code_ISICDE:
                values_split.append(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False)))
                float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False))
            pourcent = []
            total_value = 0
            item_value = []
            if len(set(values_split)) == 1 :
                for item in set(values_split):
                    if item == 0 or isnan(item):
                        for sub in code_ISICDE:
                            sum_item = output[sub].sum()
                            total_value = total_value+sum_item
                            item_value.append(sum_item)
            	for item in item_value :
                	pourcent.append(100*item/total_value)

            	for idx, x in enumerate(code_ISICDE):
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']] = float(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']=='ECO_DETAILS_DE')&(aggregation['time']==years)]['obs_value'].to_string(header=False,index=False)) * pourcent[idx] / 100
                	
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLST/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - total']] = (float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMST/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHST/sumAST


                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumHSM/sumAST


                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumLSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))  *sumMSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHSW/sumAST
                               
                        
            values_split=[]
            for sub in code_ISICF:
                values_split.append(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False)))
                float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False))
            pourcent = []
            total_value = 0
            item_value = []
            if len(set(values_split)) == 1 :
                for item in set(values_split):
                    if item == 0 or isnan(item):
                        for sub in code_ISICF:
                            sum_item = output[sub].sum()
                            total_value = total_value+sum_item
                            item_value.append(sum_item)
            	for item in item_value :
                	pourcent.append(100*item/total_value)

            	for idx, x in enumerate(code_ISICF):
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']] = float(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']=='ECO_DETAILS_F')&(aggregation['time']==years)]['obs_value'].to_string(header=False,index=False)) * pourcent[idx] / 100
                
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLST/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - total']] = (float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMST/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHST/sumAST


                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumHSM/sumAST
	
	
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumLSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))  *sumMSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHSW/sumAST
                               
        
                        
                
            values_split=[]
            for sub in code_ISICG:
                values_split.append(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False)))
                float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False))
            pourcent = []
            total_value = 0
            item_value = []
            if len(set(values_split)) == 1 :
                for item in set(values_split):
                    if item == 0 or isnan(item):
                        for sub in code_ISICG:
                            sum_item = output[sub].sum()
                            total_value = total_value+sum_item
                            item_value.append(sum_item)
            	for item in item_value :
                	pourcent.append(100*item/total_value)

            	for idx, x in enumerate(code_ISICG):
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']] = float(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']=='ECO_DETAILS_G')&(aggregation['time']==years)]['obs_value'].to_string(header=False,index=False)) * pourcent[idx] / 100
                
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLST/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - total']] = (float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMST/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHST/sumAST


                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumHSM/sumAST


                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumLSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))  *sumMSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHSW/sumAST


            values_split=[]
            for sub in code_ISICHJ:
                values_split.append(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False)))
                float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False))
            pourcent = []
            total_value = 0
            item_value = []
            if len(set(values_split)) == 1 :
                for item in set(values_split):
                    if item == 0 or isnan(item):
                        for sub in code_ISICHJ:
                            sum_item = output[sub].sum()
                            total_value = total_value+sum_item
                            item_value.append(sum_item)
            	for item in item_value :
                	pourcent.append(100*item/total_value)

            	for idx, x in enumerate(code_ISICHJ):
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']] = float(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']=='ECO_DETAILS_HJ')&(aggregation['time']==years)]['obs_value'].to_string(header=False,index=False)) * pourcent[idx] / 100
                
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLST/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - total']] = (float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMST/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHST/sumAST


                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumHSM/sumAST


                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumLSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))  *sumMSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHSW/sumAST
                               
        
            values_split=[]
            for sub in code_ISICK:
                values_split.append(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False)))
                float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False))
            pourcent = []
            total_value = 0
            item_value = []
            if len(set(values_split)) == 1 :
                for item in set(values_split):
                    if item == 0 or isnan(item):
                        for sub in code_ISICK:
                            sum_item = output[sub].sum()
                            total_value = total_value+sum_item
                            item_value.append(sum_item)
            	for item in item_value :
                	pourcent.append(100*item/total_value)

            	for idx, x in enumerate(code_ISICK):
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']] = float(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']=='ECO_DETAILS_K')&(aggregation['time']==years)]['obs_value'].to_string(header=False,index=False)) * pourcent[idx] / 100
                
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLST/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - total']] = (float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMST/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHST/sumAST


                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumHSM/sumAST


                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumLSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))  *sumMSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHSW/sumAST
                     
            values_split=[]
            for sub in code_ISICLMN:
                values_split.append(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False)))
                float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sub),['Split']].to_string(header=False, index=False))
            pourcent = []
            total_value = 0
            item_value = []
            if len(set(values_split)) == 1 :
                for item in set(values_split):
                    if item == 0 or isnan(item):
                        for sub in code_ISICLMN:
                            sum_item = output[sub].sum()
                            total_value = total_value+sum_item
                            item_value.append(sum_item)
            	for item in item_value :
                	pourcent.append(100*item/total_value)

            	for idx, x in enumerate(code_ISICLMN):
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']] = float(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']=='ECO_DETAILS_LMN')&(aggregation['time']==years)]['obs_value'].to_string(header=False,index=False)) * pourcent[idx] / 100
                
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLST/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - total']] = (float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMST/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - total']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHST/sumAST


                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumLSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumMSM/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - male']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumHSM/sumAST


                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Low qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))*sumLSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split Middle qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False)))  *sumMSW/sumAST
                	salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split High qualification employment - female']] =(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==x),['Split']].to_string(header=False,index=False))) *sumHSW/sumAST
                
                                        
        test = salary_split.copy()

        split[years]=salary_split.copy()
        return test

    results = [ray.get([calcul_ray.remote(years, salary_split2) for years in range(1995,2023)])]
    '''1995 2023'''
    '''ICI il faut faire un pause pb avec ray'''

    for a,b in zip(results[0],range(1995,2023)) :
        print(b,a)
        split[b] = a

    time.sleep(30)
    ray.shutdown()
    print('done')
    writer = pd.ExcelWriter(final_path / 'split_workforce_by_skill_newSUT.xlsx',engine='xlsxwriter')

    for year in range(1995,2023):
        split[year].to_excel(writer, sheet_name=str(year))
    writer.close()

    return split

