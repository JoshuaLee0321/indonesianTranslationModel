# -*- coding: UTF-8 -*-

import re
import unicodedata
#import server_logger
#logger = server_logger.logger()

def transform(inputs, mode="auto", big_or_small="big"):
    # if big_or_small != "big" and big_or_small != "small":
    #     raise ValueError("big_or_small參數只有有<big>和<small>兩個選項。")

    inputs = str(inputs).replace("％","%").replace("／","/").replace(".",".").replace("，",",")
    inputs = unicodedata.normalize('NFKC', inputs)

    pattern = r"[0-9]+\.?[0-9]*"

    if mode == "auto":
        tmp_output = inputs
        #pattern_pre = r"[昨|今|明]([0-9]+)[日|月|年]"
        #tmp_output = re.sub(pattern_pre,)
        # tmp_output = tmp_output.replace("-", "")
        # print(tmp_output)
        # tran 0800-? ?[0-9]{6} (電話號碼)
        # pattern = r"0800 ?[0-9]{6}"
        # tmp_output = re.sub(pattern, lambda x: one_one(
        #     x.group(), "small"), tmp_output)
        # end of tran 0800-? ?[0-9]{6}

        # tran 0[1-9]- num*{7,8} (電話or手機號碼)
        #手機號碼

        pattern = r"09[0-9]{2}\-?[0-9]{3}\-?[0-9]{3}"
        tmp_output = re.sub(pattern, lambda x: one_one(
            x.group(), "big"), tmp_output)
        #if inputs != tmp_output:
            #logger.info("判定為手機形式".format(inputs,tmp_output), extra={"ipaddr":""})

        #電話號碼
        if inputs == tmp_output:
            pattern = r"0[2-9]\-?[0-9]{7}"
            tmp_output = re.sub(pattern, lambda x: one_one(
                x.group(), "big"), tmp_output)
            #if inputs != tmp_output:
                #logger.info("判定為電話形式".format(inputs,tmp_output), extra={"ipaddr":""})

        # tran date
        lt = list(tmp_output)
        datestatus = 0
        while True:
            m = re.search(
                "([1-9]\d{3})([ \-\./年]{1})([0-1]?\d)([ \-\./月]{1})([0-3]?\d)(日?)", tmp_output)
            """m_mini = re.search(
                "([0-1]?\d)([ \-\./月]{1})([0-3]?\d)(日?)", tmp_output)
            if m == None:
                if m_mini == None:
                    break"""
            if m==None: break
            rs = m.span()[0]
            es = m.span()[1]
            m_groups = m.groups()

            y = transform(m_groups[0], mode="one_one", big_or_small="big")
            m = transform(m_groups[2], mode="all", big_or_small="big")
            d = transform(m_groups[4], mode="all", big_or_small="big")
            ymd = y + "年" + m + "月" + d + "日"

            lt[rs:es] = ymd

            tmp_output = ""

            for w in lt:
                tmp_output = tmp_output + w
            datestatus = 1
            #logger.info("判定為完整年分日期形式".format(inputs,tmp_output), extra={"ipaddr":""})
            inputs = tmp_output
        if datestatus == 0:
            pass

        else: # trans year
            pattern = r"[12]\d{3}"
            tmp_output = re.sub(pattern, lambda x: one_one(
                x.group(), "big"), tmp_output)
            #logger.info("判定為單獨年分形式".format(inputs,tmp_output), extra={"ipaddr":""})
        
        if inputs == tmp_output:
            while True:
                m = re.search(
                    "([0-1]?\d)/([0-3]?\d)(日?)", tmp_output) #5/17
                
                if m!=None:
                    rs = m.span()[0]
                    es = m.span()[1]
                    m_groups = m.groups()
                    m = transform(m_groups[0], mode="all", big_or_small="big")
                    d = transform(m_groups[1], mode="all", big_or_small="big")
                    md = m + "月" + d + "日"
                    lt[rs:es] = md

                    tmp_output = ""
                    for w in lt:
                        tmp_output = tmp_output + w
                    datestatus = 2
                    #logger.info("判定為月+日 日期形式".format(inputs,tmp_output), extra={"ipaddr":""}) #New addition
                    inputs = tmp_output
                else:
                    break

        # end of trans date
        if inputs == tmp_output:
            while True:
                m = re.search("([0-9]{1,2})\:([0-9]{1,2})", tmp_output) #cf. 運動比分、化學比例5:7 (todo)
                #在運動新聞中轉為比分判斷 (todo) 
                pattern = r"[0-9]{1,2}\:[0-9]{1,2}"
                if m!=None:
                    rs = m.span()[0]
                    es = m.span()[1]
                    m_groups = m.groups()
                    hr = transform(m_groups[0], mode="all", big_or_small="big")
                    min = transform(m_groups[1], mode="all", big_or_small="big")
                    tim = hr + "點" + min + "分"
                    lt[rs:es] = tim

                    tmp_output = ""

                    for w in lt:
                        tmp_output = tmp_output + w
                    #datestatus = 2
                    #logger.info("判定為時間形式".format(inputs,tmp_output), extra={"ipaddr":""})
                    inputs = tmp_output
                else:
                    break
                """tmp_output = re.sub(pattern, lambda x: an2cn(
                    x.group(),big_or_small='big'), tmp_output)
                if inputs != tmp_output:
                    print("判定為時間形式".format(inputs,tmp_output))
                    inputs = tmp_output
                else:
                    print('判定不為時間形式\n{}'.format(tmp_output))"""

        if inputs == tmp_output:
            pattern = r"[0-9]+[\.]?[0-9]*%" #XX.0% = XX%
            tmp_output = re.sub(pattern, lambda x: an2cn(
                x.group(),big_or_small='big'), tmp_output)
            if inputs != tmp_output:
                #logger.info("判定百分比形式".format(inputs,tmp_output), extra={"ipaddr":""})
                inputs = tmp_output
            else:
                pass
        if inputs == tmp_output:
            pattern = r"[0-9]+\-[0-9]*%" #XX.0% = XX%
            tmp_output = re.sub(pattern, lambda x: an2cn(
                x.group(),big_or_small='big'), tmp_output)
            if inputs != tmp_output:
                #logger.info("判定範圍形式".format(inputs,tmp_output), extra={"ipaddr":""})
                inputs = tmp_output
            else:
                pass
        
        #others
        if inputs == tmp_output: #1,000,000,000 NT dollars
            pattern = r"[0-9]{1,3}\,[0-9]{3}\,[0-9]{3}\,[0-9]{3}"
            tmp_output = re.sub(pattern, lambda x: an2cn(x.group(),big_or_small='big'), tmp_output)
            if inputs != tmp_output:
                #logger.info("判定為逗號分隔形式(超過十億)".format(inputs,tmp_output), extra={"ipaddr":""})
                inputs = tmp_output
        if inputs == tmp_output:
            pattern = r"[0-9]{1,3}\,[0-9]{3}\,[0-9]{3}"
            tmp_output = re.sub(pattern, lambda x: an2cn(x.group(),big_or_small='big'), tmp_output)
            if inputs != tmp_output:
                #logger.info("判定為逗號分隔形式(超過百萬)".format(inputs,tmp_output), extra={"ipaddr":""})
                inputs = tmp_output
        if inputs == tmp_output:
            pattern = r"[0-9]{1,3}\,[0-9]{3}"
            tmp_output = re.sub(pattern, lambda x: an2cn(x.group(),big_or_small='big'), tmp_output)
            if inputs != tmp_output:
                #logger.info("判定為逗號分隔形式(超過千)".format(inputs,tmp_output), extra={"ipaddr":""})
                inputs = tmp_output
        
        pattern = r"[0-9]+\.?[0-9]*"
        output = re.sub(pattern, lambda x: an2cn(x.group(),big_or_small='big'), tmp_output)
        
    elif mode == "all":
        output = re.sub(pattern, lambda x: an2cn(
            x.group(), big_or_small), inputs)
    elif mode == "one_one":
        output = re.sub(pattern, lambda x: one_one(
            x.group(), big_or_small), inputs)
    else:
        raise ValueError(f"沒有這個模式:{mode}!")

    return output


