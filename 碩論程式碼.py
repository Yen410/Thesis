import os
import shutil
import pandas as pd
import numpy as np
import math
from collections import defaultdict
from numpy import array
import pickle5 as pickle
#整理患者的所有就醫紀錄依ID分CSV
DATA = pd.read_csv('/media/lab03/YENTING/PD&PD_RA(final)/PD_FINAL.csv',encoding = "utf-8", low_memory=False)
path2 = '/media/lab03/DATADRIVE1/PD_personal_allyear/'
dfs = pd.DataFrame()
for i in DATA["ID"]:
    for ii in os.listdir('/media/lab03/DATADRIVE1/PD'):
        c = pd.read_csv('/media/lab03/DATADRIVE1/PD_personal_allyear/'+ii+'/'+i+'.csv')
        dfs = dfs.append(c)
    dfs.to_csv(path2+i+'.csv',index=False)
    dfs = dfs.drop(dfs.index)
    
#來源疾病資料前處理
#牙周病藥物格式轉換
drug_all = pd.read_csv('/media/lab03/YENTING/drug_all.csv',encoding = "utf-8", low_memory=False)#所有牙周病相關治療用藥
#drug_all to dictionary_list
drug_all_dict = drug_all.to_dict('list')
#drug_all_dic_dropna
drug_all_dict["PD_Related_disposal"] = [drug_all_dict["PD_Related_disposal"] for drug_all_dict["PD_Related_disposal"] in drug_all_dict["PD_Related_disposal"] if str(drug_all_dict["PD_Related_disposal"]) != 'nan']
drug_all_dict["PD_scaling"] = [drug_all_dict["PD_scaling"] for drug_all_dict["PD_scaling"] in drug_all_dict["PD_scaling"] if str(drug_all_dict["PD_scaling"]) != 'nan']

#欄位數值計算
PD_DATA = pd.read_csv('/media/lab03/YENTING/PD&PD_RA(final)/PD_FINAL.csv',encoding = "utf-8", low_memory=False)

path1 = '/media/lab03/YENTING/PD_personal_allyear/'
path2 = '/media/lab03/DATADRIVE1/PD_personal_vector/'#DATADRIVE1

#把list內的數字加起來
def sum_elems(a):
    sum = 0
    for i in a:
        sum += i
    return sum

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    
    return False

dfs = pd.DataFrame()
CC = []
for ii in PD_DATA["ID"]:
    data = pd.read_csv(path1+ii+'.csv',encoding="utf-8")
    
    g = 1
    person_dict_f = {}
    zero = [0,0,0,0,0]
    
    #取固定時間的資料，一個月一個月
    for t in range(1999,2011):#取年
        d1 = data["FUNC_DATE"].astype(str).str.startswith(str(t))
        data2 = data[(d1)]
        
        for tt in range(1,13):#取月 
            d2 = data2["FUNC_DATE"].astype(str).str.startswith(str(t)+str(tt).zfill(2))
            p = data2[(d2)]
            
            if p.empty:
                person_dict = {}
                person_dict.setdefault(g,[]).extend(zero)
            else:
                #p to list (取位置)
                p_a = np.array(p)#np.ndarray()
                p_a_list=p_a.tolist()#list
    
                p_long = len(p_a_list)
                
                count_ost = []#計算天數
                dru_ost = []#計算藥種類
                date_ost = []#是否有同一天拿兩種骨鬆藥
                
                count_dia_oral = []
                dru_dia_oral = []#計算藥種類
                date_dia_oral = []#是否有同一天拿兩種糖尿病藥
                
                count_dia_inj = []
                dru_dia_inj = []#計算藥種類
                date_dia_inj = []#是否有同一天拿兩種糖尿病注射藥物
                
                count_pd = []#計算天數
                dru_pd = []#計算藥種類
                date_pd = []#是否有同一天拿兩種消炎藥
                
                r = 0
                s = 0
                for i in range(0,p_long):
                    person_dict = {}
                    #PD(計算天數)
                    if p_a_list[i][16] in drug_all_dict["PD_drug"]:#16=drug_no
                        if p_a_list[i][21] not in date_pd:#21=function_date
                            if  is_number(p_a_list[i][14]) == True:#14=drug_day
                                count_pd.append(p_a_list[i][14])#14=drug_day
                                date_pd.append(p_a_list[i][21])
                                dru_pd.append(p_a_list[i][16])
                            else:
                                dru_pd.append(p_a_list[i][16])
                        else:
                            dru_pd.append(p_a_list[i][16])
                    else:
                        pass
        
                    #PD_related_disposal(計算次數)
                    if p_a_list[i][16] in drug_all_dict["PD_Related_disposal"]:#16=drug_no
                        r += 1
                        
                    else:
                        pass
        
                    #PD_scaling(計算次數)
                    if p_a_list[i][16] in drug_all_dict["PD_scaling"]:#16=drug_no
                        s += 1
                    else:
                        pass
                

                #person_dict append各數值
                    if len(list(set(dru_pd))) == 0:
                        person_dict.setdefault(g,[]).append(0)
                        person_dict.setdefault(g,[]).append(0)
                    else:
                        person_dict.setdefault(g,[]).append(sum_elems(count_pd))
                        person_dict.setdefault(g,[]).append(len(list(set(dru_pd))))
                    person_dict.setdefault(g,[]).append(r)
                    person_dict.setdefault(g,[]).append(s)
            
            person_dict_f.update(person_dict)
            g +=1
    person_df = pd.DataFrame.from_dict(person_dict_f, orient='index')
    person_df = person_df.sort_index()
    person_df.to_csv(path2+ii+'.csv')
    
    c = person_df.values

    #ADD TO LIST
    CC.append(c)

