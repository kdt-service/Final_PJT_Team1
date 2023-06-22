import pandas as pd
import torch
from transformers import ElectraForSequenceClassification, AutoTokenizer, AdamW, ElectraTokenizer
from transformers import get_linear_schedule_with_warmup
from tqdm.notebook import tqdm
from keras_preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
import random
import numpy as np

# GPU 활성화 코드
if torch.cuda.is_available():
    device = torch.device("cuda")
    print('There are %d GPU(s) available.' % torch.cuda.device_count()) # 있는지 없는지
    print('We will use the GPU:', torch.cuda.get_device_name(0))
else:
    device = torch.device("cpu")
    print('No GPU available, using the CPU instead.')

# 모델 다운로드
PATH = '/home/ubuntu/workspace/API/MODEL/model'
model = torch.load(PATH + '/koelectra_base_model.pt')  # 모델 불러오기
model.load_state_dict(torch.load(f'{PATH}/koelectra_base_model_state_dict.pt'))

# input 변환 함수
def convert_input(sentences):
    tokenizer = ElectraTokenizer.from_pretrained("monologg/koelectra-base-v3-discriminator")
    tokenized_texts = [tokenizer.tokenize(sent) for sent in sentences]
    max_len = 200
    input_ids = [tokenizer.convert_tokens_to_ids(text) for text in tokenized_texts]
    input_ids = pad_sequences(input_ids, maxlen=max_len, dtype="long", truncating="post", padding="post")
    attention_masks = []
    for seq in input_ids:
        seq_mask = [float(i>0) for i in seq]
        attention_masks.append(seq_mask)
    return input_ids, attention_masks

# 3개 레이블 예측해주는 함수.
def test_sentences(sentences):
    model.eval()
    # 문장을 입력 데이터로 변환
    input_ids, attention_masks = convert_input(sentences)
    # 데이터를 파이토치의 텐서로 변환
    inputs = torch.tensor(input_ids)
    masks = torch.tensor(attention_masks)
    # 데이터를 GPU에 넣음
    b_input_ids = inputs.to(device)
    b_input_mask = masks.to(device)
    # 그래디언트 계산 안함
    with torch.no_grad():
        outputs = model(input_ids=b_input_ids, token_type_ids=None,
                            attention_mask=b_input_mask)
    logits = outputs.logits
    logits = logits.detach().cpu().numpy()

    predictions = np.argsort(logits, axis=1)[:, -3:]  # Get indices of top 3 labels

    return predictions