from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api', methods=['POST'])
def process_data():
    # 사용자로부터 데이터 받기
    data = request.get_json()
    num = data['num']

    # 함수 사용
    result = multiple(num)

    # 결과를 JSON 형태로 반환
    response = {
        'result': result
    }
    return jsonify(response)


@app.route('/upload', methods=['POST'])
def upload_image():

    image = request.files['image']

    # image = img(image)

    image.save('uploaded_image.jpg')

    return '이미지가 성공적으로 업로드되었습니다.'

def multiple(input_data):
    
    result = input_data * 40
    
    return result

def img(img_data):

    return

if __name__ == '__main__':
    app.run(debug=True)

