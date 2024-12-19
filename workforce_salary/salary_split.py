import pandas as pd


def salary_split_year(column_names,final,classif_detail,concordance,aggregation):
    salary_split= pd.DataFrame(columns = column_names)
    
    for code in final['EXIO3'].unique():
        for a in classif_detail:
            
            'This was the correspondance to the full name of exiobase sector'
            list_name = concordance.loc[concordance['ISIC REV 4_ILO_Alteryx']==a,['Name']]
            'we changed it to the exiobase sector code -> CodeNr'
            #list_name = concordance.loc[concordance['ISIC REV 4_ILO_Alteryx']==a,['CodeNr']]
            # for b in list_name['Name']:

            for b in list_name['Name']:
                salary_split=salary_split.append(pd.Series([code,b,a,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], index=[i for i in column_names]),ignore_index=True)
    
    
    
    final = final[~final['EXIO3'].str.contains("not found")]
    
    # final 2 = final.drop (columns = ['indicator','source' ,'obs_status'])
    final.to_csv('table_workforce_by_ISO3.csv', index = False)
    
    split = {}
    writer = pd.ExcelWriter('split.xlsx',engine='xlsxwriter')

    for years in range(1995,2023):
        for code in   final['EXIO3'].unique():
            print(years, code)
            #data = '/media/ntnu/Xdrive/indecol/Projects/EXIOBASE_dev/exio3/coeff_time_series/fin/current/csv/' + str(code) +'_' + str(years) + '_usebpdom.csv'               
            data = '/media/ntnu/Xdrive/indecol/Projects/MRIOs/EXIOBASE3/EXIOBASE_3_8_2/upload_to_Box/public/SUT/' + str(code) +'_' + str(years) + '.xls'               

            #df = pd.read_csv(data)      

            df = pd.read_excel(data,'bpdom_fin')      
            
            ''' we have to use this only if we read tables from /media/ntnu/Xdrive/indecol/Projects/MRIOs/EXIOBASE3/EXIOBASE_3_8_2/upload_to_Box/public/SUT/'''
            
            df.dropna(axis = 0, how = 'all', inplace = True)
            if (df.head(1) % 1  == 0).values.any():  # Delete first row if contains integer
                 df = df.iloc[1: , :]
            df.dropna(axis = 1, how = 'all', inplace = True)
            if (df. iloc[:, 0] % 1 == 0).values.any():
                df = df.iloc[: , 1:]
            df.columns = df.iloc[0]
            '''finish here'''
            
            for sector in salary_split['Sector'].unique():
                value_low_skill = df.loc[df[df.values=='w03.a'].index.values,[sector]].to_string(index=False, header=False)
                value_middle_skill = df.loc[df[df.values=='w03.b'].index.values,[sector]].to_string(index=False, header=False)
                value_high_skill = df.loc[df[df.values=='w03.c'].index.values,[sector]].to_string(index=False, header=False)
    
                salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Low-skilled']]=float(value_low_skill)/1000000
                salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Middle-skilled']]=float(value_middle_skill)/1000000
                salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: High-skilled']]=float(value_high_skill)/1000000
                salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']] = (float(value_high_skill)+float(value_middle_skill)+float(value_low_skill))/1000000

            for map_value in salary_split['Mapping'].unique():
                salary_split.loc[(salary_split['Country']==code)&(salary_split['Mapping']==map_value),['ILO data /country / sector']] = 1000 * aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==map_value)&(aggregation['time']==years)]['obs_value'].values[0]
    
            for sector in salary_split['Sector'].unique():
                '''sassurer qy uk ny ai pas de division par 0'''
                salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split']]=1000*(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']].to_string(header=False,index=False))
                )*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==concordance.loc[concordance['Name']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(salary_split.loc[(salary_split['Country'] == code)&(salary_split['Mapping'] ==concordance.loc[concordance['Name']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(header=False,index=False)),['Compensation of employees; wages, salaries, & employers social contributions: Total']].sum(axis=0).values[0])
                
                '''this lines if only for new tables'''
                #salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split']]=1000*(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']].to_string(header=False,index=False))
                #)*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==concordance.loc[concordance['CodeNr']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(salary_split.loc[(salary_split['Country'] == code)&(salary_split['Mapping'] ==concordance.loc[concordance['CodeNr']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(header=False,index=False)),['Compensation of employees; wages, salaries, & employers social contributions: Total']].sum(axis=0).values[0])
                
                # if float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']].to_string(header=False,index=False)) != 0:
                #     salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - total']]=(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split']].to_string(header=False,index=False))*float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Low-skilled']].to_string(header = False, index=False)))/float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']].to_string(header=False,index=False))
                #     salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - male']]=float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - total']].to_string(header=False,index=False))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_M')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])
                #     salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - female']]=float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - total']].to_string(header=False,index=False))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_F')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])
    
                #     salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - total']]=(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split']].to_string(header=False,index=False))*float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Middle-skilled']].to_string(header = False, index=False)))/float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']].to_string(header=False,index=False))
                #     salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - male']]=float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - total']].to_string(header=False,index=False))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_M')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])
                #     salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - female']]=float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - total']].to_string(header=False,index=False))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_F')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])
    
                #     salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - total']]=(float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split']].to_string(header=False,index=False))*float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: High-skilled']].to_string(header = False, index=False)))/float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Compensation of employees; wages, salaries, & employers social contributions: Total']].to_string(header=False,index=False))
                #     salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - male']]=float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - total']].to_string(header=False,index=False))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_M')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])
                #     salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - female']]=float(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - total']].to_string(header=False,index=False))*(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_F')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])/(aggregation.loc[(aggregation['EXIO3']==code)&(aggregation['sex']=='SEX_T')&(aggregation['classif1']==salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Mapping']].to_string(header=False,index=False))&(aggregation['time']==years)]['obs_value'].values[0])
                #     print(salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - total']])
                    
                # else :
                #     salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - total']]=0
                #     salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - total']]=0
                #     salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - total']]=0
                #     salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - male']]=0
                #     salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - male']]=0
                #     salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - male']]=0
                #     salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Low qualification employment - female']]=0
                #     salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split Middle qualification employment - female']]=0
                #     salary_split.loc[(salary_split['Country']==code)&(salary_split['Sector']==sector),['Split High qualification employment - female']]=0
    
    
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


        

            
        split[years]=salary_split.copy()
        
        # for row in split[years].index:
        #     split[years].Sector[row]=concordance.loc[concordance['CodeNr']==a,['Name']].to_string(index=False, header=False)
        # split[years].to_excel(writer, sheet_name=str(years))
    
    
    
    for year in range(1995,2023):
        split[year].to_excel(writer, sheet_name=str(year))
    
    writer.save()
    return split

