# -*- coding: UTF-8 -*-

import re
import unicodedata
#import server_logger
#logger = server_logger.logger()

def transform_num2en(inputs, mode="auto", big_or_small="big"):
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

            y = transform_num2en(m_groups[0], mode="one_one", big_or_small="big")
            m = integer_convert(m_groups[2], big_or_small="month")
            d = transform_num2en(m_groups[4], mode="all", big_or_small="ordinal")
            ymd = y + " " + m + " " + d + " "

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
                    m = integer_convert(m_groups[0], big_or_small="month")
                    d = transform_num2en(m_groups[1], mode="all", big_or_small="ordinal")
                    md = m + " " + d + " "
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
                    hr = transform_num2en(m_groups[0], mode="all", big_or_small="big")
                    min = transform_num2en(m_groups[1], mode="all", big_or_small="big")
                    tim = hr + "o'clock" + min
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
            pattern = r"[0-9]+th"
            tmp_output = re.sub(pattern, lambda x: integer_convert(
                x.group(), "ordinal"), tmp_output)
            if inputs != tmp_output:
                #logger.info("判定為序數唸法形式".format(inputs,tmp_output), extra={"ipaddr":""})
                inputs = tmp_output
        
        if inputs == tmp_output:
            pattern = r"[0-9]+st"
            tmp_output = re.sub(pattern, lambda x: integer_convert(
                x.group(), "ordinal"), tmp_output)
            if inputs != tmp_output:
                #logger.info("判定為序數唸法形式".format(inputs,tmp_output), extra={"ipaddr":""})
                inputs = tmp_output
        if inputs == tmp_output:
            pattern = r"[0-9]+nd"
            tmp_output = re.sub(pattern, lambda x: integer_convert(
                x.group(), "ordinal"), tmp_output)
            if inputs != tmp_output:
                #logger.info("判定為序數唸法形式".format(inputs,tmp_output), extra={"ipaddr":""})
                inputs = tmp_output
        if inputs == tmp_output:
            pattern = r"[0-9]+rd"
            tmp_output = re.sub(pattern, lambda x: integer_convert(
                x.group(), "ordinal"), tmp_output)
            if inputs != tmp_output:
                #logger.info("判定為序數唸法形式".format(inputs,tmp_output), extra={"ipaddr":""})
                inputs = tmp_output

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

    output = output.replace("   ","  ").replace("  "," ")
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
            negative = "minus"
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
            output = integer_convert(range_start, big_or_small=big_or_small) + " to "\
                    + integer_convert(range_end, big_or_small=big_or_small) 
        if ":" in new_num: #time format
            split_result = new_num.split(":")
            hour_data = split_result[0]
            minute_data = split_result[1]
            if minute_data == "00":
                output = integer_convert(hour_data, big_or_small=big_or_small) + " o'clock and "
            else:
                output = integer_convert(hour_data, big_or_small=big_or_small) + " o'clock and "\
                    + integer_convert(minute_data, big_or_small=big_or_small) + " minutes "
        # 切割整数部分和小数部分
        else:
            split_result = new_num.split(".")
            len_split_result = len(split_result)
            if len_split_result == 1:
                # 不包含小数的输入
                if ("%" in new_num):
                    integer_data = split_result[0].replace("%","")
                    output = integer_convert(integer_data, big_or_small=big_or_small) + " percent "
                else:
                    integer_data = split_result[0]
                    output = integer_convert(integer_data, big_or_small=big_or_small)
            elif len_split_result == 2:
                # 包含小数的输入
                if ("%" in new_num):
                    integer_data = split_result[0]
                    decimal_data = split_result[1].replace("%","")
                    output = integer_convert(
                        integer_data, big_or_small=big_or_small) + " point " + decimal_convert(decimal_data, big_or_small="big") + "percent"
                else:
                    integer_data = split_result[0]
                    decimal_data = split_result[1]
                    output = integer_convert(
                        integer_data, big_or_small=big_or_small) + " point " +  decimal_convert(decimal_data, big_or_small="big")

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
    
    # 20,30,40...
    tens_list = ["zero","ten","twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"]
    tens_ord = ["zeroth","tenth","twentieth","thirtieth","fortieth","fiftieth","sixtieth","seventieth","eightieth","ninetieth"]
    
    # 10~19
    ten_to_TWENTY = ["ten","eleven","twelve","thirteen","fourteen","fifteen","sixteen","seventeen","eighteen","nineteen"]
    #10th~19th
    ten_to_TWENTY_ord = ["tenth","eleventh","twelveth","thirteenth","fourteenth","fifteenth","sixteenth","seventeenth","eighteenth","nineteenth"]
    numeral_list = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    unit_list = ["", "ty", "hundred", "thousand", "ty", "hundred", "million", "million", "hundred million",
                "billion", "billion", "hundred billion", "trillion", "trillion", "hundred trillion"]
    
    # use for ordinal nums (21st century) or date (July 7th)
    numeral_order_list = ["zeroth", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eightth", "ninth"]
    unit_order_list = ["", "tieth", "hundredth", "thousandth", "thousandth", "hundred thousand", "millionth", "millionth", "hundred millionth",
                        "billionth", "billionth", "hundred billionth", "trillionth", "trillionth", "hundred trillionth"]
    month_list = ["January","Febuary","March","April","May","June","July","August","September","October","November","December"]
    
    # holdover from Tailuo number normalization
    if big_or_small == "big":
        numeral_list = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
        unit_list = ["", "ty", "hundred", "thousand", "ty", "hundred", "million", "million", "hundred million",
                     "billion", "billion", "hundred billion", "trillion", "trillion", "hundred trillion"]
    elif big_or_small == "small":
        numeral_list = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
        unit_list = ["", "ty", "hundred", "thousand", "ty", "hundred", "million", "million", "hundred million",
                     "billion", "billion", "hundred billion", "trillion", "trillion", "hundred trillion"]
    
    
    elif big_or_small == "ordinal":
        numeral_list = ["zeroth", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eightth", "ninth"]
        unit_list = ["", "tieth", "hundredth", "thousandth", "thousandth", "hundred thousand", "millionth", "millionth", "hundred millionth",
                     "billionth", "billionth", "hundred billionth", "trillionth", "trillionth", "hundred trillionth"]
    # for month in date (7/7, 12/25)
    elif big_or_small == "month" :
        numeral_list = ["January","Febuary","March","April","May","June","July","August","September","October","November","December"]
        output_an = ""
        integer_data = int(integer_data)
        output_an += numeral_list[integer_data]
        output_an += " "
        return output_an
    else:
        raise ValueError("big_or_small參數只有有<big>,<small>,<ordinal>和<month>四個選項。")

    if big_or_small == "ordinal":
        temp = integer_data[-2] + integer_data[-1]
        integer_data = integer_data[:-2]
    
    # 去除前面的 0，比如 007 => 7
    integer_data = str(int(integer_data))

    len_integer_data = len(integer_data)
    if len_integer_data > len(unit_list):
        raise ValueError(f"超出数据范围，最长支持 {len(unit_list)} 位")

    output_an = ""
    need_and = 0
    for i,d in enumerate(integer_data):
        # from back to front (for getting numeral unit) 
        # 21343: 2萬-->1千-->3百-->4十-->3
        f_index = len_integer_data - i-1 
        num_index = i # from front to back (for getting number)
        #num_index = num_index - 1 #into list
        current_num = int(integer_data[num_index]) #current number
        
        #print("number: ",str(current_num)," at position ",str(num_index))
        #print("search unit in ",str(f_index))
        numbers_left = len_integer_data-num_index
        # check if we reached the end (where there are only zeros left)
        if i != len_integer_data-1:
            #all_zero = 0
            zeros = 0
            for a in range(num_index,len_integer_data):
                temp0 = int(integer_data[a]) 
                if temp0==0:
                    zeros += 1            
        else:
            zeros = 0
            
        
        # new unit numeral every three numbers
        #print(integer_data[num_index])
        
        if f_index % 3 == 0: # one thousand(<1>000), two million(<2>000000)
            try:
                temp = int (integer_data[num_index-1] + integer_data[num_index])
            except IndexError:
                temp = int (integer_data[num_index])
            if not (10<=temp<=19):
                output_an += numeral_list[current_num] + " " 
            if big_or_small=='ordinal':
                
                if numbers_left==zeros: # reached end of number, ignore rest of zeros
                    output_an += unit_order_list[f_index]
                else:
                    output_an += unit_list[f_index]
            else:
                output_an += unit_list[f_index]
        
        elif f_index % 3 == 1: # twenty one million(2<1>000000), forty two thousand (4<2>000)
            try:
                temp = int (integer_data[num_index] + integer_data[num_index+1])
            except IndexError:
                temp = int (integer_data[num_index])
            if 10 <= temp <= 19:
                if big_or_small!="ordinal":
                    if output_an!="" and output_an!=" ":
                        output_an += "and "
                    output_an += ten_to_TWENTY[temp-10]
                    output_an += " "
                else:
                    if output_an!="" and output_an!=" ":
                        output_an += "and "
                    output_an += ten_to_TWENTY_ord[temp-10]
                    output_an += " "
                if f_index==1:
                    break
            else: #two hundred and twenty one (<2>21), <4>01<0>00
                if output_an!="" and output_an!=" ":
                    output_an += "and "
                if big_or_small=='ordinal':
                
                    if numbers_left==zeros: # reached end of number, ignore rest of zeros
                        output_an += tens_ord[current_num]
                    else:
                        output_an += tens_list[current_num]
                else:
                    output_an += tens_list[current_num]
                #output_an += tens_list[current_num]
                output_an += " "
                if numbers_left==zeros: # reached end of number, ignore rest of zeros
                    break

        else: # three hundred million
            if current_num!=0:
                output_an += numeral_list[current_num] + " " + \
                    unit_list[f_index]
            else:
                if numbers_left==zeros: # reached end of number, ignore rest of zeros
                    break
                if f_index==2:
                    print("nearing end")
        output_an += " "
    if output_an[-3:-2]=="onety":
        output_an = output_an.replace("onety", "ten").replace(
        "twoty", "twenty").replace("threety", "thirty").replace("fourty", "forty")\
        .replace("fivety","fifty").replace("zero","")   #.strip("zero")
    else:
        output_an = output_an.replace("onety", "ten").replace(
        "twoty", "twenty").replace("threety", "thirty").replace("fourty", "forty")\
        .replace("fivety","fifty").replace("zero","")
        if big_or_small == "ordinal":
            try:
                output_an = output_an.replace("onetieth", "tenth").replace(
                "second tieth", "twentieth").replace("third tieth", "thirtieth").replace("fourth tieth", "fortieth")\
                .replace("fifth tieth","fiftieth").replace("zero","")
            except:
                print("output has no oridinal to fix")
        

   

    # 0 - 1 之间的小数
    if not output_an:
        output_an = "zero"

    return output_an


def decimal_convert(decimal_data, big_or_small="big"):
    len_decimal_data = len(decimal_data)

    if len_decimal_data > 15:
        #logger.warning(f"warning: 小数部分长度为{len_decimal_data}，超过15位有效精度长度，将自动截取前15位！", extra={"ipaddr":""})
        decimal_data = decimal_data[:15]
    """
    if len_decimal_data:
        output_an = ""
    else:
        output_an = ""
    """
    output_an = ""
    
    if big_or_small == "big":
        # numeral_list = ["零", "壹", "貳", "叁", "肆", "伍", "陸", "柒", "捌", "玖"]
        numeral_list = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    elif big_or_small == "small":
        # numeral_list = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
        numeral_list = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    elif big_or_small == "ordinal":
        numeral_list = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    else:
        raise ValueError("big_or_small參數只有有<big>和<small>兩個選項。")

    for data in decimal_data:
        output_an += numeral_list[int(data)]
        output_an += " "
    return output_an


def one_one(data, big_or_small="big"):
    len_data = len(data)

    if len_data > 15:
        #logger.warning(f"warning: 小数部分长度为{len_data}，超过15位有效精度长度，将自动截取前15位！", extra={"ipaddr":""})
        data = data[:15]

    output_an = ""

    if big_or_small == "big":
        # numeral_list = ["零", "壹", "貳", "叁", "肆", "伍", "陸", "柒", "捌", "玖"]
        numeral_list = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    elif big_or_small == "small":
        # numeral_list = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
        numeral_list = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    elif big_or_small == "ordinal":
        numeral_list = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    else:
        raise ValueError("big_or_small參數只有有<big>和<small>兩個選項。")

    for _data in data:
        try:
            output_an += numeral_list[int(_data)]
            output_an += " "
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
        numeral_list = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    elif big_or_small == "small":
        numeral_list = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    elif big_or_small == "ordinal":
        numeral_list = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    else:
        raise ValueError("big_or_small參數只有有<big>和<small>兩個選項。")

    for _data in data:
        try:
            output_an += numeral_list[int(_data)]
            output_an += " "
        except:
            output_an += _data
            output_an += " "
    return output_an

if __name__ == "__main__":
    data = '''
    '''
    
    data = 3540469098308190422848908402948
    
    while(1):
        data = input("input:")
        print('result:',transform_num2en(data))
        print('-------------------')
    # print((("-" * 150) + "\n") * 5)
    # print(transform_num2en(data, mode="all"))
    # print((("-" * 150) + "\n") * 5)
    # print(transform_num2en(data, mode="one_one"))
