# 생각해보니 카테고리 번호를 통해 카테고리 이름을 알고 싶은 경우가
# 무조건 생길 것으로 예상됨
# 그래서 카테고리 번호를 넣으면 카테고리 이름을 알려주는 크롤러 혹은 함수를 만들고자 함. 
# 나중에 이전 함수와 같이 활용되어 카테고리 분류에 사용될 것으로 예상됨. 

import json
import requests
import pandas as pd
import numpy as np
from collections import Counter
from fake_useragent import UserAgent

def mapping_category_titles_and_nums() -> None:
    """
    카테고리 번호를 통해 카테고리 이름을 알 수 있도록 해주는 함수. 
    
    해당 함수는 단순히 카테고리 번호에 따라 카테고리 이름이 무엇인지 매핑하여
    json파일로 내보내는 함수입니다. 
    """
    
    base_url = 'https://api.bunjang.co.kr/api/1/categories/list.json' # 비동기 방식으로 크롤링할 때 쓰일 base url
    
    ua = UserAgent(verify_ssl=False)
    fake_ua = ua.random
    headers = { 'user-agent' : fake_ua }
    
    res = requests.get(base_url, headers = headers)
    data = res.json()
    
    cat_1, cat_2, cat_3 = None, None, None # 변수 초기화
    title_1, title_2, title_3 = None, None, None
    cat_1_dict, cat_2_dict, cat_3_dict = {}, {}, {} # 카테고리 hierachy 대로 따로 ditionary 생성
        
    for cats1 in data['categories']:
        cat_1 = cats1['id'] # 가장 상위 카테고리 cat_1
        title_1 = cats1['title'] # 가장 상위 카테고리 이름
        cat_1_dict[cat_1] = title_1 # cat_1_dict에 넣어주기 
        try: # '기타' 카테고리 이후로는 'categories'가 없음.  
            for cats2 in cats1['categories']: 
                cat_2 = cats2['id'] # 다음 카테고리인 cat_2
                title_2 = cats2['title'] # 다음 카테고리 이름
                cat_2_dict[cat_2] = title_2 # cat_2_dict에 넣어주기 
                try: # cat_1, cat_2 다음 cat_3가 없는 경우가 있음. 
                    for cats3 in cats2['categories']: # 다음 세부 항목 (cat_3)는 'categories' 안에 들어있음. 
                        cat_3 = cats3['id'] # 다음 카테고리인 cat_3
                        title_3 = cats3['title'] # 카테고리명
                        cat_3_dict[cat_3] = title_3 # cat_3_dict에 넣어주기 
                except: # cat_3가 없는 경우
                    continue 

        except: # '기타' 카테고리에 걸칠 경우 break
            break 
        
        final_dict = dict(cat_1_dict, **cat_2_dict, **cat_3_dict)
        json_data = json.dumps(final_dict, indent=4)  
        with open('bungae_mapping_category_nums_and_titles.json', 'w') as f: # json 파일로 내보내기 
            f.write(json_data)
        
    return 

if __name__ == '__main__':
    mapping_category_titles_and_nums()