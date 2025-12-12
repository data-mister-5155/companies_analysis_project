import requests
import pandas as pd
import re


df_mass = pd.DataFrame()

n = 0
# Перебираем набор тегов — это основа поиска компаний на сайте
for segment_tag in ['merchendayzing', 'btl', 'full-cycle', 'event', 'communication']:
    # Локальные списки для накопления результатов по текущему тегу
    site = []
    name = []
    money = []
    inddex = []
    date_start = []
    region = []
    humans = []
    # Начальная страница тега (можно параметризовать)
    url = f"https://marketing-tech.ru/company_tags/{segment_tag}/page/2/"
    # Заголовки, чтобы притворяться браузером. Если сайт проверяет UA помогает.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": f"https://marketing-tech.ru/company_tags/{segment_tag}/",
        "Upgrade-Insecure-Requests": "1",
    }
    # Получаем HTML второй страницы только чтобы найти максимальную страницу (fragile)
    response = requests.get(url, headers=headers)

    # Парсим HTML

    integger = response.text.split(
        f'class="page-numbers dots">&hellip;</span>\n<a class="page-numbers" href="https://marketing-tech.ru/company_tags/{segment_tag}/page/')[1].split('/')[0]

    # Пробегаемся по всем страницам от 1 до integger
    for page_mad in range(1, int(integger)+1):

        url = f"https://marketing-tech.ru/company_tags/{segment_tag}/page/{str(page_mad)}/"

        response = requests.get(url, headers=headers)
        n += 1
        print(n, ") Status:", response.status_code)
        # print("Encoding:", response.encoding)

        html = response.text
        # print(page_mad)

        for i in html.split('class="company-header__company-title">\n\n\t\t\t<div class="h4 font-weight-bold">\n\t\t\t\t\n\t\t\t\t<a href="')[1:]:
            site.append(i.split('" data-wpel-link="internal">')[0])
            name.append(i.split('" data-wpel-link="internal">')
                        [1].split('</a>')[0])
            money.append(
                ''.join(i.split('<i class="income-symbol"></i>')[-1].split('\t')).split('<')[0])
            inddex.append(''.join(
                i.split('<i class="trust-index-barchart"></i')[-1].split('\t')).split('<')[0])
            date_start.append(''.join(i.split(
                '>Основана</div>\n\t\t\t\t<div class="table-row__col table-row__col_2">\n\t\t\t\t\t')[-1].split('\t')).split('</div>\n<')[0])
            region.append(''.join(i.split('target="_blank" class="link" data-wpel-link="internal">')
                          [-1].split('\t')).split('<')[0].split('\n')[-1])
            humans.append(''.join(i.split(
                '<div class="table-row__col table-row__col_1">Штат</div>\n\t\t\t\t<div class="table-row__col table-row__col_2">')[-1].split('\t')).split('<')[0])

     # Формируем DataFrame по текущему тэгу
    df = pd.DataFrame({
        "site": site,
        "name": name,
        "money": money,
        "inddex": inddex,
        "date_start": date_start,
        "region": region,
        "humans": humans
    })

    # Иногда в ячейках попадает URL (вложенные ссылки) — заменяем такие кейсы на '-'
    for i in df.columns[1:]:
        df.loc[df[i].str.contains('https://', na=False), i] = '-'

    # Находим компании, у которых в колонке money написано 'млн.' — создаём mask
    mask = df['money'].str.contains(r'млн\.', na=False, regex=True)

    # извлекаем число перед "млн."
    values = df.loc[mask, 'money'].str.extract(r'([\d\.,\s]+)')[0]

    # приводим к числу
    values = (
        values
        .str.replace(' ', '')
        .str.replace(',', '.')
        # Приводим к числовому типу: убираем пробелы, заменяем запятую на точку
        .astype(float)
    )

    # фильтр > 200 млн
    result = df.loc[mask].loc[values > 200]
    # Также объединяем те, у кого указано 'млрд.' (логика: такие компании явно крупные)

    df_btl = pd.concat(
        [df[df['money'].str.contains(r'млрд\.', na=False, regex=True)], result])
    df_btl['segment_tag'] = segment_tag

    df_mass = pd.concat([df_mass, df_btl])  # Добавляем в общий DataFrame

df_mass.to_csv('companies.csv', index=False)

# Сохраняем промежуточный CSV (если понадобится для отладки)


# ----------------------------------------------------------------------
# Второй этап: парсим страницы компаний, собирая адрес, контакты, ОГРН, сайт, описание
# ----------------------------------------------------------------------


print('Второй этап ... Ждем...')

adres = []
contacts = []
ogrn = []
companies_site = []
description = []

# Заголовки чуть другие
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "ru-RU,ru;q=0.5",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
}

for url in df_mass['site']:  # Проходимся по всем URL из df_mass (колонка site)

    response = requests.get(url, headers=headers)

    adres.append(response.text.split(
        '<div class="th pr-1">Адрес</div>\n            <div class="td">\n')[-1].split('</div>\n')[0])
    # Парсим адрес — снова основано на точной структуре HTML.

    contacts.append(response.text.split(
        '<a class="full" href="tel:')[-1].split('" title="')[0])
    # Парсим контактный телефон (берём первую вхожденную ссылку tel:)

    text = re.sub(r'<.*?>', '', response.text.split('ОГРН')[-1]).strip()
    # если в тексте есть не-цифры вокруг — оставить только цифры (по необходимости)
    digits = re.search(r'\d+', text).group(0)
    # ОГРН: берём кусок после слова "ОГРН", очищаем тэги и берем первую последовательность цифр.

    if text[:8] == 'img.lazy':  # Небольшая защита: если текст начинается с 'img.lazy' то похоже, что в разметке нет ОГРН
        ogrn.append('-')
    else:
        ogrn.append(digits)

    companies_site.append(response.text.split(
        'class="company-website-button btn mt-btn text-white font-weight-normal" href="')[-1].split('"')[0])

    text = re.sub(r'<.*?>', '', response.text.split('О компании')[-1]).strip()
    # Описание компании: берём первые 2 предложения после заголовка "О компании"

    description.append('.'.join(text.split('.')[:2]))


# Добавляем найденные колонки в итоговый DataFrame
df_mass["adres"] = adres
df_mass["contacts"] = contacts
df_mass["ogrn"] = ogrn
df_mass["companies_site"] = companies_site
df_mass["description"] = description


def money_to_number(s):
    if pd.isna(s) or s.strip() == '':
        return None
    s = s.lower().replace('\n', '').replace(
        'руб.', '').replace(' ', '').replace('\xa0', '')
    factor = 1
    if 'млн' in s:
        factor = 1_000_000
    elif 'млрд' in s:
        factor = 1_000_000_000
    # найти число через регулярку
    match = re.search(r'[\d]+[.,]?\d*', s)
    if match:
        num = float(match.group(0).replace(',', '.'))
        return num * factor
    else:
        return None


# применяем к колонке
df_mass['money_rub'] = df_mass['money'].apply(money_to_number)


# Преобразуем в числа
df_mass['inddex'] = (df_mass['inddex']
                     .str.replace('>', '')      # убрать '>'
                     .str.strip()               # убрать пробелы и переносы строк
                     .str.replace(',', '.')     # заменить ',' на '.'
                     .astype(float)             # привести к float
                     )


df_mass.to_csv('companies.csv', index=False)  # Финальный дамп
