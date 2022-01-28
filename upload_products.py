import os
from pathlib import Path
from urllib.parse import unquote, urlsplit

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


def download_file(url):
    response = requests.get(url)
    response.raise_for_status()
    url_path = urlsplit(url).path
    filename = unquote(Path(url_path).name)
    
    with open(filename, 'wb') as file:
        file.write(response.content)

    return filename


def add_file(access_token, url): 

    filepath = download_file(url)

    url = 'https://api.moltin.com/v2/files'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    files = {
        'file': open(filepath, 'rb'),
        'public': True

    }
    response = requests.post(url, headers=headers, files=files)
    os.remove(filepath)
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
        json=data
    )

    return response.json()


def add_product_to_moltin(product):
    moltin_product = add_product(
        access_token=access_token,
        name=product['name'], 
        slug=slugify(product['name']),
        sku=str(product['id']),
        description=product['description'],
        price=product['price']
    )
    product_id = moltin_product['data']['id']
    img = add_file(access_token, product['product_image']['url'])
    img_id = img['data']['id']
    create_main_image(access_token, img_id, product_id)


if __name__ == '__main__':
    load_dotenv()
    client_id = os.environ['CLIENT_ID']
    client_secret = os.environ['CLIENT_SECRET']

    address_urls = 'https://dvmn.org/media/filer_public/90/90/9090ecbf-249f-42c7-8635-a96985268b88/addresses.json'
    menu_urls = 'https://dvmn.org/media/filer_public/a2/5a/a25a7cbd-541c-4caf-9bf9-70dcdf4a592e/menu.json'

    addresses = requests.get(address_urls).json()
    products = requests.get(menu_urls).json()

    access_token = get_token(client_id, client_secret)

    for product in products:
        add_product_to_moltin(product)
