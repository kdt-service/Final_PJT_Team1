import requests
import json
from fake_useragent import UserAgent
import time
import pandas as pd

def get_nextCat(cat):
    catNm = cat.split('_')[-1]
    
    ua = UserAgent(verify_ssl=False)
    fake_ua = ua.random
    headers = { 'user-agent' : fake_ua }

    url = 'https://shopping.naver.com/api/modules/gnb/category?id={}&_vc_=396951197'.format(catNm)
    res = requests.get(url, headers = headers)
    data = res.json()
    
    if data:
        if cat == 'root': # root 일 때는 리스트에서 빼주기 
            cat_list = ['_'.join([d['catNm'], d['catId']]) for d in data]
        else:
            cat_list = ['_'.join([cat, d['catNm'], d['catId']]) for d in data]
    else:
        cat_list = [cat]
    
    return cat_list

def get_nextCat2(cat_list):
    nextCat_list = list()
    
    cnt = 0
    for cat in cat_list:
        nextCat_list += get_nextCat(cat)
        cnt+=1
        print('{} category done'.format(cnt))
        time.sleep(0.05)
    print('---------- done --------')   
    return nextCat_list

def get_mainCat_midCat_sub1Cat() -> list:
    # mainCat
    main_list = get_nextCat('root')

    # mainCat_midCat
    main_mid_list = get_nextCat2(main_list)

    # mainCat_midCat_sub1Cat
    main_mid_sub1_list = get_nextCat2(main_mid_list)
    
    return main_mid_sub1_list



if __name__ == '__main__':
    result = get_mainCat_midCat_sub1Cat()
    
    list_for_df = [r.split('_') for r in result] # 데이터 프레임으로 만들기 전 리스트
    
    df = pd.DataFrame(list_for_df, columns = ['mainCat_name', 'mainCat_id', 'midCat_name', # 데이터 프레임 화
                                           'midCat_id', 'sub1Cat_name', 'sub1Cat_id'])
    
    df.to_csv('./NS_main_mid_sub1_cat.csv', index=False)
    
    
    
    
    
    
    