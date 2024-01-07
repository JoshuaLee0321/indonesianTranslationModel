import json
import requests
from ckiptagger import construct_dictionary
word_to_weight = {        
        "3C": 2,
        "3c":2,
        "B肝": 2, # 權重較重, 代表會斷詞成 '一個' '人', 而非 '一個人'
        "C肝": 2,
        "聲光絢爛":2,
        "日益普及":2,
        "0~18歲":2,
        "0~18個月":2,
        "久坐不動":2,
        "恭喜發財":2,
        "孩童們":2,
        "不對":2,
        "不好":2,
        "不要":2,
        "不敢":2,
        "三C":2,
        "三c":2,
        "維他命A":2,
        "維他命B":2,
        "維他命C":2,
        "維他命D":2,
        "長照四包錢":2,
        "巴氏量表": 2,
        "停不下來": 2,
        "一覺到天亮": 2,
        "標靶藥物": 2,
        "標靶治療": 2,
        "高齡者": 2,
        "易累": 2,
        "黑色素瘤": 2,
        "不須要": 2,
        "不需要": 2,
        "二等親": 2
    }
dictionary2 = construct_dictionary(word_to_weight)
def call_ckip(sentence_list):
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzUxMiJ9.eyJ2ZXIiOjAuMSwiaWF0IjoxNjYyODA1MTExLCJ1c2VyX2lkIjoiMjkzIiwiaWQiOjQ2Niwic2NvcGVzIjoiMCIsInN1YiI6IiIsImlzcyI6IkpXVCIsInNlcnZpY2VfaWQiOiIxIiwiYXVkIjoid21ta3MuY3NpZS5lZHUudHciLCJuYmYiOjE2NjI4MDUxMTEsImV4cCI6MTY3ODM1NzExMX0.C1WpV4-9GxjT5qV7c1zZDStMmD3K6WGcIHZA7wrppOd_T2f_tpOcnRFKxdMGeCMBFYWIThh0HeXdjbkQ4AEZZ7SSddAn2YiOtguyVDHEyEYYeUerK_junGCXixexQ4jsM3Top8tMR6fsgHeE_jBH4KFSgeTlZLTkJMnw0ghAJYE"
    #res = requests.post("http://140.116.245.157:2001", data={"data":sentence_list, "token":token,"dict":dictionary2})
    res = requests.post("http://140.116.245.157:28961", data={"data":sentence_list, "token":token,"dict":dictionary2})
    #res = requests.post("http://140.116.245.157:28961", data={"data":sentence_list, "token":token})
    response = json.loads(res.text)

    return response["ws"], response["pos"], response["ner"]

if __name__ == "__main__":
    input_str = ["沉溺於聲光絢爛的科技"]
    print(call_ckip(input_str))

