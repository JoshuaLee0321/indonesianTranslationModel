# -*- coding: utf-8 -*-
from New_CKIP import call_ckip
from bnp_by_con import make_NP,bnp_by_con
import hanlp
import pandas
import logging
import socket
import struct
import re

tw = pandas.read_excel("output_abbr_without_embree_miniRev.xlsx")
tw2 = pandas.read_csv("ChhoeTaigi_KamJitian.csv")
twX = pandas.read_excel("output_MOE_2023_05_23.xlsx")
idioms = pandas.read_excel("idiom_tl.xlsx")

ka_attr = ['把','將','跟','向']
hoo_attr=['被','讓','使','使得']
gei_attr = ['給']
verb_attr = ['VA','VB','VC','VD','VE','VCL','VK','VG']
verbs = ['VA','VAC','VB','VC','VCL','VD','VE','VF','VG','VJ','VK','VL','V_2','VI']
adverb_attr = ['D','Dfa','Dfb']
adj_attr = ['VH','VHC','A']
comp_adverb = ['點','些','一些','一些些','很','許多']
more_than_adverb = ['還','更','來得','還要']
jump_attr = {'COMMACATEGORY','PERIODCATEGORY','PAUSECATEGORY','PARENTHESISCATEGORY','FW','QUESTIONCATEGORY','COLONCATEGORY','EXCLAMATIONCATEGORY','Tai','DASHCATEGORY','SEMICOLONCATEGORY','WHITESPACE'}
switch_ma = {'COMMACATEGORY','PERIODCATEGORY','PAUSECATEGORY','PARENTHESISCATEGORY','FW','QUESTIONCATEGORY','COLONCATEGORY','SEMICOLONCATEGORY','EXCLAMATIONCATEGORY'}

# 或者是包含CATEGORY
verb_comp = ['離開','熬','努力','下降','升高']
verb_fin_attr = ['開', '高', '壞', '麻', '完','好','掉','燃']
verb_non_fin = ['展開','解開','打開','看好','展現好','提高','離開','召開','破壞']
verb_result = ['開','著','高','低','燃']
noun_comp = ['Na','NP','Nb','Nc','Nd','Nh','Ncd']
noun_types = ['Na','Nb','Nc','Nd','Neu','Nh']
noun_number =['Neu','Nes','Nf']#量詞
loc_time = ['Nc','Nd','Ncd']
questions = ['什麼', '誰', '哪裡']
time_word = ['上午','年','天','月','星期']
jumpout= ['，','、','。','「','」','：','；','！','％','(',')','（','）',';',':']

Q_end = ['kiám','ma']
#abbr_word = ['籲','可','據','仍','如','因','正','已','但']
abbr_word = ['籲','可','據','仍','因','已','但','另','應','偶','雖','需','除','易','且','並']
#abbr_word_ext = ['呼籲','可以','根據','仍然','如','因為','正在','已經','但是']
abbr_word_ext = ['呼籲','可以','根據','仍然','因為','已經','但是','另外','應該','偶爾','雖然','需要','除了','容易','而且','並且']
sent_seg = 0
use_more_num = ['每','多']

# 1 中文 2 台羅 3 次數 4 文白 5 詞性
# 優先: 詞性>文白>次數

CKIP_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzUxMiJ9.eyJ1c2VyX2lkIjoiODUiLCJzZXJ2aWNlX2lkIjoiMSIsImV4cCI6MTYzMTQyMDEyMiwidmVyIjowLjEsInNjb3BlcyI6IjAiLCJpYXQiOjE2MTU4NjgxMjIsImF1ZCI6IndtbWtzLmNzaWUuZWR1LnR3Iiwic3ViIjoiIiwiaWQiOjM2MiwiaXNzIjoiSldUIiwibmJmIjoxNjE1ODY4MTIyfQ.qLGCAJdaCmYHt39jeuJTdi1eMFjCMRdhA9DVrFLrliiu3HCMRdG27vpG-HlMZGWUQiOuHMfmx2J43bhSa38702mOYNyG4hdHCXRBIORrHPp-qJllEQ7LiVDfrl0czFixX0ut5y5N5EN9cd4B_VPl3AoVUHq3hJeKbvWqV8Yzyms"
need_debug = 0

tw_choose = list() 
TaiwanNP = list()

def max_times(match): # match是舊辭典Dataframe
    # if (need_debug==1): print("match:\n", match)
    match_list = match.values.tolist()
    wenbai_check = match.T.values.tolist()
    
    result = ""
    temp2 = ""
    
    if "白" in wenbai_check[6]  : # 有"白"註記，優先選
        if (need_debug==1): print(match_list)
        if (need_debug==1): print(match_list[wenbai_check[6].index("白")][1])
        print("選中讀音，因有文白註記：" , match_list[wenbai_check[6].index("白")][1])
        print("\n")
        
        temp2 = match_list[wenbai_check[6].index("白")][1]
        
        #result+=match_list[wenbai_check[6].index("白")][1]
    else: # 無文白註記，比次數
        max_index = match.loc[:,"次數"].idxmax()
        print("max_index = ", max_index)
        # match_list = match.values.tolist()
        print("選中讀音，最多次數：" , match.loc[max_index][1])
        print("\n")
        
        temp2 = match.loc[max_index][1]
        
        #result += match.loc[max_index][1]
    if ";" in temp2:
        temp2 = temp2.split(";")[0]
    elif "/" in temp2:
        temp2 = temp2.split("/")[0]
    elif " （" in temp2:
        temp2 = temp2.split(" （")[0]
    elif " (" in temp2:
        temp2 = temp2.split(" (")[0]
    result+=temp2
    return result

def max_timesX(match): # match是Dataframe
    if (need_debug==1): print("match:\n", match)
    result=""
    temp2=""
    match_list = match.values.tolist()
    wenbai_check = match.T.values.tolist()
    #result = ""
    if "白" in wenbai_check[4]  : # 有"白"註記，優先選
        if (need_debug==1): print(match_list)
        print("選中讀音，因有文白註記：" , match_list[wenbai_check[4].index("白")][2])
        print("\n")
        temp2 = match_list[wenbai_check[4].index("白")][2]
        
        #result+=match_list[wenbai_check[4].index("白")][2]
        #result+=match_list[wenbai_check[3].index("白")][1]
    else: # 無文白註記，比Index
        min_index = match.loc[:,"Index"].idxmin()
        print("min_index = ", min_index)
        # match_list = match.values.tolist()
        print("選中讀音，最高Index：" , match.loc[min_index][2])
        print("\n")
        temp2 = match.loc[min_index][2]
        
        #result += match.loc[min_index][2]
        #result += match.loc[max_index][1]
    if ";" in temp2:
        temp2 = temp2.split(";")[0]
    elif "/" in temp2:
        temp2 = temp2.split("/")[0]
    elif " （" in temp2:
        temp2 = temp2.split(" （")[0]
    elif " (" in temp2:
        temp2 = temp2.split(" (")[0]
    result+=temp2
    return result



def word_by_word(match): #新辭典拆字選音
    if (need_debug==1): print("match:\n", match)
    match_list = match.values.tolist()
    wenbai_check = match.T.values.tolist()
    print(wenbai_check)
    result = ""
    numeral_list = ["零", "一","壹", "二","貳","兩", "三", "四", "五", "六", "七", "八", "九","十", "百", "千", "萬","億","兆"]
    letters = ["a","b","c","d","e","f","g","h","i","j","k"]
    temp = wenbai_check[0][0]
    temp2=""
    if temp in numeral_list:
        if "白" in wenbai_check[4]:
            if (need_debug==1): print(match_list)
            print("選中讀音，因有文白註記：" , match_list[wenbai_check[4].index("白")][2])
            print("\n")
            #tw_choose.append( match_list[wenbai_check[3].index("白")][1] )
            temp2 = match_list[wenbai_check[6].index("白")][2]
            
            #result+=match_list[wenbai_check[6].index("白")][1]
        else:
            max_index = match.loc[:,"次數"].idxmax()
            print("max_index = ", max_index)
            # match_list = match.values.tolist()
            print("選中讀音，最多次數：" , match.loc[max_index][1])
            print("\n")
            #tw_choose.append(match.loc[max_index][1])
            temp2 = match.loc[max_index][1]            
            #result += match.loc[max_index][1]
        if ";" in temp2:
            temp2 = temp2.split(";")[0]
        elif "/" in temp2:
            temp2 = temp2.split("/")[0]
        elif " （" in temp2:
            temp2 = temp2.split(" （")[0]
        elif " (" in temp2:
            temp2 = temp2.split(" (")[0]
        result+=temp2
    elif temp=='年':
        print("most likely time word")
        result+=('nî')
    elif "文" in wenbai_check[4]  : # 拆字時有"文"註記，優先選
        if (need_debug==1): print(match_list)
        print("選中讀音，因有文白註記：" , match_list[wenbai_check[4].index("文")][2])
        print("\n")
        #tw_choose.append( match_list[wenbai_check[3].index("白")][1] )
        temp2 = match_list[wenbai_check[4].index("文")][2]
        if ";" in temp2:
            temp2 = temp2.split(";")[0]
        elif "/" in temp2:
            temp2 = temp2.split("/")[0]
        elif " （" in temp2:
            temp2 = temp2.split(" （")[0]
        elif " (" in temp2:
            temp2 = temp2.split(" (")[0]
        result+=temp2
        #result+=match_list[wenbai_check[6].index("文")][1]
    else: # 無文白註記，比次數
        
        min_index = match.loc[:,"Index"].idxmin()
        print("min_index = ", min_index)
        # match_list = match.values.tolist()
        print("選中讀音，最高Index：" , match.loc[min_index][2])
        print("\n")
        temp2 = match.loc[min_index][2]
        #tw_choose.append(match.loc[max_index][1])
        
        if ";" in temp2:
            temp2 = temp2.split(";")[0]
        elif "/" in temp2:
            temp2 = temp2.split("/")[0]
        elif " （" in temp2:
            temp2 = temp2.split(" （")[0]
        elif " (" in temp2:
            temp2 = temp2.split(" (")[0]
        result+=temp2
        #result += match.loc[max_index][1]    
    return result

def word_by_wordX(match): #拆字選音 (舊辭典)
    if (need_debug==1): print("match:\n", match)
    match_list = match.values.tolist()
    wenbai_check = match.T.values.tolist()
    print(wenbai_check)
    result = ""
    numeral_list = ["零", "一","壹", "二","貳","兩", "三", "四","肆", "五", "六", "七","柒", "八","捌", "九","十", "百", "千", "萬","億","兆"]
    temp = wenbai_check[0][0]
    temp2=""
    if temp in numeral_list  : # 翻譯數字
        try:
            if "白" in wenbai_check[6]:
                if (need_debug==1): print(match_list)
                print("選中讀音，因有文白註記：" , match_list[wenbai_check[6].index("白")][1])
                print("\n")
                #tw_choose.append( match_list[wenbai_check[3].index("白")][1] )
                temp2 = match_list[wenbai_check[6].index("白")][1]
            else:
                max_index = match.loc[:,"次數"].idxmax()
                print("max_index = ", max_index)
                # match_list = match.values.tolist()
                print("選中讀音，最多次數：" , match.loc[max_index][1])
                print("\n")
                #tw_choose.append(match.loc[max_index][1])
                temp2 = match.loc[max_index][1]            
                #result += match.loc[max_index][1]
        except Exception as e:
            print(e)
            print("skip wenbai check")
            max_index = match.loc[:,"次數"].idxmax()
            print("max_index = ", max_index)
            # match_list = match.values.tolist()
            print("選中讀音，最多次數：" , match.loc[max_index][1])
            print("\n")
            #tw_choose.append(match.loc[max_index][1])
            temp2 = match.loc[max_index][1]            
            
        
        if ";" in temp2:
            temp2 = temp2.split(";")[0]
        elif "/" in temp2:
            temp2 = temp2.split("/")[0]
        elif " （" in temp2:
            temp2 = temp2.split(" （")[0]
        elif " (" in temp2:
            temp2 = temp2.split(" (")[0]
        result+=temp2
            
    elif "文" in wenbai_check[6]  : # 拆字時有"文"註記，優先選
        if (need_debug==1): print(match_list)
        print("選中讀音，因有文白註記：" , match_list[wenbai_check[6].index("文")][1])
        print("\n")
        #tw_choose.append( match_list[wenbai_check[3].index("白")][1] )
        temp2 = match_list[wenbai_check[6].index("文")][1]
        if ";" in temp2:
            temp2 = temp2.split(";")[0]
        elif "/" in temp2:
            temp2 = temp2.split("/")[0]
        elif " （" in temp2:
            temp2 = temp2.split(" （")[0]
        elif " (" in temp2:
            temp2 = temp2.split(" (")[0]
        result+=temp2
        #result+=match_list[wenbai_check[4].index("文")][2]
    else: # 無文白註記，比次數
        max_index = match.loc[:,"次數"].idxmax()
        print("max_index = ", max_index)
        # match_list = match.values.tolist()
        print("選中讀音，最多次數：" , match.loc[max_index][1])
        print("\n")
        #tw_choose.append(match.loc[max_index][1])
        temp2 = match.loc[max_index][1]            
        #result += match.loc[max_index][1]
        if ";" in temp2:
            temp2 = temp2.split(";")[0]
        elif "/" in temp2:
            temp2 = temp2.split("/")[0]
        elif " （" in temp2:
            temp2 = temp2.split(" （")[0]
        elif " (" in temp2:
            temp2 = temp2.split(" (")[0]
        result+=temp2
        #result += match.loc[min_index][2]
    
    return result


