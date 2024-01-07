import pandas as pd
from scripts.trietree import Trie

class patch_dict:
    def __init__(self) -> None:
        print("INFO | reading zh dictionary ...")
        self._orig_zh_dictionary = [i.split(' ')[0].replace("@@", '') for i in open("./translation_file/id2zh_1013/dict.zh.txt", 'r', encoding='utf-8').readlines()]
        
        print("INFO | reading idn dictionary ...")
        self._orig_id_dictionary = [i.split(' ')[0].replace("@@", '') for i in open("./translation_file/id2zh_1013/dict.en.txt", 'r', encoding='utf-8').readlines()]
        
        print("INFO | reading en dictionary ...")
        # self._orig_en_dictionary = [i.split(' ')[0].replace("@@", '') for i in open("./translation_file/zh2en_0406_Osborn/dict.en.txt", 'r', encoding='utf-8').readlines()]
        
        # for crosslingual dictionary only
        try:
            print("INFO | reading docker/logfile/ID2CH dict ...")
            self._out_dictionary = pd.read_csv('./logfile/crossLingualDictionary.csv')
        except:
            print("INFO | reading local/translation_file/ID2CH dict ...")
            self._out_dictionary = pd.read_csv('./translation_file/crossLingualDictionary.csv')
            
            
        print("INFO | preparing zh file")
        self.build_zh_trie_tree()
        self.build_zh_orig_trie()
        
        print("INFO | preparing indo file")
        self.build_id_trie_tree()
        self.build_id_orig_trie()
        
        # print("INFO | preparing en file")
        # self.build_en_trie_tree()
        # self.build_en_orig_tree()
    
    def build_en_trie_tree(self):
        self.Trie_en = Trie()
        for en in self._out_dictionary['en']:
            try:
                self.Trie_en.insert(en)
            except:
                continue
    
    def build_en_orig_tree(self):
        self.orig_Trie_en = Trie()
        for line in self._orig_en_dictionary:
            try:
                self.orig_Trie_en.insert(line)
            except:
                continue

    def build_id_trie_tree(self):
        self.Trie_id = Trie()
        for id in self._out_dictionary['idn']:
            try:
                self.Trie_id.insert(id)
            except:
                continue
    
    def build_id_orig_trie(self):
        self.orig_Trie_id = Trie()
        for line in self._orig_id_dictionary:
            try:
                self.orig_Trie_id.insert(line)
            except:
                continue
        
    def build_zh_trie_tree(self):
        self.Trie_zh = Trie()
        for ch in self._out_dictionary['zh']:
            try: 
                self.Trie_zh.insert(ch)
            except:
                continue
            
    def build_zh_orig_trie(self):
        '''
            a function used for checking if the word is located in dict.zh.txt
        '''
        self.orig_Trie_zh = Trie()
        for line in self._orig_zh_dictionary:
            try:
                self.orig_Trie_zh.insert(line)
            except:
                continue
            
    def search_word_sim(self, word: str):
        '''
            input: cutted chinese word, this will output similar words (candidate) back to user
            (ex. )
                砍死他 jieba.cut --> 砍死 他
                    砍死不存在 _orig_dictionary 中
                return {砍、砍掉、...`}
        '''
        candidate = {'match':[]}
        if word not in self._orig_zh_dictionary:
            for char in word:
                matching = [s for s in self._orig_zh_dictionary if char in s]
            for match in matching:
                candidate['match'].append(match)
        return candidate

    def search_word_dict(self,lang: str, word: str) -> dict:
        '''
            input: 字元
            return Dictionary
        '''
        if lang not in ['idn', 'zh']:
            print('only except idn and zh')
            return {}
        if lang == 'zh':
            query = self.Trie_zh.query(word)
        elif lang == 'idn':
            query = self.Trie_id.query(word)
        try:
            res = self._out_dictionary.loc[self._out_dictionary[lang] == query[0][0]].to_dict()
        except:
            return {}
        return res
