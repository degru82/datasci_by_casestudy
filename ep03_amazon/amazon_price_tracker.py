import requests
import re
import datetime
import pymongo

from bs4 import BeautifulSoup


def extract_url(url):

    # This function takes an Amazon India URL such as:
    # https://www.amazon.in/Samsung-Galaxy-M30-Gradation-Blue/dp/B07HGJJ58K/ref=br_msw_pdt-1?_encoding=UTF8&smid=A1EWEIV3F4B24B&pf_rd_m=A1VBAL9TL5WCBF&pf_rd_s=&pf_rd_r=VFJ98F93X80YWYQNR3GN&pf_rd_t=36701&pf_rd_p=9806b2c4-09c8-4373-b954-bae25b7ea046&pf_rd_i=desktop”
    # and converts them to shorter URL
    # https://www.amazon.in/dp/B07HGJJ58K which is more manageable. Also if the URL is not valid www.amazon.in URL then it would return a None

    if url.find('www.amazon.in') != -1:
        index = url.find('/dp/')
        
        if index != -1:
            index2 = index + 14
            url = 'https://www.amazon.com' + url[index:index2]

        else:
            index = url.find('/gp/')

            if index != -1:
                index2 = index + 22
                url = 'https://www.amazon.com' + url[index:index2]

            else:
                url = None

    else:
        url = None

    return url


def get_converted_price(price):

    # stripped_price = price.strip("$ ,")
    # replaced_price = stripped_price.replace(',', '')
    # converted_price = float(replaced_price)

    converted_price = float(re.sub(r'[^\d.]', '', price))

    return converted_price


def get_product_details(url):

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
    }
    details = {
        "name": "",
        "price": 0,
        "deal": True,
        "url": ""
    }

    _url = extract_url(url)
    if _url == "":
        details = None

    else:
        page = requests.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(page.content, 'html5lib')

        title = soup.find(id='productTitle')
        price = soup.find(id='priceblock_dealprice')
        if price is None:
            price = soup.find(id='priceblock_ourprice')
            details['deal'] = False

        if title is not None and price is not None:
            details['name'] = title.get_text().strip()
            details['price'] = get_converted_price(price.get_text())
            details['url'] = _url
        else:
            return None

        return details


def add_product_detail(details):

    new = db['products']
    ASIN = details['url'][len(details['url'])-10:]
    details['date'] = datetime.datetime.utcnow()

    try:

        new.update_one(
            {
                'asin': ASIN
            },
            {
                '$set': {
                    'asin': ASIN
                },
                '$push': {
                    'details': details
                }
            },
            upsert=True
        )
        return True

    except Exception as identifier:

        print(identifier)
        return False

def get_product_history(asin):

    pass


if __name__ == '__main__':

    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['amazon']

    print(get_product_details("https://www.amazon.com/Samsung-Factory-Unlocked-Warranty-Midnight/dp/B07HR4FVDG/ref=sr_1_1?keywords=samsung+galaxy+note+9&qid=1566209728&s=gateway&sr=8-1"))
