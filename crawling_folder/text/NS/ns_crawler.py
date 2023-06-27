import requests
from fake_useragent import UserAgent
import json
import time
import pandas as pd
import re
from sbth import get_sbth

def open_and_preprocess_df():
    df = pd.read_csv('./json_and_excel_files_merged.csv')
    df = df.fillna('')
    df['url'] = df['최종 URL'] # url 컬럼 이름 바꾸기
    del df['최종 URL']

    # -- cat3 기준 기타 빼야 됨 --
    # -- 그리고 reset index --
    index_list = list(df['cat3'][df['cat3'].str.contains('기타')].index)
    df = df.drop(index=index_list).copy()
    df = df.reset_index(drop=True).copy()
    
    # -- url 부분에 api 단어 추가 -- 
    df['url'] = df['url'].map(lambda x : re.sub('(.com\/search)', '.com/api/search', x))
    # -- url 중간에 빈칸이 들어가 있는 경우가 있었음 빈칸 제거 --
    df['url'] = df['url'].map(lambda x : re.sub('\s+', '', x))

    # -- cat_id 타입 int로 바꾸기 --
    df['cat_id'] = df['cat_id'].astype(int)
    
    return df

def base_crawling_code(url:str, iq:str, spec:str, cat_id:int, page_num:int):
    """
    url, iq, spec 세개를 인자로 받아 크롤링을 하는 함수. 
    """
    sbth = get_sbth()
    ua = UserAgent(verify_ssl=False) 
    fake_ua = ua.random
    headers = {
        'user-agent' : fake_ua,
        'cache-control' : 'no-cache, no-store, must-revalidate',
        'sbth' : sbth,
        'referer' : 'https://search.shopping.naver.com/search/category',    
    }

    params = (
        ('sort','rel'),
        ('pagingIndex', str(page_num)),
        ('productSet', 'total'), 
        ('pagingSize','40'),
        ('viewType','list'),
        ('iq', iq),
        ('spec', spec)
    )
        
    prd_list = list()
    res = requests.get(url, headers=headers, params=params)
    if (res.status_code == 200):
        results = res.json()

        try:
            results = results['shoppingResult']['products'] # products 키 값안에 상품 정보 들어있음. 
            
            for result in results:
                prd_id = result['id'] # id
                prd_name = result['productName'] # name
                prd_image_url = result['imageUrl'] # image_url
                prd_low_price = result['lowPrice'] # low_price

                prd_list.append([str(prd_id), prd_name, str(cat_id), prd_image_url, str(prd_low_price)])
        except:
            pass 
            
    else:
        pass
    
    return prd_list

def get_NaverPrd(url:str, iq:str, spec:str, cat_id:int, page_count = 400):
    """
    cat_id -> 크롤링하고자 하는 category id
    page_count -> 크롤링하고자 하는 페이지 수 (300 pages by default)
    """
    prd_list = list()
    for page_num in range(1, page_count+1): # 300 페이지 가져오기 
        prd_list += base_crawling_code(url, iq, spec, int(cat_id), page_num)
        print(f'-- {page_num} page done -- ')
        
        if page_num % 50 == 0:
            print('-- paused for 5 sec after crawling 50 pages -- ')
            time.sleep(5)
            
    print(f'-- category id {int(cat_id)} done --')
    print(f'-- 데이터 개수 : {len(prd_list)} --')
    
    # -- prd_list에서 데이터 프레임 만들기 --
    df = pd.DataFrame(prd_list, columns = ['id', 'name', 'cat_id', 'image_url', 'low_price'])
    
    # -- csv 파일로 내보내기 --
    # -- why? 혹시나 막힐 수도 있으니 미리미리 데이터 프레임으로 만들어 놓자 -- 
    df.to_csv(f'./cat_id_{int(cat_id)}_DF.csv', index=False)
    
    return

def run_all_process():
    df = open_and_preprocess_df()
    
    for idx in range(71, 91):  # 44부터 91까지
        url = df.iloc[idx]['url']
        iq = df.iloc[idx]['iq']
        spec = df.iloc[idx]['spec']
        cat_id = df.iloc[idx]['cat_id']
        
        get_NaverPrd(url, iq, spec, cat_id, page_count=300) # page_count는 default로 400 페이지 그러나 여기서는 300
        
        # -- 블락을 대비하여 좀 길게 time.sleep() --
        print(f'-- {idx} 번째 카테고리 done --')
        print('\n-- paused for 30 sec not to be blocked after crawling one category --\n')
        time.sleep(30)
        
    return

if __name__ == '__main__':
    run_all_process()
    

