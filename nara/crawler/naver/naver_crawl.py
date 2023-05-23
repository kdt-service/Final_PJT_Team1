import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
import time
import pandas as pd
from sbth import get_sbth
import multiprocessing


def get_ns_prd_list(cat_id: str, page_num: int) -> list:

    sbth = get_sbth() # sbth 가져오기

    ua = UserAgent(verify_ssl=False) # UserAgent 생성
    fake_ua = ua.random # UserAgent 생성

    headers = {
        'user-agent' : fake_ua,
        'cache-control' : 'no-cache, no-store, must-revalidate',
        # -- sbth 없으면 정보 안가져옴 --
        # -- update 필요할 수 있음 => 날짜 정보가 들어가 만료가 될 수 있음 -- 
        'sbth' : sbth,
        # -- referer 없으면 정보 안가져옴 --
        'referer' : 'https://search.shopping.naver.com/search/category', 
    }

    params = (
        ('sort','rel'),
        ('pagingIndex', page_num),
        ('pagingSize','40'),
        ('viewType','list'),
        # -- 여기에 해당하는 catId는 엑셀파일에 있는 catId --
        ('catId',cat_id)
    )

    url = 'https://search.shopping.naver.com/api/search/category'
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        results = res.json()
        results = results['shoppingResult']['products'] # products 키 값안에 상품 정보 들어있음. 
        
        prd_list = list()
        for result in results:
            prd_id = result['id']
            prd_name = result['productName']
            cat1_id = result['category1Id']
            cat1_name = result['category1Name']
            cat2_id = result['category2Id']
            cat2_name = result['category2Name']
            cat3_id = result['category3Id']
            cat3_name = result['category3Name']
            # -- cat 4 name -- 
            
            prd_image_url = result['imageUrl']
            prd_low_price = result['lowPrice']
            prd_list.append([prd_id, prd_name, cat1_id, cat1_name, cat2_id, 
                             cat2_name, cat3_id, cat3_name, prd_image_url, prd_low_price]) 
    else:
        prd_list.append([None, None, None, None, None,
                         None, None, None, None, None]) # 변수들 None 값으로 처리 
        
    return prd_list


def get_prd_info(cat_id: str):
    """
    cat_id -> 크롤링하고자 하는 category id \n
    page -> 250 pages by default
    """
    page = 10
    
    prd_list = list()
    for page_num in range(1, page + 1): # 250 페이지 가져오기 
        prd_list += get_ns_prd_list(cat_id, page_num)
        print('page %d done'%page_num)
        
        if page_num % 50 == 0:
            print('-- paused for 5 sec in case not to be blocked --')
            time.sleep(5)
            
    print('-- 데이터 개수 :  %d --'%(len(prd_list)))
    

    return prd_list


def get_prd_info_mp(id_list: list) -> pd.DataFrame:
    '''
    multiprocessing : prd_list -> DataFrame

    '''

    pool = multiprocessing.Pool(processes=8)
    prd_list = pool.map(get_prd_info, id_list)
    pool.close()
    pool.join()
    df = pd.DataFrame(columns = ['prd_id', 'prd_name', 'cat1_id', 'cat1_name', 'cat2_id', 
                                           'cat2_name', 'cat3_id', 'cat3_name', 'prd_image_url', 
                                           'prd_low_price'])
    for prd in prd_list :
        for pr in prd :
            df.loc[len(df)] = pr

    
    return df


if __name__ == '__main__':

    cat_list = ['50000002', '50000198', '50000305']

    a = get_prd_info_mp(cat_list)

    a.to_csv("test.csv", index=False)


    # print(get_prd_info(cat_list[0]))


#[[[],[],[],[]],[[],[],[]]]
