import requests
import json


# image_path = 'image.jpg'

# # 상품명과 상품정보
# product_name = '상품명'
# product_info = '상품 정보'

# # API 엔드포인트 URL
# url = 'http://localhost:5000/cate'

# # 이미지 파일과 상품명, 상품정보
# files = {'product_image': open(image_path, 'rb')}
# data = {'product_name': product_name, 'product_info': product_info}
# response = requests.post(url, files=files, data=data)

# result = response.json()

# print(result)


url2 = 'http://localhost:5000/price'
brand = '구찌'
typ = '신발'
data = {'product_brand': brand, 'product_type': typ}
response = requests.post(url2, data=data)

result = response.json()

print(result)