import pymysql
import pandas as pd 
from db import CategoryDB
import secret

 
if __name__ == '__main__':

    config = secret.read_config('config')

    db = CategoryDB(config)
