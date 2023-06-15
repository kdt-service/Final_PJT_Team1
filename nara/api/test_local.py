import requests
import json


url = 'http://127.0.0.1:5000/upload'
# data = {'num' : 40}
# headers = {'Content-Type': 'application/json'}
# response = requests.post(url, data=json.dumps(data),headers=headers)
# print(response.json()['result'])

image_path = 'image.jpg'


with open(image_path, 'rb') as file:
    response = requests.post(url, files={'image': file})


if response.status_code == 200:
    print('이미지 업로드가 완료되었습니다.')
else:
    print('이미지 업로드가 실패했습니다.')
