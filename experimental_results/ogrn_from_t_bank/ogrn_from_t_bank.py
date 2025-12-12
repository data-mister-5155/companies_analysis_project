
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sqlite3
import time
import pandas as pd
from lxml import html
import re
import requests
from bs4 import BeautifulSoup
import json

conn = sqlite3.connect('ogrn_from_t_bank.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS my_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site TEXT,
    tag TEXT,
    name TEXT,
    street TEXT,
    ogrn TEXT
)
""")
conn.commit()  # можно закоммитить создание (необязательно сразу, но полезно)






df = pd.read_csv('NEW_data.csv')#['adres'].values

def longest_words(strings):
    # объединяем в одну строку (на случай, если список с несколькими элементами)
    text = " ".join(strings)
    # берём слова: кириллица/латиница/цифры и дефис (дефис включён, чтобы "Санкт-Петербург" считался одним словом)
    words = re.findall(r"[А-Яа-яЁёA-Za-z0-9\-]+", text)
    if not words:
        return []
    maxlen = max(len(w) for w in words)
    # вернуть все слова максимальной длины (на случай ничьей)
    return [w for w in words if len(w) == maxlen]


d = []
for i in df['adres']:
    #print([[i]])
    #print(i.split('Россия,')[-1].split('Москва,')[-1].split('еринбург,')[-1].split('етербург,')[-1].split('льяновск,')[-1].split('овгород,')[-1].split('-на-Дону,')[-1].split('Челябинск,')[-1].split(','))
    for e in i.split('Россия,')[-1].split('Москва,')[-1].split('еринбург,')[-1].split('етербург,')[-1].split('льяновск,')[-1].split('овгород,')[-1].split('-на-Дону,')[-1].split('Челябинск,')[-1].split('ермь,')[-1].split('Саранск,')[-1].split('119049,')[-1].split(','):
        #print(e)
        if any(w in e for w in ['ул.','пр.','Ул.','тер.','пер.','улица','переулок','Каширское','проспект','пр-кт','Проспект','набережная','шоссе','Набережная','наб.',
                                'тупик','бульвар','Поля','ридриха','Спартаковский','Донская']):
            #print([e])
            #words = re.findall(r"[A-Za-zА-Яа-яЁё]+", " ".join(e))
            #longest = max(words, key=len) if words else ""

            #print([longest_words([e])[0]])            # -> Муниципальный
            d.append(longest_words([e])[0])  
            break
        else:
           # print([e],[i[:100]])
            #print(longest_words([e])[0])
            #if e[:9] != '<!DOCTYPE':
            if 'DOCTYPE'.lower() not in i.lower():
                print(555)
                d.append(longest_words([e])[0])
                print([e],[i[:100]])
                print(longest_words([e])[0]) 
            else:
                d.append('6565262626262')
                print([e],[i[:100],'6565262626262'])
                #print(longest_words([e])[0])
            break
df = pd.read_csv('eng_names.csv')#['adres'].values
df['street'] = d














# Запуск драйвера




#time.sleep(2)


url = "https://www.tbank.ru/business/contractor/company-pages/papi/dadata/suggestions/api/4_1/rs/suggest/party"

# Replace the query with what you want to search for
payload = {
    "query": "русмарке"   # <-- change this
    # you can add other fields required by the API here
}

# Minimal headers modeled from the request you pasted.
# Update / remove headers as required by the server.
headers = {
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Origin": "https://www.tbank.ru",
    "Referer": "https://www.tbank.ru/business/contractor/legal/1107746478597/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    # If the server expects sessionID or Authorization, add them:
    # "Authorization": "Bearer <token>",
    # "sessionID": "<session-id>",
}

# If you need to send the cookies shown in your capture:
cookies = {
    "__P__wuid": "43f3f1178d503211fcacdbe192c42880",
    "dco.id": "f5b7768f-9164-4c88-967c-00004551e4a1",
    # ... add any other cookie keys you need
}



d = []
n = 1


for name,street,site,tag in zip(df['name'].values,df['street'].values,df['site'].values,df['tag'].values):


    payload = {
    "query": str(name)   # <-- change this
    # you can add other fields required by the API here
}
    #params = {"Query": name}   # pass the human-readable Cyrillic string

    ##time.sleep(2)

    
    with requests.Session() as s:
        # attach cookies to session (optional)
        s.cookies.update(cookies)

        # Send POST with JSON body (requests will set Content-Length automatically)
        resp = s.post(url, json=payload, headers=headers, timeout=20)

       # print("Status:", resp.status_code)
        #print("Response headers:", resp.headers.get("content-type"))
        # Try to decode JSON — guard with try/except because response might be non-JSON
        try:
            data = resp.json()
            #import json
            #print("JSON response:")
            #print(json.dumps(data, ensure_ascii=False, indent=2))

            for i_mad in json.loads(json.dumps(data))['payload']['suggestions']:
                print([i_mad['data']['address']['unrestricted_value']])
                print([street.lower()])
                if street.lower() in i_mad['data']['address']['unrestricted_value'].lower():

                    n = n +1
                    print(n,')')
                    print(i_mad['data']['address']['unrestricted_value'])
                    print(i_mad['data']['ogrn'])
                    cursor.execute('INSERT INTO my_table (site,tag,name,street,ogrn) VALUES ( ?, ?, ?, ?, ?)', (site,tag,name, street, i_mad['data']['ogrn']))
                    conn.commit()
                    break
        except ValueError:
            print("Non-JSON response body:")
            #print(resp.text)
            cursor.execute('INSERT INTO my_table (site,tag,name,street,ogrn) VALUES ( ?, ?, ?, ?, ?)', (site,tag,name, street, 'ValueError'))
            conn.commit()






    





for name,street,site,tag in zip(df['name_discribtion'].values,df['street'].values,df['site'].values,df['tag'].values):

    payload = {
    "query": str(name)   # <-- change this
    # you can add other fields required by the API here
}
    #params = {"Query": name}   # pass the human-readable Cyrillic string

    #time.sleep(2)

    
    with requests.Session() as s:
        # attach cookies to session (optional)
        s.cookies.update(cookies)

        # Send POST with JSON body (requests will set Content-Length automatically)
        resp = s.post(url, json=payload, headers=headers, timeout=20)

        #print("Status:", resp.status_code)
        #print("Response headers:", resp.headers.get("content-type"))
        # Try to decode JSON — guard with try/except because response might be non-JSON
        try:
            data = resp.json()
           
            #print("JSON response:")
            #print(json.dumps(data, ensure_ascii=False, indent=2))

            for i_mad in json.loads(json.dumps(data))['payload']['suggestions']:
                if street.lower() in i_mad['data']['address']['unrestricted_value'].lower():

                    n = n +1
                    print(n,')')
                    print(i_mad['data']['address']['unrestricted_value'])
                    print(i_mad['data']['ogrn'])
                    cursor.execute('INSERT INTO my_table (site,tag,name,street,ogrn) VALUES ( ?, ?, ?, ?, ?)', (site,tag,name, street, i_mad['data']['ogrn']))
                    conn.commit()
                    break
        except ValueError:
            print("Non-JSON response body:")
            #print(resp.text)
            cursor.execute('INSERT INTO my_table (site,tag,name,street,ogrn) VALUES ( ?, ?, ?, ?, ?)', (site,tag,name, street, 'ValueError'))
            conn.commit()






for name,street,site,tag in zip(df['gpt'].values,df['street'].values,df['site'].values,df['tag'].values):

    payload = {
    "query": str(name)   # <-- change this
    # you can add other fields required by the API here
}
    #params = {"Query": name}   # pass the human-readable Cyrillic string

    #time.sleep(2)

    
    with requests.Session() as s:
        # attach cookies to session (optional)
        s.cookies.update(cookies)

        # Send POST with JSON body (requests will set Content-Length automatically)
        resp = s.post(url, json=payload, headers=headers, timeout=20)

        #print("Status:", resp.status_code)
        #print("Response headers:", resp.headers.get("content-type"))
        # Try to decode JSON — guard with try/except because response might be non-JSON
        try:
            data = resp.json()
            
            #print("JSON response:")
            #print(json.dumps(data, ensure_ascii=False, indent=2))

            for i_mad in json.loads(json.dumps(data))['payload']['suggestions']:
                if street.lower() in i_mad['data']['address']['unrestricted_value'].lower():

                    n = n +1
                    print(n,')')
                    print(i_mad['data']['address']['unrestricted_value'])
                    print(i_mad['data']['ogrn'])
                    cursor.execute('INSERT INTO my_table (site,tag,name,street,ogrn) VALUES ( ?, ?, ?, ?, ?)', (site,tag,name, street, i_mad['data']['ogrn']))
                    conn.commit()
                    break
        except ValueError:
            print("Non-JSON response body:")
            #print(resp.text)
            cursor.execute('INSERT INTO my_table (site,tag,name,street,ogrn) VALUES ( ?, ?, ?, ?, ?)', (site,tag,name, street, 'ValueError'))
            conn.commit()


