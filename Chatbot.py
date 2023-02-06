# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 19:29:21 2023

@author: junob
"""

from PyKakao import KoGPT
with open('API_key.txt', 'rt', encoding='UTF8') as f:
    api_key = f.read()
api = KoGPT(service_key = api_key)

max_tokens = 64

def chatbot(prompt):
    # 결과 조회
    result = api.generate(prompt, max_tokens, temperature=0.3, top_p=0.5, n=1)['generations'][0]['text'].split('\n')[0]
    #print('A:' + result)
    #result = "안녕하세요"
    return result
    