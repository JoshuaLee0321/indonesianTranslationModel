from transformers import BertTokenizerFast, AutoModelForMaskedLM, AutoModelForCausalLM

import torch
class LM:
    def __init__(self) -> None:
        # masked language model (ALBERT, BERT)
        # tokenizer = BertTokenizerFast.from_pretrained('bert-base-chinese')
        # model = AutoModelForMaskedLM.from_pretrained('ckiplab/albert-tiny-chinese') # or other models above

        # casual language model (GPT2)
        self.tokenizer = BertTokenizerFast.from_pretrained('bert-base-chinese')
        self.model = AutoModelForCausalLM.from_pretrained('ckiplab/gpt2-base-chinese') # or other models above

    def score(self, sentence):
        input_ids = self.tokenizer.encode(sentence, return_tensors='pt')
        with torch.no_grad():
            outputs = self.model(input_ids)
            logits = outputs[0]

        log_prob = torch.nn.functional.log_softmax(logits, dim=-1)
        log_prob_sentence = 0.0

        for i in range(input_ids.size(1)-1):
            log_prob_sentence += log_prob[0, i, input_ids[0, i+1]]

        # print(f'語言模型分數: {log_prob_sentence.item()}') 
        return log_prob_sentence.item()