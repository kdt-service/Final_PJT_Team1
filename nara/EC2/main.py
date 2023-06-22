import pymysql
import pandas as pd 
import csv
from datetime import timedelta, datetime

from CRAWL import bgzt_crawler, bgzt_id_crawler
from DB.module import db, secret, cleansing_df


if __name__ == '__main__':
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'--------------- log {now} ---------------')
    # crawl product - id 

    cat_list = bgzt_id_crawler.read_cat_list() 
    prd_list = bgzt_id_crawler.category_mp(cat_list) 
   
    with open('/home/ubuntu/workspace/CRAWL/cat/prd_list', 'w') as file:
        for item in prd_list:
            file.write(str(item) + '\n')
            
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'Complete id crawling & save data / {now}')

    prd_id_list = bgzt_crawler.read_to_list('/home/ubuntu/workspace/CRAWL/cat/prd_list')

    result = bgzt_crawler.product_mp(prd_id_list)
    result.to_csv('/home/ubuntu/workspace/CRAWL/data/BGZT.csv', index=False, quoting=csv.QUOTE_ALL, escapechar='\\')

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'Complete crawling bz data & save data / {now}')

    config = secret.read_config('/home/ubuntu/workspace/DB/config/config')

    my_db = db.CategoryDB(config)

    df = pd.read_csv('/home/ubuntu/workspace/CRAWL/data/BGZT.csv')
    
    # print(df.columns)
    my_db.insert_bunjang(df)

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'Insert data to DB / {now}')

    print('------------------------ End --------------------------\n')