def dict_lookup(chosen_pos,temp_Word,ch_data): #查找舊辭典
    result = ""
    
    ch_sh = ch_data.values.tolist()
        # ch_shT = ch_data.T.values.tolist()
        
    if len(ch_sh) > 1: # 有多筆結果        
        if chosen_pos == "VH" :
            res_df = ch_data.loc[ ch_data["詞性-教育部"] == "Adj" ]
        else:
            res_df = ch_data.loc[ ch_data["詞性-教育部"] == chosen_pos[0] ]
        print(chosen_pos)
        res_count = (res_df.shape)[0]
        if (need_debug==1): print(res_count)        

        if res_count == 0: # 對應詞性不存在
            
            result = max_times(ch_data)
        elif res_count == 1: # 對應詞性只有一個，選他
            res_df_list = res_df.values.tolist()
            one_choose = res_df_list[0][1]
            print("\n")
            if (need_debug==1): print(res_df_list)
            print("選中讀音，對應詞性只有一個：" , one_choose)
            result = one_choose
        else: # 對應詞性超過一個
            # 取出所有符合詞性之列表比較次數
            print("中文： ", temp_Word , " 詞性：",chosen_pos)
            result = max_times(res_df)
            """
            if chosen_pos == "VH" :
                result = max_times(ch_data.loc[ ch_data["詞性-教育部"] == "Adj" ])
            else:
                result = max_times(ch_data.loc[ ch_data["詞性-教育部"] == chosen_pos[0] ])
            """
    elif len(ch_sh)==0:
        print("無結果")
        result=""
    else: # 該詞只有一筆結果，直接選(不會是0因為empty上一層已被擋下)
        if (need_debug==1): print(ch_data)
        print("選中讀音，只有一筆結果：" , ch_sh[0][1])
        print("\n")
        #tw_choose.append( ch_sh[0][1])
        result = ch_sh[0][1]
    return result

def dict_new_lookupX(chosen_pos,temp_Word,ch_dataX): #查找新辭典
    result = ""
    #ch_data = tw.loc[ tw["中文"] == temp_Word ]
    ch_sh = ch_dataX.values.tolist()
        
    if len(ch_sh) > 1: # 有多筆結果
        # print(type(ch_data))
        if chosen_pos == "VH" or chosen_pos == "Adj":
            res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains("Adj") ]
        elif chosen_pos == "Da" or chosen_pos in adverb_attr:
            res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains("D") ]
        elif chosen_pos in verbs:
            res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains("V") ]
        elif chosen_pos in noun_types:
            res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains("N") ]
        elif chosen_pos == "Nf":
            res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains("Nf") ]
        else:
            res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains("F")]
        print(chosen_pos)
        res_count = (res_df.shape)[0]
        
        if (need_debug==1): print(res_count)
        
        if res_count == 0: # 對應詞性不存在
            result = max_timesX(ch_dataX)
        elif res_count == 1: # 對應詞性只有一個，選他
            res_df_list = res_df.values.tolist()
            one_choose = res_df_list[0][2]
            print("\n")
            print(res_df_list)
            print("選中讀音，對應詞性只有一個：" , one_choose)
            result = one_choose
        else: # 對應詞性超過一個
            # 取出所有符合詞性之列表比較次數
            print("中文： ", temp_Word , " 詞性：",chosen_pos)
            #res_df_list = res_df.values.tolist()
            which_choose = max_timesX(res_df)
            """
            if chosen_pos == "VH" :
                which_choose = max_timesX(ch_dataX.loc[ ch_dataX["詞性"].str.contains("Adj")])
            elif chosen_pos == "Da" or chosen_pos in adverb_attr:
                which_choose = max_timesX(ch_dataX.loc[ ch_dataX["詞性"].str.contains("D")])
            elif chosen_pos in verbs:
                which_choose = max_timesX(ch_dataX.loc[ ch_dataX["詞性"].str.contains("V")])
            elif chosen_pos == 'Nf':
                which_choose = max_timesX(ch_dataX.loc[ ch_dataX["詞性"].str.contains("Nf")])
            elif chosen_pos in noun_types:
                which_choose = max_timesX(ch_dataX.loc[ ch_dataX["詞性"].str.contains("N")])                            
            else:
                which_choose = max_timesX(ch_dataX.loc[ ch_dataX["詞性"].str.contains("F") ])
            """
            result = which_choose
    elif len(ch_sh)==0:
        print("無結果")
        if chosen_pos=='Neu' and temp_Word[-1]=="多":
            rx = temp_Word[:-1]
            result=mix_word(rx)+"-kuá"
        else:
            result=mix_word(temp_Word)
    else: # 該詞只有一筆結果，直接選(不會是0因為empty上一層已被擋下)
        if (need_debug==1): print(ch_dataX)
        print("選中讀音，只有一筆結果：" , ch_sh[0][2])
        print("\n")
        #tw_choose.append( ch_sh[0][1])
        result = ch_sh[0][2]
    return result



