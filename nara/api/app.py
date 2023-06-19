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

app = Flask(__name__)

def model_def(image, *text_data):
    image = None
    return [data for data in text_data], image

@app.route('/nara', methods=['POST'])
def process_data():
    if 'product_name' not in request.form or 'product_info' not in request.form or 'product_image' not in request.files:
        return '상품명, 상품정보 또는 상품이미지를 찾을 수 없습니다.', 400

    name = request.form['product_name']
    info = request.form['product_info']
    image = request.files['product_image']

    if name == '' or info == '' or image.filename == '':
        return '상품명, 상품정보 또는 이미지의 파일명이 없습니다.', 400

    # 모델링
    result = model_def(image, name, info)

    response = {
        'cate': result
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
