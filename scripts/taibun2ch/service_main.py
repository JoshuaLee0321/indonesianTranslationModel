import re
import os
import timeit
from time import time
import multiprocessing

def tai2ch_main(sentence):
    def f(tn_sequence,cn_sequence,tword,cword):
        return tword if tword in tn_sequence and cword in cn_sequence else ""
    def translation_selection(tword,candidate_list):
        twcandidate=[]
        best_count=0
        best_translation=""
        twcandidate = set(re.split(r'/',candidate_list))
        twcandidate_dic = {i:0 for i in twcandidate }
        twcandidate_re = []
        result = []
        for line in open('scripts/taibun2ch/all_tntl.trn', 'r', encoding='UTF-8'):
            tn_sequence=line.split(':')[0]
            cn_sequence=line.split(':')[2]
            for cword in twcandidate_dic:
                if cword in cn_sequence and tword in tn_sequence:
                    twcandidate_dic[cword]+=1
        return max(twcandidate_dic.keys(), key=(lambda k: twcandidate_dic[k]))

    def word_count(cword,tword):
        count=0
        #with open('output/all_tn_tl.trn','r',encoding='UTF-8-sig') as textfile:
        #for line in textfile:
        for line in open('scripts/taibun2ch/all_tn_tl.trn', 'r', encoding='UTF-8'):
            tn_sequence=re.split(':',line)[0]
            cn_sequence=re.split(':',line)[2]
            if ((cword in cn_sequence) and (tword in tn_sequence)):
                count=count+1
                #print(cn_sequence,":",tn_sequence)
        #print(tword+':'+str(count))
        # print(tword)
        #textfile.close()
        return count

    CN2TW_dict={}

    # sentence=input("請輸入句子:")
    cn_list=[]

    start = timeit.default_timer()

    for line in open('scripts/taibun2ch/TW2CN_dict_combined_20230426.txt', 'r', encoding='UTF-8'):
        #print(line)
        data = line.split('\n')
        key_value = data[0].split(':/')
        CN2TW_dict[key_value[0]] = key_value[1]

    #new_sentence=sentence.decode("utf-8") + "。。。"
    if type(sentence)=="bytes":
        new_sentence = sentence.decode('UTF-8') + "。。。"
    else:
        new_sentence = sentence + "。。。"
    # new_sentence=sentence+ "。。。"
    i=0
    tl_sentence=''
    while(i<len(new_sentence)-3):
        gram4=new_sentence[i:i+4]
        gram3=new_sentence[i:i+3]
        gram2=new_sentence[i:i+2]
        gram1=new_sentence[i]
        if (gram4 in CN2TW_dict.keys()):
            i = i+4
            # print(gram4,":",CN2TW_dict[gram4])
            tl_sentence=tl_sentence+translation_selection(gram4,CN2TW_dict[gram4])
        elif (gram3 in CN2TW_dict.keys()):
            i=i+3
            # print(gram3,":",CN2TW_dict[gram3])
            tl_sentence=tl_sentence+translation_selection(gram3,CN2TW_dict[gram3])
        elif (gram2 in CN2TW_dict.keys()):
            i=i+2
            # print(gram2,":",CN2TW_dict[gram2])
            tl_sentence=tl_sentence+translation_selection(gram2,CN2TW_dict[gram2])
        else:
            #print(gram1,":",CN2TW_dict[gram1])
            #print(len(new_sentence)-3-1)
            #print(i)
            #print(i==len(new_sentence)-3-1)
            if (gram1 in CN2TW_dict.keys()):
                if i>=len(new_sentence)-3-1 and gram1=="無":
                    tl_sentence=tl_sentence+"嗎"
                    #print(gram1,":",CN2TW_dict[gram1])
                else:
                    tl_sentence=tl_sentence+translation_selection(gram1,CN2TW_dict[gram1])
            else:
                tl_sentence=tl_sentence + '(' + gram1 + ')'
            i=i+1
    # print(sentence+":"+tl_sentence)
    # print(tl_sentence,end='\n')
    return tl_sentence
    # stop = timeit.default_timer()
    # print(stop-start)

if __name__ == '__main__':
    print(tai2ch_main(bytes("我歹腹肚","utf-8")))