def TransNP(input_ch): #翻譯名詞片語
    
    TaiwanNP.clear()
    dict_of_ch = {}
    wc , pos , _ner= call_ckip([input_ch])
    if (need_debug==1): print(wc[0])
    if (need_debug==1): print(pos[0])
    ckip_result = list()
    go_search=0
    wc = wc[0]
    pos = pos[0]
    temp_len = len(wc)
    while go_search != temp_len: #處理"不"+"到"/"懂"/"是"字尾
        print(go_search)
        if wc[go_search ]=='不' and go_search +1!=len(wc):
            if (wc[go_search+1] =='到' or wc[go_search +1] =='懂'): # V+不到/不懂 --> V+無(台羅)
                if go_search !=0: #非以"不到"或"不懂"為開頭
                    if pos[go_search-1] in verb_attr:
                        wc[go_search ]='無'
                        pos[go_search ]='VJ'
                        del(wc[go_search+1])
                        del(pos[go_search+1])
                        temp_len = len(wc) #updated length
                        go_search+=1
                        
                    else:
                        merge_str = wc[go_search ]+wc[go_search+1]
                        wc[go_search]=merge_str
                        pos[go_search]='VJ'
                        del(wc[go_search+1])
                        del(pos[go_search+1])
                        temp_len = len(wc) #updated length
                        go_search+=1
                        
                else:
                    merge_str = wc[go_search ]+wc[go_search+1]
                    wc[go_search ]=merge_str
                    pos[go_search ]='VJ'
                    del(wc[go_search+1])
                    del(pos[go_search+1])
                    temp_len = len(wc) #updated length
                    go_search+=1
                    
            elif wc[go_search+1] =='是' and pos[go_search+1] == 'SHI': #'不'+'是'
                wc[go_search ]='不是'
                pos[go_search ]='VG'
                del(wc[go_search+1])
                del(pos[go_search+1])
                temp_len = len(wc) #updated length
                go_search+=1
                #neg_plus_V += 1
            else:
                go_search+=1
        elif pos[go_search ]=='Nf' and pos[go_search-1]!='Neu':
            wc.insert(go_search,'一')
            pos.insert(go_search,'Neu')
            go_search+=1
        elif (wc[go_search] =='昨' or wc[go_search] =='今' or wc[go_search] =='明') and pos[go_search+1]=="Neu" and (wc[go_search+2] =='日' or wc[go_search+2] =='月' or wc[go_search+2] =='年'):
            rev_word = wc[go_search] + wc[go_search+2]
            wc[go_search] = rev_word
            pos[go_search] = 'Nd'
            temp = wc[go_search+1][1:-1]
            wc[go_search+1] = temp
        elif wc[go_search]=="二" and go_search +1!=len(wc): # "二+單位詞"
            if pos[go_search+1]=="Nf":
                wc[go_search]="兩"
            go_search+=1
        elif wc[go_search]=="-": # ex: 流感的潛伏期通常為 一-四 天
            if go_search-1 >0 and go_search +1!=len(wc):
                if pos[go_search-1]=="Neu" and pos[go_search+1]=="Neu":
                    wc[go_search] = "到"
            go_search+=1
        elif wc[go_search]=="、": # ex: 一、 發燒天數:約七天。二、 潛伏期:
            if go_search-1 >0 and go_search +1!=len(wc):
                if pos[go_search-1]=="Neu" and pos[go_search+1]!="Neu":
                    wc[go_search] = ":"
                    wc[go_search-1] = "第" + wc[go_search-1]
            go_search+=1
        else:
            go_search+=1
    for word in range(len(wc)):
        tmp_list = list()
        tmp_list.append(wc[word])
        tmp_list.append(pos[word])

        ckip_result.append(tmp_list)
    if (need_debug==1): print(ckip_result)
    if (need_debug==1): print(len(ckip_result))
    
    for res_index in range(len(ckip_result)):
        print("當前處裡： " , ckip_result[res_index][0])
        temp_Word = ckip_result[res_index][0]
        if ckip_result[res_index][1] not in jump_attr:
            temp_Word = ckip_result[res_index][0].replace(" ","")
        ch_dataX = twX.loc[ twX["對應華語"] ==temp_Word ]  #所有結果，不管詞性
        # 應該在這裡寫個詞性轉換，將原詞姓ckip_result[res_index][1][0]看看透過dict還是甚麼的轉成系統統一詞性等
        if ckip_result[res_index][1] in jump_attr: # 標點符號，直接丟到最終選擇台羅裡
            if ckip_result[res_index][1]=='FW':
                if not (ch_dataX.empty):
                    Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word,ch_dataX)
                    TaiwanNP.append(Tailuo)
                else:
                    Tailuo = mix_word(temp_Word)
                    TaiwanNP.append(Tailuo)
            else:
                TaiwanNP.append( ckip_result[res_index][0])
                continue
        elif ckip_result[res_index][0] =='這':
            
            if res_index+1>=len(ckip_result[res_index]):
                TaiwanNP.append("tse")
                pron_list = []
                pron_list.append("tse")
                dict_of_ch['這'] = pron_list
            else:
                try:
                    if ckip_result[res_index+1][1] in noun_number:
                        TaiwanNP.append("tsit")
                        pron_list = []
                        pron_list.append("tsit")
                        dict_of_ch['這'] = pron_list
                    else:
                        TaiwanNP.append("tse")
                        pron_list = []
                        pron_list.append("tse")
                        dict_of_ch['這'] = pron_list
                except IndexError:
                    TaiwanNP.append("tse")
                    pron_list = []
                    pron_list.append("tse")
                    dict_of_ch['這'] = pron_list
        elif ckip_result[res_index][0] =='那':
            
            if res_index+1==len(ckip_result[res_index]):
                TaiwanNP.append("he")
                pron_list = []
                pron_list.append("he")
                dict_of_ch['那'] = pron_list
            else:
                try:
                    if ckip_result[res_index+1][1] in noun_number:
                        TaiwanNP.append("hit")
                        pron_list = []
                        pron_list.append("hit")
                        dict_of_ch['那'] = pron_list
                    else:
                        TaiwanNP.append("he")
                        pron_list = []
                        pron_list.append("he")
                        dict_of_ch['那'] = pron_list
                except IndexError:
                    TaiwanNP.append("he")
                    pron_list = []
                    pron_list.append("he")
                    dict_of_ch['那'] = pron_list
        elif ckip_result[res_index][0] =='不':
            
            #no_amount_dao = 0
            #no_amount_uan = 0
            #no_plus_V = 0
            #no_plus_Adj = 0
            if res_index+1 != len(ckip_result):
                if ckip_result[res_index+1][1] in verbs:                    
                    TaiwanNP.append("m̄")
                    pron_list = []
                    pron_list.append("m̄")
                    dict_of_ch['不'] = pron_list
                elif ckip_result[res_index+1][1] =='SHI' or ckip_result[res_index+1][0] =='hōo':
                    TaiwanNP.append("m̄")
                    pron_list = []
                    pron_list.append("m̄")
                    dict_of_ch['不'] = pron_list
                elif ckip_result[res_index+1][1] in adj_attr:                    
                    TaiwanNP.append("bô")
                    pron_list = []
                    pron_list.append("bô")
                    dict_of_ch['不'] = pron_list
                elif ckip_result[res_index+1][0] =='完' or ckip_result[res_index+1][0] =='太' or ckip_result[res_index+1][0] =='在':
                    TaiwanNP.append("bô")
                    pron_list = []
                    pron_list.append("bô")
                    dict_of_ch['不'] = pron_list
                elif ckip_result[res_index+1][0] =='到':                    
                    TaiwanNP.append("bē")
                    pron_list = []
                    pron_list.append("bē")
                    dict_of_ch['不'] = pron_list
                else:
                    TaiwanNP.append("put")
                    pron_list = []
                    pron_list.append("put")
                    dict_of_ch['不'] = pron_list
            else:
                TaiwanNP.append("bô") #default
                pron_list = []
                pron_list.append("bô")
                dict_of_ch['不'] = pron_list
        else:
            if temp_Word!='':
                if temp_Word[-1] == '到' and temp_Word!='報到':
                    if ckip_result[res_index][1] in verb_attr :
                        if res_index+1 != len(ckip_result):
                            if ckip_result[res_index+1][1] in loc_time: #
                                #temp_Word = temp_Word[:-1]+'--tio̍h'
                                Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word,ch_dataX)
                                if ch_dataX.empty:  #未知詞，且是因為字尾
                                    ch_data_O = twX.loc[ twX["對應華語"] ==temp_Word[:-1] ]
                                    Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word[:-1],ch_data_O)
                                    #Tailuo = dict_lookup(ckip_result[res_index][1],temp_Word[:-1],ch_data)
                                    TaiwanNP.append(Tailuo+'-kàu')
                                    pron_list = []
                                    pron_list.append(Tailuo+'-kàu')
                                    dict_of_ch[temp_Word] = pron_list
                                else:
                                    TaiwanNP.append(Tailuo)
                                    pron_list = []
                                    pron_list.append(Tailuo)
                                    dict_of_ch[temp_Word] = Tailuo
                            else:
                                Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word[:-1],ch_dataX)
                                if ch_dataX.empty:
                                    ch_data_O = twX.loc[ twX["對應華語"] ==temp_Word[:-1] ]
                                    Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word[:-1],ch_data_O)
                                    TaiwanNP.append(Tailuo+'--tio̍h')
                                    pron_list = []
                                    pron_list.append(Tailuo+'--tio̍h')
                                    dict_of_ch[temp_Word] = pron_list
                                else:
                                    TaiwanNP.append(Tailuo)
                                    pron_list = []
                                    pron_list.append(Tailuo)
                                    dict_of_ch[temp_Word] = pron_list
                        else:
                            Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word[:-1],ch_dataX)
                            if ch_dataX.empty:
                                ch_data_O = twX.loc[ twX["對應華語"] ==temp_Word[:-1] ]
                                Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word[:-1],ch_data_O)
                                TaiwanNP.append(Tailuo+'--tio̍h')
                                pron_list = []
                                pron_list.append(Tailuo+'--tio̍h')
                                dict_of_ch[temp_Word] = pron_list
                            else:
                                TaiwanNP.append(Tailuo)
                                pron_list = []
                                pron_list.append(Tailuo)
                                dict_of_ch[temp_Word] = pron_list
                    else:
                        print("proceed")
                        mixup = mix_word(temp_Word)
                        TaiwanNP.append(mixup)
                        pron_list = []
                        pron_list.append(mixup)
                        dict_of_ch[temp_Word] = pron_list
                elif temp_Word[-1] == '完' and ckip_result[res_index][1] in verb_attr and temp_Word!='完':
                    #temp_Word = temp_Word[:-1]+' liáu'
                    print(temp_Word[:-1])
                    Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word,ch_dataX)
                    if Tailuo == "":
                        ch_data_O = twX.loc[ twX["對應華語"] ==temp_Word[:-1] ]
                        Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word[:-1],ch_data_O)
                        #Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word[:-1],ch_dataX)
                        TaiwanNP.append(Tailuo+'-liáu')
                        pron_list = []
                        pron_list.append(Tailuo+'-liáu')
                        dict_of_ch[temp_Word] = pron_list
                    else:
                        TaiwanNP.append(Tailuo)
                        pron_list = []
                        pron_list.append(Tailuo)
                        dict_of_ch[temp_Word] = pron_list
                elif (temp_Word[-1] == '年' and ckip_result[res_index][1]=='Nd'):
                    Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word,ch_dataX)
                    if Tailuo == "":
                        ch_data_O = twX.loc[ twX["對應華語"] ==temp_Word[:-1] ]
                        Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word[:-1],ch_data_O)
                        tw_choose.append(Tailuo+'-nî')
                        pron_list = []
                        pron_list.append(Tailuo+'-nî')
                        dict_of_ch[temp_Word] = pron_list
                    else:
                        tw_choose.append(Tailuo)
                        dict_of_ch[temp_Word] = Tailuo
                elif (temp_Word[-1] == '多' and ckip_result[res_index][1]=='Neu'):
                    Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word,ch_dataX)
                    if Tailuo == "":
                        ch_data_O = twX.loc[ twX["對應華語"] ==temp_Word[:-1] ]
                        Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word[:-1],ch_data_O)
                        tw_choose.append(Tailuo+'-kuá')
                        pron_list = []
                        pron_list.append(Tailuo+'-kuá')
                        dict_of_ch[temp_Word] = pron_list
                    else:
                        tw_choose.append(Tailuo)
                        dict_of_ch[temp_Word] = Tailuo
                elif (temp_Word == '戴' and res_index+1 != len(ckip_result)): #戴帽子 vs. 戴口罩 慣用詞
                    if ckip_result[res_index+1][0]=='口罩':
                        tw_choose.append("kuà") #掛口罩
                        dict_of_ch[temp_Word] = "kuà"
                    else:                        
                        Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word,ch_dataX)
                        tw_choose.append(Tailuo)
                        pron_list = []
                        pron_list.append(Tailuo)
                        dict_of_ch[temp_Word] = pron_list
                elif (temp_Word[-1] == '-' or temp_Word[0] == '-') and ckip_result[res_index][1]=="Neu":
                    temp_WordM = temp_Word.replace("-","")
                    if temp_Word[-1] == '-':
                        #temp_Word = temp_Word[:-1]
                        ch_data_O = twX.loc[ twX["對應華語"] ==temp_WordM ]
                        Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_WordM,ch_data_O)
                        
                        tw_choose.append(Tailuo+'-kàu')
                        pron_list = []
                        pron_list.append(Tailuo+'-kàu')
                        dict_of_ch[temp_Word] = pron_list
                    else:
                        #temp_Word = temp_Word[0:]
                        ch_data_O = twX.loc[ twX["對應華語"] ==temp_WordM ]
                        Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_WordM,ch_data_O)
                        
                        tw_choose.append('kàu-'+Tailuo)
                        pron_list = []
                        pron_list.append('kàu-'+Tailuo)
                        dict_of_ch[temp_Word] = pron_list
                
                elif ch_dataX.empty: # 一般中文詞但未收錄至新辭典
                    # print(ckip_result[res_index][0])
                    ch_data = tw.loc[ tw["中文"] == ckip_result[res_index][0] ]
                    if ch_data.empty: # 中文詞不在辭典裡
                        if (re.match(r'[\u4e00-\u9fff]+', ckip_result[res_index][0]))==False:
                            TaiwanNP.append(ckip_result[res_index][0])
                        else:
                            print("ch not found: " , ckip_result[res_index][0])
                            mixup = mix_word(ckip_result[res_index][0])
                            TaiwanNP.append(mixup)
                            pron_list = []
                            pron_list.append(mixup)
                            dict_of_ch[temp_Word] = pron_list
                            print("\n")
                    else: # 中文詞在辭典裡
                        # print(ch_data)
                        ch_sh = ch_data.values.tolist()
                        
                        
                        if len(ch_sh) > 1: # 有多筆結果
                            # print(type(ch_data))
                            temp_choose = []
                            for a in range(len(ch_sh)):
                                if type(ch_sh[a][1])==str:
                                    temp_choose.append(ch_sh[a][1])                                    
                            dict_of_ch[temp_Word] = temp_choose
                            if ckip_result[res_index][1] == "VH" :
                                res_df = ch_data.loc[ ch_data["詞性-教育部"] == "Adj" ]
                            else:
                                res_df = ch_data.loc[ ch_data["詞性-教育部"] == ckip_result[res_index][1][0] ]
                            print(ckip_result[res_index][1])
                            res_count = (res_df.shape)[0]
                            print(res_count)
                            if res_count == 0: # 對應詞性不存在                                
                                only_choose = max_times(ch_data)
                                TaiwanNP.append( only_choose )
                                #dict_of_ch[temp_Word] = only_choose
                            elif res_count == 1: # 對應詞性只有一個，選他
                                res_df_list = res_df.values.tolist()
                                one_choose = res_df_list[0][1]
                                print("\n")
                                print(res_df_list)
                                print("選中讀音，對應詞性只有一個：" , one_choose)
                                TaiwanNP.append( one_choose )
                                #dict_of_ch[temp_Word] = one_choose
                            else: # 對應詞性超過一個
                                # 取出所有符合詞性之列表比較次數
                                print("中文： ", ckip_result[res_index][0] , " 詞性：",ckip_result[res_index][1])
                                if ckip_result[res_index][1] == "VH" :
                                    which_choose = max_times(ch_data.loc[ ch_data["詞性-教育部"] == "Adj" ])
                                else:
                                    which_choose = max_times(ch_data.loc[ ch_data["詞性-教育部"] == ckip_result[res_index][1][0] ])
                                TaiwanNP.append(which_choose)
                                #dict_of_ch[temp_Word] = which_choose
                        else: # 該詞只有一筆結果，直接選(不會是0因為empty上一層已被擋下)
                            print(ch_data)
                            print("選中讀音，只有一筆結果：" , ch_sh[0][1])
                            print("\n")
                            TaiwanNP.append( ch_sh[0][1])
                            pron_list = []
                            pron_list.append(ch_sh[0][1])
                            dict_of_ch[temp_Word] = pron_list
                            #dict_of_ch[temp_Word] = ch_sh[0][1]
                else: #可在新辭典查詞
                    ch_shR = ch_dataX.values.tolist()
                        
                    if len(ch_shR) > 1: # 有多筆結果
                        temp_choose = []
                        for a in range(len(ch_shR)):
                            temp_choose.append(ch_shR[a][2])                                    
                        dict_of_ch[temp_Word] = temp_choose
                        # print(type(ch_data))
                        try:
                            if ckip_result[res_index][1] == "VH" or ckip_result[res_index][1] == "Adj":
                                res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains("Adj") ]
                            elif ckip_result[res_index][1] == "Da" or ckip_result[res_index][1] in adverb_attr:
                                res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains("D") ]
                            elif ckip_result[res_index][1] in verbs:
                                res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains("V") ]
                            elif ckip_result[res_index][1] in noun_types:
                                res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains("N") ]
                            elif ckip_result[res_index][1] == "Nf":
                                res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains("Nf") ]
                            else:
                                #res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains(ckip_result[res_index][1][0])]
                                res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains("F")]
                            print(ckip_result[res_index][1])
                            res_count = (res_df.shape)[0]
                            
                            print(res_count)

                            if res_count == 0: # 對應詞性不存在                                
                                only_choose = max_timesX(ch_dataX)
                                TaiwanNP.append( only_choose )
                                #dict_of_ch[temp_Word] = only_choose
                            elif res_count == 1: # 對應詞性只有一個，選他
                                res_df_list = res_df.values.tolist()
                                one_choose = res_df_list[0][2]
                                print("\n")
                                print(res_df_list)
                                print("選中讀音，對應詞性只有一個：" , one_choose)
                                TaiwanNP.append( one_choose )
                                #dict_of_ch[temp_Word] = one_choose
                            else: # 對應詞性超過一個
                                print("中文： ", ckip_result[res_index][0] , " 詞性：",ckip_result[res_index][1])
                                res_df_list = res_df.values.tolist()                                
                                which_choose = max_timesX(res_df)
                                """
                                if ckip_result[res_index][1] == "VH" :
                                    which_choose = max_timesX(ch_dataX.loc[ ch_dataX["詞性"].str.contains("Adj")])
                                elif ckip_result[res_index][1] == "Da" or ckip_result[res_index][1] in adverb_attr:
                                    which_choose = max_timesX(ch_dataX.loc[ ch_dataX["詞性"].str.contains("D")])
                                elif ckip_result[res_index][1] in verbs:
                                    which_choose = max_timesX(ch_dataX.loc[ ch_dataX["詞性"].str.contains("V")])
                                elif ckip_result[res_index][1] == 'Nf':
                                    which_choose = max_timesX(ch_dataX.loc[ ch_dataX["詞性"].str.contains("Nf")])
                                elif ckip_result[res_index][1] in noun_types:
                                    which_choose = max_timesX(ch_dataX.loc[ ch_dataX["詞性"].str.contains("N")])                            
                                else:
                                    which_choose = max_timesX(ch_dataX.loc[ ch_dataX["詞性"].str.contains("F") ])
                                """
                                TaiwanNP.append(which_choose)
                                #dict_of_ch[temp_Word] = which_choose
                        except Exception as ee:
                            print(ee)                            
                    else: # 該詞只有一筆結果，直接選(不會是0因為empty上一層已被擋下)
                        print(ch_dataX)
                        print("選中讀音，只有一筆結果：" , ch_shR[0][2])
                        print("\n")
                        TaiwanNP.append( ch_shR[0][2])
                        pron_list = []
                        pron_list.append(ch_shR[0][2])
                        dict_of_ch[temp_Word] = pron_list
            else: TaiwanNP.append(temp_Word)

    print(TaiwanNP)
    print(dict_of_ch)

    tw_NP_str = str()
    for twc in range(len(TaiwanNP)):
        if type(TaiwanNP[twc])==float: #account for nan value
            throw_in = "XXX"
        else:
            throw_in = TaiwanNP[twc]
            if ";" in throw_in and throw_in!= ";":
                throw_in = throw_in.split(";")[0]
            elif "/" in throw_in and throw_in!= "/":
                throw_in = throw_in.split("/")[0]
            elif " （" in throw_in:
                throw_in = throw_in.split(" （")[0]
            elif " (" in throw_in:
                throw_in = throw_in.split(" (")[0]
        if tw_NP_str=='': #填第一個詞
            tw_NP_str = tw_NP_str + throw_in
        elif pos[twc] in jump_attr:
            if pos[twc]!='FW' and pos[twc]!='Tai': #標點符號
                tw_NP_str = tw_NP_str + throw_in
            else: #外語詞彙或台羅音
                tw_NP_str = tw_NP_str +' ' + throw_in
        elif str.isdigit(throw_in)==True:
            tw_NP_str = tw_NP_str +' ' + throw_in
        elif pos[twc-1] in jump_attr:
            if pos[twc-1]!='FW' and pos[twc-1]!='Tai': #前一詞標點符號
                tw_NP_str = tw_NP_str + throw_in
            else: #前一句外語詞彙
                tw_NP_str = tw_NP_str +' ' + throw_in
        elif twc+1 != len(pos[0]): # while not at end
            
            if throw_in.startswith("--"): #輕聲
                tw_NP_str = tw_NP_str + throw_in
            elif (pos[twc]=='Nf' and pos[twc-1]=='Neu') or (pos[twc]=='Neu' and pos[twc-1]=='Neu'):
                tw_NP_str = tw_NP_str + "-" + throw_in
            elif pos[twc]=='DE' and throw_in=="ê":
                print("add hyphen")
                tw_NP_str = tw_NP_str + "-" + throw_in
            elif pos[twc-1]=='Nh' and throw_in != '的':
                tw_NP_str = tw_NP_str + ' ' + throw_in
            elif str.isdigit(TaiwanNP[twc-1])==True:
                tw_NP_str = tw_NP_str +' ' + throw_in
            elif TaiwanNP[twc-1] == '的' or pos[twc-1]=='Nf' or pos[twc]=='Nb' or pos[twc-1]=='Nb' or (pos[twc-1]=='Ng' and TaiwanNP[twc] != '的') or pos[twc-1] in verbs or pos[twc-1]=='Nc':
                tw_NP_str = tw_NP_str +' ' + throw_in
            else:
                print("other")
                tw_NP_str = tw_NP_str + "-" + throw_in
        else: #最後一詞
            if throw_in.startswith("--"):
                tw_NP_str = tw_NP_str + throw_in
            elif (pos[twc]=='Nf' and pos[twc-1]=='Neu') or (pos[twc]=='Neu' and pos[twc-1]=='Neu'):
                tw_NP_str = tw_NP_str + "-" + throw_in
            elif pos[twc]=='DE' and throw_in=="ê":
                print("add hyphen")
                tw_NP_str = tw_NP_str + "-" + throw_in
            elif pos[twc-1]=='Nh' and throw_in != '的':
                tw_NP_str = tw_NP_str + ' ' + throw_in
            elif str.isdigit(TaiwanNP[twc-1])==True:
                tw_NP_str = tw_NP_str +' ' + throw_in
            elif TaiwanNP[twc-1] == '的' or pos[twc-1]=='Nf' or pos[twc]=='Nb' or pos[twc-1]=='Nb'  or (pos[twc-1]=='Ng' and TaiwanNP[twc] != '的') or pos[twc-1] in verbs or pos[twc-1]=='Nc':
                tw_NP_str = tw_NP_str +' ' + throw_in
            else:
                tw_NP_str = tw_NP_str + "-" + throw_in
    
    return tw_NP_str,dict_of_ch

