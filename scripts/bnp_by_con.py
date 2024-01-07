import hanlp
from New_CKIP import call_ckip

def bnp_by_con(text,Hanlp_model):
    #article = "5月1日上海福利院甚至發生「未死亡老人」被裝進屍袋裡，險些遭火化的離譜事件"

    try:
        if text[-1] != '。':
            text = text + '。'
        else:
            pass
    except :
        return []
    res = Hanlp_model(text)
    #print(res)
    con = res['con']

    NP_lst, start_idx = recurse_con(con)
    # print(NP_lst)

    return NP_lst





def recurse_con(con, start_idx = 0):
    NP_lst = []
    # start_idx = 0
    # start_idx = start_idx

    for subtree in con:

        if subtree.label() == 'IP'  or subtree.label() == 'TOP' or subtree.label() == 'PP' or subtree.label() == 'CP' or subtree.label() == 'LCP' or subtree.label() == 'VP' or subtree.label() == 'FRAG' or subtree.label() == 'DNP' or subtree.label() == 'INC' or subtree.label() == 'UCP':
            # for subtree in tree:
            #     print(subtree.label())
                #subtree_queue.put(subtree)
            NP, start_idx = recurse_con(subtree, start_idx)
            for np in NP:
                NP_lst.append(np)
        elif subtree.label() == 'NP' or subtree.label() == 'PRN' or subtree.label() == 'QP':
            # print(tree.label())
            end_index = len(subtree.pos())
            ws = [word[0] for word in subtree.pos()]
            pos = [word[1] for word in subtree.pos()]
            NP_lst.append([''.join(ws),ws, pos, start_idx, start_idx + end_index])
            start_idx += end_index
        else:
            # print(tree.label())
            start_idx += len(subtree.pos())

    return NP_lst, start_idx

