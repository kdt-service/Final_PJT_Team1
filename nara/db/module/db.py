import pymysql
import pandas as pd
from module.cleansing_df import cleanse_bj, cleanse_naver, to_datetime, bj_url_list

class CategoryDB :

    def __init__(self, configs) -> None:
        try:
            configs['port'] = int(configs['port'])
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

        df = df.drop_duplicates(subset='prd_id')
        
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
        required_columns = ['product_id', 'product_name', 'image_url', 'image_cnt', 'price', 'info', 'cat_id', 'date', 'keywords']

        assert not set(required_columns) - set(df.columns), '칼럼이 일치하지 않습니다.'

        ## 데이터 값이 없을 수도 있음을 고려한 코드 ##
        df.fillna('', inplace=True)

        ## 클랜징 코드 넣기 ##
        df = cleanse_bj(df)
        
        df.loc[:, 'date'] = df['date'].apply(lambda x: to_datetime(x))

        ## image_url_list 로 변환하는 코드 ##
        df = bj_url_list(df)

        df = df[['product_id', 'product_name', 'image_url_list', 'price', 'info', 'cat_id', 'date', 'keywords']]
        bunjang_columns = ['id', 'name', 'image_url_list', 'price', 'info',  'cat_id', 'writed_at', 'tag']
        df.columns = bunjang_columns # df , DB 칼럼명 일치
        
        insert_sql = f"INSERT INTO bunjang_prd (`{'`,`'.join(bunjang_columns)}`) VALUES ({','.join(['%s']*len(bunjang_columns))})"
        data = [tuple(value) for value in df[bunjang_columns].values]
        
        with self.DB.cursor() as cur:
            cur.executemany(insert_sql, data)
        self.DB.commit()

        print('Insert bunjang data done!')
    
    def select_naver(self, name=None, cat_id=None, min_price = None, max_price=None) -> pd.DataFrame :
        '''네이버 DB데이터 출력\n
        name : 상품 이름, 검색어가 포함된 모든 상품 출력 \n
        cat_id : 카테고리 id \n
        min_price : 최소 가격 \n
        max_price : 최대 가격 \n
        '''
        where_sql = []
        join_sql = None
        
        main_query = 'SELECT * FROM naver_prd'

        if cat_id:
            where_sql.append(f"cat_id = {cat_id}")
            join_sql = "LEFT JOIN prd_cat ON naver_prd.cat_id = prd_cat.id"
            main_query = 'SELECT naver_prd.*, prd_cat.cat1, prd_cat.cat2, prd_cat.cat3 FROM naver_prd'

        if name is not None :
            where_sql.append(f"name LIKE '%{name}%'")
        
        if min_price is not None and max_price is not None:
            where_sql.append(f"low_price BETWEEN {min_price} AND {max_price}")
        elif min_price is not None:
            where_sql.append(f"low_price >= {min_price}")
        elif max_price is not None:
            where_sql.append(f"low_price <= {max_price}")

        if join_sql is not None :
            main_query += " " + join_sql
            if where_sql :
                main_query += f' WHERE {" AND ".join(where_sql)}'
            with self.DB.cursor() as cur:
                cur.execute(main_query)
                result = cur.fetchall()
                df_column = ['id', 'name', 'cat_id', 'image_url', 'low_price', 'cat1', 'cat2', 'cat3']
                df = pd.DataFrame(result, columns=df_column)
        else:
            if where_sql :
                main_query += f' WHERE {" AND ".join(where_sql)}'
            with self.DB.cursor() as cur:
                cur.execute(main_query)
                result = cur.fetchall()
                df_column = ['id', 'name', 'cat_id', 'image_url', 'low_price']
                df = pd.DataFrame(result, columns=df_column)

        return df
    
    def select_bunjang(self, name=None, cat_id=None, start_date=None, end_date=None, min_price = None, max_price=None, tag=None) :
        '''번개장터 DB데이터 출력\n
        name : 상품 이름, 검색어가 포함된 모든 상품 출력 \n
        cat_id : 카테고리 id \n
        start_date : 시작일 \n
        end_date : 종료일 \n
        min_price : 최소 가격 \n
        max_price : 최대 가격 \n
        tag : 상품 태그, 검색어가 포함된 모든 상품 출력 \n
        '''
        
        where_sql = []
        join_sql = "LEFT JOIN prd_cat ON bunjang_prd.cat_id = prd_cat.id"
        main_query = 'SELECT bunjang_prd.*, prd_cat.cat1, prd_cat.cat2, prd_cat.cat3 FROM bunjang_prd'

        if cat_id is not None:
            where_sql.append(f"cat_id = {cat_id}")
            # join_sql = "LEFT JOIN prd_cat ON bunjang_prd.cat_id = prd_cat.id"
            # main_query = 'SELECT bunjang_prd.*, prd_cat.cat1, prd_cat.cat2, prd_cat.cat3 FROM bunjang_prd'

        if name is not None :
            where_sql.append(f"name LIKE '%{name}%'")

        if tag is not None :
            where_sql.append(f"tag LIKE '%{tag}%'")

            
        if min_price is not None and max_price is not None:
            where_sql.append(f"price BETWEEN {min_price} AND {max_price}")
        elif min_price is not None:
            where_sql.append(f"price >= {min_price}")
        elif max_price is not None:
            where_sql.append(f"price <= {max_price}")

        if start_date is not None and end_date is not None:
            where_sql.append(f"writed_at BETWEEN '{start_date}' AND '{end_date}'")
        elif start_date is not None:
            where_sql.append(f"writed_at >= '{start_date}'")
        elif end_date is not None:
            where_sql.append(f"writed_at <= '{end_date}'")


        if join_sql is not None:
            main_query += " " + join_sql
            if where_sql :
                main_query += f' WHERE {" AND ".join(where_sql)}'
            with self.DB.cursor() as cur:
                cur.execute(main_query)
                result = cur.fetchall()
                df_column = ['id', 'name', 'image_url_list', 'price', 'info', 'cat_id', 'writed_at', 'tag', 'cat1', 'cat2', 'cat3']
                df = pd.DataFrame(result, columns=df_column)
        else:
            if where_sql :
                main_query += f' WHERE {" AND ".join(where_sql)}'
            with self.DB.cursor() as cur:
                cur.execute(main_query)
                result = cur.fetchall()
                df_column = ['id', 'name', 'image_url_list','price', 'info', 'cat_id', 'writed_at', 'tag']
                df = pd.DataFrame(result, columns=df_column)

        
        return df
    
    def get_cate(self):
        main_query = 'SELECT * FROM category_db.prd_cat;'

        with self.DB.cursor() as cur:
            cur.execute(main_query)
            result = cur.fetchall()
            df_column = ['id', 'cat1', 'cat2', 'cat3']
            df = pd.DataFrame(result, columns=df_column)
        
        return df