def an2cn(inputs=None, big_or_small="big"):
    # if big != "big" and big_or_small != "small":
    #     raise ValueError("big_or_small參數只有有<big>和<small>兩個選項。")

    if inputs is not None:
        negative = ""
        # 将数字转化为字符串
        if not isinstance(inputs, str):
            inputs = convert_number_to_string(inputs)
        # 检查数据是否有效
        check_inputs_is_valid(inputs)
        new_num = ""
        # 判断正負
        if inputs[0] == "-":
            inputs = inputs[1:]
            negative = "負"
        if "," in inputs: #ex: 13,330 = 13330
            repair = inputs.split(",")
            for restruct in repair:
                new_num+=restruct
        
        else:
            new_num = inputs
        #判斷範圍
        if "-" in new_num:
            split_result = new_num.split(":")
            range_start = split_result[0]
            range_end = split_result[1]
            output = integer_convert(range_start, big_or_small=big_or_small) + "到"\
                    + integer_convert(range_end, big_or_small=big_or_small) 
        if ":" in new_num: #time format
            split_result = new_num.split(":")
            hour_data = split_result[0]
            minute_data = split_result[1]
            if minute_data == "00":
                output = integer_convert(hour_data, big_or_small=big_or_small) + "點"
            else:
                output = integer_convert(hour_data, big_or_small=big_or_small) + "點"\
                    + integer_convert(minute_data, big_or_small=big_or_small) + "分"
        # 切割整数部分和小数部分
        else:
            split_result = new_num.split(".")
            len_split_result = len(split_result)
            if len_split_result == 1:
                # 不包含小数的输入
                if ("%" in new_num):
                    integer_data = split_result[0].replace("%","")
                    output = "百分之" + integer_convert(integer_data, big_or_small=big_or_small)
                else:
                    integer_data = split_result[0]
                    output = integer_convert(integer_data, big_or_small=big_or_small)
            elif len_split_result == 2:
                # 包含小数的输入
                if ("%" in new_num):
                    integer_data = split_result[0]
                    decimal_data = split_result[1].replace("%","")
                    output = "百分之" + integer_convert(
                        integer_data, big_or_small=big_or_small) + decimal_convert(decimal_data, big_or_small="big")
                else:
                    integer_data = split_result[0]
                    decimal_data = split_result[1]
                    output = integer_convert(
                        integer_data, big_or_small=big_or_small) + decimal_convert(decimal_data, big_or_small="big")

            else:
                raise ValueError(f"輸入格式錯誤：{inputs}！")
    else:
        raise ValueError(f"輸入數據為空！")

    return negative + output


