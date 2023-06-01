import pymysql
import pandas as pd 
from module.db import CategoryDB
from module.secret import read_config

 
if __name__ == '__main__':

    config = read_config('config/config')

    db = CategoryDB(config)

    df = db.select_bunjang()

    df.to_csv('test.csv', index=False)


        

