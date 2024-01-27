from scripts.models import *                                # for general model
from scripts.ch2tl.pinyin_API_New_0525 import *             # pinyin model
from scripts.taibun2ch.service_main import *                # 台語轉換
from scripts.mainland_2_zh import Mainland_2_zhWord         # 繁體簡體話轉換
from scripts.zh_2_mainland import zhWord_2_Mainland         # 繁體簡體話轉換
from scripts.number_normalization_ch import transform       # 正規化數字
from scripts.number_normalization_en import transform_num2en as TR_en # 正規化數字 
from scripts.utils.preprocess import *                      # 替換模組
from scripts.utils.postprocess import * 
import logging                                              # 丟 log
import time

logging.basicConfig(level=logging.DEBUG)
"""
    這個 file 主要為從 app.py 過來的接口，每一個function都必須要回傳字串
    input: 字串 <還沒翻譯>
    output: 字串 <翻譯過後的>
    pipe: hanlp 的模組，其他沒有 required 的就不需要
"""
M2zh_sp = Mainland_2_zhWord()
zh2M_sp = zhWord_2_Mainland()


# def translate_zh2id_1002(text: str, pipe) -> str:
#     '''
#         此翻譯包括 unknown replacement 技術， 基本上就是換掉模組裡面沒有的詞彙
#     '''
#     text = unk_repl(pipe, True, "zh", "idn", model_zh2id_1002, text)    
#     return text

# def translate_id2zh_1002(text: str, pipe) -> str:
#     '''
#         此翻譯包括 unknown replacement 技術， 基本上就是換掉模組裡面沒有的詞彙
#     '''
#     text = unk_repl(None, False, "idn", "zh", model_id2zh_1002, text)    
#     return text

def translate_zh2id_1013(text: str, pipe) -> str:
    '''
        此翻譯包括 unknown replacement 技術， 基本上就是換掉模組裡面沒有的詞彙
    '''
    # text = dosth(text)
    text = text.replace("甚", "什")
    text = unk_repl(pipe, True, "zh", "idn", model_zh2id_1013, text)    
    return text

def translate_id2zh_1013(text: str, pipe) -> str:
    '''
        此翻譯包括 unknown replacement 技術， 基本上就是換掉模組裡面沒有的詞彙
    '''
    srcLangText: str = text

    
    # truecasing 他太慢
    # text = truecase_using_perl(text, "./translation_file/id2zh_1013/truecase-model.en")

    # BPE ----- 真奇怪，放入 bpe 之後效果變糟？
    # logging.info("applying bpe")

    # text = applybpe(text, "id")
    # logging.info(f"applied bpe: {text}")
    
    # simple preprocess
    logging.debug("indonesian_simple_preprocess")
    text = indonesian_simple_preprocess(text) # 此時為 list，方便接下來處理
    logging.info(f"applied simple prepeocess: {text}")
    
    # replacement
    logging.debug("indonesian_replacement")
    text = indonesian_replacement(text)
    logging.info(f"applied replacement: {text}")
    
    # go into model plus unk repl
    logging.debug("--->unk_repl")
    text = unk_repl(None, False, "idn", "zh", model_id2zh_1013, " ".join(text))    
    
    logging.debug(f"--->text: {text}")
    result = list()
    
    logging.debug("--->zh_post_process")
    for item in text:    
        post =  removeBPEandNorm(item)
        post = zh_post_process(pipe, post)
        post = ruleBasedConversion(srcLangText, post)
        post = postFleuCorrectionModel(post)
        result.append(post)
        
    logging.debug(result)
    # result = confusionSetMerge(result)
        

    return result
def translate_id2zh_raw(text: str, pipe):  
    text = model_id2zh_1013.translate(text)  
    return text
if __name__ == "__main__":
    print("幹")