def check_inputs_is_valid(check_data):
    # 检查输入数据是否在规定的字典中
    all_check_keys = ["0", "1", "2", "3", "4",
                      "5", "6", "7", "8", "9", ".", "-",":", "%" ,","]
    for data in check_data:
        if data not in all_check_keys:
            raise ValueError(f"输入的数据不在转化范围内：{data}！")


def convert_number_to_string(number_data):
    # python 会自动把 0.00005 转化成 5e-05，因此 str(0.00005) != "0.00005"
    string_data = str(number_data)
    if "e" in string_data:
        string_data_list = string_data.split("e")
        string_key = string_data_list[0]
        string_value = string_data_list[1]
        if string_value[0] == "-":
            string_data = "0." + "0"*(int(string_value[1:])-1) + string_key
        else:
            string_data = string_key + "0"*int(string_value)

    return string_data


def integer_convert(integer_data, big_or_small="big"):
    """
    if big_or_small == "big":
        # numeral_list = ["零", "壹", "貳", "叁", "肆", "伍", "陸", "柒", "捌", "玖"]
        # unit_list = ["", "拾", "佰", "仟", "萬", "拾", "佰", "仟", "億", "拾", "佰", "仟", "萬", "拾", "佰",
        #              "仟", "兆", "拾", "佰", "仟", "萬", "拾", "佰", "仟", "億", "拾", "佰", "仟", "萬", "拾", "佰", "仟"]
        numeral_list = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
        unit_list = ["", "十", "百", "千", "萬", "十", "百", "千", "億", "十", "百", "千", "萬", "十", "百",
                     "千", "兆", "十", "百", "千", "萬", "十", "百", "千", "億", "十", "百", "千", "萬", "十", "百", "千"]
    elif big_or_small == "small":
        numeral_list = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
        unit_list = ["", "十", "百", "千", "萬", "十", "百", "千", "億", "十", "百", "千", "萬", "十", "百",
                     "千", "兆", "十", "百", "千", "萬", "十", "百", "千", "億", "十", "百", "千", "萬", "十", "百", "千"]
    elif big_or_small == "ordinal":
        numeral_list = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
        unit_list = ["", "十", "百", "千", "萬", "十", "百", "千", "億", "十", "百", "千", "萬", "十", "百",
                     "千", "兆", "十", "百", "千", "萬", "十", "百", "千", "億", "十", "百", "千", "萬", "十", "百", "千"]                     
    else:
        raise ValueError("big_or_small參數只有有<big>和<small>兩個選項。")
    """
    numeral_list = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]    
    unit_list = ["", "十", "百", "千", "萬", "十", "百", "千", "億", "十", "百", "千", "萬", "十", "百",
                 "千", "兆", "十", "百", "千", "萬", "十", "百", "千", "億", "十", "百", "千", "萬", "十", "百", "千"]

    # 去除前面的 0，比如 007 => 7
    integer_data = str(int(integer_data))

    len_integer_data = len(integer_data)
    if len_integer_data > len(unit_list):
        raise ValueError(f"超出数据范围，最长支持 {len(unit_list)} 位")

    output_an = ""
    for i, d in enumerate(integer_data):
        r_index = len_integer_data - i
        r_index = r_index - 1

        if int(d):
            if int(d)==2 and ((r_index % 4 == 0 or r_index % 4 == 1) and (r_index==1 or r_index==0)) and len_integer_data!=1:
                output_an += "二" + \
                    unit_list[r_index]
            elif int(d)==1 and ((r_index % 4 == 0 or r_index % 4 == 1) and (r_index==1 or r_index==0)) and len_integer_data!=1:
                output_an += "一" + \
                    unit_list[r_index]
            else:
                output_an += numeral_list[int(d)] + \
                unit_list[r_index]
        else:
            if r_index % 4 == 0:
                output_an += numeral_list[int(d)] + \
                    unit_list[r_index]

            if i > 0 and not output_an[-1] == "零":
                output_an += numeral_list[int(d)]
    if output_an[-3:-2]=="一十":
        output_an = output_an.replace("零零", "零").replace(
        "零萬", "萬").replace("零億", "億").replace("零兆", "兆")\
        .replace("一十","十").strip("零")
    else:
        output_an = output_an.replace("零零", "零").replace(
            "零萬", "萬").replace("零億", "億").replace("零兆", "兆")\
            .replace("壹十","十").replace("一十","十").strip("零")

    # 解决「一十几」和「壹拾几」问题
    if output_an[:2] in ["一十", "壹拾","壹十"]:
        output_an = output_an[1:]

    # 0 - 1 之间的小数
    if not output_an:
        output_an = "零"

    return output_an