array_CC = np.array(CC)

import pickle
f = open('PD_726485_1m.pkl','wb')
PD_726485 = pickle.dump(array_CC,f,-1)
f.close()

#目標疾病資料前處理
#RA病藥物格式轉換
drug_all = pd.read_csv('/media/lab03/YENTING/drug_all.csv',encoding = "utf-8", low_memory=False)#所有牙周病相關治療用藥
RA_drug_all = pd.read_csv('/media/lab03/YENTING/RA_drug_classify/RA_drug_all(4).csv',encoding = "utf-8", low_memory=False)#所有牙RA相關治療用藥
RA_inj = pd.read_csv('/media/lab03/YENTING/RA_drug_classify/RA_inj.csv',encoding = "utf-8", low_memory=False)
RA_oral = pd.read_csv('/media/lab03/YENTING/RA_drug_classify/RA_oral.csv',encoding = "utf-8", low_memory=False)

#drug_all to dictionary_list
drug_all_dict = drug_all.to_dict('list')
#drug_all_dic_dropna
drug_all_dict["PD_Related_disposal"] = [drug_all_dict["PD_Related_disposal"] for drug_all_dict["PD_Related_disposal"] in drug_all_dict["PD_Related_disposal"] if str(drug_all_dict["PD_Related_disposal"]) != 'nan']
drug_all_dict["PD_scaling"] = [drug_all_dict["PD_scaling"] for drug_all_dict["PD_scaling"] in drug_all_dict["PD_scaling"] if str(drug_all_dict["PD_scaling"]) != 'nan']


#RA_drug_all to dictionary_list
RA_drug_all = RA_drug_all.to_dict('list')
#RA_drug_all_dropna
RA_drug_all["ra_inj"] = [RA_drug_all["ra_inj"] for RA_drug_all["ra_inj"] in RA_drug_all["ra_inj"] if str(RA_drug_all["ra_inj"]) != 'nan']
RA_drug_all["ra_oral"] = [RA_drug_all["ra_oral"] for RA_drug_all["ra_oral"] in RA_drug_all["ra_oral"] if str(RA_drug_all["ra_oral"]) != 'nan']
RA_drug_all["ra_sup"] = [RA_drug_all["ra_sup"] for RA_drug_all["ra_sup"] in RA_drug_all["ra_sup"] if str(RA_drug_all["ra_sup"]) != 'nan']
RA_drug_all["ra_gel"] = [RA_drug_all["ra_gel"] for RA_drug_all["ra_gel"] in RA_drug_all["ra_gel"] if str(RA_drug_all["ra_gel"]) != 'nan']

#RA_inj to dictionary_list
RA_inj = RA_inj.to_dict('list')
#RA_inj_dropna
RA_inj["inj_0.54"] = [RA_inj["inj_0.54"] for RA_inj["inj_0.54"] in RA_inj["inj_0.54"] if str(RA_inj["inj_0.54"]) != 'nan']
RA_inj["inj_1.5"] = [RA_inj["inj_1.5"] for RA_inj["inj_1.5"] in RA_inj["inj_1.5"] if str(RA_inj["inj_1.5"]) != 'nan']
RA_inj["inj_1.66"] = [RA_inj["inj_1.66"] for RA_inj["inj_1.66"] in RA_inj["inj_1.66"] if str(RA_inj["inj_1.66"]) != 'nan']
RA_inj["inj_1.79"] = [RA_inj["inj_1.79"] for RA_inj["inj_1.79"] in RA_inj["inj_1.79"] if str(RA_inj["inj_1.79"]) != 'nan']
RA_inj["inj_2.9"] = [RA_inj["inj_2.9"] for RA_inj["inj_2.9"] in RA_inj["inj_2.9"] if str(RA_inj["inj_2.9"]) != 'nan']
RA_inj["inj_3.75"] = [RA_inj["inj_3.75"] for RA_inj["inj_3.75"] in RA_inj["inj_3.75"] if str(RA_inj["inj_3.75"]) != 'nan']
RA_inj["inj_4"] = [RA_inj["inj_4"] for RA_inj["inj_4"] in RA_inj["inj_4"] if str(RA_inj["inj_4"]) != 'nan']
RA_inj["inj_5.4"] = [RA_inj["inj_5.4"] for RA_inj["inj_5.4"] in RA_inj["inj_5.4"] if str(RA_inj["inj_5.4"]) != 'nan']
RA_inj["inj_7"] = [RA_inj["inj_7"] for RA_inj["inj_7"] in RA_inj["inj_7"] if str(RA_inj["inj_7"]) != 'nan']
RA_inj["inj_10"] = [RA_inj["inj_10"] for RA_inj["inj_10"] in RA_inj["inj_10"] if str(RA_inj["inj_10"]) != 'nan']
RA_inj["inj_14"] = [RA_inj["inj_14"] for RA_inj["inj_14"] in RA_inj["inj_14"] if str(RA_inj["inj_14"]) != 'nan']
RA_inj["inj_15"] = [RA_inj["inj_15"] for RA_inj["inj_15"] in RA_inj["inj_15"] if str(RA_inj["inj_15"]) != 'nan']
RA_inj["inj_20"] = [RA_inj["inj_20"] for RA_inj["inj_20"] in RA_inj["inj_20"] if str(RA_inj["inj_20"]) != 'nan']
RA_inj["inj_27"] = [RA_inj["inj_27"] for RA_inj["inj_27"] in RA_inj["inj_27"] if str(RA_inj["inj_27"]) != 'nan']
RA_inj["inj_30"] = [RA_inj["inj_30"] for RA_inj["inj_30"] in RA_inj["inj_30"] if str(RA_inj["inj_30"]) != 'nan']
RA_inj["inj_100"] = [RA_inj["inj_100"] for RA_inj["inj_100"] in RA_inj["inj_100"] if str(RA_inj["inj_100"]) != 'nan']
RA_inj["inj_150"] = [RA_inj["inj_150"] for RA_inj["inj_150"] in RA_inj["inj_150"] if str(RA_inj["inj_150"]) != 'nan']
RA_inj["inj_250"] = [RA_inj["inj_250"] for RA_inj["inj_250"] in RA_inj["inj_250"] if str(RA_inj["inj_250"]) != 'nan']
RA_inj["inj_1200"] = [RA_inj["inj_1200"] for RA_inj["inj_1200"] in RA_inj["inj_1200"] if str(RA_inj["inj_1200"]) != 'nan']

