import pandas as pd
def aggregate(new_table_150222,new_table_150222_columns):
    for code in new_table_150222.ref_area.unique():
        print(code)
        for sex in new_table_150222.sex.unique():
            for year in range(1995,2020):
    
                value_d = value_e = 0
                value_h = value_j =0
                value_l = value_m = value_n =0
                value_r = value_s = value_t = value_u = 0
    
    
                
                if not (new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_D')&(new_table_150222['time']==year),['obs_value']].isnull().values.all()) :
                    value_d = float(new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_D')&(new_table_150222['time']==year),['obs_value']].to_string(header=False,index=False))
                else : 
                    value_d = 0
                if not (new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_E')&(new_table_150222['time']==year),['obs_value']].isnull().values.all()):
                    value_e = float(new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_E')&(new_table_150222['time']==year),['obs_value']].to_string(header=False,index=False))
                else : 
                    value_e = 0
                    
                if value_d ==0 and value_e == 0:
                    continue
                else :
                    if value_d==0 or value_e ==0 :
                        new_table_150222=new_table_150222.append(pd.Series([code,sex,'ECO_ISIC_DE',year,value_d+value_e,1], index=[i for i in new_table_150222_columns]),ignore_index=True)
                    else :
                        if value_d !=0 and value_e != 0 :
                            new_table_150222=new_table_150222.append(pd.Series([code,sex,'ECO_ISIC_DE',year,(value_d+value_e)/2,2], index=[i for i in new_table_150222_columns]),ignore_index=True)
    
    
    
                if not (new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_H')&(new_table_150222['time']==year),['obs_value']].isnull().values.all()) :
                    value_h = float(new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_H')&(new_table_150222['time']==year),['obs_value']].to_string(header=False,index=False))
                else : 
                    value_h = 0
                if not (new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_J')&(new_table_150222['time']==year),['obs_value']].isnull().values.all()):
                    value_j = float(new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_J')&(new_table_150222['time']==year),['obs_value']].to_string(header=False,index=False))
                else : 
                    value_j = 0
                    
                if value_h ==0 and value_j == 0:
                    continue
                else :
                    if value_h==0 or value_j ==0 :
                        new_table_150222=new_table_150222.append(pd.Series([code,sex,'ECO_ISIC_HJ',year,value_h+value_j,1], index=[i for i in new_table_150222_columns]),ignore_index=True)
                    else :
                        if value_h !=0 and value_j != 0 :
                            new_table_150222=new_table_150222.append(pd.Series([code,sex,'ECO_ISIC_HJ',year,(value_h+value_j)/2,2], index=[i for i in new_table_150222_columns]),ignore_index=True)
    
    
    
    
                if not (new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_R')&(new_table_150222['time']==year),['obs_value']].isnull().values.all()) :
                    value_r = float(new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_R')&(new_table_150222['time']==year),['obs_value']].to_string(header=False,index=False))
                else : 
                    value_r = 0
                    
                if not (new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_S')&(new_table_150222['time']==year),['obs_value']].isnull().values.all()):
                    value_s = float(new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_S')&(new_table_150222['time']==year),['obs_value']].to_string(header=False,index=False))
                else : 
                    value_s = 0
                    
                if not (new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_T')&(new_table_150222['time']==year),['obs_value']].isnull().values.all()):
                    value_t = float(new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_T')&(new_table_150222['time']==year),['obs_value']].to_string(header=False,index=False))
                else : 
                    value_t = 0
                
                if not (new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_U')&(new_table_150222['time']==year),['obs_value']].isnull().values.all()):
                    value_u = float(new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_U')&(new_table_150222['time']==year),['obs_value']].to_string(header=False,index=False))
                else : 
                    value_u = 0
                    
                lst = [value_r, value_s,value_t,value_u] 
                if lst.count(0)==4:
                #if value_l ==0 and value_m == 0 and value_n == 0 :
                    continue
                else :
                    if lst.count(0)==3:
                        new_table_150222=new_table_150222.append(pd.Series([code,sex,'ECO_ISIC_RSTU',year,value_r+value_s+value_t+value_u,1], index=[i for i in new_table_150222_columns]),ignore_index=True)
                    else :
                        if lst.count(0)==2:
                            new_table_150222=new_table_150222.append(pd.Series([code,sex,'ECO_ISIC_RSTU',year,(value_r+value_s+value_t+value_u)/2,2], index=[i for i in new_table_150222_columns]),ignore_index=True)
                        else :
                            if lst.count(0)==1:
                                new_table_150222=new_table_150222.append(pd.Series([code,sex,'ECO_ISIC_RSTU',year,(value_r+value_s+value_t+value_u)/3,3], index=[i for i in new_table_150222_columns]),ignore_index=True)
                            else :
                                if lst.count(0)==0:
                                    new_table_150222=new_table_150222.append(pd.Series([code,sex,'ECO_ISIC_RSTU',year,(value_r+value_s+value_t+value_u)/4,3], index=[i for i in new_table_150222_columns]),ignore_index=True)
    
                if not (new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_L')&(new_table_150222['time']==year),['obs_value']].isnull().values.all()) :
                    value_l = float(new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_L')&(new_table_150222['time']==year),['obs_value']].to_string(header=False,index=False))
                else : 
                    value_l = 0
                    
                if not (new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_M')&(new_table_150222['time']==year),['obs_value']].isnull().values.all()):
                    value_m = float(new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_M')&(new_table_150222['time']==year),['obs_value']].to_string(header=False,index=False))
                else : 
                    value_m = 0
                    
                if not (new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_N')&(new_table_150222['time']==year),['obs_value']].isnull().values.all()):
                    value_n = float(new_table_150222.loc[(new_table_150222['ref_area']==code)&(new_table_150222['sex']==sex)&(new_table_150222['classif1']=='ECO_ISIC_N')&(new_table_150222['time']==year),['obs_value']].to_string(header=False,index=False))
                else : 
                    value_n = 0
                    
                lst = [value_l, value_m,value_n] 
                if lst.count(0)==3:
                #if value_l ==0 and value_m == 0 and value_n == 0 :
                    continue
                else :
                    if lst.count(0)==2:
                        new_table_150222=new_table_150222.append(pd.Series([code,sex,'ECO_ISIC_LMN',year,value_l+value_m+value_n,1], index=[i for i in new_table_150222_columns]),ignore_index=True)
                    else :
                        if lst.count(0)==1:
                            new_table_150222=new_table_150222.append(pd.Series([code,sex,'ECO_ISIC_LMN',year,(value_l+value_m+value_n)/2,2], index=[i for i in new_table_150222_columns]),ignore_index=True)
                        else :
                            if lst.count(0)==0:
                                new_table_150222=new_table_150222.append(pd.Series([code,sex,'ECO_ISIC_LMN',year,(value_l+value_m+value_n)/3,3], index=[i for i in new_table_150222_columns]),ignore_index=True)
    
    
    
    new_table_150222=new_table_150222[new_table_150222.classif1 != 'ECO_ISIC_D'].copy()
    new_table_150222=new_table_150222[new_table_150222.classif1 != 'ECO_ISIC_E'].copy()
    new_table_150222=new_table_150222[new_table_150222.classif1 != 'ECO_ISIC_H'].copy()
    new_table_150222=new_table_150222[new_table_150222.classif1 != 'ECO_ISIC_J'].copy()
    new_table_150222=new_table_150222[new_table_150222.classif1 != 'ECO_ISIC_L'].copy()
    new_table_150222=new_table_150222[new_table_150222.classif1 != 'ECO_ISIC_M'].copy()
    new_table_150222=new_table_150222[new_table_150222.classif1 != 'ECO_ISIC_N'].copy()
    new_table_150222=new_table_150222[new_table_150222.classif1 != 'ECO_ISIC_R'].copy()
    new_table_150222=new_table_150222[new_table_150222.classif1 != 'ECO_ISIC_S'].copy()
    new_table_150222=new_table_150222[new_table_150222.classif1 != 'ECO_ISIC_T'].copy()
    new_table_150222=new_table_150222[new_table_150222.classif1 != 'ECO_ISIC_U'].copy()


    return new_table_150222