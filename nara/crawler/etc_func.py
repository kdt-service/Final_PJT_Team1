import json
import pandas as pd

def read_json_file(file_path : str):
    '''
    json 파일을 읽어오는 함수
    '''
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def save_json_file(data, file_path):
    '''
    json 파일을 저장하는 함수
    '''
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def read_txt_to_list(file_path):
    '''
    txt 파일을 한줄씩 list로 읽어오는 함수\n
    [ [1줄], [2줄], [3줄], [4줄], [5줄], [6줄] ... ]
    '''
    with open(file_path, 'r') as f:
        data = f.readlines()

    id_list = []
    for i in data:
        a = list(map(lambda s: s.strip(), i.split(', ')))
        id_list += a
    
    return id_list

def save_list_to_txt(data_list : list, file_path : str):
    '''
    list를 파일로 저장하는 함수
    '''
    with open(file_path, 'w', encoding='utf-8') as file:
        for item in data_list:
            file.write(str(item) + '\n')
    print(file_path,'저장완료!')

def divide_cat_id(cat_id, size=3):
    '''
    카테고리를 3,6,9 로 나누는 함수
    size : 기본값은 3
    '''
    cat_id = str(cat_id)
    return [cat_id[0:i] for i in range(3, len(cat_id)+size, size)]

def find_cat(cat_id, cat_dict):
    '''
    cat_id 에 명칭을 꺼내는 함수
    '''
    cat_list = divide_cat_id(cat_id)
    return [cat_dict[cat].strip() for cat in cat_list]

if __name__ == '__main__':

    cat_dict = read_json_file('./data/bungae_mapping_category_nums_and_titles.json')
    print(find_cat(310090,cat_dict=cat_dict))
    print(find_cat(310090050,cat_dict=cat_dict))
    print(find_cat(500120004,cat_dict=cat_dict))
    

