from scripts import search_word
from typing import List, Tuple
from scripts.utils.replacement_dictionary import ReplDictionary, ADJDICT, CAPRULE
import subprocess
from subword_nmt.apply_bpe import BPE
import logging                                              # 丟 log
#####################################################################
#   這個檔案主要使用 unknown repl 技術將模組裡面沒有看過的詞彙轉換成   ##
#   字典裏面已經新增過的詞彙                                         ##  
#####################################################################
import time
Search = search_word.patch_dict()
logging.basicConfig(level=logging.DEBUG)

# 以下用來記錄句型
repl = ReplDictionary()
current_sentence_pattern_pointer = ""

# bpe 模組在這邊做設定
with open("translation_file/id2zh_1013/bpecode.en") as model_file:
    id_bpe_model = BPE(model_file)
    
    
    
def unk_repl(   pipe     :None,         # 斷詞使用的 pipe
                need_pipe: bool,        # 是否需要斷詞
                from_lang: str,         # 從甚麼語言翻譯
                to_lang  : str,         # 翻譯到甚麼語言
                model    : None,        # 用甚麼模組翻譯
                input_text: str,        # 輸入字串
                ) -> List[str]:               # 回傳翻譯過後的自串
    '''
        from/to lang 目前只有 en idn zh
    '''
    # 決定是否要斷詞，用 list 包起來只是方便後續作業
    if need_pipe == True:
        tmp = list(pipe(input_text)["tok"])
        seg = list()
        for item in tmp:
            for val in item:
                seg.append(val)
    else:
        seg = list(input_text.split(" "))
        
    # 初始化相對應參數
    unk_cnt = 0
    pending = []
    
    
    # 選擇 query 語言種類
    # 找找看有沒有在原本的字典裡（模組的字典，若以後要新增模組字典必須要新增 orig_ 前墜）
    orig_query_tree = None
    oov_query_tree = None
    
    if from_lang == "idn":
        orig_query_tree = Search.orig_Trie_id
        oov_query_tree = Search.Trie_id
    elif from_lang == "zh":
        orig_query_tree = Search.orig_Trie_zh
        oov_query_tree = Search.Trie_zh
    elif from_lang == "en":
        orig_query_tree = Search.orig_Trie_en
        oov_query_tree = Search.Trie_en
        
    for i in range(len(seg)):
        search_orig = orig_query_tree.query(seg[i])
        # logging.info(search_orig)
        if search_orig == []:
            # logging.info(f"not found in model dict ::{seg[i]}")
            # 搜尋失敗，代表模組字典裏面沒有，此時搜尋相對應的 xlsx 檔案
            query_result = oov_query_tree.query(seg[i])
            if query_result == []: 
                # logging.info(f"not found in global dict ::{seg[i]}" )
                # TODO，接下來可以增加辭典或是想辦法利用其他詞彙替換
                continue
            pending.append(seg[i])
            seg[i] = "^ " + str(unk_cnt)
            unk_cnt += 1
            
    
    logging.debug(str(seg))
    logging.debug(pending)
        
    # 準備開始替換
    repl_dict_from = list()
    repl_dict_to   = list()
    
    for i in range(len(pending)):
        try:
            search_result = Search.search_word_dict(lang=from_lang, word=pending[i])
            # 搜尋到的文字插入到前方
            repl_dict_from.append(search_result[from_lang])
            repl_dict_to.append(search_result[to_lang])
        except:
            continue
    
    # 模組翻譯（包括 $ 字號）
    # print(seg)
    token = model.encode(" ".join(seg))
    translations = model.generate(token, beam_size=5)
    candidates = [model.decode(t['tokens']) for t in translations]

    # select candidate with the hightest score
    text = candidates[0]
    
    # print(f"candidates: {candidates}")
    text = str(text.replace("@@ ", "-"))
    
    logging.debug(f"{text}| BEFORE REPL |")
    
    # 將翻譯前替換的詞彙替換回 $ 字號
    for i in range(len(candidates)):
        if "^" in candidates[i]:
            cnt = 0
            for dic in repl_dict_to:
                candidates[i] = candidates[i].replace("^ " + str(cnt), list(dic.values())[0])
                cnt += 1
    logging.debug(f"{candidates[i]}| AFTER REPL |")
    
    return candidates


def truecase_using_perl(text: str, model: str) -> str:
    '''
    把 truecase 模組加入
    '''    
    command = ["./scripts/utils/perls/truecase.perl", "--model", model]

    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    stdout, _ = process.communicate(text + "\n")
    # print(stdout)
    return stdout.strip().replace("\n", "")

def applybpe(text: str, language: str = "id") -> str:
    if language == "id":
        return id_bpe_model.process_line(text.strip())
    return text
        
    
    


