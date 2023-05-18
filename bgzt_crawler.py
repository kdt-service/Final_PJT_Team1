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
from fake_useragent import UserAgent

def prd_crawler(prd_id): 
    """
    상품 번호에 따라 상품 정보를 가져오는 크롤러입니다. 
    """

    ua = UserAgent(verify_ssl=False) # user-agent
    fake_ua = ua.random
    headers = { 'user-agent' : fake_ua }
    
    url = 'https://api.bunjang.co.kr/api/pms/v1/products-detail/{}?viewerUid=-1'.format(prd_id)
    res = requests.get(url, headers = headers)

    print('product id -->', prd_id)
    print('response status --> ', res)

    if res.status_code == 200:
        data = res.json()
        try:
            prd_id
            product_name = data['data']['product']['name']
            image_url = data['data']['product']['imageUrl']
            image_cnt = data['data']['product']['imageCount']
            price = data['data']['product']['price']
            info = data['data']['product']['description']
            date = data['data']['product']['updatedAt']
            cat_id = data['data']['product']['category']['id']
            keywords = ",".join(data['data']['product']['keywords'])

        except:
            product_name, image_url, image_cnt, price, info, cat_id, date, keywords =\
                None, None, None, None, None, None, None, None
    
        return [prd_id, product_name, image_url, image_cnt, price, info, cat_id, date, keywords] # 리스트로 반환
    else:
        return [prd_id, None, None, None, None, None, None, None]
    

def product_mp(prd_list:list):
    
    pool = multiprocessing.Pool(os.cpu_count()) # cpu 확인
    product_info_list = pool.map(prd_crawler, prd_list) # 카테고리 리스트에 따른 모든 상품 번호 가져오도록 Pool
    
    pool.close()
    pool.join()
    
    gc.collect()
    
    prd_df = pd.DataFrame(product_info_list, columns = ['product_id', 'product_name', 'image_url', 'image_cnt', 'price', 'info', 'cat_id', 'date', 'keywords'])
    prd_df = prd_df.dropna()
    
    return prd_df # 모든 상품 id가 들어있는 리스트 

if __name__ == '__main__':
    
    start = time.time()
    
    with open('BGZT_product_id_list.txt', 'r') as f:
        data = f.read()
    prd_id_list = data.split(',') # 상품 list

    for idx in range(9): # 분할해서 데이터 프레임으로 만들기 
        result = product_mp(prd_id_list[idx::9])
        result.to_csv(f'bungae_df_{idx}_v2.csv', index=False)
        print('{} dataframe created'.format(idx))
        time.sleep(30)
        
    #### 필요한 후속처리 ####
    # cat_id --> cat_1, cat_2, cat_3로 나눌 것인지?
    # imageUrl + imageCount 해서 image_list로 다시 만들 것인지?
    
    end = time.time()
    print('수행시간', end-start)

    gc.collect()
    
    
    
    
    
    
    
    
    
    