def mix_word(unknown_word): #拆字選音
    print ("OOV: ",unknown_word)
    unknown_word = unknown_word.replace(" ","")
    unknown_word = unknown_word.replace("-","到")
    print(len(unknown_word))
    numeral_list = ["零", "一","壹", "二","貳", "三","參", "四", "五", "六", "七","柒" "八","捌", "九","十", "百", "千", "萬","億","兆"]
    hyphen = 0
    mix = ""
    #match = re.match(r"([a-z]+)([0-9]+)", 'foofo21', re.I)
    
    for x in range(len(unknown_word)):
        word = unknown_word[x]
        print(word)
        print(str.isdigit(word))
        print(word.encode('utf-8').isalpha())
        symbols = ['(',')','（','）']
        if (( str.isdigit(word)==True) and word not in numeral_list): #非國語數字的其他符號
            print("skip")
            mix+=word
            hyphen+=1
        elif word.encode('utf-8').isalpha() is True: #英文字母縮寫 (GPT) 或新詞中的字母(維生素B12)個別發音
            signal_choose = twX.loc[ twX["對應華語"] == word ]
            print("signal_choose_alphabet" , word , "\n" , signal_choose)
            if signal_choose.empty:
                # tw_choose.append("，")
                kam_choose = tw2.loc[tw2["hanji_taibun"] == word ]
                if kam_choose.empty:
                    #_temp = "[找不到此音：" + word + "]"
                    _temp = " "
                    mix= mix+_temp
                    try:
                        if (str.isdigit(unknown_word[x+1])==True or unknown_word[x+1].encode('utf-8').isalpha()==True) and unknown_word[x+1] not in numeral_list:
                            mix+=" "
                        else:
                            mix+="-"
                            hyphen+=1
                    except Exception:
                        print("end index")

                else:
                    kam_choose_l = kam_choose.values.tolist()
                    print("kam_choose" , word , "\n" , kam_choose,"\n",kam_choose_l[0][8])
                    
                    mix+=kam_choose_l[0][8]
                    if x!= (len(unknown_word)-1):
                        if (str.isdigit(unknown_word[x+1])==True or unknown_word[x+1].encode('utf-8').isalpha()==True) and unknown_word[x+1] not in numeral_list:
                            mix+=" "
                        else:
                            mix+="-"
                            hyphen+=1
            else: #英文字母縮寫
                mix+=word_by_word(signal_choose)
                if x!= (len(unknown_word)-1):
                    if (str.isdigit(unknown_word[x+1])==True or unknown_word[x+1].encode('utf-8').isalpha()==True) and unknown_word[x+1] not in numeral_list:
                        mix+=" "
                    else:
                        mix+="-"
                        hyphen+=1
        
        elif word in numeral_list:
            if x!=0:
                if word=="一" and "百分之" in unknown_word:
                    mix+="it"
                    hyphen+=1
                elif word=="二" and "百分之" in unknown_word:
                    mix+="jī"
                    hyphen+=1
                else:                    
                    
                    signal_choose = tw.loc[ tw["中文"] == word ]
            
                    print("signal_choose_num" , word , "\n" , signal_choose)
                    if signal_choose.empty:
                        # tw_choose.append("，")
                        kam_choose = tw2.loc[tw2["hanji_taibun"] == word ]
                        if kam_choose.empty:
                            #_temp = "[找不到此音：" + word + "]"
                            _temp = " "
                            mix= mix+_temp
                            try:
                                if (str.isdigit(unknown_word[x+1])==True or unknown_word[x+1].encode('utf-8').isalpha()==True) and unknown_word[x+1] not in numeral_list:
                                    mix+=" "
                                else:
                                    mix+="-"
                                    hyphen+=1
                            except Exception:
                                print("end index")

                        else:
                            kam_choose_l = kam_choose.values.tolist()
                            print("kam_choose" , word , "\n" , kam_choose,"\n",kam_choose_l[0][8])
                            
                            mix+=kam_choose_l[0][8]
                            if x!= (len(unknown_word)-1):
                                if (str.isdigit(unknown_word[x+1])==True or unknown_word[x+1].encode('utf-8').isalpha()==True) and unknown_word[x+1] not in numeral_list:
                                    mix+=" "
                                else:
                                    mix+="-"
                                    hyphen+=1
                    else: #數字
                        mix+=word_by_word(signal_choose)
                        if x!= (len(unknown_word)-1):
                            if (str.isdigit(unknown_word[x+1])==True or unknown_word[x+1].encode('utf-8').isalpha()==True) and unknown_word[x+1] not in numeral_list:
                                mix+=" "
                            else:
                                mix+="-"
                                hyphen+=1
                    
            else: #數字 (句子開頭)
                signal_choose = tw.loc[ tw["中文"] == word ]            
                print("signal_choose_num_atzero" , word , "\n" , signal_choose)
                if signal_choose.empty:
                    # tw_choose.append("，")
                    kam_choose = tw2.loc[tw2["hanji_taibun"] == word ]
                    if kam_choose.empty:
                        #_temp = "[找不到此音：" + word + "]"
                        _temp = " "
                        mix= mix+_temp
                        try:
                            if (str.isdigit(unknown_word[x+1])==True or unknown_word[x+1].encode('utf-8').isalpha()==True) and unknown_word[x+1] not in numeral_list:
                                mix+=" "
                            elif unknown_word[x]==" ":
                                print("empty space")
                                mix+=" "
                            else:
                                mix+="-"
                                hyphen+=1
                        except Exception:
                            print("end index")

                    else:
                        kam_choose_l = kam_choose.values.tolist()
                        print("kam_choose" , word , "\n" , kam_choose,"\n",kam_choose_l[0][8])
                        
                        mix+=kam_choose_l[0][8]
                        if x!= (len(unknown_word)-1):
                            if (str.isdigit(unknown_word[x+1])==True or unknown_word[x+1].encode('utf-8').isalpha()==True) and unknown_word[x+1] not in numeral_list:
                                mix+=" "
                            else:
                                mix+="-"
                                hyphen+=1
                else: #數字 (句子開頭)
                    mix+=word_by_word(signal_choose)
                    if x!= (len(unknown_word)-1):
                        if (str.isdigit(unknown_word[x+1])==True or unknown_word[x+1].encode('utf-8').isalpha()==True) and unknown_word[x+1] not in numeral_list:
                            mix+=" "
                        else:
                            mix+="-"
                            hyphen+=1
                
        
        elif word in symbols:
            print("is symbol")
            mix+=word
            hyphen+=1
        else: #選其他字
            signal_choose = tw.loc[ tw["中文"] == word ]
            
            print("signal_choose" , word , "\n" , signal_choose)
            if signal_choose.empty:
                # tw_choose.append("，")
                kam_choose = tw2.loc[tw2["hanji_taibun"] == word ]
                if kam_choose.empty:
                    #_temp = "[找不到此音：" + word + "]"
                    _temp = " "
                    mix= mix+_temp
                    try:
                        if (str.isdigit(unknown_word[x+1])==True or unknown_word[x+1].encode('utf-8').isalpha()==True) and unknown_word[x+1] not in numeral_list:
                            mix+=" "
                        else:
                            mix+="-"
                            hyphen+=1
                    except Exception:
                        print("end index")

                else:
                    kam_choose_l = kam_choose.values.tolist()
                    print("kam_choose" , word , "\n" , kam_choose,"\n",kam_choose_l[0][8])
                    
                    mix+=kam_choose_l[0][8]
                    if x!= (len(unknown_word)-1):
                        if (str.isdigit(unknown_word[x+1])==True or unknown_word[x+1].encode('utf-8').isalpha()==True) and unknown_word[x+1] not in numeral_list:
                            mix+=" "
                        else:
                            mix+="-"
                            hyphen+=1

            else: #選其他字 (到舊辭典查)
                mix+=word_by_wordX(signal_choose)
                if x!= (len(unknown_word)-1):
                    if (str.isdigit(unknown_word[x+1])==True or unknown_word[x+1].encode('utf-8').isalpha()==True) and unknown_word[x+1] not in numeral_list:
                        mix+=" "
                    else:
                        mix+="-"
                        hyphen+=1               
            
    return mix


