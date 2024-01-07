import requests
import json
def translation_request(text : str, model: str):
    msg_dict = dict()
    msg_dict['translation_text'] = text
    msg_dict['model'] = "id2zh_kevin"
    # 翻譯中文到印尼文
    res = requests.post('http://140.116.245.157:1002/translation',data=msg_dict)
    # 翻譯印尼文到中文
    # res = requests.post('http://140.116.245.157:1002/idn2zh',data=msg_dict)
    return res.json()
if __name__ == "__main__":    
    res = translation_request("saya suka apel", "id2zh_kevin")
    # print(dict['after_translation'])
    print(res) 