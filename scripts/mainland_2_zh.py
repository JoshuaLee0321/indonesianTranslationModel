from typing import Any
import pandas as pd
from scripts.trietree import Trie


class Mainland_2_zhWord:
    def __init__(self) -> None:
        self.ZH_CH_COL = "中國的詞彙"
        self.ZH_TAI_COL = "台灣對應詞"
        self.trietree = Trie()
        self.dataframe = pd.read_csv("scripts/data/mainland_to_zh_words.csv")
        self.initTrie()

    def initTrie(self) -> None:
        for _, item in self.dataframe["中國的詞彙"].items():
            self.trietree.insert(item)

    def search_rows_by_value(self, df, column_name, value):
        return df[df[column_name] == value]

    def __call__(self, ws, *args: Any, **kwds: Any) -> Any:
        """
        args : infile (a txt file)
               insent (sentence)
               inart  (article)
        output: as is, but replaced with words
        """
        self.index = 0
        for why in ws:
            is_mainland = self.trietree.query(why)
            if len(is_mainland) != 0:
                orig_mainland = is_mainland[0][0]
                to_zh = self.search_rows_by_value(
                    self.dataframe, self.ZH_CH_COL, orig_mainland
                )
                if to_zh.empty == False:
                    orig_mainland = to_zh[self.ZH_CH_COL]
                    to_zh = to_zh[self.ZH_TAI_COL]
                    match_list = to_zh.values.tolist()
                    match_orig = orig_mainland.values.tolist()
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
