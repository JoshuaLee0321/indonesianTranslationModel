from typing import Any
import pandas as pd
from scripts.trietree import Trie # 網頁程式用的import
#from utils.trietree import Trie # 測試用的import

class zhWord_2_Mainland:
    def __init__(self) -> None:
        self.ZH_CH_COL = "中國的詞彙"
        self.ZH_TAI_COL = "台灣對應詞"
        self.trietree = Trie()
        self.dataframe = pd.read_csv("scripts/data/mainland_to_zh_words.csv")
        self.initTrie()

    def initTrie(self) -> None:
        for _, item in self.dataframe["台灣對應詞"].items():
            self.trietree.insert(item)

    def search_rows_by_value(self, df, column_name, value):
        return df[df[column_name] == value]

    def __call__(self, ws, *args: Any, **kwds: Any) -> Any:
        """
        args : infile (a txt file)
               insent (sentence)
               inart  (article)
               ws: a list of words to be transformed into zh-TW variant
        output: as is, but replaced with words
        """
        self.index = 0
        for why in ws:
            is_zh = self.trietree.query(why)
            if len(is_zh) != 0:
                orig_zh = is_zh[0][0]
                to_mainland = self.search_rows_by_value(
                    self.dataframe, self.ZH_TAI_COL, orig_zh
                )
                if to_mainland.empty == False:
                    orig_zh = to_mainland[self.ZH_TAI_COL]
                    to_mainland = to_mainland[self.ZH_CH_COL]
                    match_list = to_mainland.values.tolist()
                    match_orig = orig_zh.values.tolist()
                    temp = ws[self.index]
                    if temp != match_orig[0]:
                        b = self.index
                        while b != len(ws) - 1 and (
                            temp != match_orig[0] and match_orig[0] not in temp
                        ):
                            b += 1
                            temp += ws[b]
                        ws[self.index] = match_list[0]
                        for c in reversed(range(self.index + 1, b)):
                            ws.pop(c)
                    else:
                        ws[self.index] = match_list[0]

            self.index += 1
        return ws
    
