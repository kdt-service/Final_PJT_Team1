from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
from flask_mysqldb import MySQL
import pandas as pd
from datetime import datetime, timedelta
from API.MODEL.cat_model import test_sentences


# config 불러오기
DBconfig = {}
with open('/home/ubuntu/workspace/API/config/DBconfig', 'r') as f:
    for l in f.readlines():
        k, v = l.rstrip().split('=')
        DBconfig[k] = v

# 앱 생성
app = Flask(__name__)

# DB 연동
app.config['MYSQL_HOST'] = DBconfig['host']
app.config['MYSQL_PORT'] = int(DBconfig['port'])  
app.config['MYSQL_USER'] = DBconfig['user']
app.config['MYSQL_PASSWORD'] = DBconfig['passwd']
app.config['MYSQL_DB'] = DBconfig['db']

mysql = MySQL(app)

# 이상치 제거함수
def del_outlier(price : pd.Series) :
    des = price.describe()
    q1 = des['25%']
    q3 = des['75%']
    iqr = q3-q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    result = price[(price >= lower_bound) & (price <= upper_bound) & (price >= 5000)]
    
    return result

# 모델링 적용 함수
def model_def(image, *text_data):
    # 이미지 전처리
    image = Image.open(image)
    image = image.resize((224, 224))  # 크기 조정 (예시)
    image = np.array(image)  # NumPy 배열로 변환 (예시)
    image = image / 255.0  # 정규화 (예시)
    image = None # 오류방지코드 (임시)

    return [data for data in text_data], image # 결과 (예시)

@app.route('/test', methods=['POST'])
def test_1():

    test_d = request.form['test_data']

    results = test_sentences([test_d])

    response = {
        'test_results': results
    }

    response['test_results'] = response['test_results'].tolist()

    return jsonify(response)



# 데코레이터로 /price 경로 생성(POST)
@app.route('/price', methods=['POST'])
def market_price():
    if 'product_brand' not in request.form or 'product_type' not in request.form :
        return '상품정보를 찾을 수 없습니다.', 400
 
    day7 = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d') # 현재일수로 부터 -7일

    brand = request.form['product_brand'] # 나이키, 구찌, 프라다
    product_type = request.form['product_type'] # 신발, 지갑, 티셔츠
    
    # 쿼리문 (오늘 ~ 7일전 상품데이터)
    query = f"""
    SELECT id, price
    FROM category_db.bunjang_prd
    WHERE name LIKE '%{brand}%'
      AND name LIKE '%{product_type}%'
      AND writed_at BETWEEN '{day7} AND CURDATE()
    """

    cursor = mysql.connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()

    # df 로 변환 후 이상치 제거
    df_column = ['id','price']
    df = pd.DataFrame(result, columns=df_column)
    df.to_csv('test.csv')
    df['price'] = del_outlier(df['price'])

    mean_price = df['price'].mean()
    r_price = int(round(mean_price, -len(str(int(mean_price))) + 3))
    
    # 시세 반환
    response = {
        'market_price': r_price
    }

    return jsonify(response)

# 데코레이터로 /cate 경로 생성(POST)
@app.route('/cate', methods=['POST'])
def cate():
    
    # 데이터 key:value 확인
    if 'product_name' not in request.form or 'product_info' not in request.form or 'product_image' not in request.files:
        return '상품명, 상품정보 또는 상품이미지를 찾을 수 없습니다.', 400
    
    name = request.form['product_name']
    info = request.form['product_info']
    image = request.files['product_image']

    if name == '' or info == '' or image.filename == '':
        return '상품명, 상품정보 또는 이미지의 파일명이 없습니다.', 400

    # 모델링 적용
    result = model_def(image, name, info)

    # dict 객체으로 저장
    response = {
        'cate': result
    }

    return jsonify(response) # json 객체로 반환

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    # 15.168.68.33
    # app.run(debug=True)