def choose_main(wcR,posR,idioms):
    tw_choose.clear()
    idioms_len = 0
    all_ch_trans = {} #record each Chinese word and their translation
    go_search=0
    temp_len = len(wcR)
    while go_search != temp_len: #處理"不"+"到"/"懂"/"是"字尾
        print(go_search)
        if wcR[go_search ]=='不' and go_search +1!=len(wcR):
            if (wcR[go_search+1] =='到' or wcR[go_search +1] =='懂'): # V+不到/不懂 --> V+無(台羅)
                if go_search !=0: #非以"不到"或"不懂"為開頭
                    if posR[go_search-1] in verb_attr:
                        wcR[go_search ]='無'
                        posR[go_search ]='VJ'
                        del(wcR[go_search+1])
                        del(posR[go_search+1])
                         #updated length                        
                    else:
                        merge_str = wcR[go_search ]+wcR[go_search+1]
                        wcR[go_search]=merge_str
                        posR[go_search]='VJ'
                        del(wcR[go_search+1])
                        del(posR[go_search+1])
                         #updated length                        
                else:
                    merge_str = wcR[go_search ]+wcR[go_search+1]
                    wcR[go_search ]=merge_str
                    posR[go_search ]='VJ'
                    del(wcR[go_search+1])
                    del(posR[go_search+1])
                     #updated length
                    
            elif wcR[go_search+1] =='是' and posR[go_search+1] == 'SHI': #'不'+'是'
                wcR[go_search ]='不是'
                posR[go_search ]='VG'
                del(wcR[go_search+1])
                del(posR[go_search+1])
                 #updated length
                
            else:
                print("nothing")
            print("leave loop")
            temp_len = len(wcR)
            go_search+=1
        elif posR[go_search ]=='Nf' and posR[go_search-1]!='Neu' and wcR[go_search] in use_more_num:
            wcR.insert(go_search,'一')
            posR.insert(go_search,'Neu')
            go_search+=1
        elif wcR[go_search]=="二" and go_search +1!=len(wcR): # "二"+單位詞
            if posR[go_search+1]=="Nf":
                wcR[go_search]="兩"
            go_search+=1
        elif wcR[go_search]=="-": # ex: 流感的潛伏期通常為 一-四 天
            if go_search-1 >=0 and go_search +1!=len(wcR):
                if posR[go_search-1]=="Neu" and posR[go_search+1]=="Neu":
                    wcR[go_search] = "到"
                    posR[go_search] = "V"
            go_search+=1
        elif wcR[go_search]=="、": # ex: 一、 發燒天數:約七天。二、 潛伏期:
            if go_search-1 >=0 and go_search +1!=len(wcR):
                if posR[go_search-1]=="Neu" and posR[go_search+1]!="Neu":
                    wcR[go_search] = ":"
                    wcR[go_search-1] = "第" + wcR[go_search-1]
            go_search+=1
        else:
            go_search+=1
    
    ckip_result = list()
    

    
    for word in range(len(wcR)):
        tmp_list = list()
        #extend words
        for extend in range(len(abbr_word)):
            if wcR[word]==abbr_word[extend]:
                if abbr_word[extend]=='並' and posR[word]!='Cbb':
                    continue
                else:
                    wcR[word] = abbr_word_ext[extend]
        tmp_list.append(wcR[word])
        tmp_list.append(posR[word])

        ckip_result.append(tmp_list)
    print(ckip_result)
    print(len(ckip_result))

    
    for res_index in range(len(ckip_result)):
        if ckip_result[res_index][1] not in jump_attr:
            temp_Word = ckip_result[res_index][0].replace("  "," ")
        
            temp_Word = temp_Word.replace(" ","")
        print("當前處裡： " , temp_Word)
        if temp_Word in abbr_word:
            for extend in range(len(abbr_word)):
                if temp_Word==abbr_word[extend]:
                    temp_Word = abbr_word_ext[extend]
                    break
        if temp_Word=='[SEG]':
            temp_Word = idioms[idioms_len]
            idioms_len+=1
            #Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word,ch_dataX)
            #tw_choose.append(Tailuo)
        ch_dataX = twX.loc[ twX["對應華語"] ==temp_Word ]
        if ckip_result[res_index][1] in jump_attr or ckip_result[res_index][0]=='': # 標點符號，直接丟到最終選擇台羅裡
            if ckip_result[res_index][1]=='FW':
                if not (ch_dataX.empty):
                    Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word,ch_dataX)
                    tw_choose.append(Tailuo)
                else:
                    Tailuo = mix_word(temp_Word)
                    tw_choose.append(Tailuo)
            else:
                tw_choose.append(ckip_result[res_index][0])
                #all_ch_trans[temp_Word] = temp_Word
                continue
        elif (ckip_result[res_index][1]=='NP'): #翻譯名詞片語
            res2,CH_dic = TransNP(temp_Word)
            print(res2)
            tw_choose.append(res2)
            if (re.match(r'[\u4e00-\u9fff]+', res2))==True:
                all_ch_trans[temp_Word] = res2 #where temp_Word is key (ori. Chinese)
            else:
                all_ch_trans.update(CH_dic)
            continue
        elif temp_Word =='這':
            ch_shX = ch_dataX.values.tolist()
            temp_choose = []
            for a in range(len(ch_shX)):
                temp_choose.append(ch_shX[a][2])    #不管詞性，直接列出所有音                                
            all_ch_trans[temp_Word] = temp_choose
            
            if res_index+1==len(ckip_result[res_index]):
                tw_choose.append("tse")
                #all_ch_trans[temp_Word] = "tse"
            else:
                try:
                    if ckip_result[res_index+1][1] in noun_number:
                        tw_choose.append("tsit")
                        #all_ch_trans[temp_Word] = "tsit"
                    else:
                        tw_choose.append("tse")
                        #all_ch_trans[temp_Word] = "tse"
                except IndexError:
                    tw_choose.append("tse")
        elif temp_Word =='那':
            ch_shX = ch_dataX.values.tolist()
            temp_choose = []
            for a in range(len(ch_shX)):
                temp_choose.append(ch_shX[a][2])    #不管詞性，直接列出所有音                                
            all_ch_trans[temp_Word] = temp_choose
            if res_index+1==len(ckip_result[res_index]):
                tw_choose.append("he")
                #all_ch_trans[temp_Word] = "he"
            else:
                try:
                    if ckip_result[res_index+1][1] in noun_number:
                        tw_choose.append("hit")
                        #all_ch_trans[temp_Word] = "hit"
                    else:
                        tw_choose.append("he")
                        #all_ch_trans[temp_Word] = "he"
                except IndexError:
                    tw_choose.append("he")
                    #all_ch_trans[temp_Word] = "he"
        elif temp_Word =='不':
            ch_shX = ch_dataX.values.tolist()
            temp_choose = []
            for a in range(len(ch_shX)):
                temp_choose.append(ch_shX[a][2])    #不管詞性，直接列出所有音                                
            all_ch_trans[temp_Word] = temp_choose
            if ckip_result[res_index+1][1] in verbs:                
                tw_choose.append("m̄")
                #all_ch_trans[temp_Word] = "m̄"
            elif ckip_result[res_index+1][1] =='SHI' or ckip_result[res_index+1][0] =='hōo':
                tw_choose.append("m̄")
                #all_ch_trans[temp_Word] = "m̄"
            elif ckip_result[res_index+1][1] in adj_attr :                
                tw_choose.append("bô")
                #all_ch_trans[temp_Word] = "bô"
            elif ckip_result[res_index+1][0] =='完':                
                tw_choose.append("bô")
                #all_ch_trans[temp_Word] = "bô"
            elif ckip_result[res_index+1][0] =='到':                
                tw_choose.append("bē")
                #all_ch_trans[temp_Word] = "bē"
            else:
                tw_choose.append("put")
                #all_ch_trans[temp_Word] = "put"
        
            
        else: # 一般中文詞
            
            if temp_Word[-1] == '到' and temp_Word!='報到' and temp_Word!='到':
                if ckip_result[res_index][1] in verb_attr :
                    if res_index+1 != len(ckip_result):
                        if ckip_result[res_index+1][1] in loc_time: #
                            #temp_Word = temp_Word[:-1]+'--tio̍h'
                            Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word,ch_dataX) #查新辭典
                            if ch_dataX.empty: #未知詞，且是因為字尾
                                ch_data_O = twX.loc[ twX["對應華語"] ==temp_Word[:-1] ]
                                Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word[:-1],ch_data_O)
                                tw_choose.append(Tailuo+'-kàu')
                                pron_list = []
                                pron_list.append(Tailuo+'-kàu')
                                all_ch_trans[temp_Word] = pron_list
                                #all_ch_trans[temp_Word] = Tailuo+'-kàu'
                            else:
                                tw_choose.append(Tailuo)
                                pron_list = []
                                pron_list.append(Tailuo)
                                all_ch_trans[temp_Word] = pron_list
                        else:
                            Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word,ch_dataX) #查新辭典
                            if ch_dataX.empty:
                                ch_data_O = twX.loc[ twX["對應華語"] ==temp_Word[:-1] ]
                                Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word[:-1],ch_data_O)
                                tw_choose.append(Tailuo+'--tio̍h')
                                pron_list = []
                                pron_list.append(Tailuo+'--tio̍h')
                                all_ch_trans[temp_Word] = pron_list
                            else:
                                tw_choose.append(Tailuo)
                                pron_list = []
                                pron_list.append(Tailuo)
                                all_ch_trans[temp_Word] = pron_list
                    else:
                        Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word,ch_dataX) #查新辭典
                        if ch_dataX.empty:
                            ch_data_O = twX.loc[ twX["對應華語"] ==temp_Word[:-1] ]
                            Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word[:-1],ch_data_O)
                            tw_choose.append(Tailuo+'--tio̍h')
                            pron_list = []
                            pron_list.append(Tailuo+'--tio̍h')
                            all_ch_trans[temp_Word] = pron_list
                        else:
                            tw_choose.append(Tailuo)
                            pron_list = []
                            pron_list.append(Tailuo)
                            all_ch_trans[temp_Word] = pron_list
                else:
                    print("proceed")
                    mixup = mix_word(temp_Word)
                    tw_choose.append(mixup)
                    pron_list = []
                    pron_list.append(mixup)
                    all_ch_trans[temp_Word] = pron_list
            elif temp_Word[-1] == '完' and ckip_result[res_index][1] in verb_attr and temp_Word!='完':
                #temp_Word = temp_Word[:-1]+' liáu'
                Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word,ch_dataX)
                if Tailuo == "":
                    ch_data_O = twX.loc[ twX["對應華語"] ==temp_Word[:-1] ]
                    Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word[:-1],ch_data_O)
                    #Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word[:-1],ch_dataX)
                    tw_choose.append(Tailuo+'-liáu')
                    pron_list = []
                    pron_list.append(Tailuo+'-liáu')
                    all_ch_trans[temp_Word] = pron_list
                else:
                    tw_choose.append(Tailuo)
                    pron_list = []
                    pron_list.append(Tailuo)
                    all_ch_trans[temp_Word] = pron_list
                #tw_choose.append(Tailuo+'-liáu')
            elif (temp_Word[-1] == '年' and ckip_result[res_index][1]=='Nd'):
                Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word,ch_dataX)
                if Tailuo == "":
                    ch_data_O = twX.loc[ twX["對應華語"] ==temp_Word[:-1] ]
                    Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word[:-1],ch_data_O)
                    tw_choose.append(Tailuo+'-nî')
                    pron_list = []
                    pron_list.append(Tailuo+'-nî')
                    all_ch_trans[temp_Word] = pron_list
                else:
                    tw_choose.append(Tailuo)
                    all_ch_trans[temp_Word] = Tailuo
            elif (temp_Word[-1] == '多' and ckip_result[res_index][1]=='Neu'):
                Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word,ch_dataX)
                if Tailuo == "":
                    ch_data_O = twX.loc[ twX["對應華語"] ==temp_Word[:-1] ]
                    Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word[:-1],ch_data_O)
                    tw_choose.append(Tailuo+'-kuá')
                    pron_list = []
                    pron_list.append(Tailuo+'-kuá')
                    all_ch_trans[temp_Word] = pron_list
                else:
                    tw_choose.append(Tailuo)
                    all_ch_trans[temp_Word] = Tailuo
            elif (temp_Word == '戴' and res_index+1 != len(ckip_result)): #戴帽子 vs. 戴口罩 慣用詞
                    if ckip_result[res_index+1][0]=='口罩':
                        tw_choose.append("kuà") #掛口罩
                        all_ch_trans[temp_Word] = "kuà"
                    else:                        
                        Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_Word,ch_dataX)
                        tw_choose.append(Tailuo)
                        pron_list = []
                        pron_list.append(Tailuo)
                        all_ch_trans[temp_Word] = pron_list
            elif (temp_Word[-1] == '-' or temp_Word[0] == '-') and ckip_result[res_index][1]=="Neu":
                temp_WordM = temp_Word.replace("-","")
                if temp_Word[-1] == '-':
                    #temp_Word = temp_Word[:-1]
                    ch_data_O = twX.loc[ twX["對應華語"] ==temp_WordM ]
                    Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_WordM,ch_data_O)
                    
                    tw_choose.append(Tailuo+'-kàu')
                    pron_list = []
                    pron_list.append(Tailuo+'-kàu')
                    all_ch_trans[temp_Word] = pron_list
                else:
                    #temp_Word = temp_Word[0:]
                    ch_data_O = twX.loc[ twX["對應華語"] ==temp_WordM ]
                    Tailuo = dict_new_lookupX(ckip_result[res_index][1],temp_WordM,ch_data_O)
                    
                    tw_choose.append('kàu-'+Tailuo)
                    pron_list = []
                    pron_list.append('kàu-'+Tailuo)
                    all_ch_trans[temp_Word] = pron_list
            
                
            elif ch_dataX.empty: # 中文詞不在辭典裡
                print("ch_new not found: " , temp_Word)
                ch_data = tw.loc[ tw["中文"] == temp_Word ]
                if ch_data.empty:
                    if temp_Word[-1] == '到' and temp_Word!='報到':
                        
                        if ckip_result[res_index][1] in verb_attr and ckip_result[res_index+1][1] not in loc_time:
                            #temp_Word = temp_Word[:-1]+'--tio̍h'
                            Tailuo = dict_lookup(ckip_result[res_index][1],temp_Word[:-1],ch_data)                            
                            tw_choose.append(Tailuo+'--tio̍h')
                            pron_list = []
                            pron_list.append(Tailuo+'--tio̍h')
                            all_ch_trans[temp_Word] = pron_list
                        else:
                            print("proceed")
                            mixup = mix_word(temp_Word)
                            tw_choose.append(mixup)
                            pron_list = []
                            pron_list.append(mixup)
                            all_ch_trans[temp_Word] = pron_list
                    elif temp_Word[-1] == '完' and ckip_result[res_index][1] in verb_attr:
                        #temp_Word = temp_Word[:-1]+' liáu'
                        Tailuo = dict_lookup(ckip_result[res_index][1],temp_Word[:-1],ch_data)
                        tw_choose.append(Tailuo+'-liáu')
                        pron_list = []
                        pron_list.append(Tailuo+'-liáu')
                        all_ch_trans[temp_Word] = pron_list
                    else:
                        mixup = mix_word(ckip_result[res_index][0])
                        tw_choose.append(mixup)
                        pron_list = []
                        pron_list.append(mixup)
                        all_ch_trans[temp_Word] = pron_list
                        print("\n")
                else: # 中文詞在辭典裡
                    # print(ch_data)
                    ch_sh = ch_data.values.tolist()
                    if len(ch_sh) > 1: # 有多筆結果
                        temp_choose = []
                        for a in range(len(ch_sh)):
                            temp_choose.append(ch_sh[a][1])    #不管詞性，直接列出所有音                                
                        all_ch_trans[temp_Word] = temp_choose
                        # print(type(ch_data))
                        if ckip_result[res_index][1] == "VH" :
                            res_df = ch_data.loc[ ch_data["詞性-教育部"] == "Adj" ]
                        else:
                            res_df = ch_data.loc[ ch_data["詞性-教育部"] == ckip_result[res_index][1][0] ]
                        print(ckip_result[res_index][1])
                        res_count = (res_df.shape)[0]
                        print(res_count)

                        if res_count == 0: # 對應詞性不存在                            
                            only_choose = max_times(ch_data)
                            tw_choose.append( only_choose )
                            
                        elif res_count == 1: # 對應詞性只有一個，選他
                            res_df_list = res_df.values.tolist()
                            one_choose = res_df_list[0][1]
                            print("\n")
                            print(res_df_list)
                            print("選中讀音，對應詞性只有一個：" , one_choose)
                            tw_choose.append( one_choose )
                            
                        else: # 對應詞性超過一個
                            # 取出所有符合詞性之列表比較次數
                            print("中文： ", temp_Word , " 詞性：",ckip_result[res_index][1])
                            res_df_list = res_df.values.tolist()
                            
                            which_choose = max_times(res_df)
                            """
                            if ckip_result[res_index][1] == "VH" :
                                which_choose = max_times(ch_data.loc[ ch_data["詞性-教育部"] == "Adj" ])
                            else:
                                which_choose = max_times(ch_data.loc[ ch_data["詞性-教育部"] == ckip_result[res_index][1][0] ])
                            """
                            tw_choose.append(which_choose)
                            #all_ch_trans[temp_Word] = which_choose
                    else: # 該詞只有一筆結果，直接選(不會是0因為empty上一層已被擋下)
                        print(ch_data)
                        print("選中讀音，只有一筆結果：" , ch_sh[0][1])
                        print("\n")
                        if (ch_sh[0][1]!="NaN"):
                            tw_choose.append( ch_sh[0][1])
                            pron_list = []
                            pron_list.append(ch_sh[0][1])
                            all_ch_trans[temp_Word] = pron_list
                            #all_ch_trans[temp_Word] = ch_sh[0][1]
                        else:
                            tw_choose.append("error")
                            pron_list = []
                            pron_list.append("error")
                            all_ch_trans[temp_Word] = pron_list
            else: #找新詞點
                ch_shR = ch_dataX.values.tolist()                
                
                if len(ch_shR) > 1: # 有多筆結果
                    # print(type(ch_data))
                    temp_choose = []
                    for a in range(len(ch_shR)):
                        temp_choose.append(ch_shR[a][2])    #不管詞性，直接列出所有音                                
                    all_ch_trans[temp_Word] = temp_choose
                    try:
                        if ckip_result[res_index][1] == "VH" or ckip_result[res_index][1] == "Adj":
                            res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains("Adj") ]
                        elif ckip_result[res_index][1] == "Da" or ckip_result[res_index][1] in adverb_attr:
                            res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains("D") ]
                        elif ckip_result[res_index][1] in verbs:
                            res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains("V") ]
                        elif ckip_result[res_index][1] in noun_types:
                            res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains("N") ]
                        elif ckip_result[res_index][1] == "Nf":
                            res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains("Nf") ]
                        else:
                            #res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains(ckip_result[res_index][1][0])]
                            res_df = ch_dataX.loc[ ch_dataX["詞性"].str.contains("F")]
                        print(ckip_result[res_index][1])
                        res_count = (res_df.shape)[0]
                        
                        print(res_count)

                        if res_count == 0: # 對應詞性不存在
                            
                            only_choose = max_timesX(ch_dataX)
                            tw_choose.append( only_choose )
                            #all_ch_trans[temp_Word] = only_choose
                        elif res_count == 1: # 對應詞性只有一個，選他
                            res_df_list = res_df.values.tolist()                                
                            one_choose = res_df_list[0][2]
                            print("\n")
                            print(res_df_list)
                            print("選中讀音，對應詞性只有一個：" , one_choose)
                            tw_choose.append( one_choose )
                            #all_ch_trans[temp_Word] = one_choose
                        else: # 對應詞性超過一個
                            res_df_list = res_df.values.tolist()
                            
                            print("中文： ", ckip_result[res_index][0] , " 詞性：",ckip_result[res_index][1])
                            which_choose = max_timesX(res_df)
                            """
                            if ckip_result[res_index][1] == "VH" or ckip_result[res_index][1] == "VHC":
                                which_choose = max_timesX(ch_dataX.loc[ ch_dataX["詞性"].str.contains("Adj")])
                            elif ckip_result[res_index][1] == "Da" or ckip_result[res_index][1] in adverb_attr:
                                which_choose = max_timesX(ch_dataX.loc[ ch_dataX["詞性"].str.contains("D")])
                            elif ckip_result[res_index][1] in verbs:
                                which_choose = max_timesX(ch_dataX.loc[ ch_dataX["詞性"].str.contains("V")])
                            elif ckip_result[res_index][1] == 'Nf':
                                which_choose = max_timesX(ch_dataX.loc[ ch_dataX["詞性"].str.contains("Nf")])
                            elif ckip_result[res_index][1] in noun_types:
                                which_choose = max_timesX(ch_dataX.loc[ ch_dataX["詞性"].str.contains("N")])                            
                            else:
                                #max_times(ch_dataX.loc[ ch_dataX["詞性"].str.contains(ckip_result[res_index][1][0]) ],1)
                                which_choose = max_timesX(ch_dataX.loc[ ch_dataX["詞性"].str.contains("F") ])
                            """
                            tw_choose.append(which_choose)
                            #all_ch_trans[temp_Word] = which_choose
                    except Exception as ee:
                        print(ee)
                        #all_ch_trans[temp_Word] = "X"
                        
                else: # 該詞只有一筆結果，直接選(不會是0因為empty上一層已被擋下)
                    print(ch_dataX)
                    print("選中讀音，只有一筆結果：" , ch_shR[0][2])
                    print("\n")                    
                    tw_choose.append( ch_shR[0][2])
                    pron_list = []
                    pron_list.append(ch_shR[0][2])
                    all_ch_trans[temp_Word] = pron_list

    print(tw_choose)
    print(all_ch_trans) #完整台羅句子翻譯dict
    
    tw_choose_str = str()
    #ckip_result[res_index][1]
    for pos_in in range(len(tw_choose)):
        if type(tw_choose[pos_in])==float: #account for nan value
            throw_in = "XXX"
        else:
            throw_in = tw_choose[pos_in]
            if ckip_result[pos_in][1]!='NP':
                if ";" in throw_in and throw_in!= ";":
                    throw_in = throw_in.split(";")[0]
                elif "/" in throw_in and throw_in!= "/":
                    throw_in = throw_in.split("/")[0]
                elif " （" in throw_in:
                    throw_in = throw_in.split(" （")[0]
                elif " (" in throw_in:
                    throw_in = throw_in.split(" (")[0]
        #if type(twc)!=float:
        if throw_in!='--ah' and throw_in!='--tio̍h' and throw_in!='--ê' and not throw_in.startswith("--"):
            try:
                if ";" in throw_in and throw_in!= ";" and throw_in!="；":
                    throw_in = throw_in.split(";")[0]                    
                tw_choose_str = tw_choose_str + " " + throw_in
            except Exception as ee:
                print("word not found in dict")
                continue
        else:
            tw_choose_str = tw_choose_str + throw_in
        
    return tw_choose_str,all_ch_trans

