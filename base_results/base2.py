import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

# Загружаем исходный CSV
df = pd.read_csv('companies.csv')

# Фильтруем строки с ОГРН
df2 = df[df['ogrn'] != '-'].copy()

# Списки для результатов
inn_list = []
kpp_list = []
okved_list = []
employees_list = []
revenue_year_list = []
revenue_list = []
source_json_list = []

# Заголовки
headers_1 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0 Safari/537.36",
}

headers_2 = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "ru",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Referer": "https://companies.rbc.ru/"
}

# Сессия для запросов
s = requests.Session()
s.headers.update(headers_1)

# Основной цикл
for idx, ogrn in enumerate(df2['ogrn'], 1):
    url = f"https://companies.rbc.ru/id/{ogrn}-ooo-ooo-moskou-iven/"
    try:
        resp = s.get(url, timeout=15)
        print(idx, url, "status:", resp.status_code)
        resp.raise_for_status()
        html = resp.text

        soup = BeautifulSoup(html, "html.parser")

        # ИНН
        inn_el = soup.find("div", text="ИНН")
        inn_value = inn_el.find_next_sibling(
            "div").text.strip() if inn_el else ""
        inn_list.append(inn_value)

        # КПП
        kpp_el = soup.find("div", text="КПП")
        kpp_value = kpp_el.find_next_sibling(
            "div").text.strip() if kpp_el else ""
        kpp_list.append(kpp_value)

        # Основной ОКВЭД
        okved_el = soup.find("div", text="Основной")
        okved_value = okved_el.find_next(
            "span").text.strip() if okved_el else ""
        okved_list.append(okved_value)

        # Среднесписочная численность
        emp_el = soup.find("div", text="Среднесписочная численность")
        emp_value = emp_el.find_next_sibling(
            "div").text.strip() if emp_el else ""
        employees_list.append(emp_value)

        # --- Финансовые данные через API ---
        if inn_value:  # только если ИНН есть
            params = {"inn": inn_value}
            resp2 = s.get("https://companies.rbc.ru/api/web/v1/financial-indicators/",
                          params=params, headers=headers_2, timeout=15)
            resp2.raise_for_status()
            data = resp2.json()
            source_json_list.append(str(data))

            if data:  # если есть финансовые данные
                max_item = max(data, key=lambda x: x["data"].get("2110", 0))
                revenue_year_list.append(max_item["year"])
                revenue_list.append(max_item["data"].get("2110", 0))
            else:
                revenue_year_list.append("")
                revenue_list.append("")
        else:
            source_json_list.append("")
            revenue_year_list.append("")
            revenue_list.append("")

        time.sleep(1)  # чтобы не нагружать сервер

    except Exception as e:
        print("Error:", e)
        inn_list.append("")
        kpp_list.append("")
        okved_list.append("")
        employees_list.append("")
        revenue_year_list.append("")
        revenue_list.append("")
        source_json_list.append("")

# Присваиваем в DataFrame
df2['inn'] = pd.Series(inn_list, dtype='string')
df2['kpp'] = pd.Series(kpp_list, dtype='string')
df2['okved_main'] = pd.Series(okved_list, dtype='string')
df2['employees'] = pd.Series(employees_list, dtype='string')
df2['revenue_year'] = pd.Series(revenue_year_list, dtype='string')
df2['revenue'] = pd.Series(revenue_list, dtype='string')
df2['source_json'] = pd.Series(source_json_list, dtype='string')

# Объединяем с компаниями без ОГРН
df_mass = pd.concat([df2, df[df['ogrn'] == '-']], ignore_index=True)
df_mass.to_csv('companies.csv', index=False)
df_mass.to_excel('companies.xlsx', index=False)