#RA_oral to dictionary_list
RA_oral = RA_oral.to_dict('list')
#RA_oral_dropna
RA_oral["oral_1.5"] = [RA_oral["oral_1.5"] for RA_oral["oral_1.5"] in RA_oral["oral_1.5"] if str(RA_oral["oral_1.5"]) != 'nan']
RA_oral["oral_7.5"] = [RA_oral["oral_7.5"] for RA_oral["oral_7.5"] in RA_oral["oral_7.5"] if str(RA_oral["oral_7.5"]) != 'nan']
RA_oral["oral_10"] = [RA_oral["oral_10"] for RA_oral["oral_10"] in RA_oral["oral_10"] if str(RA_oral["oral_10"]) != 'nan']
RA_oral["oral_15"] = [RA_oral["oral_15"] for RA_oral["oral_15"] in RA_oral["oral_15"] if str(RA_oral["oral_15"]) != 'nan']
RA_oral["oral_20"] = [RA_oral["oral_20"] for RA_oral["oral_20"] in RA_oral["oral_20"] if str(RA_oral["oral_20"]) != 'nan']
RA_oral["oral_25"] = [RA_oral["oral_25"] for RA_oral["oral_25"] in RA_oral["oral_25"] if str(RA_oral["oral_25"]) != 'nan']
RA_oral["oral_30"] = [RA_oral["oral_30"] for RA_oral["oral_30"] in RA_oral["oral_30"] if str(RA_oral["oral_30"]) != 'nan']
RA_oral["oral_60"] = [RA_oral["oral_60"] for RA_oral["oral_60"] in RA_oral["oral_60"] if str(RA_oral["oral_60"]) != 'nan']
RA_oral["oral_100"] = [RA_oral["oral_100"] for RA_oral["oral_100"] in RA_oral["oral_100"] if str(RA_oral["oral_100"]) != 'nan']
RA_oral["oral_120"] = [RA_oral["oral_120"] for RA_oral["oral_120"] in RA_oral["oral_120"] if str(RA_oral["oral_120"]) != 'nan']
RA_oral["oral_150"] = [RA_oral["oral_150"] for RA_oral["oral_150"] in RA_oral["oral_150"] if str(RA_oral["oral_150"]) != 'nan']
RA_oral["oral_200"] = [RA_oral["oral_200"] for RA_oral["oral_200"] in RA_oral["oral_200"] if str(RA_oral["oral_200"]) != 'nan']
RA_oral["oral_250"] = [RA_oral["oral_250"] for RA_oral["oral_250"] in RA_oral["oral_250"] if str(RA_oral["oral_250"]) != 'nan']
RA_oral["oral_400"] = [RA_oral["oral_400"] for RA_oral["oral_400"] in RA_oral["oral_400"] if str(RA_oral["oral_400"]) != 'nan']
RA_oral["oral_500"] = [RA_oral["oral_500"] for RA_oral["oral_500"] in RA_oral["oral_500"] if str(RA_oral["oral_500"]) != 'nan']
RA_oral["oral_516"] = [RA_oral["oral_516"] for RA_oral["oral_516"] in RA_oral["oral_516"] if str(RA_oral["oral_516"]) != 'nan']
RA_oral["oral_1000"] = [RA_oral["oral_1000"] for RA_oral["oral_1000"] in RA_oral["oral_1000"] if str(RA_oral["oral_1000"]) != 'nan']
RA_oral["oral_1200"] = [RA_oral["oral_1200"] for RA_oral["oral_1200"] in RA_oral["oral_1200"] if str(RA_oral["oral_1200"]) != 'nan']
RA_oral["oral_2000"] = [RA_oral["oral_2000"] for RA_oral["oral_2000"] in RA_oral["oral_2000"] if str(RA_oral["oral_2000"]) != 'nan']

