import pandas as pd
import json
ADJDICT:list = ["sampit", "kecil", "malam", 
           "besar", "tinggi", "pendek", 
           'cepat', "lambat", "panans", 
           "dingin", "mahal", "murah", "sibuk",
           "jernih", "kacau","sederhana", "rumit",
           "cantik", "jelek", "gembira", "sedih",
           "bising", "bodoh", "menarik", "energik"
           "malas", "sehat", "asing", "biasa"
           "baru",
        ]
CAPRULE:list = [
    "SD", "China", "Taiwan", "Slim", "WC"
]
class ReplDictionary:
    def __init__(self) -> None:
        # 先處理字典，將字典裏面的東西讀出來
        with open('scripts/utils/replacement.json', 'r', encoding='utf-8') as f:
            self.syndict = dict(json.load(f))
            
    def word_repl(self, input_text: str) -> str:
        for k, v in self.syndict.items():
            # 也就是說，如果同義詞出現的話，那就優先替換成辭典裡面有的
            if input_text in v:
                return k
        return None
        
        
        
    