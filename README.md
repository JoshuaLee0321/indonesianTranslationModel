
# Usage : 
```python=
from fairseq.models.transformer import TransformerModel
model = TransformerModel.from_pretrained(
  './translation_file',
  checkpoint_file='checkpoint_best.pt',
)
translated = model("text")
```

# 注意，怎麼斷詞的就要怎麼在這邊轉換

:::info
todo : 之後要把斷詞的程式改成hanlp
:::

```python=
text = '我想吃蘋果'
text = ' '.join(jieba.cut(text))
print(model.translate(cc.convert(text)))
```

[檢體轉繁體](https://yanwei-liu.medium.com/python%E8%87%AA%E7%84%B6%E8%AA%9E%E8%A8%80%E8%99%95%E7%90%86-%E5%9B%9B-%E7%B9%81%E7%B0%A1%E8%BD%89%E6%8F%9B%E5%88%A9%E5%99%A8opencc-74021cbc6de3)


:::warning
目前已經都修改 api 的呼叫方法
API 呼叫方法改為：
```python=
import requests
# 注意，這邊的參數為 required
    msg_dict['translation_text'] = text
    msg_dict['model'] = model
res = requests.post('url/translation',data=msg_dict)
```
:::

# 2023/4/25 改動

* 目前把所有翻譯都從主程式搬出到 scripts.translate 中，若要新增任何 model，以下為流程
!!! 注意 !!! 檢體跟繁體要搞清楚
1. 請先行至 scripts.models 中新增你的模型
2. 接下來至 scripts.translate 中把那個語言的翻譯模組放上去
3. 之後去 scripts.services 中新增那個語言要回傳的東西 text -> text(str)
--- 如果要放在網頁上的話 ---
4. 去 templates.index.html 裡面 新增 option， option的 values 要是 services 裡面的參數

# 2023/6/17 改動

* 翻譯網路API加入台羅華語雙向翻譯
# 啟動翻譯網路API
docker run -dit --restart always --name indo -p 1002:1002 -v /home/mi2s/Translation_project/logfile/:/app/logfile/ indo_translation:latest



