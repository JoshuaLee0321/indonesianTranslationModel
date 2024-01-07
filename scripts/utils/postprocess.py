import hanlp
import json
from scripts.utils.postProcessStatic import *

with open("scripts/utils/commonMistakes.json", 'r', encoding='utf-8') as f:
    COMMONMISTAKES = dict(json.load(f))


def zh_post_process(pipe, text: str, level: int = 1):
    hanlp_result = pipe(text)
    tok = hanlp_result['tok']
    pos = hanlp_result['pos']
    
    # # 從後面往前面檢查
    # for sentTok in range(len(tok)):
    #     for atom in range(len(tok[sentTok]), 0, -1):
    #         pass
        
    # 從前面往後面檢查
    for sentTok in range(len(tok)):
        
        for atom in range(len(tok[sentTok])):
            
            # 如果只有單個名詞，檢查之後是否存在單一動詞 + 名詞的 VV
            if pos[sentTok][atom] == "NN":
                #記錄當前的單一名詞
                record : str = tok[sentTok][atom]
                for i in range(atom, len(tok[sentTok])):
                    if pos[sentTok][i] == "VV" and record in tok[sentTok][i]:
                        # 也就是說，如果明明前面出現了同樣的名詞，在翻譯的時候把最後的名詞替換
                        # 下去比較符合語意
                        tok[sentTok][i] = tok[sentTok][i].replace(record, '')
    
    # rule based replacement
    before :str = " ".join([" ".join(item) for item in tok]).split(" ")
    before.append("EOL") # 防止跳脫
    
    pos = " ".join([" ".join(item) for item in pos]).split(" ")    
    pos.append("EOL")
    # -------------------------------------- # 
    after = list()
    
    for i in range(len(before) - 1):
        after.append(before[i])
        if before[i].isdigit() and before[i + 1] not in MEASURE_WORDS:
            if (pos[i + 1] == "PU"):
                continue
            after.append("個")
            
    if "EOL" in after:
        after.remove("EOL")
    
    after = " ".join(after)
    # -------------------------------------- # 
    # print("after", after)
    for k, v in REPL_RULE.items():
        for possibility in v:
            if possibility in after:
                after = after.replace(possibility, k)
                
    return after

def removeBPEandNorm(text: str) -> str:
    # for indonesian
    text = text.replace("& quot ;", "")
    text = text.replace("@@", "-")
    text = text.replace(" @ @", "")
    return text
def ruleBasedConversion(srcLangText: str, targetLangText: str) -> str:
    # for indonesian
    
    if "Saya kira" in srcLangText or "Aku kira" in srcLangText or "Dia kira" in srcLangText:
        # print("##########################", srcLangText)
        # print(targetLangText)
        targetLangText = targetLangText.replace("我 想", "我以為")
        targetLangText = targetLangText.replace("他 想", "他以為")
        
    if "SD" in srcLangText or "sekolah dasar" in srcLangText:
        targetLangText = targetLangText.replace("高中", "小學")
    
    if "magang" in srcLangText:
        targetLangText = targetLangText.replace("实习 医生", "實習生")
        
    return targetLangText
def confusionSetMerge(textList: list):
    
    result = [x.split(" ") for x in textList]
    # 權重最高的是 textList[0]
    # 也就是第一個
    highestResult = result[0]
    
    # 檢查如果其他 set 都存在的話，那就要放進去

    return result
    
def postFleuCorrectionModel(sentence: str) -> str:
    for ans, mistakes in COMMONMISTAKES.items():
        for mistake in mistakes:
            if mistake in sentence:
                sentence = sentence.replace(mistake, ans)
            
    return sentence

    
if __name__ == "__main__":
    zh_post_process()