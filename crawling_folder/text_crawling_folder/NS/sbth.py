from Crypto.Cipher import AES
import re
import requests
from datetime import datetime


def pad (data):
    '''패딩함수
    '''
    BLOCK_SIZE = 16
    pad = BLOCK_SIZE - len(data) % BLOCK_SIZE
    return data + pad * chr(pad)

def get_value(k, txt):
    return re.search(f'{k}\:\"[^\"]+', txt).group().split('\"')[-1]

def generate_password():
  now = datetime.now()
  return "sb" + now.strftime("%Y-%m-%dT%H:%M:%S.%fZ") + "th"

def get_sbth() -> str :
    '''sbth 값 가져오는 함수
    '''
    r = requests.get('https://ssl.pstatic.net/shoppingsearch/static/pc/pc-230518-163244/_next/static/chunks/pages/_app-e00a32acfd8347ef.js', headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
    })

    idx = r.text.index('algorithm:')

    txt = re.search('algo[^\}]+', r.text[idx:]).group()

    key = get_value('key', txt)
    iv = get_value('iv', txt)

    aes = AES.new(key.encode(), AES.MODE_CBC, iv.encode())

    pw = generate_password()

    data = pad(pw)

    encrypted = aes.encrypt(data.encode())

    sbth = encrypted.hex()

    return sbth


if __name__ == '__main__':
    print(get_sbth())