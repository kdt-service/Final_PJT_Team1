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

        ua = UserAgent(verify_ssl=False)
        fake_ua = ua.random
        headers = { 'user-agent' : fake_ua }
    
        url = "https://api.bunjang.co.kr/api/1/find_v2.json?"
        params = {
            'f_category_id' : category_num, 
            'page' : str(page_num), 
            'order': 'date', # 최신순
            'req_ref': 'category', 
            'request_id': '2023517001018', 
            'stat_device': "w",
            "n" : '100',
            'version' : '4'
            }
        res = requests.get(url, headers = headers, params=params)
        data = res.json()
        
        prd_id_list = [datas['pid'] for datas in data['list']] # product id 리스트로 만들어주기 

        if page_num == 4: # 페이지 4개씩 ==> 대략 400개 상품 
            break
            
        if data['no_result']: # page수가 지정한 페이지 수보다 적을 경우 break
            break
            
        page_num += 1
        
    print('category num %s done'%(category_num))
    time.sleep(0.03) 
    
    return prd_id_list


def category_mp(cat_list: list):
    """
    첫번째 pool 함수
    카테고리 리스트를 받아서 전체 상품 번호 리스트를 반환하는 함수입니다. 
    """
    pool = multiprocessing.Pool(32) # 사용 가능한 cpu 확인
    result = pool.map(prd_id_extractor, cat_list) # 카테고리 리스트에 따른 모든 상품 번호 가져오도록 Pool
    
    prd_list = list()
    for r in result:
        prd_list += r
        
    pool.close()
    pool.join()
    
    gc.collect()
    return prd_list # 모든 상품 id가 들어있는 리스트 

if __name__ == '__main__':
    start = time.time()
    
    cat_list = extract_usable_cat_id_only() # url과 같이 사용이 가능한 카테고리 리스트
    prd_list = category_mp(cat_list) # Pool 사용하여 카테고리에 따라 모든 상품 id 가져오기 
   
    with open('BGZT_product_id_list.txt', 'w+') as file:
        file.write(','.join(prd_list))
    
    end = time.time()
    print('수행시간', end-start)

    
    
    
    
    
    
    
    
    
    