def decimal_convert(decimal_data, big_or_small="big"):
    len_decimal_data = len(decimal_data)

    if len_decimal_data > 15:
        #logger.warning(f"warning: 小数部分长度为{len_decimal_data}，超过15位有效精度长度，将自动截取前15位！", extra={"ipaddr":""})
        decimal_data = decimal_data[:15]
    
    if len_decimal_data:
        output_an = "點"
    else:
        output_an = ""

    
    if big_or_small == "big":
        # numeral_list = ["零", "壹", "貳", "叁", "肆", "伍", "陸", "柒", "捌", "玖"]
        numeral_list = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
    elif big_or_small == "small":
        # numeral_list = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
        numeral_list = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
    elif big_or_small == "ordinal":
        numeral_list = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
    else:
        raise ValueError("big_or_small參數只有有<big>和<small>兩個選項。")

    for data in decimal_data:
        output_an += numeral_list[int(data)]
    return output_an


def one_one(data, big_or_small="big"):
    len_data = len(data)

    if len_data > 15:
        #logger.warning(f"warning: 小数部分长度为{len_data}，超过15位有效精度长度，将自动截取前15位！", extra={"ipaddr":""})
        data = data[:15]

    output_an = ""

    if big_or_small == "big":
        # numeral_list = ["零", "壹", "貳", "叁", "肆", "伍", "陸", "柒", "捌", "玖"]
        numeral_list = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
    elif big_or_small == "small":
        # numeral_list = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
        numeral_list = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
    elif big_or_small == "ordinal":
        numeral_list = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
    else:
        raise ValueError("big_or_small參數只有有<big>和<small>兩個選項。")

    for _data in data:
        try:
            output_an += numeral_list[int(_data)]
        except:
            # output_an += _data
            pass
    return output_an


