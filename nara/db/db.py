import pymysql
import pandas as pd
from cleansing import cleanse_bj, cleanse_naver, to_datetime, bj_url_list

class CategoryDB :

    def __init__(self, configs) -> None:
        try:
            configs['port'] = int(configs.pop('port'))
            self.DB = pymysql.connect(**configs)
            print('데이터베이스 연결 성공')
        except pymysql.err.OperationalError as e:
            print("데이터베이스 연결 실패:", e)

    def __del__(self) -> None:
        # 데이터베이스 연결 해제
        self.DB.close()

    def insert_naver(self, df:pd.DataFrame) :
        '''네이버 데이터 삽입\n
        '''
        required_columns = ['prd_id','prd_name','cat_id','prd_image_url','prd_low_price']
        
        assert not set(required_columns) - set(df.columns), '칼럼이 일치하지 않습니다.'
        
        ## 데이터 값이 없을수도있음을 고려한 코드 ##
        df.fillna('', inplace=True)

        ## 클랜징 코드 넣기 ##

        df = cleanse_naver(df)

        naver_colums = ['id','name','cat_id','image_url','low_price'] 
        df.columns = naver_colums # df , DB 칼럼명 일치

        insert_sql = f"INSERT INTO naver_prd (`{'`,`'.join(naver_colums)}`) VALUES ({','.join(['%s']*len(naver_colums))})"
        data = [tuple(value) for value in df[naver_colums].values]

        with self.DB.cursor() as cur:
            cur.executemany(insert_sql, data)
        self.DB.commit()

        print('Insert naver data done!')

    def insert_bunjang(self, df:pd.DataFrame) :
        '''번개장터 데이터 삽입\n
        '''
        required_columns = ['prd_id','prd_name','base_url','image_cnt','prd_info','price','cat_id','datetime','prd_status','prd_tag']
        
        assert not set(required_columns) - set(df.columns), '칼럼이 일치하지 않습니다.'

        ## 데이터 값이 없을수도있음을 고려한 코드 ##
        df.fillna('', inplace=True)

        ## 클랜징 코드 넣기 ##
        df = cleanse_bj(df)

        df['date'] = df['date'].apply(lambda x: to_datetime(x))

        ## image_url_list 로 변환하는 코드 ##
        df = bj_url_list(df)

        df = df[[['prd_id','prd_name','image_url_list','prd_info','price','cat_id','datetime','prd_status','prd_tag']]]
        bunjang_columns = ['id', 'name', 'image_url_list','info', 'price', 'cat_id', 'writed_at', 'status', 'tag']
        df.columns = bunjang_columns # df , DB 칼럼명 일치
        
        insert_sql = f"INSERT INTO bunjang_prd (`{'`,`'.join(bunjang_columns)}`) VALUES ({','.join(['%s']*len(bunjang_columns))})"
        data = [tuple(value) for value in df[bunjang_columns].values]
        
        with self.DB.cursor() as cur:
            cur.executemany(insert_sql, data)
        self.DB.commit()

        print('Insert bunjang data done!')
    
    def select_naver(self, id=None, name=None, cat_id=None, low_price = None) :
        where_sql = []
        



        return
    
    def select_bunjang(self, id=None, price=None, cat_id=None, start_date=None, end_date=None, status=None, tag=None) :
        where_sql = []
        
        if start_date and end_date:
            where_sql.append(f"writed_at BETWEEN '{start_date}' AND '{end_date}'")
        elif start_date:
            where_sql.append(f"writed_at >= '{start_date}'")
        elif end_date:
            where_sql.append(f"writed_at <= '{end_date}'")

        return
    