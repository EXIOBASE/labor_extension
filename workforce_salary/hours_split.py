import pandas as pd

''' 
ATTENTION JE DOIS GENERER UN NOUVEAU WEIGHTED HOURS !!!'''

def hours_split_year(all_countries,concordance,av2):
    hours_split= pd.DataFrame(columns = ['EXIO3','Sector','Mapping', 'Hours High qualification employement - total', 'Hours Middle qualification employement - total', 'Hours Low qualification employement - total','Hours High qualification employement - male', 'Hours Middle qualification employement - male', 'Hours Low qualification employement - male','Hours High qualification employement - female', 'Hours Middle qualification employement - female', 'Hours Low qualification employement - female'])
    
    for code in all_countries.EXIO3:
        # for a in hours_main_country.classif1.unique():
        for a in hours_RoW.classif1.unique():
    
            'This was the correspondance to the full name of exiobase sector'
            list_name = concordance.loc[concordance['ISIC REV 4_ILO_Alteryx']==a,['Name']]
            'we changed it to the exiobase sector code -> CodeNr'
            #list_name = concordance.loc[concordance['ISIC REV 4_ILO_Alteryx']==a,['CodeNr']]
            # for b in list_name['Name']:

            for b in list_name['Name']:
                hours_split=hours_split.append(pd.Series([code,b,a,0,0,0,0,0,0,0,0,0], index=[i for i in hours_split.columns]),ignore_index=True)
    hours_split_empty = hours_split.copy()
    
    xl = pd.ExcelFile('split_updated_1610.xlsx')



    hourSplit = {}
    writer = pd.ExcelWriter('hours_split.xlsx',engine='xlsxwriter')

    for years in range(2020,2021):
        hours_split = hours_split_empty.copy()

        workforce_year = xl.parse(str(years))

        for code in  all_countries.EXIO3:
            print(code)
            if code =='AT':
                if code in list_RoW :      
                    for sector in hours_split['Sector'].unique():
                        pop_high_skill_men = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == sector),'Split High qualification employment - male'].to_string(index=False, header=False))
                        pop_middle_skill_men = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == sector),'Split Middle qualification employment - male'].to_string(index=False, header=False))
                        pop_low_skill_men = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == sector),'Split Low qualification employment - male'].to_string(index=False, header=False))
    
                        pop_high_skill_women = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == sector),'Split High qualification employment - female'].to_string(index=False, header=False))
                        pop_middle_skill_women = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == sector),'Split Middle qualification employment - female'].to_string(index=False, header=False))
                        pop_low_skill_women = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == sector),'Split Low qualification employment - female'].to_string(index=False, header=False))
    
    
                        vacation = float(vacation_average.loc[vacation_average.EXIO3 == code,'Total Paid Vacation Days'].to_string(index=False,header=False))
                        
                        classif1 = concordance.loc[concordance['Name']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(index = False, header = False)
                        
                        hours_M = float(av2.loc[(av2.EXIO3 ==code) & (av2.sex == 'SEX_M') &(av2.classif1==classif1)&(av2.time == years),'Weighted average working hours'].to_string(index = False, header = False))
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - male' ] = pop_high_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - male' ] = pop_middle_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - male' ] = pop_low_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        
                        hours_F = float(av2.loc[(av2.EXIO3 ==code) & (av2.sex == 'SEX_F') &(av2.classif1==classif1)&(av2.time == years),'Weighted average working hours'].to_string(index = False, header = False))
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - female' ] = pop_high_skill_women * (hours_F/5) * (365-vacation) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - female' ] = pop_middle_skill_women * (hours_F/5) * (365-vacation) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - female' ] = pop_low_skill_women * (hours_F/5) * (365-vacation) / 1000000
    
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - total' ] = (pop_high_skill_men * (hours_M/5) * (365-vacation) / 1000000) + (pop_high_skill_women * (hours_F/5) * (365-vacation) / 1000000)
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - total' ] = (pop_middle_skill_men * (hours_M/5) * (365-vacation) / 1000000) + (pop_middle_skill_women * (hours_F/5) * (365-vacation) / 1000000)
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - total' ] = (pop_low_skill_men * (hours_M/5) * (365-vacation) / 1000000) + (pop_low_skill_women * (hours_F/5) * (365-vacation) / 1000000) 
                        
                elif code =='TW':
                    for sector in hours_split['Sector'].unique():
                        pop_high_skill_men = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == sector),'Split High qualification employment - male'].to_string(index=False, header=False))
                        pop_middle_skill_men = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == sector),'Split Middle qualification employment - male'].to_string(index=False, header=False))
                        pop_low_skill_men = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == sector),'Split Low qualification employment - male'].to_string(index=False, header=False))
    
                        pop_high_skill_women = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == sector),'Split High qualification employment - female'].to_string(index=False, header=False))
                        pop_middle_skill_women = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == sector),'Split Middle qualification employment - female'].to_string(index=False, header=False))
                        pop_low_skill_women = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == sector),'Split Low qualification employment - female'].to_string(index=False, header=False))
    
    
                        vacation = float(vacation_average.loc[vacation_average.EXIO3 == 'WA','Total Paid Vacation Days'].to_string(index=False,header=False))
                        
                        classif1 = concordance.loc[concordance['Name']==sector,['ISIC REV 4_ILO_Alteryx']].to_string(index = False, header = False)
                        
                        hours_M = float(av2.loc[(av2.EXIO3 =='WA') & (av2.sex == 'SEX_M') &(av2.classif1==classif1)&(av2.time == years),'Weighted average working hours'].to_string(index = False, header = False))
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - male' ] = pop_high_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - male' ] = pop_middle_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - male' ] = pop_low_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        
                        hours_F = float(av2.loc[(av2.EXIO3 =='WA') & (av2.sex == 'SEX_F') &(av2.classif1==classif1)&(av2.time == years),'Weighted average working hours'].to_string(index = False, header = False))
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - female' ] = pop_high_skill_women * (hours_F/5) * (365-vacation) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - female' ] = pop_middle_skill_women * (hours_F/5) * (365-vacation) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - female' ] = pop_low_skill_women * (hours_F/5) * (365-vacation) / 1000000
    
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - total' ] = (pop_high_skill_men * (hours_M/5) * (365-vacation) / 1000000) + (pop_high_skill_women * (hours_F/5) * (365-vacation) / 1000000)
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - total' ] = (pop_middle_skill_men * (hours_M/5) * (365-vacation) / 1000000) + (pop_middle_skill_women * (hours_F/5) * (365-vacation) / 1000000)
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - total' ] = (pop_low_skill_men * (hours_M/5) * (365-vacation) / 1000000) + (pop_low_skill_women * (hours_F/5) * (365-vacation) / 1000000) 
                        
                    
                else :
                    for sector in hours_split['Sector'].unique():
                        pop_high_skill_men = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == sector),'Split High qualification employment - male'].to_string(index=False, header=False))
                        print(sector,pop_high_skill_men)
                        pop_middle_skill_men = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == sector),'Split Middle qualification employment - male'].to_string(index=False, header=False))
                        pop_low_skill_men = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == sector),'Split Low qualification employment - male'].to_string(index=False, header=False))
    
                        pop_high_skill_women = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == sector),'Split High qualification employment - female'].to_string(index=False, header=False))
                        pop_middle_skill_women = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == sector),'Split Middle qualification employment - female'].to_string(index=False, header=False))
                        pop_low_skill_women = 1000* float(workforce_year.loc[(workforce_year.Country == code) & (workforce_year.Sector == sector),'Split Low qualification employment - female'].to_string(index=False, header=False))
    
    
                        vacation = float(vacation_average.loc[vacation_average.EXIO3 == code,'Total Paid Vacation Days'].to_string(index=False,header=False))
                        classif1 = concordance.loc[concordance['Name']==sector,['Summary']].to_string(index = False, header = False)
                        letter = classif1.split('.',1)[0]
                        print(letter)
                        hours_M = float(hours.loc[(hours.EXIO3 ==code) & (hours.sex == 'SEX_M') &(hours.classif1=='ECO_DETAILS_'+letter)&(hours.time == years),'average weekly hours'].to_string(index = False, header = False))
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - male' ] = pop_high_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - male' ] = pop_middle_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - male' ] = pop_low_skill_men * (hours_M/5) * (365-vacation) / 1000000
                        hours_F = float(hours.loc[(hours.EXIO3 ==code) & (hours.sex == 'SEX_F') &(hours.classif1=='ECO_DETAILS_'+letter)&(hours.time == years),'average weekly hours'].to_string(index = False, header = False))
    
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - female' ] = pop_high_skill_women * (hours_F/5) * (365-vacation) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - female' ] = pop_middle_skill_women * (hours_F/5) * (365-vacation) / 1000000
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - female' ] = pop_low_skill_women * (hours_F/5) * (365-vacation) / 1000000
    
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours High qualification employement - total' ] = (pop_high_skill_men * (hours_M/5) * (365-vacation) / 1000000) + (pop_high_skill_women * (hours_F/5) * (365-vacation) / 1000000)
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Middle qualification employement - total' ] = (pop_middle_skill_men * (hours_M/5) * (365-vacation) / 1000000) + (pop_middle_skill_women * (hours_F/5) * (365-vacation) / 1000000)
                        hours_split.loc[(hours_split.EXIO3 ==code) & (hours_split.Sector==sector),'Hours Low qualification employement - total' ] = (pop_low_skill_men * (hours_M/5) * (365-vacation) / 1000000) + (pop_low_skill_women * (hours_F/5) * (365-vacation) / 1000000) 
          
        hourSplit[years]=hours_split.copy()


        writer = pd.ExcelWriter('hours_split_0312.xlsx',engine='xlsxwriter')
    
        for year in range(1995,2023):
            hourSplit[year].to_excel(writer, sheet_name=str(year))        
        writer.save()
        


        xls = pd.ExcelFile('hours_split_0312.xlsx')
        xls2 = pd.ExcelFile('split_updated_1610.xlsx')
        exio3_regions = pd.read_csv('aux/region_EXIO3.csv')

        final_table= pd.DataFrame(columns = ['region','sector', 'Employment: Low-skilled male', 'Employment: Low-skilled female', 'Employment: Medium-skilled male','Employment: Medium-skilled female', 'Employment: High-skilled male', 'Employment: High-skilled female','Employment hours: Low-skilled male', 'Employment hours: Low-skilled female', 'Employment hours: Medium-skilled male',  'Employment hours: Medium-skilled female','Employment hours: High-skilled male',  'Employment hours: High-skilled female'])
        final_table_empty = final_table.copy()
        final = {}
        for years in range(1995,2023):
            print(years)
            final_table=final_table_empty.copy()
            whours = pd.read_excel(xls, str(years))
            whours=whours.drop(['Unnamed: 0'],axis =1)

            pop = pd.read_excel(xls2, str(years))
            pop=pop.drop(['Unnamed: 0'],axis =1)
            pop = pop.dropna()


            for code in  exio3_regions['EXIO3']:
                print(code)
                for sector in whours['Sector'].unique(): 
                    if not sector in pop.loc[(pop.Country == code),'Sector'].values : 
                        new_row = pd.DataFrame({'region':[code],   'sector':[sector],   'Employment: Low-skilled male': [0],'Employment: Low-skilled female': [0],'Employment: Medium-skilled male':[0],'Employment: Medium-skilled female': [0],'Employment: High-skilled male':[0],'Employment: High-skilled female':[0], 'Employment hours: Low-skilled male' :[0],  'Employment hours: Low-skilled female' :[0],'Employment hours: Medium-skilled male' :[0],  'Employment hours: Medium-skilled female' :[0],'Employment hours: High-skilled male' :[0],  'Employment hours: High-skilled female' :[0]})
                    else :
                        
                        new_row = pd.DataFrame({'region':[code],   'sector':[sector],   'Employment: Low-skilled male': [float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split Low qualification employment - male'].to_string(header=False,index=False))],'Employment: Low-skilled female': [float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split Low qualification employment - female'].to_string(header=False,index=False))],'Employment: Medium-skilled male':[float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split Middle qualification employment - male'].to_string(header=False,index=False))],'Employment: Medium-skilled female': [float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split Middle qualification employment - female'].to_string(header=False,index=False))],'Employment: High-skilled male':[float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split High qualification employment - male'].to_string(header=False,index=False))],'Employment: High-skilled female':[float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split High qualification employment - female'].to_string(header=False,index=False))], 'Employment hours: Low-skilled male' :[float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours Low qualification employement - male' ].to_string(index=False,header=False))],  'Employment hours: Low-skilled female' :[float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours Low qualification employement - female' ].to_string(index=False,header=False))],'Employment hours: Medium-skilled male' :[float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours Middle qualification employement - male' ].to_string(index=False,header=False))],  'Employment hours: Medium-skilled female' :[float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours Middle qualification employement - female' ].to_string(index=False,header=False))],'Employment hours: High-skilled male' :[float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours High qualification employement - male' ].to_string(index=False,header=False))],  'Employment hours: High-skilled female' :[float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours High qualification employement - female' ].to_string(index=False,header=False))]})
                    
                    #new_row = pd.DataFrame({'region':[code],   'sector':[sector],   'Employment: Low-skilled male': [float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split Low qualification employment - male'].to_string(header=False,index=False))],'Employment: Low-skilled female': [float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split Low qualification employment - female'].to_string(header=False,index=False))],'Employment: Medium-skilled male':[float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split Middle qualification employment - male'].to_string(header=False,index=False))],'Employment: Medium-skilled female': [float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split Middle qualification employment - female'].to_string(header=False,index=False))],'Employment: High-skilled male':[float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split High qualification employment - male'].to_string(header=False,index=False))],'Employment: High-skilled female':[float(pop.loc[(pop.Country == code)&(pop.Sector ==sector),'Split High qualification employment - female'].to_string(header=False,index=False))], 'Employment hours: Low-skilled male' : [float(whours.loc[(whours.EXIO3 ==code) & (whours.Sector==sector),'Hours Low qualification employement - male'].to_string(index=False,header=False))]})
                    final_table=pd.concat([final_table,new_row])

            final[years]=final_table.copy()

        writer = pd.ExcelWriter('final_labor.xlsx',engine='xlsxwriter')
    
        for year in range(1995,2023):
            table_pivot = final[year].pivot_table(columns=['region','sector'],sort = False)
            table_pivot.to_excel(writer, sheet_name=str(year))        
        writer.save()


         #    table_pivot = df1.pivot_table(columns=['EXIO3','Sector'],sort = False)
            
         # writer = pd.ExcelWriter('aggregation_per_year.xlsx', engine='xlsxwriter')
         
         # for year in range(1961,2022):
         #      table_pivot.loc[:,'Y'+str(year)].to_excel(writer, sheet_name=str(year))
         # writer.close()
    
         #writer.save()
    
         '''
         To access values for a certain location and certain year
         '''
         #table_pivot.loc['BE','Y1961']
    
         '''
         To access a table for a particular year
         '''
         #table_pivot.loc[:,'Y1961']
    
         #return
     
     
     
     
     
