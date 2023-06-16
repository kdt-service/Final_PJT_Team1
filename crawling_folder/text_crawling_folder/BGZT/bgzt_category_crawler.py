import json
import requests
import pandas as pd
import numpy as np
import gc

def crawl_category_nums():
    """
    category dictionary function 
    카테고리 번호만으로 json 파일 만들기 
    번호만 있었을 때 나중에 상세정보 크롤링을 할 때 편리할 것으로 예상됨. 
    
    만약 번호말고 다른 정보도 필요하다면 코드를 수정하여 
    카테고리 이름도 가져올 수 있음. 
    """
    
    base_url = 'https://api.bunjang.co.kr/api/1/categories/list.json' # 비동기 방식으로 크롤링할 때 쓰일 base url
    headers = { 
    'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }
    res = requests.get(base_url, headers = headers)
    data = res.json()
    
    cat_1, cat_2, cat_3 = None, None, None # 변수 초기화
    cat_dict = {} # 최종적으로 넣어줄 category dictionary 
    
    for cats1 in data['categories']:
        cat_1 = cats1['id'] # 가장 상위 카테고리 cat_1
        try: # '기타' 카테고리 이후로는 'categories'가 없음.  
            tmp_dict = {} # 임시적으로 담아줄 dictionary
            for cats2 in cats1['categories']: 
                cat_2 = cats2['id'] # 다음 카테고리인 cat_2
                tmp_dict[cat_2] = [] # cat_2 이름별로 따로 빈 리스트 만들어주기 
                try: # cat_1, cat_2 다음 cat_3가 없는 경우가 있음. 
                    for cats3 in cats2['categories']: # 다음 세부 항목 (cat_3)는 'categories' 안에 들어있음. 
                        cat_3 = cats3['id'] 
                        tmp_dict[cat_2].append(cat_3) # 아까 만들어 주었던 빈 리스트에 cat_3 항목들 넣어주기 
                    cat_dict[cat_1] = tmp_dict
                except:
                    cat_3 = None # cat_3가 없는 경우 None으로 채워주기
                    tmp_dict[cat_2].append(cat_3)
                cat_dict[cat_1] = tmp_dict

        except: # '기타' 카테고리에 걸칠 경우 break
            break 
            
    json_data = json.dumps(cat_dict, indent=4)  
    with open('bungae_unique_category_numbers.json', 'w') as f: # json 파일로 내보내기 
        f.write(json_data)
        
    gc.collect() 
        
    return

if __name__ == '__main__':
    crawl_category_nums()