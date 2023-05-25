import time
import requests
import json
import pandas as pd
import multiprocessing
from fake_useragent import UserAgent


def write_error_log(response, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(response.text)

def id_crawler(id : int | str) -> list :
    '''
    input id -> product list
    '''
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
            product_name = product_info['data']['product']['name'] # 제품명
            image_url = product_info['data']['product']['imageUrl'] # 이미지url
            price = product_info['data']['product']['price'] # 가격
            info = product_info['data']['product']['description'].replace('\n', ' ').strip() # 제품설명
            cat_id = product_info['data']['product']['category']['id'] # 카테고리 id
            date = product_info['data']['product']['updatedAt'] # date 형태가 '2023-05-16T16:18:23.422Z'
            sale_status = product_info['data']['product']['saleStatus'] # 판매상태
            status = product_info['data']['product']['status'] # 상품상태

        except KeyError:
            # product_name, image_url, price, cat_id, date, sale_status, status = None, None, None, None, None, None, None
            product_name, image_url, price, info, cat_id, date, sale_status, status = None, None, None, None, None, None, None, None

        return [id ,product_name, image_url, price, info, cat_id, date, sale_status, status]
        # [id, product_name, image_url, price, cat_id, date, sale_status, status]
    
    else:
        return [id, None, None, None, None, None, None, None]
    
    

#  [product_id ,product_name, image_url, price, info, cat_id, date, sale_status, status]



def id_crawler_mp(id_list: list) -> pd.DataFrame:
    '''
    multiprocessing : id_list -> DataFrame

    '''

    pool = multiprocessing.Pool(processes=8)
    result = pool.map(id_crawler, id_list)
    pool.close()
    pool.join()

    # product_df = pd.DataFrame(result, columns=['product_id' ,'product_name', 'image_url', 'price', 'cat_id', 'date', 'sale_status', 'status'])
    product_df = pd.DataFrame(result, columns=['product_id' ,'product_name', 'image_url', 'price', 'info', 'cat_id', 'date', 'sale_status', 'status'])

    return product_df

# def save_to_csv_file()

if __name__ == '__main__':

    import csv

    start = time.time()

    with open('id_list.txt', 'r') as f:
        data = f.readlines()

    id_list = []
    for i in data:
        a = list(map(lambda s: s.strip(), i.split(', ')))
        id_list += a


    result1 = id_crawler_mp(id_list[0::7])
    result1.to_csv('BGZT1.csv', index=False, quoting=csv.QUOTE_ALL, escapechar='\\')
    time.sleep(5)
    end = time.time()
    print("1/7 수행시간: %f 초" % (end - start))

    result1 = id_crawler_mp(id_list[1::7])
    result1.to_csv('BGZT2.csv', index=False, quoting=csv.QUOTE_ALL, escapechar='\\')
    time.sleep(5)
    end = time.time()
    print("2/7 수행시간: %f 초" % (end - start))

    result1 = id_crawler_mp(id_list[2::7])
    result1.to_csv('BGZT3.csv', index=False, quoting=csv.QUOTE_ALL, escapechar='\\')
    time.sleep(5)
    end = time.time()
    print("3/7 수행시간: %f 초" % (end - start))

    result1 = id_crawler_mp(id_list[3::7])
    result1.to_csv('BGZT4.csv', index=False, quoting=csv.QUOTE_ALL, escapechar='\\')
    time.sleep(5)
    end = time.time()
    print("4/7 수행시간: %f 초" % (end - start))

    result1 = id_crawler_mp(id_list[4::7])
    result1.to_csv('BGZT5.csv', index=False, quoting=csv.QUOTE_ALL, escapechar='\\')
    time.sleep(5)
    end = time.time()
    print("5/7 수행시간: %f 초" % (end - start))

    result1 = id_crawler_mp(id_list[5::7])
    result1.to_csv('BGZT6.csv', index=False, quoting=csv.QUOTE_ALL, escapechar='\\')
    time.sleep(5)
    end = time.time()
    print("6/7 수행시간: %f 초" % (end - start))

    result1 = id_crawler_mp(id_list[6::7])
    result1.to_csv('BGZT7.csv', index=False, quoting=csv.QUOTE_ALL, escapechar='\\')
    time.sleep(5)
    end = time.time()
    print("7/7 수행시간: %f 초" % (end - start))