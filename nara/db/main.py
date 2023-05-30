import pymysql
import pandas as pd 
from module.db import CategoryDB
from module.secret import read_config

 
if __name__ == '__main__':

    config = read_config('config/config')

    db = CategoryDB(config)

    df = pd.read_csv('data/concat_bj_data.csv', dtype={'image_url': str})
    db.insert_bunjang(df=df) 


        