def grammarlyCH(ch,pos): #將華語語句轉成台語文法
    
    passed_ka = 0
    pi_sentence = 0 #含'比'字的比較句
    
    error_list=[]
    templist=[]
    sent_seg=0
    index = 0
    tw_correction = list()
    print(len(ch))
    
    while index!= len(ch):
        print(index)
        #tw_index+=1
        print("當前處裡： " , ch[index])
        if ch[index]=='了': #了字句
            if index == (len(ch)-1): #句尾
                templist.append(index)
                templist.append("'了'助詞語法轉換:句尾")
                error_list.append(templist)
                templist=[]
                #tw_correction.append('--ah')
                index+=1
            elif index == (len(ch)-2) and (pos[index+1] in jump_attr or ch[index+1] == '嗎'): #句尾
                templist.append(index)
                templist.append("'了'助詞語法轉換:句尾")
                error_list.append(templist)
                templist=[]
                #tw_correction.append('--ah')
                index+=1
            elif pos[index+1] in jump_attr or pos[index+1]=='T': #句號、逗號表示句段
                templist.append(index)
                templist.append("'了'助詞語法轉換:句尾")
                error_list.append(templist)
                templist=[]
                #tw_correction.append('--ah')
                index+=1
            elif passed_ka==1:
                templist.append(index)
                templist.append("'把'字句和'了'字句在同一句時，'了'省略")
                error_list.append(templist)
                templist=[]
                #tw_correction.append('')
                index+=1
                #tw_correction no append
            else:
                if pos[index]=='Di' or pos[index]=='T': #時態標記或語助詞
                    print('DI test')
                    if ch[index-1]=='':
                        prev_word = "XXX"
                    else:
                        prev_word = ch[index-1]
                    if index+2 < len(ch):
                        #print(ch[index-1])
                        #print(ch[index+2])
                        if prev_word[-1] in verb_comp or passed_ka==1 or ch[index+2] in time_word: #"了"為補語
                            templist.append(index)
                            templist.append("'了'助詞語法轉換 未刪減")
                            error_list.append(templist)
                            templist=[]
                            index+=1
                            
                        else:
                            print(pos[index+1])
                            if pos[index+1] in comp_adverb and pos[index-1]=='VH': #比較句
                                if pi_sentence != 1: #無"比"字的比較句
                                    templist.append(index)
                                    templist.append("比較句語法轉換V4:sub. + adj. + 了 + adv. --> sub. + 有 + adv + khah + adj")
                                    error_list.append(templist)
                                    templist=[]
                                    index+=1
                                else: #同時有"比"字和"了"字的比較句
                                    templist.append(index)
                                    templist.append("'了'助詞語法轉換 未刪減")
                                    error_list.append(templist)
                                    templist=[]
                                    index+=1
                            elif (pos[index+1] in adverb_attr):
                                print("'了'助詞語法轉換 未刪減")
                                templist.append(index)
                                templist.append("'了'助詞語法轉換 未刪減")
                                error_list.append(templist)
                                templist=[]
                                #tw_correction no append
                                index+=1
                            elif index-2>=0:
                                if prev_word=='過' and pos[index-2] in verb_attr: #去/吃+過+了
                                    templist.append(index)
                                    templist.append("'了'助詞語法轉換 未刪減")
                                    error_list.append(templist)
                                    templist=[]
                                    index+=1
                                else:
                                    templist.append(index)
                                    templist.append("'了'助詞語法轉換:未對調")
                                    error_list.append(templist)
                                    templist=[]
                                    index+=1
                            else:
                                templist.append(index)
                                templist.append("'了'助詞語法轉換:未對調")
                                error_list.append(templist)
                                templist=[]
                                index+=1
                            
                    else:
                        if (prev_word[-1] in verb_comp) or passed_ka==1 : #"了"當補語/助詞 或句子有"共"字句
                            templist.append(index)
                            templist.append("'了'助詞語法轉換: 未刪減")
                            error_list.append(templist)
                            templist=[] #tw_correction no append
                            index+=1
                            
                        else:
                            if pos[index+1] in adverb_attr and pos[index-1]=='VH': #比較句句型第四類
                                if pi_sentence != 1:
                                    templist.append(index)
                                    templist.append("比較句語法轉換V4:sub. + adj. + 了 + adv. --> sub. + 有 + adv + khah + adj")
                                    error_list.append(templist)
                                    templist=[]
                                    index+=1
                                else:
                                    templist.append(index)
                                    templist.append("'了'助詞語法轉換 未刪減")
                                    error_list.append(templist)
                                    templist=[]
                                    index+=1
                            else:
                                templist.append(index)
                                templist.append("'了'助詞語法轉換:未對調")
                                error_list.append(templist)
                                templist=[]
                                index+=1
                else:
                    index+=1

        elif ch[index] == "過" and pos[index] == 'Di': #時態標記(過去/完成式)
            if index==len(ch)-1: #至句尾
                index+=1
            elif ch[index+1]=='了' and pos[index] == 'Di':#時態標記
                index+=1
            
            else:
                templist.append(index)
                templist.append("'過'字句語法轉換:完成式")
                error_list.append(templist)
                templist=[]
                #place = 
                #tw_correction[index-1]='ū'
                #tw_correction.append(alignTW[tw_index-1])
                index+=1

        elif ch[index] in ka_attr and pos[index] == 'P': #翻成台漢'共'的介系詞
            templist.append(index)
            templist.append("'共'字句語法轉換")
            error_list.append(templist)
            templist=[]
            passed_ka=1
            #tw_correction.append('kā')
            index+=1
        elif ch[index] in hoo_attr:
            if (ch[index]=='讓'):
                templist.append(index)
                templist.append("'被'字句語法轉換B:未翻成hōo")
                error_list.append(templist)
                templist=[]
                tw_correction.append('hōo')
                index+=1
            elif (pos[index+1] in verb_attr) :
                templist.append(index)
                templist.append("'被'字句語法轉換A:未翻成hōo lâng")
                error_list.append(templist)
                templist=[]
                tw_correction.append('hōo lâng')
                index+=1
            else:
                templist.append(index)
                templist.append("'被'字句語法轉換B:未翻成hōo")
                error_list.append(templist)
                templist=[]
                #tw_correction.append('hōo')
                index+=1
                
        elif ch[index]=='給':
            if passed_ka==1:
                templist.append(index)
                templist.append("'給'字句語法轉換V4: '把'字句和'給'字句在同一句時，'給'翻成hōo")
                error_list.append(templist)
                templist=[]
                #tw_correction.append('hōo')
                index+=1
            else:
                verb = sent_seg
                stopper = 0
                passed_verb = 0
                #if pos[index-1]==''
                while verb!= len(ch) and pos[verb] not in jump_attr:
                    #verb +=1
                    if pos[verb] in verb_attr and ch[verb]!='給':                        
                        stopper = 2
                    elif pos[verb] in jump_attr:
                        stopper = 1
                    if stopper==1 or stopper==2:
                        break
                    verb +=1
                print("verb index: ",str(verb))
                print("stopper: ",stopper)
                if stopper!=0:
                    if verb<index: #'給'在後，動詞在前
                        if (ch[verb][-1] in verb_fin_attr or ch[verb]=='給'):
                            templist.append(index)
                            templist.append("'給'字句語法轉換V3: 給在後")
                            error_list.append(templist)
                            templist=[]
                            #tw_correction.append(alignTW[tw_index])
                            index+=1
                        else:
                            index+=1
                    else: #'給'在前，動詞在後
                        if ch[verb][-1] not in verb_fin_attr and ch[verb]!='給':
                            templist.append(index)
                            templist.append("'給'字句語法轉換V1: 給在前")
                            error_list.append(templist)
                            templist=[]
                            #tw_correction.append('kā')
                            index+=1
                        else:
                            templist.append(index)
                            templist.append("'給'字句語法轉換V2: 給在前, 動詞為動結式")
                            error_list.append(templist)
                            templist=[]
                            #tw_correction.append(alignTW[tw_index])
                            index+=1

                else: #該句只有"給"字(give)作為動詞
                    templist.append(index)
                    templist.append("'給'字句語法轉換VR: 單一'給'作為動詞")
                    error_list.append(templist)
                    templist=[]
                    #tw_correction.append(alignTW[tw_index])
                    index+=1
                    
        elif ch[index] == '比' and pos[index]=='P':
            pi_sentence = 1
            temp_in = index
            tik = 0
            adj = 0
            adv_Search = 0
            breaker = 0
            while temp_in != len(ch)-1 and pos[temp_in] not in jump_attr:
                print(temp_in)
                if ch[temp_in] == '得' and pos[temp_in-1] in verb_attr:
                    tik = 1
                    breaker=1
                    break
                elif pos[temp_in] == 'VH' or pos[temp_in] == 'VHC':
                    adj = 1
                    breaker=1
                    break
                elif pos[temp_in] in adverb_attr :
                    if ch[temp_in] not in more_than_adverb:
                        try:
                            if pos[temp_in+1] in verb_attr:
                                adv_Search = 1
                                breaker=1
                            break
                        except IndexError:
                            break
                    else:
                        adv_Search = 3
                        break
                else:
                    temp_in +=1
                if breaker==1:
                    break
            print (tik,adj,adv_Search)
            #if alignTW[tw_index] == 'pí':
            if adj==1 and tik!=1:
                templist.append(index)
                templist.append("比較句語法轉換V1: A + 比 +B + adj --> A + khah + adj + B")
                error_list.append(templist)
                templist=[]
                #tw_correction.append(alignTW[tw_index])
                index+=1
            elif tik==1:
                templist.append(index)
                templist.append("比較句語法轉換V2: sub1+v+obj+比+sub2+v+得+adj --> sub1+v+obj+v+了+比+sub2+khah+adj")
                error_list.append(templist)
                templist=[]
                erase = index
                """
                while erase != len(ch)-1:
                    if (ch[erase]=='更' or ch[erase]=='還'):
                        ch.pop(erase)
                        pos.pop(erase)
                        break
                    erase+=1
                """
                #tw_correction.append(alignTW[tw_index])
                index+=1
            elif adv_Search==1:
                if tik!=1:
                    templist.append(index)
                    templist.append("比較句語法轉換V3: sub1+比+sub2+adv.+VN+comp. --> sub1+khah+adj.+sub2+comp+VN")
                    error_list.append(templist)
                    templist=[]
                    #tw_correction.append(alignTW[tw_index])
                    index+=1
                else:
                    #tw_correction.append(alignTW[tw_index])
                    index+=1
                    #continue
            elif adv_Search==3:
                templist.append(index)
                templist.append("比較句語法轉換V5: sub1+比+sub2+adv.(還、更...等比較型副詞)+comp. --> sub1+比+sub2+khah+comp")
                error_list.append(templist)
                templist=[]
                #tw_correction.append(alignTW[tw_index])
                index+=1
                
            elif adj==0 and tik==0 and adv_Search==0:
                index+=1
                
                #elif adv==1
        elif pos[index] in verb_attr: #verb related grammar
            print('verb')
            if ch[index]=='':
                index+=1
            elif index+2 != len(ch) and index!= len(ch)-1: #未達到最後一詞
                if ch[index+1]=='著' and pos[index+1]=='Di' and ch[index+2] in noun_comp: #中文: 動詞+著+受詞 --> 台語: 受詞+動詞+咧
                    templist.append(index)
                    templist.append("'著'字句語法轉換")
                    error_list.append(templist)
                    templist=[]
                    #tw_correction[index]=alignTW[tw_index+1]
                    #tw_correction.append(alignTW[tw_index-1])
                    #tw_correction.append('leh')

                    index+=2
                else:
                    if ch[index][-1] in verb_fin_attr and ch[index] !='完' and ch[index] not in verb_non_fin:
                        print(pos[index])
                        if pos[index+1] in noun_comp:
                            templist.append(index)
                            templist.append("動結式賓語未提前")
                            error_list.append(templist)
                            templist=[]
                            #fill = alignTW[tw_index]
                            #tw_correction[index] = alignTW[tw_index]
                            #tw_correction.append(alignTW[tw_index-1])
                            #tw_correction.append(alignTW[tw_index])
                            index+=1
                        elif (pos[index+1] == 'Neqa' or pos[index+1]== 'Neu') and pos[index+2] == 'Nf': #動結式動詞後接數詞
                            templist.append(index)
                            templist.append("台語量詞不可直接接動結式動詞後")
                            error_list.append(templist)
                            templist=[]
                            #tw_correction.append(alignTW[tw_index])
                            index+=1
                        else:
                            #tw_correction.append(alignTW[tw_index])
                            index+=1
                            #continue\
                    elif '給' in ch[index][-1] and pos[index]=='VD':
                        templist.append(index)
                        templist.append("'給'字句語法轉換V3.1: V+給 型動詞")
                        error_list.append(templist)
                        templist=[]
                        #tw_correction.append(alignTW[tw_index])
                        index+=1
                    else:
                        #tw_correction.append(alignTW[tw_index])
                        index+=1
                        
            else:#接近最後一詞
                
                if ch[index][-1] in verb_fin_attr: #動結式動詞
                    print(pos[index])
                    if index+1!= len(pos):
                        if pos[index+1] in noun_comp:
                            templist.append(index)
                            templist.append("動結式賓語未提前")
                            error_list.append(templist)
                            templist=[]
                            #tw_correction.append(alignTW[tw_index-1])
                            #tw_correction.append(alignTW[tw_index])
                            index+=1
                        elif pos[index+1] == 'Neqa' or pos[index+1]== 'Neu': #數詞
                            templist.append(index)
                            templist.append("台語量詞不可直接接動結式動詞後")
                            error_list.append(templist)
                            templist=[]
                            
                            index+=1
                        else:
                            #tw_correction.append(alignTW[tw_index])
                            index+=1
                            #continue
                    else:
                        #tw_correction.append(alignTW[tw_index])
                        index+=1
                else:
                    #tw_correction.append(alignTW[tw_index])
                    index+=1
        #elif
        
        elif pos[index] == 'Neqa' and len(ch[index])==3 and ch[index][-1]==ch[index][-2]:#一+重疊量詞
            templist.append(index)
            templist.append("單位詞/量詞數字重複")
            error_list.append(templist)
            templist=[]
            
            index+=1
        elif ch[index] == '是' and index!=0 and (pos[index-1]=='VH' or pos[index-1]=='A'):
            temp_in = index
            while temp_in != len(ch):
                if ch[temp_in] == "？" or ch[temp_in] == "?":

                    templist.append(index)
                    templist.append("問句中'是'未提前")
                    error_list.append(templist)
                    templist=[]
                    
                    #index+=1
                    break
                else:
                    temp_in +=1
            index+=1

        elif ch[index] =='兩三':
            templist.append(index)
            templist.append("'兩三'字句語法轉換")
            error_list.append(templist)
            templist=[]
            #tw_correction.append('tsi̍t-puànn')
            index+=1
        elif ch[index] =='嗎':
            templist.append(index)
            templist.append("疑問詞'嗎'語法轉換")
            error_list.append(templist)
            templist=[]
            index+=1
        elif pos[index] in jump_attr:
            sent_seg = index
            #tw_correction.append(alignTW[tw_index])
            if(ch[index]=='。'):
                passed_ka=0
            index+=1
        elif pos[index]=='NP' and '兩三' in ch[index]:
            print(ch[index])
            #print(alignTW[tw_index])
            #print('tsi̍t-puànn' in alignTW[tw_index])
            #if ('tsi̍t-puànn' in alignTW[tw_index])==False:
            print('discovered')
            templist.append(index)
            templist.append("'兩三'字句錯誤")
            error_list.append(templist)
            templist=[]
            index+=1
        elif ch[index] == '不錯':
            print("type不錯")
            if index-1>=0:
                if "起來" in ch[index-1] and pos[index-1]=='D':
                    templist.append(index)
                    templist.append("'V+起來+不錯'句型應翻為'bē-pháinn+V.'")
                    error_list.append(templist)
                    templist=[]
                    index+=1
                else:
                    index+=1
            else:
                index+=1

        else:            
            index+=1
            
        #index+=1
        #tw_index+=1
    
    return(error_list,tw_correction)



