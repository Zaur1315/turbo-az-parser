import json
import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(filename='parser_errors.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


def get_car():
    try:
        with open('db.json', encoding='utf-8') as file:
            db = json.load(file)
    except FileNotFoundError:
        db = {}

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }

    url = 'https://turbo.az/autos?q%5Bsort%5D=&q%5Bmake%5D%5B%5D=&q%5Bmodel%5D%5B%5D=&q%5Bused%5D=&q%5Bregion%5D%5B%5D=&q%5Bregion%5D%5B%5D=1&q%5Bregion%5D%5B%5D=3&q%5Bprice_from%5D=&q%5Bprice_to%5D=7500&q%5Bcurrency%5D=azn&q%5Bloan%5D=0&q%5Bbarter%5D=0&q%5Bcategory%5D%5B%5D=&q%5Bcategory%5D%5B%5D=14&q%5Bcategory%5D%5B%5D=2&q%5Bcategory%5D%5B%5D=28&q%5Bcategory%5D%5B%5D=5&q%5Bcategory%5D%5B%5D=21&q%5Bcategory%5D%5B%5D=6&q%5Bcategory%5D%5B%5D=22&q%5Bcategory%5D%5B%5D=8&q%5Bcategory%5D%5B%5D=1&q%5Bcategory%5D%5B%5D=4&q%5Byear_from%5D=&q%5Byear_to%5D=&q%5Bcolor%5D%5B%5D=&q%5Bfuel_type%5D%5B%5D=&q%5Bgear%5D%5B%5D=&q%5Btransmission%5D%5B%5D=&q%5Btransmission%5D%5B%5D=2&q%5Btransmission%5D%5B%5D=3&q%5Btransmission%5D%5B%5D=4&q%5Bengine_volume_from%5D=&q%5Bengine_volume_to%5D=&q%5Bpower_from%5D=&q%5Bpower_to%5D=&q%5Bmileage_from%5D=&q%5Bmileage_to%5D=500000&q%5Bonly_shops%5D=&q%5Bprior_owners_count%5D%5B%5D=&q%5Bseats_count%5D%5B%5D=&q%5Bmarket%5D%5B%5D=&q%5Bcrashed%5D=1&q%5Bpainted%5D=1&q%5Bfor_spare_parts%5D=0'

    try:
        r = requests.get(url=url, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при выполнении запроса: {e}")
        return {}

    soup = BeautifulSoup(r.text, 'lxml')
    articles_cards = soup.find_all('div', class_='products-i')
    fresh_cars = {}

    for article in articles_cards:
        try:
            article_id = article.find('a', class_="products-i__link").get('href').split('/')[-1].split('-')[0]
        except AttributeError:
            continue
        if article_id in db:
            continue
        else:
            article_url = f'https://turbo.az{article.find("a", class_="products-i__link").get("href")}'
            article_attr = article.find('div', class_='products-i__attributes').text.strip()
            article_info = article.find('div', class_='products-i__datetime').text.strip()
            article_name = article.find('div', class_='products-i__name').text.strip()
            article_price = article.find('div', class_='products-i__price').text.strip()
            article_info_arr = article_info.split(',')
            article_date = article_info_arr[1]
            article_city = article_info_arr[0]
            article_attr_arr = article_attr.split(',')
            article_year = article_attr_arr[0]
            article_engine = article_attr_arr[1]
            article_run = article_attr_arr[2]
            if article_city == 'Bakı' or article_city == 'Sumqayıt':
                db[article_id] = {
                    'id': article_id,
                    'url': article_url,
                    'name': article_name,
                    'price': article_price,
                    'date': article_date,
                    'year': article_year,
                    'engine': article_engine,
                    'run': article_run,
                    'city': article_city,
                }
                fresh_cars[article_id] = {
                    'id': article_id,
                    'url': article_url,
                    'name': article_name,
                    'price': article_price,
                    'date': article_date,
                    'year': article_year,
                    'engine': article_engine,
                    'run': article_run,
                    'city': article_city,
                }

    try:
        with open('db.json', 'w', encoding='utf-8') as file:
            json.dump(db, file, indent=4, ensure_ascii=False)
    except IOError as e:
        logging.error(f"Ошибка при записи в файл: {e}")
    return fresh_cars


def main():
    print(get_car())


if __name__ == "__main__":
    main()