def one_one_reserve(data, big_or_small="big"):
    len_data = len(data)

    if len_data > 15:
        #logger.warning(f"warning: 小数部分长度为{len_data}，超过15位有效精度长度，将自动截取前15位！", extra={"ipaddr":""})
        data = data[:15]

    output_an = ""

    if big_or_small == "big":
        numeral_list = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
    elif big_or_small == "small":
        numeral_list = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
    elif big_or_small == "ordinal":
        numeral_list = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
    else:
        raise ValueError("big_or_small參數只有有<big>和<small>兩個選項。")

    for _data in data:
        try:
            output_an += numeral_list[int(_data)]
        except:
            output_an += _data
    return output_an

if __name__ == "__main__":
    data = '''
    '''
    data = '''
    即時新聞／綜合報導〕世界衛生組織（WHO）15日召開記者會，日本媒體《NHK》提問，世衛將台灣孤立在外，但世衛秘書長譚德塞（Tedros Adhanom Ghebreyesus）避談有關台灣的問題，由另外3名官員接力10分鐘回答，以「一個中國」當作擋箭牌。

    綜合媒體報導，日本《NHK》記者以連線方式提問，點名譚德塞，問到世衛刻意孤立台灣，並將政治凌駕於公共衛生之上，且美國國務院批評世衛未將台灣早期提供的資訊提供給全球，但譚德塞避談有關台灣的問題，由世衛公共衛生緊急計畫執行主任萊恩（Michael Ryan）、世衛副法律顧問索羅門（Steven Solomon），以及世衛研究冠狀病毒部門的范科霍芙（Maria Van Kerkhove）等3名官員回答。

    萊恩表示，去年12月31日，關於武漢市一系列非典型肺炎的訊息有多個消息來源，但實際上這些消息源自武漢衛健委網站上的新聞稿及出版物，世衛與各機構進行多方溝通，最後是世衛與中國正式確認這項訊息。

    索羅門則回應指出，世衛是由國家組成的國際組織，政治問題必須由194個會員國做決定，且世衛為聯合國機構之一，聯合國早在1971年就已通過決議，由中華人民共和國在聯合國中取代中華民國，世衛立場與聯合國保持一致，1972年在第25.1號決議做出同樣決定。索羅門說，世衛的任務是致力促進世界各地所有人的健康，這意味著為全人類服務，無論身在台灣、中國或其他任何地方。

    范科霍芙也說，她在2月及15日稍早與台灣透過電話聯繫，與台灣的科學家與公衛專家交換意見，並與第一線工作者及參與這場大流行疾病的人員交流。
    '''
    data = 3540469098308190422848908402948
    data = '''中時電子報
    FACEBOOK
    LINE
    行動APP
    簡繁
    旺旺中時媒體集團
    新冠肺炎特別報導
    關閉
    關鍵字
    請輸入關鍵字
    新冠肺炎
    即時
    政治
    政治首頁
    總覽
    言論
    生活
    娛樂
    財經
    社會
    話題
    有影
    國際
    軍事
    兩岸
    時尚
    體育
    科技
    玩食
    專輯
    新冠肺炎
    即時
    政治
    政治首頁
    總覽
    言論
    生活
    娛樂
    財經
    社會
    話題
    有影
    國際
    軍事
    兩岸
    時尚
    體育
    科技
    玩食
    專輯
    首頁
    政治
    滿意蔡政府這項紓困嗎？江啟臣「最新民調」一面倒
    11:112020/04/15 中時電子報 李俊毅
    Facebook

    Messenger

    Line

    Weibo

    Twitter

    Telegram

    複製連結
    國民黨主席江啟臣。(圖/本報資料照)
    國民黨主席江啟臣。(圖/本報資料照)
    Facebook

    Messenger

    Line

    Weibo

    Twitter

    Telegram

    複製連結
    字級設定：小中大特
    民進黨政府近期在最新的紓困案決定採發放紓困券方式，助業者度過難關，但要先掏錢消費才能享25%折價，且最多只能折千元，甚至限定使用支付APP，諸多設限讓國民黨立院黨團多次呼籲，政府直發現金最有感。黨主席江啟臣也在近日做網路民調，投票結果驚人。

    江啟臣昨14日在臉書進行網路投票大調查，他表示，疫情全球蔓延，衝擊台灣經濟，目前無薪假勞工數量持續攀升，一個無薪假的勞工就代表著背後一家嗷嗷待哺孩子，政府此時應該站出來讓民眾渡過這一關。

    他並提出兩個方案，分別是國民黨團版和政院版本，並請網友投票，認為哪一個方案符合需求。

    國民黨版：政府直接發現金、按所得級距排富、消費場所不受限

    政院版：酷碰券，先掏錢才能享折價，支付享25%折扣，每月最多折1000元、必須綁定行動支付平台與敬老卡，且限定商家。

    投票約15小時後，已累積近2萬人投票，有96%網友投給國民黨「發現金」版本，僅只有有4%網友投給政院的「酷碰券」版本。兩個選項結果差異可說是一面倒，顯見政院版本還有很大的檢討控間。

    台北市長最新民調出爐！網一看驚呆：他2022無敵....
    韓國瑜議會質詢時間曝？黃捷傻眼！韓粉終於反擊
    他遭1450圍剿...陳學聖怒喊：陳時中出來講啊！
    港媒來台直擊曝高雄夜市現況！攤商淚崩喊5字...
    高嘉瑜「為這事」遭黨紀重罰... 網一句話怒嗆民進黨！
    民進黨下一步？趙少康預測冷笑：這招蔡不敢
    陳柏惟嗆華航「該做這事」！網傻眼：真可憐啊...
    韓上任後 網驚：可惡！高雄這區20年後竟變了
    韓被爆請辭？藍營人士揭秘辛
    台買廣告登紐時反擊譚德塞 網友最新評價曝光！
    川普撤資WHO...網：譚德塞又找到新金主了！
    林書豪3千餘字吐美國疫情實況 竟遭1450灌爆？
    陸官媒為何警告民進黨？趙少康分析後大驚！

    (中時電子報)

    # 江啟臣 #國民黨 #民調 #民進黨 #武漢肺炎 #新冠肺炎 #世衛
    政治熱門新聞
    滿意蔡政府這項紓困嗎？江啟臣「最新民調」一面倒 - 政治
    台買廣告登紐時反擊譚德塞 網友最新評價曝光！ - 政治
    台北市長最新民調出爐！網一看驚呆：他2022無敵 - 政治
    藍委舉辦「華航改名」投票 結果嚇死人！ - 政治
    韓被爆請辭？藍營人士揭秘辛 - 政治
    高嘉瑜「為這事」遭黨重罰...網一句話怒嗆民進黨！ - 政治
    陳柏惟嗆「華航該做這事」網傻眼：真可憐啊... - 政治
    韓國瑜進議會時間曝光？黃捷怒嗆！韓粉終反擊 - 政治
    上海記者張經義來自台灣？陸委會：涉違兩岸條例將依法查處 - 政治
    林書豪遭1450圍剿...陳學聖怒點名他：還要躲嗎？ - 政治

    也許您會感興趣
    推薦閱讀
    四叉貓現身擔任「數位諸葛亮」決選提問人 江啟臣盼助國民黨重新設計 
    四叉貓現身擔任「數位諸葛亮」決選提問人 江啟臣盼助國民黨重新設計
    15:082020/04/11 政治
    藍數位行銷科技長人選出爐 由Dcard創辦人簡勤佑出任 
    藍數位行銷科技長人選出爐 由Dcard創辦人簡勤佑出任
    19:402020/04/11 政治
    疫情燒進日本皇宮？驚傳「皇室護衛官」確診新冠肺炎 
    疫情燒進日本皇宮？驚傳「皇室護衛官」確診新冠肺炎
    20:422020/04/11 國際
    快評》國民黨老店重開端出新菜色 也不應忘了原味 
    快評》國民黨老店重開端出新菜色 也不應忘了原味
    20:262020/04/12 政治
    國民黨不排除赴陸溝通 
    國民黨不排除赴陸溝通
    04:102020/04/13 焦點新聞
    國民黨論述模糊 陸學者：從寬理解 
    國民黨論述模糊 陸學者：從寬理解
    04:102020/04/13 焦點新聞
    老店新開張 勿忘老味道 
    老店新開張 勿忘老味道
    04:102020/04/13 政治要聞
    爭取2022市長當選、議員過半 綠議員登記角逐市黨部主委 
    爭取2022市長當選、議員過半 綠議員登記角逐市黨部主委
    10:592020/04/13 政治
    藍營笑不敢改華航　林佳龍嗆「先改台灣國民黨」 
    藍營笑不敢改華航　林佳龍嗆「先改台灣國民黨」
    11:092020/04/14 生活
    笑你不敢 國民黨激林佳龍遭反嗆 
    笑你不敢 國民黨激林佳龍遭反嗆
    01:242020/04/15 政治要聞
    發表意見

    與我聯絡報紙讀者服務新聞授權
    服務條款隱私權聲明一起做公益
    旺旺集團旺旺中時媒體集團
    時報資訊關於我們
    請尊重智慧財產權勿任意轉載違者依法必究© 1995 - 2020 China Times Group.
    回到頁首
    發表意見
    免費電話
001   中央信託  0800-088898
0800-055099
002   農民銀行  0800-000584
003   交通銀行  0800-055968
004   臺灣銀行  (可手機)0800-000258
0800-025168
005   土地銀行  0800-282099
0800-089369
(可手機)0800-231590
006   合作金庫  0800-033175
007   第一銀行  0800-031111
(信用卡)0800-052888
008   華南銀行  (可手機)0800-036132
(可手機)0800-231039
009   彰化銀行  0800-365889
0800-021268
010   花旗(台灣)銀行 0800-022866
(可手機)0800-000881
011   上海商銀  (可手機，掛失)0800-003111
(可手機)0800050111
012   台北富邦  08000000000

0800-000000
​09-3715761
02-24214602
04-22446541
07-6112626
02-33226009
04-23502691
03-8538000
0800-021268
09-82307522
300
    '''
    while(1):
        data = input("input:")
        print('result:',transform(data))
        print('-------------------')
    # print((("-" * 150) + "\n") * 5)
    # print(transform(data, mode="all"))
    # print((("-" * 150) + "\n") * 5)
    # print(transform(data, mode="one_one"))
