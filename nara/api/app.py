# def img(img_data):
#     # 이미지 변환을 정의한 딕셔너리
#     data_transforms = {
#         'train': transforms.Compose([
#             transforms.RandomResizedCrop(224),
#             transforms.RandomHorizontalFlip(),
#             transforms.ToTensor(),
#             transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
#         ]),
#         'val': transforms.Compose([
#             transforms.Resize(256),
#             transforms.CenterCrop(224),
#             transforms.ToTensor(),
#             transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
#         ]),
#     }

#     # 이미지 변환 수행
#     transformed_data = data_transforms['val'](img_data)

#     return transformed_data
   
###################################################################################################

from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
from flask_mysqldb import MySQL
import pandas as pd
from datetime import datetime, timedelta

DBconfig = {}
with open('config/DBconfig', 'r') as f:
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

@app.route('/price', methods=['POST'])
def market_price():
    if 'product_brand' not in request.form or 'product_type' not in request.form :
        return '상품정보를 찾을 수 없습니다.', 400
 
    day7 = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d') 

    brand = request.form['product_brand'] # 나이키, 구찌, 프라다
    product_type = request.form['product_type'] # 신발, 지갑, 티셔츠
    

    query = """
    SELECT id, price
    FROM category_db.bunjang_prd
    WHERE name LIKE %(brand)s
      AND name LIKE %(product_type)s
      AND writed_at BETWEEN %(date)s AND CURDATE()
    """
    params = {
        'brand': f'%{brand}%',
        'product_type': f'%{product_type}%',
        'date': day7
    }

    cursor = mysql.connection.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()

    df_column = ['id','price']
    df = pd.DataFrame(result, columns=df_column)
    df['price'] = del_outlier(df['price'])

    mean_price = df['price'].mean()
    r_price = int(round(mean_price, -len(str(int(mean_price))) + 3))

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
    # app.run(host='0.0.0.0', port=8080)
    app.run(debug=True)