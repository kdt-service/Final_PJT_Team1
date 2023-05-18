import json
import requests
import pandas as pd
import numpy as np
from multiprocessing import Pool
import multiprocessing
import time
import gc
import os
import random


############### 첫번째 pool ########################################################

def extract_usable_cat_id_only():
    # 이전에 만들었던 json 파일에서 정보 가져오기
    with open('./bungae_unique_category_numbers.json', 'r') as file: 
        data = json.load(file)
    
    # 최상단 목록을 뺀 나머지 cat_2, cat_3 카테고리 번호들 가져오기 
    new_dict = dict()
    for i in list(data.values()):
        new_dict.update(i)
        
    # 3번째 하위 카테고리 목록이 없는 경우도 있는데
    # 그럴때는 2번째 하위 항목의 카테고리 번호로 크롤링을 해야함. 
    # 때문에 크롤링할 때 필요한 None 값이 아닌 카테고리 번호들만 따로 리스트로 만들기
    usable_cat_list = list()
    for x in new_dict.keys():
        if new_dict[x][0] == None:
            usable_cat_list.append(x)
        else:
            usable_cat_list.extend(new_dict[x])
            
    return usable_cat_list

def prd_id_extractor(category_num):
    """
    category id를 사용하여 상품 고유 번호를 뽑아오는 크롤러 입니다. 
    """
    page_num = 0
    while True: 
        url = "https://api.bunjang.co.kr/api/1/find_v2.json?"
        params = {
            'f_category_id' : category_num, # 바뀔 부분 1
            'page' : str(page_num), # 바뀔 부분 2 
            'order': 'date', # 최신순? 
            'req_ref': 'category', 
            'request_id': '2023517001018', # 이 부분 어떻게 해결? 
            'stat_device': "w",
            "n" : '100',
            'version' : '4'
        }
        headers = {
            'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }
        res = requests.get(url, headers = headers, params=params)
        data = res.json()

        prd_id_list = [datas['pid'] for datas in data['list']] # product id 리스트로 만들어주기 

        if page_num == 4: # 우선 page수를 4까지 지정 ==> 대략 400개 
            break
            
        if data['no_result']: # page수가 지정한 페이지 수보다 적을 경우 break
            break
            
        page_num += 1
        
    print('category num %s done'%(category_num))
    time.sleep(0.03) 
    
    return prd_id_list


def prd_mp_1(cat_list:list):
    """
    첫번째 pool 함수
    카테고리 리스트를 받아서 전체 상품 번호 리스트를 반환하는 함수입니다. 
    """
    pool = multiprocessing.Pool(os.cpu_count()) # 사용 가능한 cpu 확인
    result = pool.map(prd_id_extractor, cat_list) # 카테고리 리스트에 따른 모든 상품 번호 가져오도록 Pool
    
    prd_list = list()
    for r in result:
        prd_list += r
        
    pool.close()
    pool.join()
    
    gc.collect()
    return prd_list # 모든 상품 id가 들어있는 리스트 

############### 두번째 pool ########################################################
def prd_crawler(prd_id): 
    """
    상품 번호에 따라 상품 정보를 가져오는 크롤러입니다. 
    """
    url = 'https://api.bunjang.co.kr/api/pms/v1/products-detail/{}?viewerUid=-1'.format(prd_id)
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
    }
    res = requests.get(url, headers = headers)
    data = res.json()
    
    try:
        product_id = data['data']['product']['pid']
        product_name = data['data']['product']['name']
        image_url = data['data']['product']['imageUrl']
        image_cnt = data['data']['product']['imageCount']
        price = data['data']['product']['price']
        info = data['data']['product']['description']
        date = data['data']['product']['updatedAt']
        cat_id = data['data']['product']['category']['id']
        keywords = ",".join(data['data']['product']['keywords'])

    except:
        product_id, product_name, image_url, image_cnt, price, info, cat_id, date, keywords =\
            None, None, None, None, None, None, None, None, None
        
    print('product id %s done'%(product_id))
    time.sleep(1) # block을 당할 가능성을 줄이기 위해 time.sleep 조금 길게 둠. 
    
    return [product_id, product_name, image_url, image_cnt, price, info, cat_id, date, keywords] # 리스트로 반환

def prd_mp_2(prd_list:list):
    """
    두번째 pool 함수
    """
    pool = multiprocessing.Pool(os.cpu_count()) # 사용 가능한 cpu 확인
    product_info_list = pool.map(prd_crawler, prd_list) # 카테고리 리스트에 따른 모든 상품 번호 가져오도록 Pool
                                                # --> 바로 리스트로 나옴
    pool.close()
    pool.join()
    
    gc.collect()
    
    prd_df = pd.DataFrame(product_info_list, columns = ['product_id', 'product_name', 'image_url', 'image_cnt', 'price', 'info', 'cat_id', 'date', 'keywords'])
    prd_df = prd_df.dropna()
    
    return prd_df # 모든 상품 id가 들어있는 리스트 

if __name__ == '__main__':
    start = time.time()
    cat_list = extract_usable_cat_id_only() # url과 같이 사용이 가능한 카테고리 리스트
    prd_list = prd_mp_1(cat_list) # Pool 사용하여 카테고리에 따라 모든 상품 id 가져오기 

    for idx in range(9): # 분할해서 데이터 프레임으로 만들기 
        try:
            result = prd_mp_2(prd_list[idx::9])
            result.to_csv(f'bungae_df_{idx}.csv', index=False)
            print('{} dataframe created'.format(idx))
            time.sleep(6)
        except:
            pass
        
    #### 필요한 후속처리 ####
    # cat_id --> cat_1, cat_2, cat_3로 나눌 것인지?
    # imageUrl + imageCount 해서 image_list로 다시 만들 것인지?
    
    end = time.time()
    print('수행시간', end-start)

    gc.collect()
    
    
    
    
    
    
    
    
    
    