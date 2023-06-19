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

# 앱 생성
app = Flask(__name__)

# 모델링 적용 함수
def model_def(image, *text_data):

    # 이미지 전처리
    image = Image.open(image)
    image = image.resize((224, 224))  # 크기 조정 (예시)
    image = np.array(image)  # NumPy 배열로 변환 (예시)
    image = image / 255.0  # 정규화 (예시)
    image = None # 오류방지코드 (임시)

    return [data for data in text_data], image

# 데코레이터로 /nara 경로 생성(POST)
@app.route('/nara', methods=['POST'])
def process_data():
    
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
    app.run(debug=True)