def make_NP(NP_list,ws,pos):
    wc_x=[]
    pos_x=[]
    if len(NP_list) !=0:
        NPs = 0
        tempNP = NP_list[NPs][0] #current NP
        if "。" in tempNP:
            tempNP = tempNP.split("。")[0]
        print(tempNP)
        start_end_list = []
        marker = 0
        temp = ''
        begin = 0
        temp_len = 0 #num of words in temp
        NP_start = NP_list[NPs][1][0].replace("。","") #NP的第一個詞
        NP_end_index = NP_list[NPs][4] #Hanlp 該BNP結尾
        NP_check = 1 #是否檢查是NP開頭
        end = 0
        #special=0 #當Hanlp與CKIP斷詞標準不同
        #word2 = 0 #ckip index
        for word2 in range(len(ws)):
            noSpace = ws[word2].replace(" ","")
            REviseLine = noSpace.replace("\n","")
            if noSpace in tempNP or REviseLine in tempNP: #將單詞加至NP
                print("word in tempNP")
                temp += ws[word2]
                temp_len +=1
                if temp !="，" and temp.startswith("，"):
                    temp = temp[1:]
                    wc_x.append("，")
                    pos_x.append("COMMACATEGORY")
                """
                if temp == tempNP: #已加好NP
                    end = word2
                    ws_x.append(temp)
                    pos_x.append('NP')
                    temp=''
                    NPs+=1
                    if NPs != len(NP_list):
                        tempNP = NP_list[NPs][0] #下一個NP
                """
            elif (NP_start in ws[word2] or NP_start in noSpace) and len(NP_start)<len(noSpace) and NP_start!="": #單詞長於NP
                print("word being longer than NP_start")
                if word2+1 != len(ws):
                    if (temp + ws[word2+1]) in tempNP:
                        temp += NP_start
                        temp_len += 1
                        NP_listlen = len(NP_list[NPs][1])
                        if (NP_listlen==1):
                            if ws[word2].split(NP_start)[0]!="":
                                wc_x.append(ws[word2].split(NP_start)[0])
                            else:
                                wc_x.append(ws[word2].split(NP_start)[1])
                            pos_x.append(pos[word2])
                        
                    #temp += NP_start
                    
                    else:
                        wc_x.append(ws[word2])
                        pos_x.append(pos[word2])
                else:
                    if temp in tempNP:
                        temp += NP_start
                        temp_len += 1
                        NP_listlen = len(NP_list[NPs][1])
                        if (NP_listlen==1):
                            if ws[word2].split(NP_start)[0]!="":
                                wc_x.append(ws[word2].split(NP_start)[0])
                            else:
                                wc_x.append(ws[word2].split(NP_start)[1])
                            pos_x.append(pos[word2])
                        
                    #temp += NP_start
                    
                    else:
                        wc_x.append(ws[word2])
                        pos_x.append(pos[word2])
            else: #len(NP_start)>len(noSpace)
                print("word being shorter than NP_start")
                if temp!="": #discard current set of temp NP
                    wc_x.append(ws[word2-1])
                    pos_x.append(pos[word2-1])
                    #temp=""
                wc_x.append(ws[word2])
                pos_x.append(pos[word2])
                
            print("decide NP ",ws[word2])
            print("current temp: ",temp)
            print("next NP: ",tempNP)
            print(tempNP==NP_start)

            if ((temp == tempNP or temp.replace(" ", "")==tempNP) and tempNP!="") or word2==len(ws)-1 or word2>NP_end_index: #已加好NP
                end = word2
                print("temp: ",temp)
                print("completed tempNP: ",tempNP)
                if word2==len(ws)-1 and temp=="":
                    print("at the end")
                elif word2>NP_end_index and temp=="":
                    print("continue")
                    continue
                else:
                    wc_x.append(temp)
                    pos_x.append('NP')
                    """
                    if (temp_len!=1):
                        wc_x.append(temp)
                        pos_x.append('NP')
                    else:
                        wc_x.append(ws[word2])
                        pos_x.append(pos[word2])
                    """
                NP_check=1
                temp=''
                NPs+=1
                if NPs < len(NP_list):
                    tempNP = NP_list[NPs][0] #下一個NP
                    NP_start = NP_list[NPs][1][0]
                    NP_end_index = NP_list[NPs][4]
            else: 
                print("temp progress: ",temp)
                if temp == NP_start and NP_check==1: #開始加入, 因為剛好CKIP斷詞符合Hanlp BNP 第一個斷詞
                    NP_check=0
                    #if NP_start == tempNP:

                else:
                    #print("is length temp bigger: ",len(temp)>len(NP_start))
                    #print("is length temp shorter: ",len(temp)<len(NP_start))
                    if NP_check==0: #加NP中
                        print('skip process')
                    else: #NP_check==1, continue search
                        print("not in yet: ",temp)
                        if temp.startswith(",") and temp_len>=1:
                            temp = temp[1:]
                        print("revise temp: ",temp)
                        if (temp_len==1 and temp!=tempNP[0]) and tempNP[0] not in temp: #
                            temp=''
                        else:
                            if word2+1 != len(ws):
                                tempStr = temp+ws[word2+1]
                                print("tempStr, ",tempStr)
                                if tempStr not in NP_start:
                                    if NP_start not in tempStr:
                                        NP_check=1
                                        print("reset")
                                        temp='' #false alarm, reset
                                    else:
                                        print("V1 ready to make NP")
                                        NP_check=0
                                else:
                                    if tempStr[0]!=NP_start:
                                        print("word not the beginning of NP")
                                        NP_check=1
                                    else:
                                        print("V2/ ready to make NP")
                                        NP_check=0

            if NP_start=="":
                print("end of NPs")
                #wc_x.append(ws[word2])
                #pos_x.append(pos[word2])
            print("add in NP: ",NP_check)
            print("beginning of NP",NP_start)

            

            print("NP made: ",temp == tempNP)
            
            
            """
            if len(temp)>len(NP_start): #len(在NP中的CKIP詞彙)>len(在NP中的Hanlp詞彙)
                print("bigger")
                if NP_start in temp and temp in tempNP:
                    print("temp is longer but still in NP")
                    NP_check=1
                else:
                    tempX =NP_start
                    wc_x.append(wc[0][word2].split(tempX)[0])
                    pos_x.append(pos[0][word2])
                    NP_check=0
            elif len(temp)<len(NP_start) and temp in NP_start and temp!="":  #len(在NP中的CKIP詞彙)<len(在NP中的Hanlp詞彙)
                if temp[0]==NP_start[0]: #temp為BNP開頭
                    print("temp is shorter while being in NP")
                    NP_check=1
                else:
                    print("is separate")
                    wc_x.append(wc[0][word2])
                    pos_x.append(pos[0][word2])
                    temp=""
                    NP_check=0
            else:
                if word2>NP_end_index: #超過NP在Hanlp範圍
                    wc_x.append(wc[0][word2])
                    pos_x.append(pos[0][word2])
                    NPs+=1
                    if NPs < len(NP_list):
                        tempNP = NP_list[NPs][0] #下一個NP
                        NP_start = NP_list[NPs][1][0]
                        NP_end_index = NP_list[NPs][4]
                    
                temp=''
            """
            if NPs >=len(NP_list):
                tempNP = ""
                NP_start = ""
                NP_end_index = len(ws)

            
            """
            if marker==0:
                begin = word2
                marker=1
            if temp == tempNP: #已加好NP
                end = word2
                wc_x.append(temp)
                pos_x.append('NP')
                temp=''
                NPs+=1
                tempNP = NP_list[NPs][0] #下一個NP
            """
                #throughNP = 0
                #begin=NP_list[throughNP]
    else:
        wc_x = ws
        pos_x = pos
    return wc_x,pos_x

