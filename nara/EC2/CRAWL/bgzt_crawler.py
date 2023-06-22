from bs4 import BeautifulSoup as bs
import requests
from fake_useragent import UserAgent
from multiprocessing import Pool
import multiprocessing
import time
import gc
import json
import pandas as pd

def read_to_list(file_path):

    with open(file_path, 'r') as f:
        data = f.readlines()

    id_list = []
    for i in data:
        a = list(map(lambda s: s.strip(), i.split(', ')))
        id_list += a
    
    return id_list

def product_info_crawler(pid):
    """ 
    제품 상세 정보를 가져오는 함수 
    """
    ua = UserAgent(verify_ssl=False)
    fake_ua = ua.random
    headers = {
        'user-agent' : fake_ua
    }

    url = 'https://api.bunjang.co.kr/api/pms/v1/products-detail/{}?viewerUid=-1'.format(pid)
    res = requests.get(url, headers = headers)
    # print('id -->', pid)
    # print('response -->', res)

    if (res.status_code == 200) and (res.headers["content-type"].strip().startswith("application/json")):
        product_info = res.json()

        try :
            product_name = product_info['data']['product']['name'] # 제품명
            image_url = product_info['data']['product']['imageUrl'] # 이미지url
            image_cnt = product_info['data']['product']['imageCount']
            price = product_info['data']['product']['price'] # 가격
            info = product_info['data']['product']['description'].replace('\n', ' ').strip() # 제품설명
            cat_id = product_info['data']['product']['category']['id'] # 카테고리 id
            date = product_info['data']['product']['updatedAt'] # '2023-05-16T16:18:23.422Z'
            keywords = ",".join(product_info['data']['product']['keywords'])

        except KeyError:
            product_name, image_url, image_cnt, price, info, cat_id, date, keywords =\
                None, None, None, None, None, None, None, None
            

        return [pid ,product_name, image_url, image_cnt, price, info, cat_id, date, keywords]
    
    else:
        return [pid, None, None, None, None, None, None, None, None]


def product_mp(product_list : list) -> pd.DataFrame :
    """ 
    제품 상세 정보 리스트를 가져와 데이터프레임을 반환하는 함수
    """
    pool = multiprocessing.Pool(processes=8) # cpu 확인
    product_info_list = pool.map(product_info_crawler, product_list) # 카테고리 리스트에 따른 모든 상품 번호 가져오도록 Pool
    
    pool.close()
    pool.join()
    
    gc.collect()
    
    prd_df = pd.DataFrame(product_info_list, columns = ['product_id', 'product_name', 'image_url', 'image_cnt', 'price', 'info', 'cat_id', 'date', 'keywords'])
    
    return prd_df


if __name__ == '__main__':
    import csv

    start = time.time()
    
    prd_id_list = read_to_list('/home/ubuntu/workspace/CRAWL/cat/prd_list')

    result = product_mp(prd_id_list)
    result.to_csv('/home/ubuntu/workspace/CRAWL/data/BGZT.csv', index=False, quoting=csv.QUOTE_ALL, escapechar='\\')
    
    end = time.time()
    print('수행시간', end-start)

