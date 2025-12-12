
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sqlite3
import time
import pandas as pd
from lxml import html
import re
import requests
from bs4 import BeautifulSoup


conn = sqlite3.connect('ogrn_from_rbc.db')
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




options = Options()
options.add_argument("--auto-open-devtools-for-tabs")
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

# Запуск драйвера
driver = webdriver.Chrome(options=options)

driver.get("https://companies.rbc.ru/search")

time.sleep(2)


#url = "https://spark-interfax.ru/search"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) "
                  "Gecko/20100101 Firefox/118.0"
}
d = []
n = 1


for name,street,site,tag in zip(df['name'].values,df['street'].values,df['site'].values,df['tag'].values):
    #params = {"Query": name}   # pass the human-readable Cyrillic string
    driver.get("https://companies.rbc.ru/search/?query="+str(name))
    time.sleep(2)

    
    
    try:
        html = driver.page_source
        #resp = requests.get(url, params=params, headers=headers, timeout=15, verify=False)
        #resp.raise_for_status()  # raise HTTPError on bad status
        #resp.encoding = resp.apparent_encoding  # ensure correct charset (often utf-8)
        #html = resp.text

        soup = BeautifulSoup(html, "lxml")  # or "html.parser"
        # example: print page title
        #print("Title:", soup.title.string.strip() if soup.title else "no title")
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        #d.append(e)
        cursor.execute('INSERT INTO my_table (site,tag,name,street,ogrn) VALUES ( ?, ?, ?, ?, ?)', (site,tag,name, street, str(e)))
        conn.commit()


    for i_mad in html.split('class="company-detail-layout__aside"')[0].split('class="company-detail-layout__content"')[-1].split('class="company-card info-card"')[1:10]:
        if street.lower() in i_mad.lower():
            n = n +1
            print(n,')',[re.findall(r'\d+', i_mad.split('ОГРН:')[-1].split('class="company-card__block"')[0])[0]])
            
            print([street])
            #d.append(i_mad.split('ОГРН')[-1].split('class="company-card__block"')[0])
            cursor.execute('INSERT INTO my_table (site,tag,name,street,ogrn) VALUES ( ?, ?, ?, ?, ?)', (site,tag,name, street, re.findall(r'\d+', i_mad.split('ОГРН:')[-1].split('class="company-card__block"')[0])[0]))
            conn.commit()
            break
#df['ogrn_mad'] = d

#df.to_csv('ogrn_mad.csv')





for name,street,site,tag in zip(df['name_discribtion'].values,df['street'].values,df['site'].values,df['tag'].values):
    #params = {"Query": name}   # pass the human-readable Cyrillic string
    driver.get("https://companies.rbc.ru/search/?query="+str(name))
    time.sleep(2)

    
    
    try:
        html = driver.page_source
        #resp = requests.get(url, params=params, headers=headers, timeout=15, verify=False)
        #resp.raise_for_status()  # raise HTTPError on bad status
        #resp.encoding = resp.apparent_encoding  # ensure correct charset (often utf-8)
        #html = resp.text

        soup = BeautifulSoup(html, "lxml")  # or "html.parser"
        # example: print page title
        #print("Title:", soup.title.string.strip() if soup.title else "no title")
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        #d.append(e)
        cursor.execute('INSERT INTO my_table (site,tag,name,street,ogrn) VALUES ( ?, ?, ?, ?, ?)', (site,tag,name, street, str(e)))
        conn.commit()


    for i_mad in html.split('class="company-detail-layout__aside"')[0].split('class="company-detail-layout__content"')[-1].split('class="company-card info-card"')[1:10]:
        if street.lower() in i_mad.lower():
            n = n +1
            print(n,')',[re.findall(r'\d+', i_mad.split('ОГРН:')[-1].split('class="company-card__block"')[0])[0]])
            
            print([street])
            #d.append(i_mad.split('ОГРН')[-1].split('class="company-card__block"')[0])
            cursor.execute('INSERT INTO my_table (site,tag,name,street,ogrn) VALUES ( ?, ?, ?, ?, ?)', (site,tag,name, street, re.findall(r'\d+', i_mad.split('ОГРН:')[-1].split('class="company-card__block"')[0])[0]))
            conn.commit()
            break






for name,street,site,tag in zip(df['gpt'].values,df['street'].values,df['site'].values,df['tag'].values):
    #params = {"Query": name}   # pass the human-readable Cyrillic string
    driver.get("https://companies.rbc.ru/search/?query="+str(name))
    time.sleep(2)

    
    
    try:
        html = driver.page_source
        #resp = requests.get(url, params=params, headers=headers, timeout=15, verify=False)
        #resp.raise_for_status()  # raise HTTPError on bad status
        #resp.encoding = resp.apparent_encoding  # ensure correct charset (often utf-8)
        #html = resp.text

        soup = BeautifulSoup(html, "lxml")  # or "html.parser"
        # example: print page title
        #print("Title:", soup.title.string.strip() if soup.title else "no title")
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        #d.append(e)
        cursor.execute('INSERT INTO my_table (site,tag,name,street,ogrn) VALUES ( ?, ?, ?, ?, ?)', (site,tag,name, street, str(e)))
        conn.commit()


    for i_mad in html.split('class="company-detail-layout__aside"')[0].split('class="company-detail-layout__content"')[-1].split('class="company-card info-card"')[1:10]:
        if street.lower() in i_mad.lower():
            n = n +1
            print(n,')',[re.findall(r'\d+', i_mad.split('ОГРН:')[-1].split('class="company-card__block"')[0])[0]])
            
            print([street])
            #d.append(i_mad.split('ОГРН')[-1].split('class="company-card__block"')[0])
            cursor.execute('INSERT INTO my_table (site,tag,name,street,ogrn) VALUES ( ?, ?, ?, ?, ?)', (site,tag,name, street, re.findall(r'\d+', i_mad.split('ОГРН:')[-1].split('class="company-card__block"')[0])[0]))
            conn.commit()
            break