#欄位數值計算
PD_RA_DATA = pd.read_csv('/media/lab003/YENTING/PD&PD_RA(final)/PD_RA_FINAL(31390).csv',encoding = "utf-8", low_memory=False)

path1 = '/media/lab003/YENTING/PD_RA_personal_allyear/'
path2 = '/home/lab003/PD_RA_personal_vector/'#DATADRIVE1

#把list內的數字加起來
def sum_elems(a):
    sum = 0
    for i in a:
        sum += i
    return sum

#取出各RA藥的DDD量
def get_key (dict, value):
    return [k for k, v in dict.items() if value in v]


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    
    return False

dfs = pd.DataFrame()
CC_2 = []
for ii in PD_noRA_DATA["ID"]:
    data = pd.read_csv(path1+ii+'.csv',encoding="utf-8")
    
    g = 1
    person_dict_f = {}
    zero = [0,0,0,0,0,0,0,0]
    
    #取固定時間的資料，一個月一個月
    for t in range(1999,2011):#取年
        d1 = data["FUNC_DATE"].astype(str).str.startswith(str(t))
        data2 = data[(d1)]
        
        for tt in range(1,13):#取月 
            d2 = data2["FUNC_DATE"].astype(str).str.startswith(str(t)+str(tt).zfill(2))
            p = data2[(d2)]
            
            if p.empty:
                person_dict = {}
                person_dict.setdefault(g,[]).extend(zero)
            else:
                #p to list (取位置)
                p_a = np.array(p)#np.ndarray()
                p_a_list=p_a.tolist()#list
    
                p_long = len(p_a_list)
               
                
                count_pd = []#計算天數
                dru_pd = []#計算藥種類
                date_pd = []#是否有同一天拿兩種消炎藥
                
                count_pd = []#計算天數
                dru_pd = []#計算藥種類
                date_pd = []#是否有同一天拿兩種消炎藥
                
                count_ra_oral = []
                dru_ra_oral = []#計算藥種類
                date_ra_oral = []#是否有同一天拿兩種ra藥
                
                count_ra_inj = []
                dru_ra_inj = []#計算藥種類
                date_ra_inj = []#是否有同一天拿兩種ra注射藥
             
                
                r = 0
                s = 0
                for i in range(0,p_long):
                    person_dict = {}        
                    #PD(計算天數)
                    if p_a_list[i][16] in drug_all_dict["PD_drug"]:#16=drug_no
                        if p_a_list[i][21] not in date_pd:#21=function_date
                            if  is_number(p_a_list[i][14]) == True:#14=drug_day
                                count_pd.append(p_a_list[i][14])#14=drug_day
                                date_pd.append(p_a_list[i][21])
                                dru_pd.append(p_a_list[i][16])
                            else:
                                dru_pd.append(p_a_list[i][16])
                        else:
                            dru_pd.append(p_a_list[i][16])
                    else:
                        pass
        
                    #PD_related_disposal(計算次數)
                    if p_a_list[i][16] in drug_all_dict["PD_Related_disposal"]:#16=drug_no
                        r += 1
                        
                    else:
                        pass
        
                    #PD_scaling(計算次數)
                    if p_a_list[i][16] in drug_all_dict["PD_scaling"]:#16=drug_no
                        s += 1
                    else:
                        pass
                    
                    #RA_oral(計算DDD)
                    if p_a_list[i][16] in RA_drug_all["ra_oral"]:#16=drug_no
                        if p_a_list[i][17] == str("1/2"):
                            count_ra_oral.append(0.5)
                            date_ra_oral.append(p_a_list[i][21])
                            dru_ra_oral.append(p_a_list[i][16])
                        else:
                            if p_a_list[i][17] == str("1 1/2"):
                                count_ra_oral.append(1.5)
                                date_ra_oral.append(p_a_list[i][21])
                                dru_ra_oral.append(p_a_list[i][16])
                            else:
                                if p_a_list[i][17] == str("1/4"):
                                    count_ra_oral.append(0.25)
                                    date_ra_oral.append(p_a_list[i][21])
                                    dru_ra_oral.append(p_a_list[i][16])
                                else:
                                    if is_number(p_a_list[i][17]) == True:
                                        k1 = get_key(RA_oral,p_a_list[i][16])
                                        DDD1 = RA_oral[k1[0]][len(RA_oral[k1[0]])-1]
                                        count_ra_oral.append(int(float(p_a_list[i][17]))/int(DDD1))#17=drug_use，除DDD
                                        date_ra_oral.append(p_a_list[i][21])
                                        dru_ra_oral.append(p_a_list[i][16])
                                    else:
                                        dru_ra_oral.append(p_a_list[i][16])
                    else:
                        pass
                    
                    #RA_inj(計算DDD)
                    if p_a_list[i][16] in RA_drug_all["ra_inj"]:#16=drug_no
                        if p_a_list[i][17] == str("1/2"):
                            count_ra_inj.append(0.5)
                            date_ra_inj.append(p_a_list[i][21])
                            dru_ra_inj.append(p_a_list[i][16])
                        else:
                            if p_a_list[i][17] == str("1 1/2"):
                                count_ra_inj.append(1.5)
                                date_ra_inj.append(p_a_list[i][21])
                                dru_ra_inj.append(p_a_list[i][16])
                            else:
                                if p_a_list[i][17] == str("1/4"):
                                    count_ra_inj.append(0.25)
                                    date_ra_inj.append(p_a_list[i][21])
                                    dru_ra_inj.append(p_a_list[i][16])
                                else:
                                    if is_number(p_a_list[i][17]) == True:
                                        k1 = get_key(RA_inj,p_a_list[i][16])
                                        DDD1 = RA_inj[k1[0]][len(RA_inj[k1[0]])-1]
                                        count_ra_inj.append(int(float(p_a_list[i][17]))/int(DDD1))#17=drug_use，除DDD
                                        date_ra_inj.append(p_a_list[i][21])
                                        dru_ra_inj.append(p_a_list[i][16])
                                    else:
                                        dru_ra_sup.append(p_a_list[i][16])
                    else:
                        pass
                                

                #person_dict append各數值
                    if len(list(set(dru_pd))) == 0:
                        person_dict.setdefault(g,[]).append(0)
                        person_dict.setdefault(g,[]).append(0)
                    else:
                        person_dict.setdefault(g,[]).append(sum_elems(count_pd))
                        person_dict.setdefault(g,[]).append(len(list(set(dru_pd))))
                    person_dict.setdefault(g,[]).append(r)
                    person_dict.setdefault(g,[]).append(s)
                    #加入RA
                    if len(list(set(dru_ra_oral))) == 0:
                        person_dict.setdefault(g,[]).append(0) 
                        person_dict.setdefault(g,[]).append(0)
                    else:
                        person_dict.setdefault(g,[]).append(sum_elems(count_ra_oral))
                        person_dict.setdefault(g,[]).append(len(list(set(dru_ra_oral)))
                    if len(list(set(dru_ra_inj))) == 0:
                        person_dict.setdefault(g,[]).append(0) 
                        person_dict.setdefault(g,[]).append(0)
                    else:
                        person_dict.setdefault(g,[]).append(sum_elems(count_ra_inj))
                        person_dict.setdefault(g,[]).append(len(list(set(dru_ra_inj)))            
            person_dict_f.update(person_dict)
            g +=1
    person_df = pd.DataFrame.from_dict(person_dict_f, orient='index')
    person_df = person_df.sort_index()
    person_df.to_csv(path2+ii+'.csv')
    
    c = person_df.values

    #ADD TO LIST
    CC_2.append(c)
array_CC_2 = np.array(CC_2)

import pickle
f = open('PD_RA_31390_1m.pkl','wb')
PD_RA_31390 = pickle.dump(array_CC_2,f,-1)
f.close()
      
#將資料整理成不同時間長度的序列資料(在此僅呈現類風濕的資料，牙周病資料的整理方法相同)
f = open('/home/lab03/new pd&pd_ra/PD_RA_31390_1m.pkl','rb')
d = pickle.load(f)
f.close()
d.shape                                                     

#2 months
import torch
tensor_zero = torch.zeros([31390,72,8])
tensor_zero.type(torch.cuda.FloatTensor)

for i in range(0,len(d)):
    ii=0
    i_0 = 0
    i_1 = 1 
    while i_1 < 144:
        d_2 = d[i][i_0] + d[i][i_1]
        d_2 = [float(x) for x in d_2[0:8]]
        d_2 = torch.from_numpy(np.asarray(d_2))
        d_2 = d_2.type(torch.cuda.FloatTensor)
        tensor_zero[i][ii] = tensor_zero[i][ii].cuda()+d_2.cuda()
        ii+=1
        i_0 += 2
        i_1 += 2
print(tensor_zero.shape)
f = open("/home/lab03/new pd&pd_ra/PD_RA_31390_2m.pkl","wb")
PD_RA_31390_2m = pickle.dump(tensor_zero,f,-1)
                                                            
#3 months
tensor_zero2 = torch.zeros([31390,48,8])
tensor_zero2.type(torch.cuda.FloatTensor)

for i in range(0,len(d)):
    ii=0
    i_0 = 0
    i_1 = 1 
    i_2 = 2
    while i_2 < 144:
        d_2 = d[i][i_0] + d[i][i_1] + d[i][i_2]
        d_2 = [float(x) for x in d_2[0:8]]
        d_2 = torch.from_numpy(np.asarray(d_2))
        d_2 = d_2.type(torch.cuda.FloatTensor)
        tensor_zero2[i][ii] = tensor_zero2[i][ii].cuda()+d_2.cuda()
        ii+=1
        i_0 += 3
        i_1 += 3
        i_2 += 3
print(tensor_zero2.shape)  
f = open("/home/lab03/new pd&pd_ra/PD_RA_31390_3m.pkl","wb")
PD_RA_31390_3m = pickle.dump(tensor_zero2,f,-1)

#4 months                                                            
tensor_zero3 = torch.zeros([31390,36,8])
tensor_zero3.type(torch.cuda.FloatTensor)

for i in range(0,len(d)):
    ii=0
    i_0 = 0
    i_1 = 1 
    while i_1 < 72:
        tensor_zero_2 = tensor_zero[i][i_0] + tensor_zero[i][i_1]
        tensor_zero_2 = [float(x) for x in tensor_zero_2[0:8]]
        tensor_zero_2 = torch.from_numpy(np.asarray(tensor_zero_2))
        tensor_zero_2 = tensor_zero_2.type(torch.cuda.FloatTensor)
        tensor_zero3[i][ii] = tensor_zero3[i][ii].cuda()+tensor_zero_2.cuda()
        ii+=1
        i_0 += 2
        i_1 += 2
print(tensor_zero3.shape)
f = open("/home/lab03/new pd&pd_ra/PD_RA_31390_4m.pkl","wb")
PD_RA_31390_4m = pickle.dump(tensor_zero3,f,-1)
  
                                                            
#預測模型                                                            
#來源疾病病程預測模型
import torch
import torch.nn as nn
import pickle5 as pickle

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch.nn.functional as F
%matplotlib inline
import torch.utils.data as Data
from torchvision import datasets
import torchvision.transforms as transforms
from sklearn.model_selection import train_test_split
import gc
gc.collect()                                                            
                                                            
f = open('/home/lab03/new pd&pd_ra/PD_724155_3m.pkl','rb')
tensor_zero = pickle.load(f)
f.close()

train_dataset = tensor_zero[:int(0.7*len(tensor_zero))]
test_dataset = tensor_zero[int(0.7*len(tensor_zero)):]
test_loader=Data.DataLoader(dataset = test_dataset, batch_size = 1000)

class lstm_Attention(nn.Module):
    def __init__(self, input_size=4, hidden_size=128, output_size=4):
        super(lstm_Attention, self).__init__()
        self.hidden_size=hidden_size
        self.input_size=input_size
        self.output_size=output_size
        
        self.lstm = nn.Sequential(
            nn.LSTM(input_size=self.input_size, hidden_size=self.hidden_size, batch_first = True)
        )
        
        self.fc = nn.Sequential(
            nn.Linear(self.hidden_size, self.output_size),
            nn.ReLU()
        )
                
    def attention_net(self, lstm_output, final_state):
        self.hidden = final_state.permute(1, 2, 0)   
        self.attn_weights = torch.bmm(lstm_output, self.hidden).squeeze(2)
        self.soft_attn_weights = F.softmax(self.attn_weights, 1)
        self.figure = torch.bmm(lstm_output.transpose(1, 2), self.soft_attn_weights.unsqueeze(2)).squeeze(2)
        return self.figure.cuda(), self.soft_attn_weights.cpu().data.numpy()
    
    def forward(self, x):
        out, (final_hidden_state, final_cell_state) = self.lstm(x)
        attn_output, attention_weight = self.attention_net(out, final_hidden_state)
        output = self.fc(attn_output)
        return output, attention_weight  
            
print(torch.cuda.is_available())                                                            
torch.cuda.set_device(0)
LSTM_Attention_3m = lstm_Attention()
LSTM_Attention_3m.cuda()

optimizer = torch.optim.Adam(LSTM_Attention_3m.parameters(), lr=1e-4)
loss_func = nn.MSELoss().cuda() 
                                                            
#trainning
 from torch.autograd import Variable
import time
import random

train_ls = []
val_ls = []
test_ls = []
epoch = 50
seed_n = range(0,1000000)
seed_list = random.sample(seed_n, epoch)

start = time.time()
for i in range(epoch):

    train, validation = train_test_split(train_dataset, test_size = 0.2, random_state = seed_list[i])
    train_loader=Data.DataLoader(dataset = train, batch_size = 1000)
    validation_loader=Data.DataLoader(dataset = validation, batch_size = 1000)
    
    LSTM_Attention_3m.train()
    for idx,(train_data) in enumerate(train_loader):
        loss = 0
        train_datas = torch.log10(train_data+1)
        for j in range(44):
            train_data1 = train_datas[:,j:j+4,:]
            train_data1 = Variable(train_data1.type(torch.cuda.FloatTensor))
            train_label = train_datas[:,j+4,:]
            train_label = Variable(train_label.type(torch.cuda.FloatTensor))
        
            pred,  train_att_w = LSTM_Attention_3m(train_data1)
            ls = loss_func(pred,train_label)
            loss += ls
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
            
    train_ls.append(ls.item())
    
    ## evaluation part 

    LSTM_Attention_3m.eval()
    
    for idx, (val_data) in enumerate(validation_loader):
        val_datas = torch.log10(val_data+1)
        for j in range(44):
            val_data1 = val_datas[:,j:j+4,:]
            val_data1 = Variable(val_data1.type(torch.cuda.FloatTensor))
            val_label = val_datas[:,j+4,:]
            val_label = Variable(val_label.type(torch.cuda.FloatTensor))
        
            val_pred, val_att_w = LSTM_Attention_3m(val_data1)
            val_loss = loss_func(val_pred,val_label)        
    val_ls.append(val_loss.item())
    
    for idx, (test_data) in enumerate(test_loader):
        test_datas = torch.log10(test_data+1)
        for j in range(44):
            test_data1 = test_datas[:,j:j+4,:]
            test_data1 = Variable(test_data1.type(torch.cuda.FloatTensor))
            test_label = test_datas[:,j+4,:]
            test_label = Variable(test_label.type(torch.cuda.FloatTensor))
        
            test_pred, test_att_w = LSTM_Attention_3m(test_data1)
            test_loss = loss_func(test_pred,test_label)        
    test_ls.append(test_loss.item())
        
    print('epoch %d, train_loss: %.4f, val_loss: %.4f, test_loss: %.4f' %(i+1,ls.item(),val_loss.item(),test_loss.item()))
print("train_avg_loss:%.4f, val_avg_loss:%.4f, test_avg_loss:%.4f" %(np.mean(train_ls),np.mean(val_ls),np.mean(test_ls)))

end = time.time()
print("執行時間：%f 秒" % (end - start))
#存模型
torch.save(LSTM_Attention_3m,'/home/lab03/weight_pkl/LSTM_Attention_3m.pkl')
torch.save(LSTM_Attention_3m.state_dict(),"/home/lab03/weight_pkl/LSTM_Attention_3m_para.pkl",_use_new_zipfile_serialization=False) 

#繪製模型訓練的loss圖                                                            
import matplotlib.pyplot as plt
plt.title('model loss')
plt.plot(train_ls, label='train')
plt.plot(val_ls, label='val')
plt.plot(test_ls, label='test')
my_x_ticks = np.arange(0, len(train_ls), 5)
plt.xticks(my_x_ticks)
plt.xlabel('epoch')  
plt.ylabel('loss')
plt.legend()
plt.savefig('/home/lab03/Desktop/PD_loss/LSTM_Attention_3m.png',dpi=750)
plt.show()                                                              
                                                            
                                                            
#目標疾病病程預測模型
f = open('/home/lab03/new pd&pd_ra/PD_RA_28303_3m.pkl','rb')
tensor_zero = pickle.load(f)
f.close()

train_dataset = tensor_zero[:int(0.7*len(tensor_zero)),:,:]
test_dataset = tensor_zero[int(0.7*len(tensor_zero)):,:,:]
test_loader=Data.DataLoader(dataset = test_dataset, batch_size = 300) 
                                                            
#建立一個符合來源疾病的模型，用以裝入訓練好的來源疾病模型權重                                                       
class lstm_Attention(nn.Module):
    def __init__(self, input_size=4, hidden_size=128, output_size=4):
        super(lstm_Attention, self).__init__()
        self.hidden_size=hidden_size
        self.input_size=input_size
        self.output_size=output_size
        
        self.lstm = nn.Sequential(
            nn.LSTM(input_size=self.input_size, hidden_size=self.hidden_size, batch_first = True)
        )
        
        self.fc = nn.Sequential(
            nn.Linear(self.hidden_size, self.output_size),
            nn.ReLU()
        )
                
    def attention_net(self, lstm_output, final_state):
        self.hidden = final_state.permute(1, 2, 0)   
        self.attn_weights = torch.bmm(lstm_output, self.hidden).squeeze(2)
        self.soft_attn_weights = F.softmax(self.attn_weights, 1)
        self.figure = torch.bmm(lstm_output.transpose(1, 2), self.soft_attn_weights.unsqueeze(2)).squeeze(2)
        return self.figure.cuda(), self.soft_attn_weights.cpu().data.numpy()
    
    def forward(self, x):
        out, (final_hidden_state, final_cell_state) = self.lstm(x)
        attn_output, attention_weight = self.attention_net(out, final_hidden_state)
        output = self.fc(attn_output)
        return output, attention_weight                                                            
               
print(torch.cuda.is_available())
torch.cuda.set_device(0)
lstm_Attention().cuda()

#載入權重
PD_LSTM_3m = lstm_Attention()
PD_LSTM_3m.load_state_dict(torch.load("/home/lab03/weight_pkl/LSTM_Attention_3m_para.pkl"))
PD_LSTM_3m.cuda()
                                                            
#目標模型
class lstm_T(nn.Module):

    def __init__(self, input_size=8, output_size=4):
        super(lstm_T, self).__init__()
        # lstm的输入 #batch,seq_len, input_size
        self.input_size=input_size
        self.output_size=output_size
        
        self.fc1 = nn.Sequential(
            nn.Linear(self.input_size, 4),
        )
        self.model = PD_LSTM_3m
        
        self.fc2 = nn.Sequential(
            nn.Linear(128, 4),
            nn.ReLU()
        )

    def forward(self,x):
        out = self.fc1(x)
        out,_ = self.model.lstm(out)
        output = self.fc2(out[:,-1,:])
        return output                                                            
                                                            
print(torch.cuda.is_available())
torch.cuda.set_device(0)
LSTM_3m_T_FT = lstm_T()
LSTM_3m_T_FT.cuda()

optimizer_fc1 = torch.optim.Adam(LSTM_3m_T_FT.fc1.parameters(), lr=1e-4)
optimizer_fc2 = torch.optim.Adam(LSTM_3m_T_FT.fc2.parameters(), lr=1e-4)
optimizer_model = torch.optim.Adam(LSTM_3m_T_FT.model.parameters(), lr=1e-4)
loss_func = nn.MSELoss().cuda()
                                                            
#trainning
from torch.autograd import Variable
import time
import random

num_epoch = 20
train_ls = []
val_ls = []
test_ls = []
finetune_times = 0

start = time.time()
for i in range(num_epoch):
    
    train, validation = train_test_split(train_dataset, test_size = 0.2, random_state = i)
    train_loader=Data.DataLoader(dataset = train, batch_size = 300)
    validation_loader=Data.DataLoader(dataset = validation, batch_size = 300)
    
    LSTM_Att_3m_T_FT_1.train()
    for idx,(train_data) in enumerate(train_loader):
        loss = 0
        train_datas = torch.log10(train_data+1)
        for j in range(44):
            train_data1 = train_datas[:,j:j+4,:]
            train_data1 = Variable(train_data1.type(torch.cuda.FloatTensor))
            train_label = train_datas[:,j+4,4:8]
            train_label = Variable(train_label.type(torch.cuda.FloatTensor))
        
            pred, train_att_w = LSTM_Att_3m_T_FT_1(train_data1)
            ls = loss_func(pred,train_label)
            loss += ls
        
        x = random.uniform(0,10)
        if x <= 1:
            optimizer_fc1.zero_grad()
            optimizer_fc2.zero_grad()
            optimizer_model.zero_grad()
            loss.backward()
            optimizer_fc1.step()
            optimizer_fc2.step()
            optimizer_model.step()
            finetune_times += 1
        else:
            optimizer_fc1.zero_grad()
            optimizer_fc2.zero_grad()
            loss.backward()
            optimizer_fc1.step()
            optimizer_fc2.step()
            
    train_ls.append(ls.item())
    
    ## evaluation part 

    LSTM_Att_3m_T_FT_1.eval()
    
    for idx, (val_data) in enumerate(validation_loader):
        val_datas = torch.log10(val_data+1)
        for j in range(44):
            val_data1 = val_datas[:,j:j+4,:]
            val_data1 = Variable(val_data1.type(torch.cuda.FloatTensor))
            val_label = val_datas[:,j+4,4:8]
            val_label = Variable(val_label.type(torch.cuda.FloatTensor))
        
            val_pred, val_att_w = LSTM_Att_3m_T_FT_1(val_data1)
            val_loss = loss_func(val_pred,val_label)        
    val_ls.append(val_loss.item())
    
    for idx, (test_data) in enumerate(test_loader):
        test_datas = torch.log10(test_data+1)
        for j in range(44):
            test_data1 = test_datas[:,j:j+4,:]
            test_data1 = Variable(test_data1.type(torch.cuda.FloatTensor))
            test_label = test_datas[:,j+4,4:8]
            test_label = Variable(test_label.type(torch.cuda.FloatTensor))
        
            test_pred, test_att_w = LSTM_Att_3m_T_FT_1(test_data1)
            test_loss = loss_func(test_pred,test_label)        
    test_ls.append(test_loss.item())
        
    print('epoch %d, train_loss: %.4f, val_loss: %.4f, test_loss: %.4f' %(i+1,ls.item(),val_loss.item(),test_loss.item()))
print("train_avg_loss:%.4f, val_avg_loss:%.4f, test_avg_loss:%.4f" %(np.mean(train_ls),np.mean(val_ls),np.mean(test_ls)))
print("finetune_times:", finetune_times)
end = time.time()
print("執行時間：%f 秒" % (end - start))

#存模型
torch.save(LSTM_Att_3m_T_FT_1,'/home/lab03/RA_weight_pkl/output(12c_4)/transfer/LSTM_Att_3m_T_FT_1.pkl')
torch.save(LSTM_Att_3m_T_FT_1.state_dict(),"/home/lab03/RA_weight_pkl/output(12c_4)/transfer/LSTM_Att_3m_T_FT_1_para.pkl",_use_new_zipfile_serialization=False)
                                                            
#繪製模型訓練的loss圖 
import matplotlib.pyplot as plt
plt.title('model loss')
plt.plot(train_ls, label='train_loss')
plt.plot(val_ls, label='val_loss')
plt.plot(test_ls, label='test_loss')
my_x_ticks = np.arange(0, 20, 1)
plt.xticks(my_x_ticks)
plt.legend()
plt.xlabel('epoch')  
plt.ylabel('loss')
plt.savefig('/home/lab03/Desktop/RA_T_loss/LSTM_Att_3m_T_FT_1.png',dpi=750)
plt.show()
                                                 
#將模型訓練時的注意力權重視覺化，用以暸解每個時間點資訊的重要程度
df = pd.DataFrame(np.array([train_att_w[16],#病患一的4個時間點之注意力權重
                            train_att_w[246],#病患二的4個時間點之注意力權重
                            train_att_w[164]#病患三的4個時間點之注意力權重
                             ]),
                   columns=['t1', 't2', 't3', 't4'])
df.index = ['Patient_1', 'Patient_2', 'Patient_3']  

import seaborn as sns
%matplotlib inline
plt.figure(figsize=(10, 4))
plt.rc('font',family='Times New Roman',size=16)
sns.heatmap(data=df,cmap="YlGnBu",vmin=0,vmax=0.8,linewidths=1,linecolor="white",annot=True,annot_kws={"size":16})
plt.yticks(rotation='horizontal')
plt.savefig('/home/lab03/Desktop/att.png',dpi=750)
plt.tight_layout()
plt.show()                                                            