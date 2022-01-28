import os

import requests
from dotenv import load_dotenv
from slugify import slugify


def get_token(client_id, client_secret):
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }

    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    response.raise_for_status()
    return response.json()['access_token']


def add_product(access_token, name, slug, sku, description, price):

    headers = {
        'Authorization': access_token,
        'Content-Type': 'application/json',
    }

    product_descriprion = {
        'type': 'product',
        'name': name,
        'slug': slug,
        'sku': sku,
        'description': description,
        'manage_stock': False,
        'price': [
            {
                'amount': price,
                'currency': 'RUB',
                'includes_tax': True
            }
        ],
        'status': 'live',
        'commodity_type': 'physical'
    }

    response = requests.post(
        'https://api.moltin.com/v2/products',
        headers=headers,
        json={'data': product_descriprion}
    )

    return response.json()


def add_file(access_token, file_url): 

    headers = {
        'Content-Type': 'multipart/form-data',
        'Authorization': access_token   ,
    }

    files = {
        'file-location': file_url,
    }

    response = requests.post('https://api.moltin.com/v2/files', headers=headers, files=files)

    return response.json()


def create_main_image(access_token, img_id, product_id):
    headers = {
        'Authorization': access_token,
        'Content-Type': 'application/json',
    }

    data = {
        'data': {
            'type': 'main_image',
            'id': img_id
        }
    }

    response = requests.post(
        'https://api.moltin.com/v2/products/{}/relationships/main-image'.format(product_id),
        headers=headers,
        data=data
    )

    return response.json()


load_dotenv()
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']

address_urls = 'https://dvmn.org/media/filer_public/90/90/9090ecbf-249f-42c7-8635-a96985268b88/addresses.json'
menu_urls = 'https://dvmn.org/media/filer_public/a2/5a/a25a7cbd-541c-4caf-9bf9-70dcdf4a592e/menu.json'

addresses = requests.get(address_urls).json()
products = requests.get(menu_urls).json()
product_test = products[0]

access_token = get_token(client_id, client_secret)

product = add_product(
    access_token=access_token,
    name=product_test['name'], 
    slug=slugify(product_test['name']),
    sku=str(product_test['id']),
    description=product_test['description'],
    price=product_test['price']
)
product_id = product['data']['id']

url = 'https://dodopizza-a.akamaihd.net/static/Img/Products/Pizza/ru-RU/1626f452-b56a-46a7-ba6e-c2c2c9707466.jpg'
img = add_file(access_token, url)
print(img)
img_id = img['data']['id']

create_main_image(access_token, img_id, product_id)
