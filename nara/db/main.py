import pymysql
import pandas as pd 
from module.db import CategoryDB
from module.secret import read_config

 
if __name__ == '__main__':

    config = read_config('config/config')

    db = CategoryDB(config)

    a = db.select_bunjang(status='USED')

    print(a.head(3))