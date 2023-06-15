import requests
import json


url = 'http://15.168.68.33:8080/api'
data = {'num' : 40}
headers = {'Content-Type': 'application/json'}
response = requests.post(url, data=json.dumps(data),headers=headers)
print(response.json()['result'])