import json
import requests
import pandas as pd
import numpy as np
from multiprocessing import Pool
import multiprocessing
import time
import gc
from fake_useragent import UserAgent

def extract_usable_cat_id_only() -> list:
    """ 
    category id json파일을 불러와 중분류, 소분류 category id를 추출하는 함수입니다.
    """
    with open('data/bungae_unique_category_numbers.json', 'r') as file: 
        data = json.load(file)
    
    new_dict = {}
    for value in data.values():
        new_dict.update(value)

    usable_cat_id = []
    for key, value in new_dict.items():
        if value == [None]:
            usable_cat_id.append(key)
        else:
            usable_cat_id.extend(value)
    
    return usable_cat_id 

def prd_id_extractor(category_num: str) -> list:
    """
    category id를 사용하여 제품id를 추출하는 함수입니다.
    """
    page_num = 0
    while True: 

        ua = UserAgent(verify_ssl=False)
        fake_ua = ua.random
        headers = {
            'user-agent' : fake_ua
        }

    
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
        
        prd_id_list = [datas['pid'] for datas in data['list']]

        if page_num == 4: # 카테고리 당 4페이지씩 (400개)
            break
            
        if data['no_result']: # page수가 지정한 페이지 수보다 적을 경우 break
            break
            
        page_num += 1
        
    print('category num %s done'%(category_num))
    time.sleep(0.03) 
    
    return prd_id_list


def category_mp(cat_list: list) -> list:
    """
    첫번째 pool 함수
    카테고리 리스트를 받아서 전체 제품id 리스트를 반환하는 함수입니다.
    """
    pool = multiprocessing.Pool(32) 
    result = pool.map(prd_id_extractor, cat_list)
    
    final_prd_id = []
    for r in result:
        final_prd_id += r
        
    pool.close()
    pool.join()
    
    gc.collect()
    return final_prd_id 

# def write_error_log(response, filename):
#     with open(filename, 'w', encoding='utf-8') as file:
#         file.write(response.text)


def prd_info_crawler(id : int | str) -> list :
    """ 
    제품id를 받아 아래와 같은 리스트형태로 제품 상세정보를 가져오는 함수입니다.
    [제품id, 제품명, 이미지url, 이미지개수, 가격, 제품설명, 카테고리id, 업로드날짜, 제품상태, 제품태그]
    """
    ua = UserAgent(verify_ssl=False)
    fake_ua = ua.random
    headers = {
        'user-agent' : fake_ua
    }

    product = f'https://api.bunjang.co.kr/api/pms/v1/products-detail/{id}?viewerUid=-1'

    response = requests.get(product, headers=headers)

    print('INSERT ID :', id)
    print(response)

    if (response.status_code == 200) and (response.headers["content-type"].strip().startswith("application/json")):
        product_info = response.json()

        try :
            prd_name = product_info['data']['product']['name'] # 제품명
            base_url = product_info['data']['product']['imageUrl'] # 이미지url(파라미터만 변경하여 이미지가져오는 base_url)
            image_cnt = product_info['data']['product']['imageCount'] # 이미지 개수
            price = product_info['data']['product']['price'] # 가격
            prd_info = product_info['data']['product']['description'].replace('\n', ' ').strip() # 제품설명
            cat_id = product_info['data']['product']['category']['id'] # 카테고리 id
            datetime = product_info['data']['product']['updatedAt'] # '2023-05-16T16:18:23.422Z' 형태
            prd_status = product_info['data']['product']['status'] # 제품상태(USED/NEW)
            prd_tag = ",".join(product_info['data']['product']['keywords']) # 제품 태그

        except KeyError:
            prd_name, base_url, image_cnt, price, prd_info, cat_id, datetime, prd_status, prd_tag =\
                None, None, None, None, None, None, None, None, None

        return [id ,prd_name, base_url, image_cnt, price, prd_info, cat_id, datetime, prd_status, prd_tag]
    
    else:
        return [id, None, None, None, None, None, None, None, None, None]
    

def product_mp(id_list : list) -> pd.DataFrame :
    """ 
    두번째 pool 함수
    제품id 리스트를 가져와 제품상세정보 데이터프레임을 반환하는 함수입니다.
    """
    pool = multiprocessing.Pool(processes=8)
    product_info_list = pool.map(prd_info_crawler, id_list)
    
    pool.close()
    pool.join()
    
    gc.collect()
    
    prd_df = pd.DataFrame(product_info_list, columns = ['prd_id' ,'prd_name', 'base_url', 'image_cnt', 'price', 'prd_info', 'cat_id', 'datetime', 'prd_status', 'prd_tag'])
    prd_df = prd_df.dropna()
    
    return prd_df


if __name__ == '__main__':
    
    import csv

    start = time.time()
    
    cat_list = extract_usable_cat_id_only() # raw category list -> usable category list
    prd_id_list = category_mp(cat_list) # category id list -> prd id list

    result1 = product_mp(prd_id_list[0::7]) # prd id list -> final df
    result1.to_csv('BGZT1.csv', index=False, quoting=csv.QUOTE_ALL, escapechar='\\') # to csv
    time.sleep(5)
    end = time.time()
    print("1/7 수행시간: %f 초" % (end - start))

    # result2 = product_mp(prd_id_list[1::7])
    # result2.to_csv('BGZT2.csv', index=False, quoting=csv.QUOTE_ALL, escapechar='\\')
    # time.sleep(5)
    # end = time.time()
    # print("2/7 수행시간: %f 초" % (end - start))

    # result3 = product_mp(prd_id_list[2::7])
    # result3.to_csv('BGZT3.csv', index=False, quoting=csv.QUOTE_ALL, escapechar='\\')
    # time.sleep(5)
    # end = time.time()
    # print("3/7 수행시간: %f 초" % (end - start))

    # result4 = product_mp(prd_id_list[3::7])
    # result4.to_csv('BGZT4.csv', index=False, quoting=csv.QUOTE_ALL, escapechar='\\')
    # time.sleep(5)
    # end = time.time()
    # print("4/7 수행시간: %f 초" % (end - start))

    # result5 = product_mp(prd_id_list[4::7])
    # result5.to_csv('BGZT5.csv', index=False, quoting=csv.QUOTE_ALL, escapechar='\\')
    # time.sleep(5)
    # end = time.time()
    # print("5/7 수행시간: %f 초" % (end - start))

    # result6 = product_mp(prd_id_list[5::7])
    # result6.to_csv('BGZT6.csv', index=False, quoting=csv.QUOTE_ALL, escapechar='\\')
    # time.sleep(5)
    # end = time.time()
    # print("6/7 수행시간: %f 초" % (end - start))

    # result7 = product_mp(prd_id_list[6::7])
    # result7.to_csv('BGZT7.csv', index=False, quoting=csv.QUOTE_ALL, escapechar='\\')
    # time.sleep(5)
    # end = time.time()
    # print("7/7 수행시간: %f 초" % (end - start))