import re
import pandas as pd
from datetime import datetime

# 특수기호 제거 함수
def remove_pmarks(text):
    ''' 특수기호 및 괄호 제거 \n
    '''
    cleaned_text = re.sub(r"[\!\@\#\$\%\^\&\*\.\,\~]", "", text) # 특수기호 제거
    cleaned_text = re.sub(r"[\[\]\(\)]", "", cleaned_text)  # (),[] 제거
    return cleaned_text

# 이모티콘 제거 함수
def remove_emojis(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # 이모티콘1 (일반)
                               u"\U0001F300-\U0001F5FF"  # 이모티콘2 (시계, 날씨 등)
                               u"\U0001F680-\U0001F6FF"  # 이모티콘3 (차, 비행기 등)
                               u"\U0001F1E0-\U0001F1FF"  # 이모티콘4 (국기 등)
                               u"\U00002600-\U000027BF"  # 이모티콘5 (기타)
                               u"\U0001F900-\U0001F9FF"  # 이모티콘6 (심볼, 표시 등)
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def to_datetime(date_string):
    try:
        datetime_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        datetime_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    return datetime_obj

# 번개장터 클렌징 함수
def cleanse_bj(df:pd.DataFrame):
    '''번개장터 클렌징 함수 \n
    
    '''
    # 칼럼별 클렌징 함수 적용
    df['prd_name'] = df['prd_name'].apply(remove_pmarks) 
    df['info'] = df['info'].apply(lambda x: remove_emojis(remove_pmarks(x)))
    df['info'] = df['info'].apply(lambda x: re.sub(r'(\n+|\t+|\.+)', ' ', x))
    df['info'] = df['info'].apply(lambda x: re.sub(r' +', ' ', x))
    
    return df

# 네이버 클렌징 함수
def cleanse_naver(df:pd.DataFrame):
    '''네이버 클렌징 함수 \n
    '''
    # 칼럼별 클렌징 함수 적용
    df['name'] = df['name'].apply(remove_pmarks)

    return df

def bj_url_list(df:pd.DataFrame):
    '''base_url -> list로 변환
    '''
    list1 = df[['base_url','image_count']].values.tolist()
    result = []
    for l in range(len(list1)):
        result.append(str([list1[l][0].replace('{cnt}', str(n)) for n in range(1, int(list1[l][1]+1))]))

    df['image_url_list'] = result

    return df
    
