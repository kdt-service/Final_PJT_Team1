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

def read_cat_list():

    with open('/home/ubuntu/workspace/CRAWL/cat/cat_list', 'r') as f:
        data = f.readlines()

    cat_list = []
    for i in data:
        a = list(map(lambda s: s.strip(), i.split(', ')))
        cat_list += a
    
    return cat_list

def prd_id_extractor(category_num):
    """
    category id를 사용하여 상품 고유 번호를 뽑아오는 크롤러 입니다. 
    """

    prd_id_list = []

    ua = UserAgent(verify_ssl=False)
    fake_ua = ua.random
    headers = { 'user-agent' : fake_ua }

    url = "https://api.bunjang.co.kr/api/1/find_v2.json?"
    for n in range(2):
        params = {
            'f_category_id' : category_num, 
            'page' : str(n), 
            'order': 'date', # 최신순
            "n" : '100',
            }
        
        res = requests.get(url, headers = headers, params=params)
        data = res.json()
        
        prd_id_list.extend([datas['pid'] for datas in data['list']])


    # print('category num %s done'%(category_num))
    time.sleep(1.25) 
    
    return prd_id_list


def category_mp(cat_list: list):
    """
    첫번째 pool 함수
    카테고리 리스트를 받아서 전체 상품 번호 리스트를 반환하는 함수입니다. 
    """
    pool = multiprocessing.Pool(4) # 사용 가능한 cpu 확인
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
    
    cat_list = read_cat_list() 
    prd_list = category_mp(cat_list) 
   
    with open('/home/ubuntu/workspace/CRAWL/cat/prd_list', 'w') as file:
        for item in prd_list:
            file.write(str(item) + '\n')

    end = time.time()
    print('수행시간', end-start)

    
    
    
    
    
    
    
    
    
    