def recorrect(ch,tag,error): #文法轉換模組    
    index = 0
    addition = 0
    print(len(ch))
    
    #for index in range(len(ch)):
    for index in range(len(error)):
        print(error[index][0]) #word
        print(error[index][1]) #error type
        fixit = error[index][0]+addition #根據斷詞決定刪減/增加index
        if (error[index][1]=="'兩三'字句錯誤"):
            #fixit = error[index][0]
            if tag[index] == 'Neqa':
                print(ch[fixit])
                x = ch[fixit].replace('兩三','一半')
                ch[fixit]=x
                tag[fixit] = "Tai"
            else: #'兩三'翻成'niu-sam'
                print(ch[fixit])
                x = ch[fixit].replace('兩三','一半')
                print(x)
                ch[fixit]=x
                tag[fixit] = "Tai"
                """
                i = error[index][0]
                tempA = ch[i].split('niú-sam')
                print(tempA)
                if len(tempA)==2:
                    print(tempA[0])
                    ch[i] = tempA[0]+'tsi̍t-puànn'+tempA[1]
                """
        elif (error[index][1]=="'了'助詞語法轉換:句尾"):
            ch[fixit] = '--ah'
            tag[fixit] = "Tai"
        elif (error[index][1]=="'把'字句和'了'字句在同一句時，'了'省略"):
            ch.remove(ch[fixit])
            tag.remove(tag[fixit])
            addition = addition-1
        elif (error[index][1]=="'了'助詞語法轉換 未刪減"):
            ch.remove(ch[fixit])
            tag.remove(tag[fixit])
            addition = addition-1
        elif (error[index][1]=="'了'助詞語法轉換:未對調"):
            ch[fixit]='ū'
            tag[fixit] = "Tai"
            temp = ch[fixit]
            ch[fixit] = ch[fixit-1]
            ch[fixit-1] = temp
            temp2 = tag[fixit]
            tag[fixit] = tag[fixit-1]
            tag[fixit-1] = temp2
        elif (error[index][1]=="'過'字句語法轉換:完成式"):
            ch[fixit]='ū'
            tag[fixit] = "Tai"
            temp = ch[fixit]
            ch[fixit] = ch[fixit-1]
            ch[fixit-1] = temp
            temp2 = tag[fixit]
            tag[fixit] = tag[fixit-1]
            tag[fixit-1] = temp2
        elif (error[index][1]=="'共'字句語法轉換"):
            ch[fixit]='kā'
            tag[fixit] = "Tai"
        elif (error[index][1]=="'被'字句語法轉換A:未翻成hōo lâng"):
            ch[fixit]='hōo lâng'
            tag[fixit] = "Tai"
        elif (error[index][1]=="'被'字句語法轉換B:未翻成hōo"):
            ch[fixit]='hōo'
            tag[fixit] = "Tai"
        elif (error[index][1]=="'給'字句語法轉換V4: '把'字句和'給'字句在同一句時，'給'翻成hōo"):
            ch[fixit]='hōo'
            tag[fixit] = "Tai"
        elif (error[index][1]=="'給'字句語法轉換V1: 給在前"):
            ch[fixit]='kā'
            tag[fixit] = "Tai"
        elif (error[index][1]=="'給'字句語法轉換V2: 給在前, 動詞為動結式" or error[index][1]=="'給'字句語法轉換VR: 單一'給'作為動詞"):
            ch[fixit]='hōo'
            tag[fixit] = "Tai"
        elif (error[index][1]=="'給'字句語法轉換V3: 給在後"):
            ch[fixit]='hōo'
            tag[fixit] = "Tai"
            temp = ch[fixit]
            temp2 = ch[fixit+1]
            ch[fixit]=ch[fixit+2]
            ch[fixit+1]=ch[fixit+3]
            ch[fixit+2] = ch[fixit+4]
            ch[fixit+3] = temp
            ch[fixit+4] = temp2
            temp = tag[fixit]
            temp2 = tag[fixit+1]
            tag[fixit]=tag[fixit+2]
            tag[fixit+1]=tag[fixit+3]
            tag[fixit+2] = tag[fixit+4]
            tag[fixit+3] = temp
            tag[fixit+4] = temp2
        elif (error[index][1]== "'給'字句語法轉換V3.1: V+給 型動詞") and ch[fixit]!='遞給': #and "hōo" not in TW[fixit]: #在連動句中
            if '給' in ch[fixit]:
                temp = ch[fixit].split('給')[0]
                print(ch[fixit])
                #ch[fixit] = temp+'予'
                ch[fixit]= temp+'予'
                tag[fixit] = "Tai"
                temp = ch[fixit]
                temp2 = ch[fixit+1]
                ch[fixit]=ch[fixit+2]
                ch[fixit+1]=ch[fixit+3]
                ch[fixit+2] = ch[fixit+4]
                ch[fixit+3] = temp
                ch[fixit+4] = temp2
                temp = tag[fixit]
                temp2 = tag[fixit+1]
                tag[fixit]=tag[fixit+2]
                tag[fixit+1]=tag[fixit+3]
                tag[fixit+2] = tag[fixit+4]
                tag[fixit+3] = temp
                tag[fixit+4] = temp2
            else:
                continue
            
        elif (error[index][1]=="比較句語法轉換V1: A + 比 +B + adj --> A + khah + adj + B"):
            ch[fixit]='khah'
            tag[fixit] = "Tai"
            
            temp = ch[fixit+1]
            ch[fixit+1]=ch[fixit+2]
            ch[fixit+2]=temp
            temp = tag[fixit+1]
            tag[fixit+1]=tag[fixit+2]
            tag[fixit+2]=temp
        elif (error[index][1]=="比較句語法轉換V2: sub1+v+obj+比+sub2+v+得+adj --> sub1+v+obj+v+了+比+sub2+khah+adj"):
            #比+sub2+v --> v<+了>+比+sub2 <>:insert
            
            temp = ch[fixit]
            ch[fixit]=ch[fixit+2]
            ch[fixit+2] = ch[fixit+1]
            ch[fixit+1] = temp

            temp = tag[fixit]
            tag[fixit]=tag[fixit+2]
            tag[fixit+2] = tag[fixit+1]
            tag[fixit+1] = temp

            ch[fixit+3] = 'khah'
            tag[fixit+3] = "Tai"
            ch.insert(fixit+1,'liáu')
            tag.insert(fixit+1,'Tai')
            addition = addition+1
        elif (error[index][1]=="比較句語法轉換V3: sub1+比+sub2+adv.+VN+comp. --> sub1+khah+adj.+sub2+comp+VN"):
            ch[fixit]='khah'
            tag[fixit] = "Tai"

            tempA = ch[fixit+2]
            ch[fixit+2] = ch[fixit+1]
            ch[fixit+1] = tempA
            print(ch[fixit+3])
            print(ch[fixit+4])
            tempB = ch[fixit+4]
            print(tempB)
            ch[fixit+4] = ch[fixit+3]
            ch[fixit+3] = tempB

            tempA = tag[fixit+2]
            tag[fixit+2] = tag[fixit+1]
            tag[fixit+1] = tempA
            print(tag[fixit+3])
            print(tag[fixit+4])
            tempB = tag[fixit+4]
            print(tempB)
            tag[fixit+4] = tag[fixit+3]
            tag[fixit+3] = tempB
        elif (error[index][1]=="比較句語法轉換V4:sub. + adj. + 了 + adv. --> sub. + 有 + adv + khah + adj"):
            temp = ch[fixit-1] #adj.
            temp2 = ch[fixit+1] #adv.
            ch[fixit+1]='khah'
            ch[fixit-1]='ū'
            ch[fixit]=temp2 #adv
            ch.insert(fixit+1,temp)
            #ch.append(temp)
            addition = addition+1
        elif (error[index][1]=="比較句語法轉換V5: sub1+比+sub2+adv.(還、更...等比較型副詞)+comp. --> sub1+比+sub2+khah+comp"):
            temp = fixit
            while ch[temp] not in more_than_adverb :
                temp+=1
            ch[temp] = 'khah'
            tag[temp] = 'Tai'
            if ch[temp+1] in more_than_adverb:
                ch.remove(ch[temp+1])
                tag.remove(tag[temp+1])
                addition = addition-1
            else: print("nothing")
            #else
        elif (error[index][1]=="動結式賓語未提前") or (error[index][1]=="問句中'是'未提前"):
            temp = ch[fixit]
            ch[fixit]=ch[fixit+1]
            ch[fixit+1]=temp
            temp = tag[fixit]
            tag[fixit]=tag[fixit+1]
            tag[fixit+1]=temp
        elif (error[index][1]=="台語量詞不可直接接動結式動詞後"): #舉高三次, 吃完三碗
            
            temp = ch[fixit-1] #動結式動詞 吃完
            tempA = tag[fixit-1]
            temp2 = ch[fixit+1] #Nf. 量詞
            temp2A = tag[fixit+1]
            temp3 = ch[fixit-1][-1] #表示動結式的字尾
            temp3A = "D" #副詞
            temp4 = ch[fixit-1][:-1] #動詞
            temp4A = tag[fixit-1]
            ch[fixit-1] = temp4
            tag[fixit-1] = temp4A
            ch.insert (fixit+2,temp)
            tag.insert (fixit+2,tempA)
            #ch.insert (fixit+2,temp4)
            #tag.insert (fixit+2,temp4A)
            #吃+三+碗+吃完
        elif (error[index][1]=="疑問詞'嗎'語法轉換"): #'嗎'在台語翻成'敢'，放在主詞後
            try:
                search = fixit
                while search!=0 and (tag[search] not in switch_ma and tag[search]!='SHI'):
                    
                    search = search-1
                ch.remove(ch[fixit])
                tag.remove(tag[fixit])
                print(search)
                if tag[search]=='SHI':
                    ch.insert(search,'kám')
                    tag.insert(search, 'Tai')
                else:
                    if search+1<len(tag):
                        if tag[search+1] in noun_comp:
                            ch.insert(search+2,'kám')
                            tag.insert(search+2, 'Tai')
                        else:
                            ch.insert(search+1,'kám')
                            tag.insert(search+1, 'Tai')
                    else:
                        print("index out of range, switching '嗎'語法 solution")
                        ch[fixit] = 'bô'
                        tag[fixit] = 'Tai'
            except IndexError:
                print("index out of range, switching '嗎'語法 solution")
                ch[fixit] = 'bô'
                tag[fixit] = 'Tai'
            
        elif (error[index][1]=="單位詞/量詞數字重複"): #一隻隻、一個個...
            temp = len(ch[fixit])
            temp2 = ch[fixit][:temp-1]
            print(temp2)
            temp3 = temp2 + ch[fixit][0] + ch[fixit][temp-1:]
            #temp2 = temp[0]+"-"+temp[1]
            #temp2 = temp2 + "-"+ temp2
            ch[fixit]= temp3
            # tag[fixit] is the same
        elif (error[index][1]=="'著'字句語法轉換"):
            temp = ch[fixit]
            tempA = tag[fixit]
            ch[fixit] = ch[fixit+2]
            tag[fixit] = tag[fixit+2]
            ch[fixit+1] = temp
            tag[fixit+1] = tempA
            ch[fixit+2] = "--leh" #接在動詞後，表示動作持續
            tag[fixit+2] = "Tai"
        elif error[index][1]=="'V+起來 / 不錯'句型應翻為'bē-pháinn+V.'":
            #TW[fixit] = "bē-pháinn"
            Swap = ch[fixit-1][0]
            ch[fixit-1] = "bē-pháinn"
            tag[fixit-1] = "Tai"
            ch[fixit] = Swap
            tag[fixit] = "V"
            #TW[fixit]
        else:
            print('beta')
    new_string = ""
    for i in range(len(ch)):
        new_string += ch[i]
        #if i != len(ch)-1:
        #    new_string += " "
    return(ch,tag,new_string)

