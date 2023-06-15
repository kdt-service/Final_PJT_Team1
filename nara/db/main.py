import pymysql
import pandas as pd 
from module.db import CategoryDB
from module.secret import read_config

 
if __name__ == '__main__':

    config = read_config('config/config')

    db = CategoryDB(config)

    # df = pd.read_csv('data2/bgzt.csv')
    # df = df[['id', 'name', 'image_url', 'image_cnt', 'price', 'info', 'cat_id', 'writed_at', 'tag']]

    # df.rename(columns={
    #     'id': 'product_id',
    #     'name': 'product_name',
    #     'writed_at': 'date',
    #     'tag': 'keywords',
    #     }, inplace=True)
    
    # print(df.columns)
    # db.insert_bunjang(df)

    # df = pd.read_csv('data2/naver.csv')
    # print(df.columns)

    # df.rename(columns={
    #     'id': 'prd_id',
    #     'name': 'prd_name',
    #     'image_url': 'prd_image_url',
    #     'low_price': 'prd_low_price',
    #     }, inplace=True)
    
    # db.insert_naver(df)

    # df = db.get_cate()

    # df = db.select_bunjang(cat_id=400080300)

    # df.to_csv('cate22.csv',index=False)

    

        

