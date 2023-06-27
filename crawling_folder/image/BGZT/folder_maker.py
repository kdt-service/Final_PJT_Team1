import os
import pandas as pd

def make_folders_for_image():
    df = pd.read_csv('./bungae_df_for_image_crawling.csv')
    cat_id_list = list(df['cat_id'].unique())
    
    for cat_id in cat_id_list:
        # -- 폴더 이름은 원하시는 대로 변경해주세요 --
        # -- bungae_fashion_image 부분 변경해주시면 돼요 --
        os.makedirs(f'./bungae_fashion_image/{cat_id}')
        
    return 

if __name__ == '__main__':
    make_folders_for_image()