class tl_idiom_seg():
    def __init__(self,sentence) -> None:
        self.dictionary = dict()
        with open('idiom_dict.txt','r',encoding='utf-8') as dictionary: # load dictionary into mem
            for data in dictionary:
                self.dictionary[data.strip()] = True
        self.sentence = sentence
        self.num,self.temp = 0,0
        self.result,self.map,self.num_of_idiom = list(),dict(),list()
        start = 0
        while start < len(sentence):
            temp = self._find_idiom(sentence[start:])
            self.result.append(temp)
            start += self.temp
        self.result = ''.join(self.result)
    def _find_idiom(self,sentence) ->None:
        x = len(sentence)
        while x>0:
            self.temp = x
            if sentence.isascii() and sentence.isalnum():
                return sentence
            elif x == 1:
                return sentence
            elif sentence in self.dictionary:
                self.map[self.num] = sentence
                self.num+=1
                return '[SEG]'
            else:
                x -= 1
                sentence = sentence[0:x]

def FullAPI(data,Hanlp):
    if re.search(r'[\u4e00-\u9fff]+', data):        
        sent = tl_idiom_seg(sentence=data)
        all_idiom = list(sent.map.values())        
        NP_list = bnp_by_con(sent,Hanlp)
        wc , pos , _ner= call_ckip([sent.result])
        old_ws = wc[0]
        old_pos = pos[0]
        new_ws,new_pos = make_NP(NP_list,old_ws,old_pos)
        grammar_error,right_sen = grammarlyCH(new_ws,new_pos)
        new_wc,new_pos,trans_sen = recorrect(new_ws,new_pos,grammar_error) #
        try:
            data,all_ch = choose_main(new_wc,new_pos,all_idiom) #翻譯
            #data,dict_this = choose_main(new_wc,new_pos) #翻譯
            data = data.replace("("," ").replace(")","")
            #dict_this.update({'tailuo': data})
            all_ch.update({'tailuo': data})
        except Exception:
            print(Exception)
            logging.info(Exception)
            data = ""
            all_ch={}
            #dict_this.update({'tailuo': data})
            all_ch.update({'tailuo': data})
        
    else:
        print("all tailuo")
        #data=""
        #dict_this['tailuo'] = data
        all_ch = {}
        all_ch['tailuo'] = data
    #strKey+=str(a)
    #all_ch[strKey] = dict_this
    """
    sentence_list = []
    all_ch = {}
    if "。" in sentence:
        temp = sentence.split("。")
        for x in temp:
            if "!」" in x:
                tempA = x.split("!」")
                for y in tempA:
                    sentence_list.append(y)
            elif "。」" in x:
                tempA = x.split("。」")
                for y in tempA:
                    sentence_list.append(y)
            else:
                sentence_list.append(x)
            
    else:        
        sentence_list.append(sentence)
    a=0
    for data in sentence_list:
        strKey = "sent"
        a+=1
        dict_this = {}
        if re.search(r'[\u4e00-\u9fff]+', data):
            
            sent = tl_idiom_seg(sentence=data)
            all_idiom = list(sent.map.values())
            NP_list = bnp_by_con(sent,Hanlp)
            wc , pos , _ner= call_ckip([sent.result])
            old_ws = wc[0]
            old_pos = pos[0]
            new_ws,new_pos = make_NP(NP_list,old_ws,old_pos)
            grammar_error,right_sen = grammarlyCH(new_ws,new_pos)
            new_wc,new_pos,trans_sen = recorrect(new_ws,new_pos,grammar_error) #
            try:
                #data,all_ch = choose_main(new_wc,new_pos) #翻譯
                data,dict_this = choose_main(new_wc,new_pos) #翻譯
                data = data.replace("("," ").replace(")","")
                dict_this.update({'tailuo': data})
                #all_ch.update({'tailuo': data})
            except Exception:
                print(Exception)
                logging.info(Exception)
                data = ""
                dict_this.update({'tailuo': data})
                #all_ch.update({'tailuo': data})
            
        else:
            print("all tailuo")
            dict_this['tailuo'] = data
            
            #all_ch['tailuo'] = data
        strKey+=str(a)
        all_ch[strKey] = dict_this
    """
    #return data,all_ch
    return data,all_ch




if __name__ == "__main__":
    Hanlp = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH)
    
    root_logger= logging.getLogger()
    root_logger.setLevel(logging.INFO) 
    handler = logging.FileHandler('pinyin_API.log', 'a+', 'utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s')) 
    root_logger.addHandler(handler)
    while True:
        
        data = input("insert sentence: ") 
        finalTL,all_ch = FullAPI(data,Hanlp)
        print(finalTL)
        print(all_ch)
            
            
            
            #logging.info('TL = {}'.format(finalTL), extra=self.msgs)
          
                
        #except KeyboardInterrupt or Exception:
        #    print ("Shutdown requested...exiting")
        """
        if Exception:
            print(Exception)
            logging.info(Exception)
        else:
            logging.info(KeyboardInterrupt)
            print ("Shutdown requested...exiting")
        """
            
            
    #workbook.close()
                    
            
        
        