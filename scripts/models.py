from fairseq.models.transformer import TransformerModel

from opencc import OpenCC
import logging

############# Models put right here #################
logging.basicConfig(
    level=logging.DEBUG
)
# simplified to Traditional
# use cc.convert(text)
s2t = OpenCC('s2t')
t2s = OpenCC('t2s')
# Language Model #
############## LM = lm_score.LM() ############
logging.info("start loading model and dictionary")
# Search dictionary


############## fairseq model #################

# model_zh2id_1002 = TransformerModel.from_pretrained(
#     './translation_file/zh2id_1002',
#     checkpoint_file='checkpoint_best.pt',
# )
# model_id2zh_1002 = TransformerModel.from_pretrained(
#     './translation_file/id2zh_1002',
#     checkpoint_file='checkpoint_best.pt',
# )

model_zh2id_1013 = TransformerModel.from_pretrained(
    './translation_file/zh2id_1013',
    checkpoint_file='checkpoint_best.pt',
    device_map='cuda'
)
model_id2zh_1013 = TransformerModel.from_pretrained(
    './translation_file/id2zh_1013',
    checkpoint_file='checkpoint_best.pt',
    device_map='cuda'
)

## logging
logging.info("loading models complete")