def indonesian_simple_preprocess(text: str) -> List[str]:
    '''
    目前在此 function 中解決的問題有：\n
        1. 簡易標點符號問題\n
        2. 簡易大小寫問題：在 CAPRULE 中\n
        3. 特殊解法 \n
        4. 字尾的干擾： ku, mu, kami, kita, nya, mereka\n
    '''
    
    
    # 逗號會導致錯誤，所有標點符號都要被完整隔開
    text = text.replace(",", " , ")
    text = text.replace(".", " . ")
    text = text.replace("!", " ! ")
    text = text.replace("?", " ? ")
    text = text.replace(";", " ; ")
    text = text.replace(":", " : ")
    text = text.replace("(", " ( ")
    text = text.replace(")", " ) ")
    text = text.replace("[", " [ ")
    text = text.replace("]", " ] ")
    text = text.replace("{", " { ")
    text = text.replace("}", " } ")
    text = text.replace("\\", " \\ ")
    text = text.replace("/", " / ")
    text = text.split(" ")
    
    # 處理有些文字必須要大寫的問題 truecase 太慢，決定不使用
    for i in range(len(text)):
        if text[i] not in CAPRULE:
            text[i] = text[i].lower()
    
    # 1, 2, 此區處理字首字尾以及特殊狀況
    for i in range(len(text)):
        if "ku" == text[i][-2:]:
            # 先查查看是否存在字典中
            data:list = Search.orig_Trie_id.query(text[i])
            if len(data) == 0:
                # 代表找不到，要拆開
                text[i] = text[i][:-2] + " " + 'ku'
            continue
        
        if "mu" == text[i][-2:]:
            data:list = Search.orig_Trie_id.query(text[i])
            if len(data) == 0:
                text[i] = text[i][:-2] + " " + 'mu'
            continue
        
        if "nya" == text[i][-3:]:
            data:list = Search.orig_Trie_id.query(text[i])
            if len(data) == 0:
                text[i] = text[i][:-3] + " " + 'nya'
            continue
        if "kita" == text[i][-4:]:
            data:list = Search.orig_Trie_id.query(text[i])
            if len(data) == 0:
                text[i] = text[i][:-4] + " " + 'kita'
            continue
        if "kami" == text[i][-4:]:
            data:list = Search.orig_Trie_id.query(text[i])
            if len(data) == 0:
                text[i] = text[i][:-4] + " " + 'kami'
            continue
        if "mereka" == text[i][-6:]:
            data:list = Search.orig_Trie_id.query(text[i])
            if len(data) == 0:
                text[i] = text[i][:-6] + " " + 'mereka'
            continue
        
        # 特殊狀況
        if '-' in text[i]:
            data:list = Search.orig_Trie_id.query(text[i])
            if len(data) == 0:
                text[i] = text[i].replace("-", " - ")
        try:
            if "baik-baik" == text[i] and "semua" != text[i - 1]:
                text[i] = "semua " + text[i]
                
            if text[i] + text[i + 1] == "kesana":
                if text[i - 1] == "caranya":
                    continue
                text[i] = "caranya " + text[i]
            if text[i] == "supaya":
                if text[i - 1] != ",":
                    text[i] = ", supaya"
        except:
            continue
            
            
            

    return  text
# 以下 function 假設了這個 function 被翻譯出來的文字為錯誤的，我們根據模組本身性質做調整
# TODO: 試驗 n-gram 有沒有辦法矯正
# TODO: 試驗其他 language model 是否有辦法矯正
# TODO: 先檢測是否為正常的句子
def post_process_replacement(   text: str,              # 輸入文字，判斷是否低於 language model 的某個定值，或是存在過多 dash
                                language_model: None,   # Language Model, 必須要符合 language_model(text, "lang") => 某機率
                                replace_policy: None,   # 替換規則，目前還沒想到
                                replace_mech : None,    # 替換機制，目前還沒有想到
                                ):
    return "Not available"

# 這個 function 會比較已經存在的 sentence pattern
# 如果比對成功，也就是找到了一個 pattern 是 本身就存在 pattern dict 中的
# 我們只會回傳比對成功與否
def is_fitting_sentence_pattern(sentence: str, lang: str) -> bool:
    return False

# 如果前者比對成功之後，我們使用這裡存在的字典翻譯過去
# 相對應的存取方法為
# (@verb) ==> (@動詞), (@動詞) ==> (@verb)
# (@Noun) ==> (@名詞), (@名詞) ==> (@noun) 
# TODO: 目前想不到好的方法存資料，現在只能用 O(N) 的方法使用
# 且目前都先使用增加辭典的方法
def sentence_pattern_translation(   sentence: str,      # 輸入文字
                                    from_lang: str,     # 輸入文字的語言
                                    to_lang             # 你想要翻譯成的語言
                                    ) -> str:
    
    return "Not available"

def sentence_post_process(before_translation: List[str], # 翻譯之前的文字，用 hanlp 隔開
                          confusion_set: List[str], # 
                          from_language: str, 
                          to_language: str, 
                          ):
    # 這個功能是用來選擇要如何選 candidate 中最好的那一個
    
    return

def indonesian_replacement(input_sent: List[str]):
    sent = input_sent
    for i in range(len(sent)):
        # 先找 動詞
        item =  repl.word_repl(sent[i])
        if item is not None:
            sent[i] = item
            
    # 形容詞替換的功能
    for adj in ADJDICT:
        for i in range(len(sent)):
            if "ke" + adj + "an" == sent[i]:
                sent[i] = "terlalu " + adj
            if "ter" + adj == sent[i]:
                sent[i] = "paling " + adj
                
    # phrase 轉換功能
    for i in range(len(sent)):
        try:
            if (sent[i] + " " + sent[i + 1] == "relaksasikan diri"
                    ) or (sent[i] + " " + sent[i + 1] == "Relaksasikan diri"):
                sent[i] = "tolong dir"
                sent[i + 1] = "kau santai"
            if (sent[i] + " " + sent[i + 1] == "cukup makan"
                    ) or (sent[i] + " " + sent[i + 1] == "Cukup makan"):
                sent[i] = "kenyang "
                sent[i + 1] = ""
        except:
            continue
        
    return sent

