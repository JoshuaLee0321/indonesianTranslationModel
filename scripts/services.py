from scripts import translate
import logging
logging.basicConfig(
    level=logging.DEBUG
)
def translation(args, pipe):
    '''
        input : args {model}
        output: str(translated text) , None
    '''    
    if args['model'] == 'en2zh':
        with open('./translation_file/logfile/log_en2zh.txt', 'a', encoding='utf-8') as log:
            log.write(args['translation_text'] + '\n')
        text = args['translation_text']
        text = translate.translate_en2zh(text)
        logging.info('en2zh, %s', text)

    # elif args['model'] == 'zh2id_1002':
    #     text = args['translation_text']
    #     text = translate.translate_zh2id_1002(text, pipe)
    #     logging.info('zh2id_1002, %s', text)
    
    # elif args['model'] == 'id2zh_1002':
    #     text = args['translation_text']
    #     text = translate.translate_id2zh_1002(text, pipe)
    #     logging.info('id2zh_1002, %s', text)   
        
    elif args['model'] == 'zh2id_1013':
        text = args['translation_text']
        text = translate.translate_zh2id_1013(text, pipe)
        logging.info('zh2id_1013, %s', text)
    
    elif args['model'] == 'id2zh_1013':
        text = args['translation_text']
        text = translate.translate_id2zh_1013(text, pipe)
        logging.info('id2zh_1013, %s', text)   

    elif args['model'] == "id2zh_raw":
        text = args['translation_text']
        text = translate.translate_id2zh_raw(text, pipe)
        logging.info('id2zh_raw, %s', text)   
    # # add elif ...
    

    else:
        return None
    return text
    