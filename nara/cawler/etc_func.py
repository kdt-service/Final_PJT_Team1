import requests
import json
import pandas as pd

def read_json_file(file_path : str):
    '''
    json 파일을 읽어주는 함수
    '''
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def save_list_to_txt(data_list : list, file_path : str):
    '''
    list를 파일로 저장하는 함수
    '''
    with open(file_path, 'w', encoding='utf-8') as file:
        for item in data_list:
            file.write(str(item) + '\n')
    print(file_path,'저장완료!')
