# 임의의 데이터를 추출거나 삽입할때, 사용하는 py 파일

import pymysql
import pandas as pd 
from module.db import CategoryDB
from module.secret import read_config

 
if __name__ == '__main__':

    config = read_config('/home/ubuntu/workspace/DB/config/config')

    db = CategoryDB(config)

    # df = pd.read_csv('/home/ubuntu/workspace/CRAWL/data/BGZT.csv')
    
    # print(df.columns)
    # db.insert_bunjang(df)


    # 카테고리 리스트 가져오기
    # df = db.get_cate()

    # 조건에 맞는 데이터 가져오기
    # df = db.select_bunjang(start_date='2023-06-19')



    

        