def make_NP_other(All_NP,seg,pos2):
    start_indexes = [item[3] for item in NP_list]
    end_indexes = [item[4] for item in NP_list]
    Hanlp_NP_ws = [item[1] for item in NP_list]
    constitute_NP = [item[0] for item in NP_list]
    ckip_start_index = []
    ckip_end_index = []
    wc_y = []
    pos_y = []
    i=0
    while i != len(start_indexes):
        j = start_indexes[i] #where should NP begin in CKIP
        tempNP = constitute_NP[i] # the current NP
        NP_begin = Hanlp_NP_ws[i][0] #the first word in NP
        temp = 0 #start index
        temp2 = 0 # end index
        tempStr = ""
        if seg[j]==NP_begin:
            temp = j
            tempStr += seg[temp]
            temp+=1
            while tempStr!=tempNP or temp!=len(ws):
                tempStr += seg[temp]
                temp+=1
                print(tempStr)
            print(tempStr)
            print(temp)
        else:
            if seg[j] in NP_begin: #len(temp)>len(NP_start)
                print("temp")




if __name__ == '__main__':
    Hanlp = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH)
    while (1):
        article = input("語句: ")
        article_alt = transform(article) 
        ws,pos,_ner = call_ckip([article])
        ws = ws[0]
        pos = pos[0]
        NP_list = bnp_by_con(article,Hanlp)
        #print(NP_list)
        wc_x = []
        pos_x = []
        
        new_ws,new_pos = make_NP(NP_list,ws,pos)
        
        #print(NP_list)
        constitute_NP = [item[0] for item in NP_list]
        
        Hanlp_split = [item[1] for item in NP_list]
        
        print("original ws: ",ws)
        print("original pos: ",pos)
        print("func ws: ",new_ws)
        print("func pos: ",new_pos)
        new_NP = []
        for i in range(len(new_ws)):
            if new_pos[i]=="NP":
                temp = []
                temp.append(new_ws[i])
                temp.append(new_pos[i])
                new_NP.append(temp)
        print("Hanlp 名詞片語: ",constitute_NP)
        print("Hanlp NP length: ",len(constitute_NP))
        print(Hanlp_split)
        print("論文前處理合成名詞片語: ",new_NP)

        ws,pos,_ner = call_ckip([article_alt])
        ws = ws[0]
        pos = pos[0]
        NP_list = bnp_by_con(article_alt,Hanlp)
        #print(NP_list)
        wc_x = []
        pos_x = []
        
        new_ws,new_pos = make_NP(NP_list,ws,pos)
        
        #print(NP_list)
        constitute_NP = [item[0] for item in NP_list]
        
        Hanlp_split = [item[1] for item in NP_list]
        
        print("original ws: ",ws)
        print("original pos: ",pos)
        print("func ws: ",new_ws)
        print("func pos: ",new_pos)
        new_NP = []
        for i in range(len(new_ws)):
            if new_pos[i]=="NP":
                temp = []
                temp.append(new_ws[i])
                temp.append(new_pos[i])
                new_NP.append(temp)
        print("Hanlp 名詞片語(數字正規化後): ",constitute_NP)
        print("Hanlp NP length: ",len(constitute_NP))
        print(Hanlp_split)
        print("論文前處理合成名詞片語(數字正規化後): ",new_NP)

